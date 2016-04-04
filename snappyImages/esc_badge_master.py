"""ESC Badge - master script for SNAP Badges at ESC 

Operation:

Always send "heartbeat" mcast 1-hop every 5 sec.

Initial state is running "show scroller" script.
  - Scrolls default (ESC 2016) or personalized message, plus "interest" icons
  - When near another badge (heartbeat RSSI high), flash "HI"
        - When other badge matches our "interests", flash special sequence
  - When near "many" other badges (N > 5), flash synchronized fireworks
  
  - "Master Show Broadcast" can override all other modes, with synchronized message for display
    ** Initiated from laptop (Synapse guys)
    ** Messages MUST synchronize among all badges!!!
  - Contest mode:
    ** Initially all count down: 10...3..2...1...
    ** All flashing in synchronicity (flash/flash/flash x 10 cycles)
    ** Successively, badges fade to dark until only winner remains!
    ** Final winner enters "happy dance"
    
  - NOTE: S8 is the "Anti-Social" bit. When ON, you don't participate in remote-initiated multiplayer modes (including HI)...
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
from menu_select import *
from drivers.Doodads import *

from snake import *
from show_scroller import *
from rollerball import *
from breakout import *
from remote import *
from dice import *
from rps import *

# Top menu icons are a range of Doodads fontset
esc_topmenu_icons = '\x80\x81\x82\x83\x84\x85\x92\x87\x88\x89\x8A'

esc_selection_contexts = (show_scroller_context,
                          None,  # user_msg
                          rps_context,  # RPS
                          snake_context,  # snake
                          rollerball_context,  # rollerball
                          breakout_context,  # breakout
                          dice_context,  # dice
                          None,  # reflex
                          None,  # level
                          None,  # spectrum
                          remote_context)  # robot controller

esc_btn_hold = 0

@setHook(HOOK_STARTUP)
def start():
    set_display_driver(as1115_write_matrix_symbol)
    badge_start()
    
    # Reduce radio transmit power, since we only want to socialize with nearby badges
    txPwr(0)   # approx 0dBm
    
    # We need buttons
    setPinDir(BUTTON_LEFT, False)
    setPinPullup(BUTTON_LEFT, True)
    monitorPin(BUTTON_LEFT, True)
    setPinDir(BUTTON_RIGHT, False)
    setPinPullup(BUTTON_RIGHT, True)
    monitorPin(BUTTON_RIGHT, True)
    
    # Initialize the app-switching...
    app_switch_set_exit(enter_top_menu)
    app_switch_set_background_1s(esc_background_tick)
    
    # Initially, default to "show_scroller" app
    app_switch(show_scroller_context)
    
def menu_hook(menu_selected):
    context = esc_selection_contexts[menu_selected]
    if context:
        app_switch(context)

def enter_top_menu():
    """This is the app_exit() hook for sub-menu scripts - returns execution to top menu"""
    menu_define(esc_topmenu_icons, Doodads, Doodads_widths, menu_hook, menu_selected)
    
    # Assorted cleanup
    as1115_wr(FEATURE, 0)  # Disable blinking and other shenanigans

    # Switch to the "menu_select" app
    app_switch(menu_context)
    
def esc_background_tick():
    """Called every 1s tick"""
    global esc_btn_hold
    
    # Detect "both buttons held" exit command
    lb = not readPin(BUTTON_LEFT)
    rb = not readPin(BUTTON_RIGHT)
    
    # Exit to menu if both buttons held for 1-2 secs
    if lb and rb:
        esc_btn_hold += 1
        if esc_btn_hold == 2:
            enter_top_menu()
            esc_btn_hold = 0
    else:
        esc_btn_hold = 0
