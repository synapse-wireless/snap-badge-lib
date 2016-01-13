"""Test fonts"""

from drivers.fonts_8x8 import *
from drivers.OEM6x8 import *
from drivers.DEF8x8 import *

tick_count = 0
UPDATE_RATE = 15  # centiseconds

# Test string with each of 128 chars
CHAR_TEST_STR = ''.join(map(chr, xrange(128)))

@setHook(HOOK_STARTUP)
def test1():
    #load_font(OEM6x8, OEM6x8_widths)
    load_font(DEF8x8, DEF8x8_widths)
    #set_scroll_text("The Quick Brown Fox Jumped Over The Lazy Dogs  " + CHAR_TEST_STR)
    set_scroll_text("Hello, Jonathan! ")
    set_display_driver(test_display_driver_mcast)

@setHook(HOOK_10MS)
def tick10ms():
    global tick_count
    tick_count += 1
    if tick_count == UPDATE_RATE:
        tick_count = 0
        update_scroll_text(1)
    
    
if __name__ == '__main__':    
    test1()
    
    for i in xrange(100):
        update_scroll_text(2)
