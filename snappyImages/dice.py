"""Dice - daily dose of random for the SNAP Badge

Detect "dice roll" motion using the accelerometer: hold badge vertical, then horizontal to 
throw the dice.

Multiplayer mode: when multiple nearby badges are running this script, a dice roll on one will trigger
the others. This allows any number of dice to be thrown simultaneously.

"""

from drivers.snap_badge import *
from drivers.fonts_8x8 import *
from drivers.Doodads import *
from animation import *
from drivers.true_random import *

# Dice icons are the following indices of Doodads fontset
dice_icons = '\x07\x08\x09\x0A\x0B\x0C\x0D'

dice_is_vert = False
NEARBY_SIGNAL = 60   # Threshold for nearby badges we want to associate with (-dBm)

def dice_start():
    """Startup hook when run standalone"""
    global current_context
    current_context = dice_context
    set_display_driver(as1115_write_matrix_symbol)
    badge_start()
    dice_init()
    
def dice_init():
    """Initialize application - get our animation icons loaded up"""
    load_font(Doodads, Doodads_widths)
    anim_init(dice_icons, 8, dice_anim_done)

def dice_anim_done():
    """End of 'dice roll' animation is when we actually choose the randomized result"""
    i = true_random() / 683   # Scale from 0-4095 to range 0-5
    anim_show(i)

def dice_down():
    """Someone has thrown down the dice! Triggered by accelerometer."""
    anim_begin()
    mcastRpc(1, 1, 'dice_remote_down')

def dice_remote_down():
    """Remote RPC call - another die was thrown, so let's join the game"""
    # Only respond if badge is in "dice" mode
    if current_context == dice_context:
        # Only respond to nearby badges 
        if getLq() < NEARBY_SIGNAL:
            anim_begin()

def dice_tick10ms():
    """Called by system every 10ms"""
    global dice_is_vert
    
    # Call the animation tick
    anim_tick10ms()
    
    # Poll the accelerometer. Hold the badge vertical, then horizontal to "throw" dice.
    lis_read()
    #print lis_axis_x, ",", lis_axis_y, ",", lis_axis_z
    if lis_axis_z < 1000:
        dice_is_vert = True
    elif lis_axis_z > 10000:
        if dice_is_vert:
            dice_down()
        dice_is_vert = False
            

# Hook context, for multi-app switching via app_switch.py
dice_context = (dice_init, None, dice_tick10ms, None, None, None)

# Set hooks if running game standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, dice_start)
    snappyGen.setHook(SnapConstants.HOOK_10MS, dice_tick10ms)



    