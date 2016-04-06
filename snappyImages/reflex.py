"""Reflex test - how fast are you?



"""

from drivers.snap_badge import *
from drivers.fonts_8x8 import *
from drivers.DEF8x8 import *
from animation import *
from drivers.true_random import *
from drivers.atmega128rfa1_timers import *

# Reflex countdown animation icons are the following indices of Doodads fontset
reflex_countdown_icons = '3 2 1 '

reflex_t_trigger = 0  # Trigger timer
REFLEX_INIT = 0
REFLEX_ARMED = 1
REFLEX_RUNNING = 2
REFLEX_SHOW = 3
reflex_state = REFLEX_INIT

REFLEX_TEST_TIMEOUT = 15625 # counts = 1sec @ 15625Hz

REFLEX_SCROLL_RATE = 8
reflex_scroll_tick = 0

def reflex_start():
    """Startup hook when run standalone"""
    set_display_driver(as1115_write_matrix_symbol)
    badge_start()
    reflex_init()
    
def reflex_init():
    """Initialize application"""
    global reflex_t_trigger, reflex_state, reflex_scroll_tick
    reflex_t_trigger = 0
    reflex_scroll_tick = REFLEX_SCROLL_RATE
    reflex_state = REFLEX_INIT

    load_font(DEF8x8, DEF8x8_widths)
    anim_init(reflex_countdown_icons, 50, reflex_test_begin)
    anim_begin(1)
    
    # Initialize a hardware timer for accurate measurements (15625Hz clock)
    timer_init(TMR1, WGM_NORMAL, CLK_FOSC_DIV1024, 0)

def reflex_test_begin():
    global reflex_t_trigger, reflex_state
    reflex_t_trigger = 1000 + true_random()   # About 1-5 seconds from now
    reflex_state = REFLEX_ARMED

def reflex_tick1ms():
    """Called by system every 1ms"""
    if not readPin(BUTTON_RIGHT) or not readPin(BUTTON_LEFT):
        if reflex_state == REFLEX_RUNNING:
            count = get_tmr_count(TMR1)
            reflex_results(count / 16)  # ms
        elif reflex_state == REFLEX_ARMED:
            reflex_results(-1)

def reflex_fire():
    global reflex_state
    display_drv(SYM_ALL_ON)
    set_tmr_count(TMR1, 0)
    reflex_state = REFLEX_RUNNING

def reflex_results(tm):
    global reflex_state
    if tm > 0:
        set_scroll_text('\x03' + str(tm) + 'ms  ')
    elif tm < 0:
        set_scroll_text("\x13 ERR")
    else:
        set_scroll_text("\x15  TIMEOUT")
        
    reflex_state = REFLEX_SHOW
    
def reflex_tick10ms():
    """Called by system every 10ms"""
    global reflex_t_trigger, reflex_scroll_tick
    
    anim_tick10ms()
    
    # If trigger timer has elapsed, pull the trigger!
    if reflex_state == REFLEX_ARMED:
        reflex_t_trigger -= 10
        if reflex_t_trigger <= 0:
            reflex_fire()
    elif reflex_state == REFLEX_RUNNING:
        count = get_tmr_count(TMR1)
        if count > REFLEX_TEST_TIMEOUT:
            reflex_results(0)
    elif reflex_state == REFLEX_SHOW:
        #display_drv(SYM_CHECKERBOARD)
        reflex_scroll_tick -= 1
        if reflex_scroll_tick == 0:
            update_scroll_text(1)
            reflex_scroll_tick = REFLEX_SCROLL_RATE

    
# Hook context, for multi-app switching via app_switch.py
reflex_context = (reflex_init, reflex_tick1ms, reflex_tick10ms, None, None, None)

# Set hooks if running game standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, reflex_start)
    snappyGen.setHook(SnapConstants.HOOK_1MS, reflex_tick1ms)
    snappyGen.setHook(SnapConstants.HOOK_10MS, reflex_tick10ms)



    