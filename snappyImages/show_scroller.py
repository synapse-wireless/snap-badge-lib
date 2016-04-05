"""Scrolling text messages for SNAP Badge"""

from drivers.snap_badge import *

from drivers.fonts_8x8 import *
from drivers.DEF8x8 import *
from drivers.batmon import *

show_scroller_text = "ESC 2016   "

tick_count = 0
UPDATE_RATE = 15  # centiseconds
app_exit = None
show_info_mode = False
antisocial = True

def show_scroller_start():
    """Startup hook when run standalone"""
    set_display_driver(as1115_write_matrix_symbol)
    badge_start()
    show_scroller_init()
    
def show_scroller_init():
    load_font(DEF8x8, DEF8x8_widths)
    update_dipsw(False)

def show_scroller_tick10ms():
    global tick_count, show_info_mode
    tick_count += 1
    if tick_count == UPDATE_RATE:
        tick_count = 0
        wrap = update_scroll_text(1)
        if wrap and not show_info_mode:
            # Poll during vertical blanking interval :)
            poll_dipsw()
            
    # If either button is held, display sys-info
    if not (readPin(BUTTON_RIGHT) and readPin(BUTTON_LEFT)):
        if not show_info_mode:
            show_info_mode = True
            batt_mv = str(batmon_mv())
            info_text = batt_mv[0] + '.' + batt_mv[1:3] + "V Batt="
            set_scroll_text(info_text)
    else:
        if show_info_mode:
            show_info_mode = False
            update_dipsw(False)
    
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
        update_dipsw(True)

def update_dipsw(dip_change):
    global antisocial
    
    stext = show_scroller_text
    
    user_msg = loadNvParam(NV_USER_MSG)
    if user_msg:
        stext = user_msg + '  ' + show_scroller_text
        i_disp = 0
    else:
        i_disp = len(stext)
    
    if dip_change:
        i_disp = len(stext)
    
    antisocial = (dipsw & DIP_S8) != 0
    
    if not antisocial:
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
    set_scroll_index(i_disp)


# Hook context, for multi-app switching via app_switch.py
show_scroller_context = (show_scroller_init, None, show_scroller_tick10ms, None, None, show_scroller_pin_event)

# Set hooks if running game standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, show_scroller_start)
    snappyGen.setHook(SnapConstants.HOOK_10MS, show_scroller_tick10ms)
    snappyGen.setHook(SnapConstants.HOOK_GPIN, show_scroller_pin_event)


