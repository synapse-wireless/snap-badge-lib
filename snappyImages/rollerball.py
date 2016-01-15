"""SNAP Badge Accelerometer Experiments"""

from drivers.snap_badge import *
from drivers.lis3dh_accel import *
from pixel_lib import *
from fixed_point import *

# FP stands for Fixed Point...

# MAke FP counterparts to some contants from pixel_lib
FP_MIN_X = to_FP(MIN_X, 0)
FP_MAX_X = to_FP(MAX_X, 0)
FP_MIN_Y = to_FP(MIN_Y, 0)
FP_MAX_Y = to_FP(MAX_Y, 0)

# NOTE - these have to be set correctly for the chosen FP_SCALING!

# Force a terminal velocity (the screen is not very big!)
TERMINAL_VELOCITY = to_FP(1, 0)

# Technically this is % velocity lost due to friction, not the actual friction...
FRICTION = to_FP(0, 99)
#FRICTION = to_FP(1, 0) # 100% transfer AKA no loss

REBOUND = to_FP(0, -95) # rebounds in the opposite direction PLUS loses some energy
#REBOUND = to_FP(-1, 0) # rebounds perfectly in the opposite direction

@setHook(HOOK_STARTUP)
def start():
    uniConnect(3,4)
    uniConnect(3,5)
    ucastSerial("\x00\x00\x01")

    badge_init_pins()
    lis_init()
    badge_led_array_enable(True)
    
    init_game()

@setHook(HOOK_10MS)
#@setHook(HOOK_100MS)
#@setHook(HOOK_1S)
def tick_100ms():
    update_ball()
    refresh_pixels()

def init_game():
    global ball_x, ball_y
    # Note that all of these are instantaneous, not average!
    # (We will be computing the averages over each interval from these)
    global ball_x_vel, ball_y_vel
    global ball_x_accel, ball_y_accel

    cls()

    ball_x = to_FP(MIN_X+3, 0)
    ball_y = to_FP(MIN_Y+3, 0)

    ball_x_vel = to_FP(0, 0)
    ball_y_vel = to_FP(0, 0)

    ball_x_accel = to_FP(0, 0)
    ball_y_accel = to_FP(0, 0)

    set_pixel(from_FP(ball_x), from_FP(ball_y))

    refresh_pixels()

def update_ball():
    global ball_x, ball_y
    # Note that all of these are instantaneous, not average!
    # (We will be computing the averages further below in this same routine)
    global ball_x_vel, ball_y_vel
    global prev_ball_x_vel, prev_ball_y_vel
    global ball_x_accel, ball_y_accel
    global prev_ball_x_accel, prev_ball_y_accel

    lis_read() # Get the instantaneous accelerations from the accelerometer

    # Keep in mind the following divisions also includes an implicit UP-scaling to Fixed Point
    # Good values here depend on how often you are calling update_ball() too
    scaled_x_accel = lis_axis_x / 500
    scaled_y_accel = -(lis_axis_y / 500)

    #print 'lis_axis_x=', lis_axis_x,
    #print_labeled_FP(' scaled_x_accel=', scaled_x_accel)

    prev_ball_x_accel = ball_x_accel
    prev_ball_y_accel = ball_y_accel

    ball_x_accel = scaled_x_accel
    ball_y_accel = scaled_y_accel

    #print_labeled_FP(' prev_ball_x_accel=', prev_ball_x_accel)
    #print_labeled_FP(' ball_x_accel=', ball_x_accel)
    #print_labeled_FP(' total=', prev_ball_x_accel + ball_x_accel)
    average_x_accel = multiply_FP( prev_ball_x_accel + ball_x_accel, POINT_FIVE)
    average_y_accel = multiply_FP( prev_ball_y_accel + ball_y_accel, POINT_FIVE)

    prev_ball_x_vel = ball_x_vel
    prev_ball_y_vel = ball_y_vel

    ball_x_vel += average_x_accel
    ball_y_vel += average_y_accel

    # VERY CRUDE simulation of FRICTION too
    ball_x_vel = multiply_FP( ball_x_vel, FRICTION)
    ball_y_vel = multiply_FP( ball_y_vel, FRICTION)

    average_x_vel = multiply_FP( prev_ball_x_vel + ball_x_vel, POINT_FIVE)
    average_y_vel = multiply_FP( prev_ball_y_vel + ball_y_vel, POINT_FIVE)

    # Enforce terminal velocity
    if average_x_vel > TERMINAL_VELOCITY:
        average_x_vel = TERMINAL_VELOCITY
    if average_x_vel < -TERMINAL_VELOCITY:
        average_x_vel = -TERMINAL_VELOCITY
    if average_y_vel > TERMINAL_VELOCITY:
        average_y_vel = TERMINAL_VELOCITY
    if average_y_vel < -TERMINAL_VELOCITY:
        average_y_vel = -TERMINAL_VELOCITY

    # Compute TENTATIVE next position for the ball
    new_x = ball_x + average_x_vel
    new_y = ball_y + average_y_vel

    #print_labeled_FP(' xacc=', average_x_accel)
    #print_labeled_FP(' xvel=', average_x_vel)
    #print_labeled_FP(' x=', new_x)
    #print

    # "Bounce" off of the boundaries
    if new_x < FP_MIN_X:
        # Perfect rebounds
        #ball_x_vel *= -1
        # Simulate inelasticity too
        ball_x_vel = multiply_FP( ball_x_vel, REBOUND)
        new_x = FP_MIN_X

    if new_x > FP_MAX_X:
        # Perfect rebounds
        #ball_x_vel *= -1
        # Simulate inelasticity too
        ball_x_vel = multiply_FP( ball_x_vel, REBOUND)
        new_x = FP_MAX_X

    if new_y < FP_MIN_Y:
        # Perfect rebounds
        #ball_y_vel *= -1
        # Simulate inelasticity too
        ball_y_vel = multiply_FP( ball_y_vel, REBOUND)
        new_y = FP_MIN_Y

    if new_y > FP_MAX_Y:
        # Perfect rebounds
        #ball_y_vel *= -1
        # Simulate inelasticity too
        ball_y_vel = multiply_FP( ball_y_vel, REBOUND)
        new_y = FP_MAX_Y

    reset_pixel(from_FP(ball_x), from_FP(ball_y))
    set_pixel(from_FP(new_x), from_FP(new_y))

    ball_x = new_x
    ball_y = new_y
