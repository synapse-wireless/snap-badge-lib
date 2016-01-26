"""
Diversion - SNAKE GAME - Can you maintain YOUR left/right orientation?
LEFT BUTTON to turn counter-clockwise
RIGHT BUTTON to turn clockwise

Currently just a prototype (you cannot win)
Also needs better "animation" when food eaten
"""

from drivers.snap_badge import *
from pixel_lib import *

MIN_DIR = 0
MAX_DIR = 3

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

# These are (x,y) pairs, indexed by the above DIRS
OFFSETS = ( (0,-1), (1,0), (0,1), (-1,0) )

STARTING_LENGTH = 3
STARTING_X = 3
STARTING_Y = MAX_Y
STARTING_DIR = UP

@setHook(HOOK_STARTUP)
def start():
    badge_init_pins()
    lis_init()
    badge_led_array_enable(True)
    as1115_wr(GLOB_INTENS, 10) # (I just don't like full brightness, your eyes may vary)
    
    monitorPin(BUTTON_LEFT, True)
    monitorPin(BUTTON_RIGHT, True)

    init_game()

def encode_coords(x, y):
    return (y << 4) | x

def decode_x(code):
    return code & 0x0F

def decode_y(code):
    return code >> 4

def add_segment(x, y):
    global player_segments

    set_pixel(x, y)
    refresh_pixels()

    player_segments = [ encode_coords(x, y) ] + player_segments

def move_player(dir):
    global player_x, player_y, player_length

    delta_x = OFFSETS[dir][0]
    delta_y = OFFSETS[dir][1]
    
    player_x += delta_x
    player_y += delta_y

    if invalid_coords(player_x, player_y):
        game_over()

    if (player_x == food_x) and (player_y == food_y):
        reset_pixel(food_x, food_y)
        player_length += 1
        spawn_food()

def draw_snake(render_flag):
    for code in player_segments:
        x = decode_x(code)
        y = decode_y(code)
        if render_flag:
            set_pixel(x, y)
        else:
            reset_pixel(x, y)
    refresh_pixels()

def game_over():
    cycles = 3
    while cycles > 0:
        draw_snake(False)
        sleep(0, 1)
        draw_snake(True)
        sleep(0, 1)
        cycles -= 1
    init_game()

def spawn_food():
    global food_x, food_y
    while True:
        food_x = random() % (MAX_X + 1)
        food_y = random() % (MAX_Y + 1)
        if test_pixel(food_x, food_y) == False:
            set_pixel(food_x, food_y)
            refresh_pixels()
            return

def init_game():
    global player_x, player_y, player_dir, player_length, player_segments

    cls()

    player_x = STARTING_X
    player_y = STARTING_Y
    player_dir = STARTING_DIR

    player_segments = []

    player_length = STARTING_LENGTH
    while len(player_segments) < STARTING_LENGTH:
        add_segment(player_x, player_y)
        sleep(0, 1)
        move_player(player_dir)

    spawn_food()

@setHook(HOOK_1S)
def tick():
    global player_segments

    move_player(player_dir)

    if len(player_segments) >= player_length:
        code = player_segments[-1] # get the end of the tail
        x = decode_x(code)
        y = decode_y(code)
        reset_pixel(x, y)
        player_segments = player_segments[0:player_length-1]
    
    add_segment(player_x, player_y)

@setHook(HOOK_GPIN)
def pin_event(pin, is_set):
    global player_dir
    if not is_set:
        if pin == BUTTON_LEFT:
            player_dir -= 1
            if player_dir < MIN_DIR:
                player_dir = MAX_DIR
        elif pin == BUTTON_RIGHT:
            player_dir += 1
            if player_dir > MAX_DIR:
                player_dir = MIN_DIR
