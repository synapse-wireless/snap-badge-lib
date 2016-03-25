"""ESC Badge - master script for SNAP Badges at ESC 

Operation:

Always send "heartbeat" mcast 1-hop every 5 sec.

Initial state is running "show scroller" script.
  - Scrolls default (ESC 2016) or personalized message, plus "interest" icons
  - When near another badge (heartbeat RSSI high), flash "HI"
        - When other badge matches our "interests", flash special sequence
  - When near "many" other badges (N > 5), flash synchronized fireworks
  - "Master Show Broadcast" can override all other modes, with synchronized message for display
  - NOTE: S8 is the "Anti-Social" bit. When ON, you don't participate in remote-initiated multiplayer modes...
  - When both buttons pressed, enter "menu select" mode
        - Select from the following:
            - Enter personal message
            - RPS game (host/join)  ** NOTE: Default game running in SHOW mode
                                    **       (shake while holding button to start)
            - Snake game
            - Rollerball game
            - Breakout game
            - Dice
            - Reflex test (reaction game)
            - Spirit Level
            - Spectrum Analyzer
            - Robot Controller
            - ??Maze tag game (host/join)
            - ??Pong game (host/join)

"""

from drivers.snap_badge import *

from app_switch import *
app_hook_init(snappyGen.setHook)

from snake import *
from menu_select import *
from drivers.Doodads import *
from show_scroller import *

# Top menu icons are a range of Doodads fontset
esc_topmenu_icons = ''.join([chr(rc) for rc in xrange(128,139)])
esc_selection_contexts = (show_scroller_context,
                          None,  # user_msg
                          None,  # RPS
                          snake_context,  # snake
                          None,  # rollerball
                          None,  # breakout
                          None,  # dice
                          None,  # reflex
                          None,  # level
                          None,  # spectrum
                          None)  # robot controller


@setHook(HOOK_STARTUP)
def start():
    set_display_driver(as1115_write_matrix_symbol)
    badge_start()
    
    # We need buttons
    setPinDir(BUTTON_LEFT, False)
    setPinPullup(BUTTON_LEFT, True)
    monitorPin(BUTTON_LEFT, True)
    setPinDir(BUTTON_RIGHT, False)
    setPinPullup(BUTTON_RIGHT, True)
    monitorPin(BUTTON_RIGHT, True)
    
    app_switch_set_exit(enter_top_menu)
    app_switch(show_scroller_context)
    
def menu_hook(menu_selected):
    context = esc_selection_contexts[menu_selected]
    if context:
        app_switch(context)

def enter_top_menu():
    """The app_exit() hook for sub-menu scripts - returns execution to top menu"""
    menu_define(esc_topmenu_icons, Doodads, Doodads_widths, menu_hook, 0)
    app_switch(menu_context)
    
    