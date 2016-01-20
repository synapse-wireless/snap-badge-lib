"""Using the accelerometer to make a remote control"""

from drivers.snap_badge import *
from drivers.lis3dh_accel import *

ACCEL_THRESHOLD = 1500 # smaller number makes it more sensitive to tilt, bigger = less sensitive

# OOOOOOOO
# OOOOOOOO
# OOOOOOOO
# OOO**OOO
# OOO**OOO
# OOOOOOOO
# OOOOOOOO
# OOOOOOOO
CENTER_SQUARE = "\x00\x00\x00\x18\x18\x00\x00\x00"

# OOO**OOO
# OO****OO
# O******O
# OOO**OOO
# OOO**OOO
# OOOOOOOO
# OOOOOOOO
# OOOOOOOO
UP_ARROW = "\x18\x3C\x7E\x18\x18\x00\x00\x00"

# OOOOOOOO
# OOOOOOOO
# OOOOOOOO
# OOO**OOO
# OOO**OOO
# O******O
# OO****OO
# OOO**OOO
DOWN_ARROW = "\x00\x00\x00\x18\x18\x7E\x3C\x18"

# OOOOOOOO
# OO*OOOOO
# O**OOOOO
# *****OOO
# *****OOO
# O**OOOOO
# OO*OOOOO
# OOOOOOOO
LEFT_ARROW = "\x00\x20\x60\xF8\xF8\x60\x20\x00"

# OOOOOOOO
# OOOOO*OO
# OOOOO**O
# OOO*****
# OOO*****
# OOOOO**O
# OOOOO*OO
# OOOOOOOO
RIGHT_ARROW = "\x00\x04\x06\x1F\x1F\x06\x04\x00"


@setHook(HOOK_STARTUP)
def start():
    uniConnect(3,4)
    uniConnect(3,5)
    ucastSerial("\x00\x00\x01")

    badge_init_pins()
    lis_init()
    badge_led_array_enable(True)
    as1115_wr(GLOB_INTENS, 10) # (I just don't like full brightness, your eyes may vary)
    
    monitorPin(BUTTON_LEFT, True)
    monitorPin(BUTTON_RIGHT, True)

    as1115_write_matrix_symbol(CENTER_SQUARE)

@setHook(HOOK_100MS)
def tick():
    if readPin(BUTTON_RIGHT) == False:
        poll_accelerometer()

@setHook(HOOK_GPIN)
def pin_event(pin, is_set):
    if not is_set:
        if pin == BUTTON_LEFT:
            stop()
        elif pin == BUTTON_RIGHT:
            pass

def move_up():
    print "up"
    as1115_write_matrix_symbol(UP_ARROW)
    if readPin(BUTTON_RIGHT) == False:
        mcastRpc(1, 1, "remote_says_up")

def move_down():
    print "down"
    if readPin(BUTTON_RIGHT) == False:
        as1115_write_matrix_symbol(DOWN_ARROW)
    mcastRpc(1, 1, "remote_says_down")

def move_left():
    print "left"
    if readPin(BUTTON_RIGHT) == False:
        as1115_write_matrix_symbol(LEFT_ARROW)
    mcastRpc(1, 1, "remote_says_left")

def move_right():
    print "right"
    if readPin(BUTTON_RIGHT) == False:
        as1115_write_matrix_symbol(RIGHT_ARROW)
    mcastRpc(1, 1, "remote_says_right")

def stop():
    print "stop"
    mcastRpc(1, 1, "remote_says_stop")
    as1115_write_matrix_symbol(CENTER_SQUARE)

def poll_accelerometer():
    lis_read() # Get the instantaneous accelerations from the accelerometer

    y_axis = True
    if lis_axis_y > ACCEL_THRESHOLD:
        move_up()
    elif lis_axis_y < -ACCEL_THRESHOLD:
        move_down()
    else:
        y_axis = False

    x_axis = True
    if lis_axis_x > ACCEL_THRESHOLD:
        move_right()
    elif lis_axis_x < -ACCEL_THRESHOLD:
        move_left()
    else:
        x_axis = False

    if  not x_axis and not y_axis:
        stop()

