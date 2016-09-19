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
free_fall = False
next_fall_timeout = 10
SETUP_TIME_OFFSET = 250

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
    
    init_free_fall_timer()
    # Initialize zero-g interrupt
    gesture_set_zero_g()
    lis_interrupt_check()
    setRate(3)


@setHook(HOOK_10MS)
def tick10ms():
    global scroll_tick_count
    scroll_tick_count += 1
    if scroll_tick_count == TEXT_SCROLL_RATE:
        scroll_tick_count = 0
        update_scroll_text(1)   # Does nothing if no scroll text
        
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
def tick_100ms():
    global delay_counter
    global game_change_state

    if game_change_state:
        game_change_state -= 1
        if game_change_state == 0:
            stop_scroll_text()
            
    # Blocking window after fall - When the tag hits the ground, it usually bounces triggering a new fall
    # event. Let's block for a period of time to ignore the bounces
    global free_fall
    global next_fall_timeout
    if next_fall_timeout:
        next_fall_timeout -=1
        if next_fall_timeout == 0:
            free_fall = False
            gesture_set_zero_g()
            lis_interrupt_check()
            monitorPin(ACC_INT1, True)


@setHook(HOOK_GPIN)
def pin_event(pin, is_set):
    global free_fall, next_fall_timeout
    
    if pin == ACC_INT1:
        if is_set:
            if free_fall:
                fall_time = get_tmr_count(TMR5) + SETUP_TIME_OFFSET
                fall_height = calc_fall_height(fall_time)
                
                # Prepare for next fall
                next_fall_timeout = 15
                
                text = str(fall_height/10) + '.' + str(fall_height%10) + '"  '
                set_scroll_text(text)
            else:
                # We are in free-fall, Reset counter and begin counting
                set_tmr_count(TMR5, 0)
                #free_fall = True
                monitorPin(ACC_INT1, False)
                
                gesture_set_high_g()
                lis_interrupt_check()
                while not lis_interrupt_check():
                    pass
                # landed
                fall_time = get_tmr_count(TMR5) + SETUP_TIME_OFFSET
                fall_height = calc_fall_height(fall_time)
                
                # Prepare for next fall
                next_fall_timeout = 15
                
                text = str(fall_height/10) + '.' + str(fall_height%10) + '"  '
                set_scroll_text(text)
                