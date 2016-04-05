"""Drive the robot - this is the main SNAPpy script for the Badge-robot.

The robot uses an Adafruit motor shield v2, driving a low-cost dual-motor platform.
This script is loaded on the badge which is mounted to the robot, with the motor shield attached.

Functions are defined here to allow easy over-the-air control from a remote SNAP device.
The direct low-level ada_moto_* commands can also be called over the air.

"""

from drivers.snap_badge import *
from snap_shields.ada_moto_v2 import *
from sweep_leds import *

# Define H-bridge channels our motors are attached to
ROBOT_MOTOR_LEFT = 3
ROBOT_MOTOR_RIGHT = 2


# The following speed is conservative (it can go MUCH faster)
ROBOT_SPEED = 80
TURN_DIFF = 25

def set_speed(new_speed):
    global ROBOT_SPEED
    ROBOT_SPEED = new_speed

@setHook(HOOK_STARTUP)
def start():
    badge_start()
    ada_moto_init()

@setHook(HOOK_100MS)
def tick100ms():
    sweep_tick()

#
# Robot capabilities
#
def robot_forward():
    ada_moto_fwd(ROBOT_MOTOR_LEFT, ROBOT_SPEED)
    ada_moto_fwd(ROBOT_MOTOR_RIGHT, ROBOT_SPEED)

def robot_forward_and_left():
    ada_moto_fwd(ROBOT_MOTOR_LEFT, ROBOT_SPEED-TURN_DIFF)
    ada_moto_fwd(ROBOT_MOTOR_RIGHT, ROBOT_SPEED)

def robot_forward_and_right():
    ada_moto_fwd(ROBOT_MOTOR_LEFT, ROBOT_SPEED)
    ada_moto_fwd(ROBOT_MOTOR_RIGHT, ROBOT_SPEED-TURN_DIFF)

def robot_backward():
    ada_moto_rev(ROBOT_MOTOR_LEFT, ROBOT_SPEED)
    ada_moto_rev(ROBOT_MOTOR_RIGHT, ROBOT_SPEED)

def robot_backward_and_left():
    ada_moto_rev(ROBOT_MOTOR_LEFT, ROBOT_SPEED)
    ada_moto_rev(ROBOT_MOTOR_RIGHT, ROBOT_SPEED-TURN_DIFF)

def robot_backward_and_right():
    ada_moto_rev(ROBOT_MOTOR_LEFT, ROBOT_SPEED-TURN_DIFF)
    ada_moto_rev(ROBOT_MOTOR_RIGHT, ROBOT_SPEED)

def robot_spin_left():
    ada_moto_rev(ROBOT_MOTOR_LEFT, ROBOT_SPEED)
    ada_moto_fwd(ROBOT_MOTOR_RIGHT, ROBOT_SPEED)

def robot_spin_right():
    ada_moto_fwd(ROBOT_MOTOR_LEFT, ROBOT_SPEED)
    ada_moto_rev(ROBOT_MOTOR_RIGHT, ROBOT_SPEED)

def robot_all_stop():
    ada_moto_stop(ROBOT_MOTOR_LEFT)
    ada_moto_stop(ROBOT_MOTOR_RIGHT)


# The following is about mapping remote commands to local capabilities.
# The extra level of indirection is to keep the two codebases decoupled.
# See remote.py for WHERE these RPCs come from
def remote_says_up():
    robot_forward()

def remote_says_up_left():
    robot_forward_and_left()

def remote_says_up_right():
    robot_forward_and_right()

def remote_says_down():
    robot_backward()

def remote_says_down_left():
    robot_backward_and_left()

def remote_says_down_right():
    robot_backward_and_right()

def remote_says_left():
    robot_spin_left()

def remote_says_right():
    robot_spin_right()

def remote_says_centered():
    robot_all_stop()
