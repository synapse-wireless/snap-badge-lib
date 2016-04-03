"""RPS - Rock, Paper, Scissors game
   A timeless classic way to make life's many unimportant decisions. Let random fate decide!
   SPLUNGE!

Usage:
  Press Left or Right button to reset game.
  Use classic "down" motion with badge to sequence through RPS states: 1-2-3.
  On '3' your random choice will be displayed, and sent to other players!
  Multiplayer results are as follows:
    If it's a tie, all winners will flash.
    If you win, you'll see a victory animation.
    If you lose


"""

from drivers.snap_badge import *
from drivers.Doodads import *
from animation import *
from drivers.true_random import *
from gestures import *

NEARBY_SIGNAL = 60   # Threshold for nearby badges we want to associate with (-dBm)

def rps_start():
    """Startup hook when run standalone"""
    global current_context
    current_context = rps_context
    set_display_driver(as1115_write_matrix_symbol)
    badge_start()
    rps_init()
    
def rps_init():
    """Initialize application - get our animation icons loaded up"""
    gesture_set_callback(rps_gestures)
    load_font(Doodads, Doodads_widths)
    
def rps_gestures(gest_type):
    """Callback from gesture detection lib"""
    if gest_type == GESTURE_DOWN:
        rps_fist()

def rps_fist():
    """Fist down event"""
    print "Fist!"

def rps_tick10ms():
    """Called by system every 10ms"""
    global rps_inertial_debounce

    gesture_poll_10ms()


# Hook context, for multi-app switching via app_switch.py
rps_context = (rps_init, None, rps_tick10ms, None, None, None)

# Set hooks if running game standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, rps_start)
    snappyGen.setHook(SnapConstants.HOOK_10MS, rps_tick10ms)



    