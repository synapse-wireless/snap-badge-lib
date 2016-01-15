"""Accelerometer Experiments"""

from drivers.snap_badge import *
from drivers.lis3dh_accel import *
from pixel_lib import *

@setHook(HOOK_STARTUP)
def start():
    badge_init_pins()
    lis_init()
    badge_led_array_enable(True)
    
    init_game()

@setHook(HOOK_100MS)
def tick_100ms():
    update_ball()
    refresh_pixels()

def init_game():
    global ball_x, ball_y, ball_x_vel, ball_y_vel

    cls()

    ball_x = MIN_X+3
    ball_y = MIN_Y+3

    ball_x_vel = 0
    ball_y_vel = 0
    
    set_pixel(ball_x, ball_y)

    refresh_pixels()

def update_ball():
    global ball_x, ball_y, ball_x_vel, ball_y_vel

    lis_read()
    
    if lis_axis_x < -1000:
        ball_x_vel = -1
    elif lis_axis_x > +1000:
        ball_x_vel = +1
    else:
        ball_x_vel = 0

    if lis_axis_y < -1000:
        ball_y_vel = +1
    elif lis_axis_y > +1000:
        ball_y_vel = -1
    else:
        ball_y_vel = 0

    # Compute TENTATIVE next position for the ball
    new_x = ball_x + ball_x_vel
    new_y = ball_y + ball_y_vel

    # Usually the breakout playfield has VISIBLE boundaries
    # Here we don't have the pixels to spare, so we detect
    # the "walls" based solely on coordinates
    if new_x < MIN_X:
        ball_x_vel *= -1
        new_x = ball_x + ball_x_vel
        ball_x_vel = 0

    if new_x > MAX_X:
        ball_x_vel *= -1
        new_x = ball_x + ball_x_vel
        ball_x_vel = 0

    if new_y < MIN_Y:
        ball_y_vel *= -1
        new_y = ball_y + ball_y_vel

    if new_y > MAX_Y:
        ball_y_vel *= -1
        new_y = ball_y + ball_y_vel

    reset_pixel(ball_x, ball_y)
    set_pixel(new_x, new_y)
    ball_x = new_x
    ball_y = new_y

