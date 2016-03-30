"""Classic Breakout game ported to SNAP Badge"""

from drivers.snap_badge import *
from pixel_lib import *

MIN_BRICK_LINE = 0
MAX_BRICK_LINE = 3

delay = 0
delay_counter = 0

def breakout_start():
    """Startup hook when run standalone"""
    badge_start()
    
    monitorPin(BUTTON_LEFT, True)
    monitorPin(BUTTON_RIGHT, True)

    breakout_init()

def breakout_set_delay(new_delay):
    global delay, delay_counter
    delay = new_delay
    delay_counter = delay
    
def breakout_tick100ms():
    global delay_counter
    if delay_counter > 0:
        delay_counter -= 1
        if delay_counter == 0:
            delay_counter = delay
        else:
            return
    _update_ball()
    refresh_pixels()

def breakout_pin_event(pin, is_set):
    if not is_set:
        # Button combinations
        #lb = not readPin(BUTTON_LEFT)
        #rb = not readPin(BUTTON_RIGHT)
        
        # TODO Decide if buttons can be HELD down too
        if pin == BUTTON_LEFT:
            paddle_left()
        elif pin == BUTTON_RIGHT:
            paddle_right()

def breakout_init():
    global ball_x, ball_y, ball_x_vel, ball_y_vel
    global paddle_x, paddle_y, paddle_width
    global score

    score = 0
    
    cls()

    row = MIN_BRICK_LINE
    while row <= MAX_BRICK_LINE:
        col = MIN_X
        while col <= MAX_X:
            set_pixel(col, row)
            col += 1
        row += 1

    # Experiment - try for a psuedo-3D effect by applying a gradient to the entire screen
    as1115_wr(DIG01_INTENS, 0x10)
    as1115_wr(DIG23_INTENS, 0x32)
    as1115_wr(DIG45_INTENS, 0x54)
    as1115_wr(DIG67_INTENS, 0x76)

    paddle_x = 0 # we are tracking the paddle by it's left-most edge
    paddle_y = 7
    paddle_width = 3
    
    paddle(True)

    ball_x = MIN_X+3
    ball_y = MAX_BRICK_LINE + 1

    ball_x_vel = 1
    ball_y_vel = 1
    
    set_pixel(ball_x, ball_y)

    refresh_pixels()

    breakout_set_delay(0)


def paddle(is_visible):
    # Draw the paddle
    count = paddle_width
    if is_visible:
        while count:
            count -= 1
            set_pixel(paddle_x+count, paddle_y)
    else:
        while count:
            count -= 1
            reset_pixel(paddle_x+count, paddle_y)

def paddle_left():
    global paddle_x
    paddle(False)
    # Don't allow the paddle to go off screen at all
    #if paddle_x > MIN_X:
    # Allow paddle to go partially off screen so "english" can be applied
    if paddle_x > (MIN_X - (paddle_width-1)):
        paddle_x -= 1
    paddle(True)
    refresh_pixels()

def paddle_right():
    global paddle_x
    paddle(False)
    # Don't allow the paddle to go off screen at all
    #if paddle_x <= (MAX_X - paddle_width):
    # Allow paddle to go partially off screen so "english" can be applied
    if paddle_x < MAX_X:
        paddle_x += 1
    paddle(True)
    refresh_pixels()

def _update_ball():
    global ball_x, ball_y, ball_x_vel, ball_y_vel, score

    # Compute TENTATIVE next position for the ball
    new_x = ball_x + ball_x_vel
    new_y = ball_y + ball_y_vel

    # Usually the breakout playfield has VISIBLE boundaries
    # Here we don't have the pixels to spare, so we detect
    # the "walls" based solely on coordinates
    if new_x < MIN_X:
        ball_x_vel *= -1
        new_x = ball_x + ball_x_vel

    if new_x > MAX_X:
        ball_x_vel *= -1
        new_x = ball_x + ball_x_vel

    if new_y < MIN_Y:
        ball_y_vel *= -1
        new_y = ball_y + ball_y_vel

    if new_y > MAX_Y:
        ball_y_vel *= -1
        new_y = ball_y + ball_y_vel

    # Check for collisions with visible pixels
    brick_erase = False
    if test_pixel(new_x, new_y):
        # If it was a brick we hit, erase it
        if (new_y <= MAX_BRICK_LINE) and (new_y >= MIN_BRICK_LINE):
            brick_erase = True
            saved_x1 = new_x
            saved_x2 = ball_x
            saved_y = new_y
        # else if it was the paddle, adjust ball angle based on WHERE it hit
        elif new_y == paddle_y:
            # This code is specific to the 3-pixel paddle
            if ball_x == paddle_x + 1: # Center hit
                ball_x_vel = 0
            elif ball_x == paddle_x: # Left hit
                if ball_x_vel == 0:
                    ball_x_vel = 1 # (gets negated down below)
            elif ball_x == paddle_x + 2: # Right hit
                if ball_x_vel == 0:
                    ball_x_vel = -1 # (gets negated down below)

        # Make the rebounds aesthetically pleasing
        if test_pixel(ball_x, new_y) and not test_pixel(new_x, ball_y):
            ball_y_vel *= -1
        elif test_pixel(new_x, ball_y) and not test_pixel(ball_x, new_y):
            ball_x_vel *= -1
        else:        
            ball_x_vel *= -1
            ball_y_vel *= -1

        # Incorporate any adjustments (rebounds)
        new_x = ball_x + ball_x_vel
        new_y = ball_y + ball_y_vel

    if brick_erase:
        if test_pixel(saved_x1, saved_y):
            score += 1
            reset_pixel(saved_x1, saved_y)
        if test_pixel(saved_x2, saved_y): # aesthetics
            score += 1
            reset_pixel(saved_x2, saved_y)

    reset_pixel(ball_x, ball_y)
    set_pixel(new_x, new_y)
    ball_x = new_x
    ball_y = new_y

# Hook context, for multi-app switching via app_switch.py
breakout_context = (breakout_init, None, None, breakout_tick100ms, None, breakout_pin_event)

# Set hooks if running game standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, breakout_start)
    snappyGen.setHook(SnapConstants.HOOK_10MS, breakout_tick100ms)
    snappyGen.setHook(SnapConstants.HOOK_GPIN, breakout_pin_event)


