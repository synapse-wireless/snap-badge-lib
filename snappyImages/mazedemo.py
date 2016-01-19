"""Demo - explore a maze larger than the 8x8 screen"""

from drivers.snap_badge import *
from maze_lib import *
from pixel_lib import *

MIN_SCALE = 2
MAX_SCALE = 7

view_x = 0
view_y = 0

scale = MIN_SCALE

@setHook(HOOK_STARTUP)
def start():
    uniConnect(3,4)
    uniConnect(3,5)
    ucastSerial("\x00\x00\x01")

    badge_init_pins()
    badge_led_array_enable(True)
    as1115_wr(GLOB_INTENS, 10) # (I just don't like full brightness, your eyes may vary)
    
    monitorPin(BUTTON_LEFT, True)
    monitorPin(BUTTON_RIGHT, True)

    init_game()

def zoom_in():
    global scale
    if scale < MAX_SCALE:
        scale += 1
    display_view()

def zoom_out():
    global scale
    if scale > MIN_SCALE:
        scale -= 1
    display_view()

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

def display_view():
    y = MIN_Y
    while y <= MAX_Y:
        x = MIN_X
        while x <= MAX_X:
            world_x = x + view_x
            world_y = y + view_y
            maze_x = world_x / scale
            maze_y = world_y / scale
            maze_cell = maze[ maze_y * maze_width + maze_x]
            x_offset = world_x % scale
            y_offset = world_y % scale

            # TEMP CODE
            if (x_offset == 0) and (maze_cell & WEST_WALL):
                set_pixel(x, y)
            elif (y_offset == 0) and (maze_cell & NORTH_WALL):
                set_pixel(x, y)
            else:
                reset_pixel(x, y)
            x += 1
        y += 1

    refresh_pixels()
