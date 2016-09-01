"""Scrolling text messages for SNAP Badge

   Also incorporates "social mode" - displaying animations when other badges with overlapping
   interests are near.
"""

from drivers.snap_badge import *

from drivers.fonts_8x8 import *
from drivers.DEF8x8 import *
from drivers.Doodads import *
from drivers.batmon import *
from animation import *

show_scroller_text = "ESC 2016   "

tick_count = 0
UPDATE_RATE = 15  # centiseconds
app_exit = None
show_info_mode = False

ANTISOCIAL_BIT = DIP_S8
antisocial = True
SOCIAL_NEARBY_SIGNAL = 50   # Threshold for nearby badges we want to associate with (-dBm)
hello_timer = 0
HELLO_RATE = 20   # seconds minimum between "Hello" animations

# How often shall we say "hello" to meet other badges
SOCIAL_ADVERTISE_INTERVAL = 5  # seconds
social_advertise_tick = 0


def show_scroller_start():
    """Startup hook when run standalone"""
    global current_context
    current_context = show_scroller_context
    set_display_driver(as1115_write_matrix_symbol)
    badge_start()

    # Reduce radio transmit power, since we only want to socialize with nearby badges
    txPwr(0)   # approx 0dBm
    
    show_scroller_init()
    
def show_scroller_init():
    load_font(DEF8x8, DEF8x8_widths)
    update_dipsw(False)

def show_scroller_tick10ms():
    global tick_count, show_info_mode
    
    if animating():
        anim_tick10ms()
        return
    
    tick_count += 1
    if tick_count == UPDATE_RATE:
        tick_count = 0
        wrap = update_scroll_text(1)   # Draw to screen
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
    
def show_scroller_tick1s():
    global hello_timer

    if not animating():
        # Suspend social activity whilst animating
        hello_timer += 1
        socialize()
    
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
    
    antisocial = (dipsw & ANTISOCIAL_BIT) != 0
    
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

def socialize():
    """Say "hello" - be social! Called once per second or in response to another socialite"""
    global social_advertise_tick
    if not antisocial:
        social_advertise_tick += 1
        # Advertise only so often, and only when we can reciprocate
        if social_advertise_tick == SOCIAL_ADVERTISE_INTERVAL:
            social_advertise_tick = 0
            if hello_timer > HELLO_RATE:
                send_hello(True)

def send_hello(initiating):
    """Send hello message with current interests, indicating whether we're initiating or reciprocating"""
    interests = dipsw & DIP_INTERESTS
    print "send hello"
    mcastRpc(1, 1, 'hello', interests, initiating)
            
def hello(interests, initiating):
    """Over-the-air solicitation (or reciprocation) from another badge, presenting the wearer's 'interests' bitmask"""
    global hello_timer
    print "rx hello, lq=", getLq()
    # Only respond if badge is in "show scroller" mode, and signal is nearby
    if current_context == show_scroller_context and getLq() < SOCIAL_NEARBY_SIGNAL:
        if not antisocial and hello_timer > HELLO_RATE:
            hello_timer = 0
            my_interests = dipsw & DIP_INTERESTS
            mutual = interests & my_interests
            if mutual:
                show_mutual_interests(mutual)
                if initiating:
                    send_hello(False)  # reciprocate
            
# Animations, designed to play at rate=20
anim_analog = '\x23\x23\x73\x74\x75\x76\x77\x78\x73\x74\x75\x76\x77\x78'
anim_digital = '\x96\x96\x96\x96\x9e\x9f\x9e\x9f\x9e\x9f\x9e\x9f\x9e\x9f'
anim_stem = '\x25\x25\x25\x25\x0f\x0e\x98\x99\x9a\x9b\x97\x97\x97\x97\x97\x97'
anim_hardware = '\x27\x27\x27\x27\x96\x96\x96\x24\x24\x23\x23\x23'
anim_software = '\x28\x28\x28\x28\x9c\x9d\x9c\x9d\x9c\x9d\x9c\x9d'
anim_iot = '\x00\x26\x26\x26\x93\x94\x95\x93\x94\x95\x93\x94\x95'

def show_mutual_interests(mutual):
    """Play animations for all mutual interests (bitmask) in sequence"""
    interest_set = ''
    if mutual & DIP_ANALOG:
        interest_set += anim_analog
    if mutual & DIP_DIGITAL:
        interest_set += anim_digital
    if mutual & DIP_STEM:
        interest_set += anim_stem
    if mutual & DIP_HARDWARE:
        interest_set += anim_hardware
    if mutual & DIP_SOFTWARE:
        interest_set += anim_software
    if mutual & DIP_IOT:
        interest_set += anim_iot

    load_font(Doodads, Doodads_widths)
    anim_init(interest_set, 20, interest_anim_done)
    anim_begin(3)
    
def interest_anim_done():
    # Restore scrolling font
    load_font(DEF8x8, DEF8x8_widths)

# Hook context, for multi-app switching via app_switch.py
show_scroller_context = (show_scroller_init, None, show_scroller_tick10ms, None, show_scroller_tick1s, show_scroller_pin_event)

# Set hooks if running game standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, show_scroller_start)
    snappyGen.setHook(SnapConstants.HOOK_10MS, show_scroller_tick10ms)
    snappyGen.setHook(SnapConstants.HOOK_1S, show_scroller_tick1s)
    snappyGen.setHook(SnapConstants.HOOK_GPIN, show_scroller_pin_event)


