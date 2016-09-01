"""Level - handy tool for installing whiteboards, hanging pictures, etc.
   Press and hold either button to "lock" level display.
"""

from drivers.snap_badge import *
from drivers.fonts_8x8 import *
from drivers.Doodads import *

def level_start():
    """Startup hook when run standalone"""
    set_display_driver(as1115_write_matrix_symbol)
    badge_start()
    level_init()
    
def level_init():
    """Initialize application"""
    load_font(Doodads, Doodads_widths)
    
def disp_2_digits(i, rot):
    sym = ''

    if i < 100:
        si = str(i)
        if len(si) == 1:
            si = '0' + si
        
        rdig_code = ord(si[1])
        rdig = get_indexed_sym(rdig_code)
        ldig_code = ord(si[0])
        lwidth = get_indexed_width(ldig_code)
        ldig = get_indexed_sym(ldig_code)

        for row in xrange(8):
            r = ord(ldig[row]) | (ord(rdig[row]) >> 5)
            sym += chr(r & 0xFF)

        sym = rotate_sym(sym, rot)

        display_drv(sym)

def level_tick100ms():
    """Called by system every 100ms"""
    
    # If either button is held, do not update display
    if not (readPin(BUTTON_RIGHT) and readPin(BUTTON_LEFT)):
        return

    # Poll the accelerometer
    lis_read()
    level_rot = 270 if lis_axis_x > 0 else 90
    val = abs(lis_axis_y) / 178
    if val > 90:
        val = 90
    disp_2_digits(val, level_rot)


# Hook context, for multi-app switching via app_switch.py
level_context = (level_init, None, None, level_tick100ms, None, None)

# Set hooks if running standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, level_start)
    snappyGen.setHook(SnapConstants.HOOK_100MS, level_tick100ms)



    