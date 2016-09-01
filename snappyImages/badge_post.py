"""Badge Post - receive and act upon informational display messages broadcast from remote hosts.

Animations can be used for remote-controlled synchronized party fun...
  mcastRpc(1, 2, 'anime', '\x73\x74\x75\x76\x77\x78', 5, 10)  # sine wave
  mcastRpc(1, 2, 'anime', '\x6c\x00\x6c\x00\x6c\x00\x00\x00', 50, 4)  # jaws
  mcastRpc(1, 2, 'anime', '\x0e\x0f', 30, 10)  # beat
  mcastRpc(1, 2, 'anime', '\x8d\x8e\x8d\x8f\x8d\x8e\x8f', 15, 10)  # dance
  
  mcastRpc(1, 2, 'message', "Lunch! ", 30)  # Show "Lunch!" message for 30 seconds
  
Broadcast pings and dmcast of animations can be used for contests, with random selection controlled by
a SNAP Connect app at the central host.

"""

from drivers.snap_badge import *
from drivers.fonts_8x8 import *
from drivers.DEF8x8 import *
from drivers.Doodads import *
from app_switch import *
from animation import *

tick_count = 0
UPDATE_RATE = 15  # centiseconds
app_exit = None
prior_context = None
msg_duration = 0

def messaging_start():
    """Startup hook when run standalone"""
    set_display_driver(as1115_write_matrix_symbol)
    badge_start()
    messaging_init()
    
def messaging_init():
    pass

def save_context():
    """Save current context so we can resume later"""
    global prior_context
    if current_context != messaging_context:
        prior_context = current_context

def message(message_text, duration):
    """Over the air command: display message text for specified duration in seconds"""
    global msg_duration
    save_context()
    app_switch(messaging_context)
    
    # Set message and switch over
    load_font(DEF8x8, DEF8x8_widths)
    msg_duration = duration
    set_scroll_text(message_text)

def anime(icon_set, rate, loop_count):
    """Over the air command: display animation using Doodads font"""
    save_context()
    app_switch(messaging_context)
    
    load_font(Doodads, Doodads_widths)
    anim_init(icon_set, rate, messaging_resume_prior)
    anim_begin(loop_count)

def messaging_resume_prior():
    """We now return to your regularly scheduled programming"""
    if prior_context:
        app_switch(prior_context)

def messaging_tick10ms():
    global tick_count
    if msg_duration:
        tick_count += 1
        if tick_count == UPDATE_RATE:
            tick_count = 0
            update_scroll_text(1)
    else:
        anim_tick10ms()
    
def messaging_tick1s():
    global msg_duration
    if msg_duration:
        msg_duration -= 1
        if not msg_duration:
            messaging_resume_prior()     
    
def messaging_pin_event(pin, is_set):
    if not is_set:
        # Button combinations
        lb = not readPin(BUTTON_LEFT)
        rb = not readPin(BUTTON_RIGHT)
        
        # Exit to menu if both buttons pressed
        if lb and rb:
            if app_exit:
                app_exit()



# Hook context, for multi-app switching via app_switch.py
messaging_context = (messaging_init, None, messaging_tick10ms, None, messaging_tick1s, messaging_pin_event)

# Set hooks if running game standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, messaging_start)
    snappyGen.setHook(SnapConstants.HOOK_10MS, messaging_tick10ms)
    snappyGen.setHook(SnapConstants.HOOK_1S, messaging_tick1s)
    snappyGen.setHook(SnapConstants.HOOK_GPIN, messaging_pin_event)


