"""Groovy LED sweeping effect. Yes, like KITT in Knight Rider :)"""

from drivers.snap_badge import *
from pixel_lib import *

# Binary map representing 64 pixel sweep pattern. Visualize by rotating your head 90 deg CCW.
sweep_map = (0b00001110,
             0b00111010,
             0b01111011,
             0b11110001, 
             0b11110001, 
             0b01111011, 
             0b00111010, 
             0b00001110)
             
sweep_col = 0
sweep_dir = +1

def sweep_start():
    """Startup init when running standalone"""
    badge_start()

def sweep_tick():
    """Call on 100ms tick event"""
    global sweep_col, sweep_dir
    
    sweep_mask = sweep_map[sweep_col]

    cls()
    for row in xrange(8):
        if sweep_mask & (0x80 >> row):
            set_pixel(sweep_col, row)
    
    refresh_pixels()
    sweep_col = sweep_col + sweep_dir
    if sweep_col == 0 or sweep_col == 7:
        sweep_dir *= -1

# Set hooks if running standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, sweep_start)
    snappyGen.setHook(SnapConstants.HOOK_100MS, sweep_tick)
