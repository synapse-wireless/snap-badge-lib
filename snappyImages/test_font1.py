"""Test fonts"""

from drivers.snap_badge import *

from drivers.fonts_8x8 import *
from drivers.OEM6x8 import *
from drivers.DEF8x8 import *

sim_badge = False

tick_count = 0
UPDATE_RATE = 15  # centiseconds

# Test string with each of 128 chars
CHAR_TEST_STR = ''.join(map(chr, xrange(128)))

@setHook(HOOK_STARTUP)
def test1():
    #load_font(OEM6x8, OEM6x8_widths)
    load_font(DEF8x8, DEF8x8_widths)
    set_scroll_text("The Quick Brown Fox Jumped Over The Lazy Dogs  " + CHAR_TEST_STR)
    
    if sim_badge:
        set_display_driver(test_display_driver_mcast)
    else:
        set_display_driver(as1115_write_matrix_symbol)
        badge_start()
        monitorPin(BUTTON_LEFT, True)
        monitorPin(BUTTON_RIGHT, True)


@setHook(HOOK_10MS)
def tick10ms():
    global tick_count
    tick_count += 1
    if tick_count == UPDATE_RATE:
        tick_count = 0
        update_scroll_text(1)
    
@setHook(HOOK_GPIN)
def pin_event(pin, is_set):
    if not is_set:
        # Button combinations
        lb = not readPin(BUTTON_LEFT)
        rb = not readPin(BUTTON_RIGHT)

        if lb and rb:
            if cur_fontset == DEF8x8:
                load_font(OEM6x8, OEM6x8_widths)
            else:
                load_font(DEF8x8, DEF8x8_widths)
        
        elif pin == BUTTON_LEFT:
            set_scroll_text("Hi Max!   ")
        elif pin == BUTTON_RIGHT:
            set_scroll_text("ESC 2016   ")
            
