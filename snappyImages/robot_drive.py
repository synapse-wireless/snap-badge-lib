"""Drive the robot"""

from drivers.snap_badge import *
from snap_shields.ada_moto_v2 import *

ROBOT_MOTOR_LEFT = 3
ROBOT_MOTOR_RIGHT = 2

ROBOT_SPEED = 1

def set_speed(new_speed):
    global ROBOT_SPEED
    ROBOT_SPEED = new_speed

@setHook(HOOK_STARTUP)
def start():
    badge_start()
    ada_moto_init()

def robot_forwards():
    ada_moto_fwd(ROBOT_MOTOR_LEFT, ROBOT_SPEED)
    ada_moto_fwd(ROBOT_MOTOR_RIGHT, ROBOT_SPEED)

def robot_backwards():
    ada_moto_rev(ROBOT_MOTOR_LEFT, ROBOT_SPEED)
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


# The following is about mapping remote commands to local capabilities
# The extra level of indirection is to keep the two codebases decoupled
# See remote.py for where these come from
def remote_says_up():
    robot_forwards()

def remote_says_down():
    robot_backwards()

def remote_says_left():
    robot_spin_left()

def remote_says_right():
    robot_spin_right()

def remote_says_stop():
    robot_all_stop()
