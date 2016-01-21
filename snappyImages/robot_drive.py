"""Drive the robot"""

from drivers.snap_badge import *
from snap_shields.ada_moto_v2 import *

ROBOT_MOTOR_LEFT = 3
ROBOT_MOTOR_RIGHT = 2

#
# The following are 1: Conservative (it can go MUCH faster) and
# 2: currently reversed, since higher duty cycle == SLOWER
#
ROBOT_SPEED = 50
TURN_DIFF = 25

def set_speed(new_speed):
    global ROBOT_SPEED
    ROBOT_SPEED = new_speed

@setHook(HOOK_STARTUP)
def start():
    badge_start()
    ada_moto_init()

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
