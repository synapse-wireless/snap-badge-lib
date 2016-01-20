"""Demo - explore a maze larger than the 8x8 screen"""

# No actual goal yet. Intent is to choose a square to lead to the "next level down"
# Will need to highlight this square in some way.
# Should git a scrolling message when you descend to the next level
# Etc. See also TODOs throughout code

from drivers.snap_badge import *
from drivers.lis3dh_accel import *
from maze_lib import *
from pixel_lib import *

MIN_SCALE = 2
MAX_SCALE = 7

ACCEL_THRESHOLD = 1500 # smaller number makes it more sensitive to tilt, bigger = less sensitive

MARGIN = 2 # How close to allow the player to the edge of the screen before inducing scrolling

BLINK_COUNTDOWN = 10
BLINK_DURATION = 5
blink_counter = BLINK_COUNTDOWN

view_x = 0 # World Coordinates
view_y = 0 # World Coordinates

player_x = 1 # Screen Coordinates, which have to be mapped back to World Coordinates
player_y = 1 # Screen Coordinates, which have to be mapped back to World Coordinates

scale = MIN_SCALE

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

    init_game()

@setHook(HOOK_100MS)
def tick():
    global blink_counter
    poll_accelerometer()

    # Do something to make the player stand out from the walls...
    if blink_counter > 0:
        blink_counter -= 1
        if blink_counter < BLINK_DURATION:
            reset_pixel(player_x, player_y)
            refresh_pixels()
        if blink_counter == 0:
            blink_counter = BLINK_COUNTDOWN
            set_pixel(player_x, player_y)
            refresh_pixels()

# TODO - This does not take the player into account at all!
def zoom_in():
    global scale
    if scale < MAX_SCALE:
        scale += 1
    display_view()
    refresh_pixels()

# TODO - This does not take the player into account at all!
def zoom_out():
    global scale
    if scale > MIN_SCALE:
        scale -= 1
    display_view()
    refresh_pixels()

@setHook(HOOK_GPIN)
def pin_event(pin, is_set):
    if not is_set:
        if pin == BUTTON_LEFT:
            zoom_out()
        elif pin == BUTTON_RIGHT:
            zoom_in()

def init_game():
    cls()

    generate_maze(15, 15, 0, 0)

    display_view()
    display_player()

    refresh_pixels()

def display_view():
    y = MIN_Y
    while y <= MAX_Y:
        x = MIN_X
        while x <= MAX_X:
            world_x = x + view_x
            world_y = y + view_y

            # Draw solid pixels outside the bounds of the maze
            # (Solid black would require extra code to draw the EAST and SOUTH boundary walls
            if (world_x >= (maze_width * scale)) or (world_y >= (maze_height * scale)):
                set_pixel(x, y)
            else:
                # We are WITHIN the boundaries of the maze, draw the walls
                maze_x = world_x / scale
                maze_y = world_y / scale
                maze_cell = maze[ maze_y * maze_width + maze_x]
                x_offset = world_x % scale
                y_offset = world_y % scale
                # TODO Re-think the most NORTH-WEST pixel
                # Currently corners sometimes appear "gapped"
                if (x_offset == 0) and (maze_cell & WEST_WALL):
                    set_pixel(x, y)
                elif (y_offset == 0) and (maze_cell & NORTH_WALL):
                    set_pixel(x, y)
                else:
                    reset_pixel(x, y)
            x += 1
        y += 1

def display_player():
    set_pixel(player_x, player_y)

def attempt_move(delta_x, delta_y):
    global player_x, player_y
    global view_x, view_y

    candidate_x = player_x + delta_x
    candidate_y = player_y + delta_y

    # Player not allowed to move off screen...
    if invalid_coords(candidate_x, candidate_y):
        return

    # Player not allowed to walk through walls...
    if test_pixel(candidate_x, candidate_y):
        return

    # We also prefer scrolling the view to getting too close to edges
    view_adjusted = False
    if (delta_x == -1) and (view_x > 0) and (candidate_x < (MIN_X + MARGIN)):
        view_x -= 1
        view_adjusted = True
    if (delta_x == 1) and (view_x < ((maze_width * scale) - MAX_X)) and (candidate_x > (MAX_X - MARGIN)):
        view_x += 1
        view_adjusted = True
    if (delta_y == -1) and (view_y > 0) and (candidate_y < (MIN_Y + MARGIN)):
        view_y -= 1
        view_adjusted = True
    if (delta_y == 1) and (view_y < ((maze_height * scale) - MAX_Y)) and (candidate_y > (MAX_Y - MARGIN)):
        view_y += 1
        view_adjusted = True

    if view_adjusted:
        # Move the view...
        display_view()
        set_pixel(player_x, player_y)
    else:
        # Move the player...
        reset_pixel(player_x, player_y)
        player_x = candidate_x
        player_y = candidate_y
        set_pixel(player_x, player_y)

    refresh_pixels()

def move_up():
    #print "up"
    attempt_move(0, -1)

def move_down():
    #print "down"
    attempt_move(0, 1)

def move_left():
    #print "left"
    attempt_move(-1, 0)

def move_right():
    #print "right"
    attempt_move(1, 0)

def poll_accelerometer():
    lis_read() # Get the instantaneous accelerations from the accelerometer

    if lis_axis_y > ACCEL_THRESHOLD:
        move_up()
    elif lis_axis_y < -ACCEL_THRESHOLD:
        move_down()

    if lis_axis_x > ACCEL_THRESHOLD:
        move_right()
    elif lis_axis_x < -ACCEL_THRESHOLD:
        move_left()
