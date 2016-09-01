"""Frankenscript! - interim, cobbled together demo for early ESC promotion.
   A combination of Breakout, Font-test, and Rollerball. Please refer to those individual scripts 
   for future work.
"""

from drivers.snap_badge import *

from drivers.fonts_8x8 import *
from drivers.OEM6x8 import *
from drivers.DEF8x8 import *
from pixel_lib import *
from fixed_point import *
from free_fall import *
from gestures import *

scroll_tick_count = 0
TEXT_SCROLL_RATE = 10  # centiseconds
game_change_state = 0

# Latest DIP switch value
dipsw = 0x00


# Free-fall timer
flash_count = 0

@setHook(HOOK_STARTUP)
def start():
    badge_start()
    
    monitorPin(ACC_INT1, True)
    monitorPin(BUTTON_LEFT, True)
    monitorPin(BUTTON_RIGHT, True)
    set_display_driver(as1115_write_matrix_symbol)
    load_font(DEF8x8, DEF8x8_widths)
    
    lis_ctrl(1, 0x9f) # Run accelerometer at 5kHz
    lis_ctrl(2, 0x00)
    lis_ctrl(3, 0x40)
    lis_ctrl(4, 0x00)
    lis_ctrl(5, 0x08)
    
    # Initialize zero-g interrupt
    gesture_set_double_tap()
    lis_interrupt_check()
    setRate(3)
    
@setHook(HOOK_1S)
def tick_1s():
    global dipsw, packetserial_countdown
    pulsePin(STATUS_LED, 200, False)
    
    # Poll DIP switch
    sw = ~as1115_rd(KEYB)
    if sw != dipsw:
        dipsw = sw
        handle_dipsw()
        
def handle_dipsw():
    if dipsw & 0x80:
        if dipsw & 0x01:
            # Breakout
            set_scroll_text("")
        elif dipsw & 0x02:
            # Accel demo
            set_scroll_text("")
        elif dipsw & 0x04:
            pass
        elif dipsw & 0x08:
            set_scroll_text("Hi Max   ")
        elif dipsw & 0x10:
            set_scroll_text("Hi Pam   ")
        elif dipsw & 0x20:
            set_scroll_text("Screaming Circuits   ")
        elif dipsw & 0x40:
            set_scroll_text("Sunstone Circuits   ")
        else:
            set_scroll_text("ESC 2016   ")
    else:
        stext = ""
        if dipsw & 0x01:
            stext += "STEM  "
        if dipsw & 0x02:
            stext += "Analog  "
        if dipsw & 0x04:
            stext += "Digital  "
        if dipsw & 0x08:
            stext += "Hardware  "
        if dipsw & 0x10:
            stext += "Software  "
        if dipsw & 0x20:
            stext += "IoT  "
            
        if stext:
            set_scroll_text(stext)
        else:
            set_scroll_text("ESC 2016   ")

def set_delay(new_delay):
    global delay, delay_counter
    delay = new_delay
    delay_counter = delay

@setHook(HOOK_100MS)
def timer_100ms():
    global flash_count

    if flash_count:
        flash_count -=1
        if flash_count == 0:
            led_off()


@setHook(HOOK_GPIN)
def pin_event(pin, is_set):
    global flash_count
    
    if pin == ACC_INT1:
        if is_set:
            flash_count = 4
            led_on()
            
def led_on():
    for x in xrange(2,6):
        for y in xrange(2,6):
            set_pixel(x, y)
    refresh_pixels()
    
def led_off():
    cls()
    refresh_pixels()