"""ESC Badge - master script for SNAP Badges at ESC 

Operation: This script manages a top-level menu, and invokes "sub-application" scripts.

Initial state is running "show scroller" script.
  - When both buttons pressed, enter "menu select" mode
        - Select from the following:
            - Show scroller (includes "hello" multiplayer mode)
            - Enter personal message (see user_message.py for details)
            - RPS game (multiplayer)
            - Snake game
            - Rollerball game
            - Breakout game
            - Dice (multiplayer)
            - Reflex test (reaction game)
            - Spirit Level
            - Spectrum Analyzer
            - Robot Controller

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
from badge_post import *
from user_message import *
from level import *
from spectrum import *
from reflex import *

# Top menu icons are a range of Doodads fontset
esc_topmenu_icons = '\x80\x81\x82\x83\x84\x85\x0B\x87\x88\x89\x8A'

esc_selection_contexts = (show_scroller_context,
                          user_message_context,  # user_msg
                          rps_context,  # RPS
                          snake_context,  # snake
                          rollerball_context,  # rollerball
                          breakout_context,  # breakout
                          dice_context,  # dice
                          reflex_context,  # reflex
                          level_context,  # level
                          spectrum_context,  # spectrum
                          remote_context)  # robot controller

esc_btn_hold = 0
cur_topmenu_selection = 0
lock_rotation = False

@setHook(HOOK_STARTUP)
def start():
    global lock_rotation
    
    set_display_driver(as1115_write_matrix_symbol)
    badge_start()
    
    # We need buttons
    setPinDir(BUTTON_LEFT, False)
    setPinPullup(BUTTON_LEFT, True)
    monitorPin(BUTTON_LEFT, True)
    setPinDir(BUTTON_RIGHT, False)
    setPinPullup(BUTTON_RIGHT, True)
    monitorPin(BUTTON_RIGHT, True)
    
    # Reduce radio transmit power, since we only want to socialize with nearby badges
    # Hold right button on boot to get default higher tx power
    if readPin(BUTTON_RIGHT):
        txPwr(0)   # approx 0dBm
    
    # Hold left button on boot to lock rotation
    lock_rotation = not readPin(BUTTON_LEFT)
    
    # Initialize the app-switching...
    app_switch_set_exit(enter_top_menu)
    app_switch_set_background_1s(esc_background_tick)
    
    # Initially, default to "show_scroller" app
    app_switch(show_scroller_context)
    
    
def menu_hook(menu_selected):
    global cur_topmenu_selection
    cur_topmenu_selection = menu_selected
    context = esc_selection_contexts[menu_selected]
    if context:
        app_switch(context)

def enter_top_menu():
    """This is the app_exit() hook for sub-menu scripts - returns execution to top menu"""
    menu_define(esc_topmenu_icons, Doodads, Doodads_widths, menu_hook, cur_topmenu_selection)
    
    # Assorted cleanup
    as1115_wr(FEATURE, 0)  # Disable blinking and other shenanigans

    # Switch to the "menu_select" app
    app_switch(menu_context)
    
    menu_play_exit_anim()
    
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

    if not lock_rotation:
        poll_rotation()
    
def poll_rotation():
    """Support screen-rotation"""
    lis_read()
    print lis_axis_x, ",", lis_axis_y, ",", lis_axis_z
    
    # Rotate display, with deadband around lying flat
    if lis_axis_y > 5000 or lis_axis_y < -5000:
        rot = 180 if lis_axis_y > 0 else 0
        set_screen_rotation(rot)

