"""Dice - daily dose of random for the SNAP Badge

TODO:
  Multiplayer: successive dice choose random offset to animation delay

"""

from drivers.snap_badge import *
from drivers.fonts_8x8 import *
from drivers.Doodads import *
from animation import *
from drivers.true_random import *

dice_is_vert = False
dice_icons = ''.join([chr(dc) for dc in xrange(7,13)])

def dice_start():
    set_display_driver(as1115_write_matrix_symbol)
    badge_start()
    dice_init()
    
def dice_init():
    load_font(Doodads, Doodads_widths)
    anim_init(dice_icons, 8, dice_anim_done)

def dice_anim_done():
    i = true_random() / 684   # range 0-5
    anim_show(i)

def dice_down():
    print "down"
    anim_show(0)
    anim_begin()

def dice_tick10ms():
    global dice_is_vert
    anim_tick10ms()
    
    lis_read()
    #print lis_axis_x, ",", lis_axis_y, ",", lis_axis_z
    if lis_axis_z < 1000:
        dice_is_vert = True
    elif lis_axis_z > 10000:
        if dice_is_vert:
            dice_down()
        dice_is_vert = False
            

# Hook context, for multi-app switching via app_switch.py
dice_context = (dice_init, None, dice_tick10ms, None, None, None)

# Set hooks if running game standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, dice_start)
    snappyGen.setHook(SnapConstants.HOOK_10MS, dice_tick10ms)



    