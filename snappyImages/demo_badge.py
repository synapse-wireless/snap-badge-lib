"""Frankenscript! - interim, cobbled together demo for early ESC promotion.
   A combination of Breakout, Font-test, and Rollerball. Please refer to those individual scripts 
   for future work.
"""

from drivers.snap_badge import *

from drivers.fonts_8x8 import *
from drivers.OEM6x8 import *
from drivers.DEF8x8 import *
from pixel_lib import *
from fixed_point import *

scroll_tick_count = 0
TEXT_SCROLL_RATE = 10  # centiseconds

# Latest DIP switch value
dipsw = 0x00

# Breakout
MIN_BRICK_LINE = 0
MAX_BRICK_LINE = 3
delay = 0
delay_counter = 0

# Rollerball
# MAke FP counterparts to some contants from pixel_lib
FP_MIN_X = to_FP(MIN_X, 0)
FP_MAX_X = to_FP(MAX_X, 0)
FP_MIN_Y = to_FP(MIN_Y, 0)
FP_MAX_Y = to_FP(MAX_Y, 0)
# Force a terminal velocity (the screen is not very big!)
TERMINAL_VELOCITY = to_FP(1, 0)
# Technically this is % velocity lost due to friction, not the actual friction...
FRICTION = to_FP(0, 99)
REBOUND = to_FP(0, -95) # rebounds in the opposite direction PLUS loses some energy


@setHook(HOOK_STARTUP)
def start():
    badge_start()
    
    monitorPin(BUTTON_LEFT, True)
    monitorPin(BUTTON_RIGHT, True)
    set_display_driver(as1115_write_matrix_symbol)
    load_font(DEF8x8, DEF8x8_widths)


@setHook(HOOK_10MS)
def tick10ms():
    global scroll_tick_count
    scroll_tick_count += 1
    if scroll_tick_count == TEXT_SCROLL_RATE:
        scroll_tick_count = 0
        update_scroll_text(1)   # Does nothing if no scroll text

    if dipsw & 0xff == 0x82:
        roller_update_ball()
        refresh_pixels()


@setHook(HOOK_1S)
def tick_1s():
    global dipsw, packetserial_countdown
    pulsePin(STATUS_LED, 200, False)
    
    # Poll DIP switch
    sw = ~as1115_rd(KEYB)
    if sw != dipsw:
        dipsw = sw
        handle_dipsw()
        
def handle_dipsw():
    if dipsw & 0x80:
        if dipsw & 0x01:
            # Breakout
            set_scroll_text("")
            init_game()
        elif dipsw & 0x02:
            # Accel demo
            set_scroll_text("")
            roller_init_game()
        elif dipsw & 0x04:
            pass
        elif dipsw & 0x08:
            set_scroll_text("Hi Max   ")
        elif dipsw & 0x10:
            set_scroll_text("Hi Pam   ")
        elif dipsw & 0x20:
            set_scroll_text("Screaming Circuits   ")
        elif dipsw & 0x40:
            set_scroll_text("Sunstone Circuits   ")
        else:
            set_scroll_text("ESC 2016   ")
    else:
        stext = ""
        if dipsw & 0x01:
            stext += "STEM  "
        if dipsw & 0x02:
            stext += "Analog  "
        if dipsw & 0x04:
            stext += "Digital  "
        if dipsw & 0x08:
            stext += "Hardware  "
        if dipsw & 0x10:
            stext += "Software  "
        if dipsw & 0x20:
            stext += "IoT  "
            
        if stext:
            set_scroll_text(stext)
        else:
            set_scroll_text("ESC 2016   ")

def set_delay(new_delay):
    global delay, delay_counter
    delay = new_delay
    delay_counter = delay

@setHook(HOOK_100MS)
def tick_100ms():
    global delay_counter

    # Breakout
    if dipsw & 0xff == 0x81:
        if delay_counter > 0:
            delay_counter -= 1
            if delay_counter == 0:
                delay_counter = delay
            else:
                return
        update_ball()
        refresh_pixels()


@setHook(HOOK_GPIN)
def pin_event(pin, is_set):
    # Breakout
    if dipsw & 0xff == 0x81:
        if not is_set:
            if pin == BUTTON_LEFT:
                paddle_left()
            elif pin == BUTTON_RIGHT:
                paddle_right()

def init_game():
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

    set_delay(0)


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
    # Allow paddle to go partially off screen so "english" can be applied
    if paddle_x > (MIN_X - (paddle_width-1)):
        paddle_x -= 1
    paddle(True)
    refresh_pixels()

def paddle_right():
    global paddle_x
    paddle(False)
    # Allow paddle to go partially off screen so "english" can be applied
    if paddle_x < MAX_X:
        paddle_x += 1
    paddle(True)
    refresh_pixels()

def update_ball():
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

def roller_init_game():
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

def roller_update_ball():
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
