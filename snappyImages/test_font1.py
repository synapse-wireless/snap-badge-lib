"""Test fonts"""

from drivers.fonts_8x8 import *
from drivers.OEM6x8 import *



def test1():
    load_font(OEM6x8, OEM6x8_widths)
    #set_scroll_text("Hello, Brad  ")
    set_scroll_text("Braille 123")
    set_display_driver(test_display_driver2)

@setHook(HOOK_1S)
def tick1s():
    update_scroll_text()
    
    
if __name__ == '__main__':    
    test1()
    
    for i in xrange(100):
        update_scroll_text()
