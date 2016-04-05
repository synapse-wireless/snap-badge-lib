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

BUTTON_POLL_RATE = 5  # 10ms polls per button_poll
button_poll_ticks = BUTTON_POLL_RATE
button_hold_count = 0
BUTTON_HELD_ADVANCE = 10  # Button polls before advancing menu selection
BUTTON_HELD_RAPID = 30

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


def menu_button_poll():
    global menu_selected, sel_left_state, sel_right_state, button_poll_ticks, button_hold_count
    
    button_poll_ticks -= 1
    if button_poll_ticks:
        return
    else:
        button_poll_ticks = BUTTON_POLL_RATE
    
    # Ignore buttons while doing select animation (also serves as debounce interval)
    if animating():
        return

    # Current button states
    cur_left = not readPin(BUTTON_LEFT)
    cur_right = not readPin(BUTTON_RIGHT)
    
    # "Press/Release" events indicate state changed since last poll
    left_press = cur_left and not sel_left_state
    left_release = not cur_left and sel_left_state
    right_press = cur_right and not sel_right_state
    right_release = not cur_right and sel_right_state
    both_held = cur_left and cur_right
    both_press = (left_press or right_press) and both_held
    
    # Remember state for next time
    sel_left_state = cur_left
    sel_right_state = cur_right
    
    if left_release or right_release:
        button_hold_count = 0
    
    # Advance to next/prev selection
    if left_press:
        menu_selected -= 1
        button_hold_count = 0
    elif cur_left and not both_held:
        button_hold_count += 1
        if button_hold_count > BUTTON_HELD_RAPID:
            menu_selected -= 1
        elif button_hold_count > BUTTON_HELD_ADVANCE:
            if not (button_hold_count % 4):
                menu_selected -= 1
            
    if right_press:
        menu_selected += 1
        button_hold_count = 0
    elif cur_right and not both_held:
        button_hold_count += 1
        if button_hold_count > BUTTON_HELD_RAPID:
            menu_selected += 1
        elif button_hold_count > BUTTON_HELD_ADVANCE:
            if not (button_hold_count % 4):
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
    menu_button_poll()
    
def menu_update_display():
    display_drv(get_indexed_sym(ord(menu_items[menu_selected])))


# Hook context, for multi-app switching via app_switch.py
menu_context = (menu_init, None, menu_tick10ms, None, None, None)

# Set hooks if running game standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, menu_start)
    snappyGen.setHook(SnapConstants.HOOK_10MS, menu_tick10ms)


