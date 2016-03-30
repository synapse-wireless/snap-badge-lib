"""Using the accelerometer to make a remote control"""

from drivers.snap_badge import *
from eight_way_symbols import *

ACCEL_THRESHOLD = 1500 # smaller number makes it more sensitive to tilt, bigger = less sensitive


def remote_start():
    """Startup hook when run standalone"""
    badge_start()
    
    monitorPin(BUTTON_LEFT, True)
    monitorPin(BUTTON_RIGHT, True)
    remote_init()

def remote_init():
    as1115_write_matrix_symbol(CENTER_SQUARE)

def remote_tick100ms():
    if readPin(BUTTON_RIGHT) == False:
        poll_accelerometer()

def remote_pin_event(pin, is_set):
    if not is_set: # Presses...
        if pin == BUTTON_LEFT:
            centered()
        elif pin == BUTTON_RIGHT:
            pass # Other code checks that it is being HELD DOWN
    else: # Releases...
        if pin == BUTTON_LEFT:
            pass # available
        elif pin == BUTTON_RIGHT:
            centered()

def up():
    as1115_write_matrix_symbol(UP_ARROW)
    if readPin(BUTTON_RIGHT) == False:
        mcastRpc(1, 1, "remote_says_up")

def up_right():
    as1115_write_matrix_symbol(UP_RIGHT_ARROW)
    if readPin(BUTTON_RIGHT) == False:
        mcastRpc(1, 1, "remote_says_up_right")

def up_left():
    as1115_write_matrix_symbol(UP_LEFT_ARROW)
    if readPin(BUTTON_RIGHT) == False:
        mcastRpc(1, 1, "remote_says_up_left")

def down():
    as1115_write_matrix_symbol(DOWN_ARROW)
    if readPin(BUTTON_RIGHT) == False:
        mcastRpc(1, 1, "remote_says_down")

def down_right():
    as1115_write_matrix_symbol(DOWN_RIGHT_ARROW)
    if readPin(BUTTON_RIGHT) == False:
        mcastRpc(1, 1, "remote_says_down_right")

def down_left():
    as1115_write_matrix_symbol(DOWN_LEFT_ARROW)
    if readPin(BUTTON_RIGHT) == False:
        mcastRpc(1, 1, "remote_says_down_left")

def left():
    as1115_write_matrix_symbol(LEFT_ARROW)
    if readPin(BUTTON_RIGHT) == False:
        mcastRpc(1, 1, "remote_says_left")

def right():
    as1115_write_matrix_symbol(RIGHT_ARROW)
    if readPin(BUTTON_RIGHT) == False:
        mcastRpc(1, 1, "remote_says_right")

def centered():
    as1115_write_matrix_symbol(CENTER_SQUARE)
    mcastRpc(1, 1, "remote_says_centered")

def poll_accelerometer():
    lis_read() # Get the instantaneous accelerations from the accelerometer

    # Translate 4-way tilt into 9 possible commands

    tilt_up = False
    tilt_down = False
    if lis_axis_y > ACCEL_THRESHOLD:
        tilt_up = True
    elif lis_axis_y < -ACCEL_THRESHOLD:
        tilt_down = True

    tilt_left = False
    tilt_right = False
    if lis_axis_x > ACCEL_THRESHOLD:
        tilt_right = True
    elif lis_axis_x < -ACCEL_THRESHOLD:
        tilt_left = True

    # If they are holding the remote level
    if not (tilt_up or tilt_down or tilt_left or tilt_right):
        centered()
    elif tilt_up:
        if tilt_left:
            up_left()
        elif tilt_right:
            up_right()
        else:
            up()
    elif tilt_down:
        if tilt_left:
            down_left()
        elif tilt_right:
            down_right()
        else:
            down()
    elif tilt_left:
        left() # diagonals already checked up above...
    elif tilt_right:
        right() # diagonals already checked up above...

# Hook context, for multi-app switching via app_switch.py
remote_context = (remote_init, None, None, remote_tick100ms, None, remote_pin_event)

# Set hooks if running game standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, remote_start)
    snappyGen.setHook(SnapConstants.HOOK_100MS, remote_tick100ms)
    snappyGen.setHook(SnapConstants.HOOK_GPIN, remote_pin_event)



