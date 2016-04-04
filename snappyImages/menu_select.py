"""menu_select: SNAP Badge script to allow user selection from a list of icons.
"""

from drivers.fonts_8x8 import *
from drivers.Doodads import *
from animation import *

# Play animation (Doodads font indices) to confirm selection
menu_selected_anim = "\x72\x71\x70\x6f\x6e\x6d\x69\x69"

menu_selected = 0
menu_fontset = None
menu_fontwidth = None
menu_items = None
menu_select_callback = None

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
    
    # Test menu
    menu_define("\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29", Doodads, Doodads_widths, None, 0)
    
    menu_init()
    
def menu_init():
    """Initialize menu selection. Assumes badge already initialized, and a menu defined."""
    global sel_left_state, sel_right_state
    sel_left_state = not readPin(BUTTON_LEFT)
    sel_right_state = not readPin(BUTTON_RIGHT)

    anim_init(menu_selected_anim, 3, selected_anim_done)

    load_font(menu_fontset, menu_fontwidth)
    menu_update_display()

def menu_define(items, fontset, fontwidth, hook, first):
    """Define a new menu. Only one at a time can be held."""
    global menu_selected, menu_items, menu_select_callback,  menu_fontset, menu_fontwidth
    menu_fontset = fontset
    menu_fontwidth = fontwidth
    menu_items = items
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
    if animating():
        return

    # Advance to next/prev selection
    if left_press:
        menu_selected -= 1
    if right_press:
        menu_selected += 1

    menu_selected %= len(menu_items)
    
    if both_press:
        # Pressing both buttons ultimately generates "Select" callback
        load_font(Doodads, Doodads_widths)
        anim_begin(1)
    else:
        menu_update_display()

def selected_anim_done():
    """Called when 'selected' animation completes"""
    load_font(menu_fontset, menu_fontwidth)
    menu_update_display()
    if menu_select_callback:
        menu_select_callback(menu_selected)

def menu_tick10ms():
    anim_tick10ms()
        
def menu_update_display():
    display_drv(get_indexed_sym(ord(menu_items[menu_selected])))


# Hook context, for multi-app switching via app_switch.py
menu_context = (menu_init, None, menu_tick10ms, None, None, menu_pin_event)

# Set hooks if running game standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, menu_start)
    snappyGen.setHook(SnapConstants.HOOK_GPIN, menu_pin_event)
    snappyGen.setHook(SnapConstants.HOOK_10MS, menu_tick10ms)



            

