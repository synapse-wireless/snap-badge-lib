"""menu_select: SNAP Badge script to allow user selection from a list of icons.

TODO: factor out animation, replace with animation.py helper functions.

"""

from drivers.fonts_8x8 import *
from drivers.Doodads import *

SELECT_ANIM_ICON_BASE = 108   # Doodads font index

menu_selected = 0
menu_fontset = None
menu_fontwidth = None
menu_items = None
menu_select_callback = None
menu_anim_tick = 0   # Animation based on 10ms tick
menu_anim_rate = 5   # Ticks per animation frame

# Button states
sel_left_state = False
sel_right_state = False


def menu_start():
    """Startup hook when run standalone"""
    set_display_driver(as1115_write_matrix_symbol)
    badge_start()
    setPinDir(BUTTON_LEFT, False)
    setPinPullup(BUTTON_LEFT, True)
    monitorPin(BUTTON_LEFT, True)
    setPinDir(BUTTON_RIGHT, False)
    setPinPullup(BUTTON_RIGHT, True)
    monitorPin(BUTTON_RIGHT, True)
    menu_init()
    
def menu_init():
    """Initialize menu selection. Assumes badge already initialized."""
    global sel_left_state, sel_right_state
    sel_left_state = not readPin(BUTTON_LEFT)
    sel_right_state = not readPin(BUTTON_RIGHT)

    menu_update_display()
    
    setPinDir(STATUS_LED, True)
    writePin(STATUS_LED, True)   # Active low

def menu_define(items, fontset, fontwidth, hook, first):
    """Define a new menu"""
    global menu_selected, menu_items, menu_select_callback,  menu_fontset, menu_fontwidth
    menu_fontset = fontset
    menu_fontwidth = fontwidth
    menu_items = items
    load_font(menu_fontset, menu_fontwidth)
    menu_select_callback = hook
    menu_selected = first

def menu_pin_event(pin, is_set):
    global menu_selected, sel_left_state, sel_right_state
    
    cur_left = not readPin(BUTTON_LEFT)
    cur_right = not readPin(BUTTON_RIGHT)
    
    left_press = cur_left and not sel_left_state
    right_press = cur_right and not sel_right_state
    both_press = (left_press or right_press) and (cur_left and cur_right)
    sel_left_state = left_press
    sel_right_state = right_press
    
    # Ignore buttons while doing select animation (also serves as debounce interval)
    if select_anim_countdown:
        return

    # Advance to next/prev selection
    if left_press:
        menu_selected -= 1
    if right_press:
        menu_selected += 1

    menu_selected %= len(menu_items)
    
    if both_press:
        # Pressing both buttons ultimately generates "Select" callback
        start_select_animation()
    else:
        menu_update_display()


select_anim_countdown = 0
def start_select_animation():
    global select_anim_countdown
    select_anim_countdown = 6   # Number of icons in animation, zero returns to menu selection
    load_font(Doodads, Doodads_widths)
    select_anim_show()

def select_anim_show():
    display_drv(get_indexed_sym(SELECT_ANIM_ICON_BASE + select_anim_countdown))
    pulsePin(STATUS_LED, 10, False)

def menu_tick10ms():
    global menu_anim_tick
    
    if menu_anim_tick:
        menu_anim_tick -= 1
    else:
        menu_anim_tick = menu_anim_rate
        menu_anim_frame()
        
def menu_anim_frame():
    global select_anim_countdown
    
    if select_anim_countdown:
        select_anim_countdown -= 1
        if select_anim_countdown:
            select_anim_show()
        else:
            load_font(menu_fontset, menu_fontwidth)
            menu_update_display()
            menu_select_callback(menu_selected)
    
        
def menu_update_display():
    display_drv(get_indexed_sym(ord(menu_items[menu_selected])))


# Hook context, for multi-app switching via app_switch.py
menu_context = (menu_init, None, menu_tick10ms, None, None, menu_pin_event)

# Set hooks if running game standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, menu_start)
    snappyGen.setHook(SnapConstants.HOOK_GPIN, menu_pin_event)
    snappyGen.setHook(SnapConstants.HOOK_100MS, menu_tick100ms)



            

