"""Scrolling text messages for SNAP Badge"""

from drivers.snap_badge import *

from drivers.fonts_8x8 import *
#from drivers.OEM6x8 import *
from drivers.DEF8x8 import *

show_scroller_text = "ESC 2016   "

tick_count = 0
UPDATE_RATE = 15  # centiseconds
app_exit = None


def show_scroller_start():
    """Startup hook when run standalone"""
    set_display_driver(as1115_write_matrix_symbol)
    badge_start()
    show_scroller_init()
    
def show_scroller_init():
    load_font(DEF8x8, DEF8x8_widths)
    update_dipsw()

def show_scroller_tick10ms():
    global tick_count
    tick_count += 1
    if tick_count == UPDATE_RATE:
        tick_count = 0
        wrap = update_scroll_text(1)
        if wrap:
            # Poll during vertical blanking interval :)
            poll_dipsw()
    
def show_scroller_pin_event(pin, is_set):
    if not is_set:
        # Button combinations
        lb = not readPin(BUTTON_LEFT)
        rb = not readPin(BUTTON_RIGHT)
        
        # Exit to menu if both buttons pressed
        if lb and rb:
            if app_exit:
                app_exit()

dipsw = 0x00
def poll_dipsw():
    """Poll DIP switch"""
    global dipsw
    sw = ~as1115_rd(KEYB)
    if sw != dipsw:
        dipsw = sw
        update_dipsw()

def update_dipsw():
    stext = show_scroller_text
    
    if dipsw & DIP_STEM:
        stext += "STEM  "
    if dipsw & DIP_ANALOG:
        stext += "Analog  "
    if dipsw & DIP_DIGITAL:
        stext += "Digital  "
    if dipsw & DIP_HARDWARE:
        stext += "Hardware  "
    if dipsw & DIP_SOFTWARE:
        stext += "Software  "
    if dipsw & DIP_IOT:
        stext += "IoT  "
        
    set_scroll_text(stext)


# Hook context, for multi-app switching via app_switch.py
show_scroller_context = (show_scroller_init, None, show_scroller_tick10ms, None, None, show_scroller_pin_event)

# Set hooks if running game standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, show_scroller_start)
    snappyGen.setHook(SnapConstants.HOOK_10MS, show_scroller_tick10ms)
    snappyGen.setHook(SnapConstants.HOOK_GPIN, show_scroller_pin_event)


