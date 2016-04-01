"""Animation helper for SNAP Badge"""

from drivers.snap_badge import *

anim_rate = 0       # Number of 10ms ticks per frame
anim_icon_set = ""  # Indices into currently loaded fontset
anim_done = None    # Must be set to callback function
anim_countdown = 0
anim_tick = 0

def anim_init(icon_set, rate, done_callback):
    """Initialize with icons to animate between, frame-rate, and callback when done"""
    global anim_icon_set, anim_rate, anim_done
    anim_icon_set = icon_set
    anim_rate = rate
    anim_done = done_callback

def anim_begin():
    """Start animating!"""
    global anim_countdown, anim_tick
    anim_show(0)
    anim_countdown = len(anim_icon_set) + 1
    anim_tick = 0

def anim_tick10ms():
    """Call this from SNAPpy's HOOK_10MS to drive animation"""
    global anim_tick
    
    if anim_tick:
        anim_tick -= 1
    else:
        anim_tick = anim_rate
        anim_frame()

def anim_show(i):
    """Show the indexed icon"""
    display_drv(get_indexed_sym(ord(anim_icon_set[i])))

def anim_frame():
    """Show the next frame - driven by time tick"""
    global anim_countdown
    if anim_countdown:
        anim_countdown -= 1
        if anim_countdown:
            i = len(anim_icon_set) - anim_countdown
            anim_show(i)
        else:
            anim_done()
    
