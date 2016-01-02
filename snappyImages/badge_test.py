"""Test script for SNAP Badge"""

from drivers.snap_badge import *
from drivers.lis3dh_accel import *
from drivers.as1115_led_keyscan import *

# Latest DIP switch value
dipsw = 0x00

@setHook(HOOK_STARTUP)
def start():
    badge_init_pins()
    lis_init()
    writePin(LED_PWR_EN, True)
    as1115_init()
    
    monitorPin(BUTTON_LEFT, True)
    monitorPin(BUTTON_RIGHT, True)
    monitorPin(ACC_INT1, True)
    
@setHook(HOOK_1S)
def tick_1s():
    global dipsw
    pulsePin(STATUS_LED, 200, False)
    
    sw = as1115_rd(KEYA)
    if sw != dipsw:
        dipsw = sw
        ds = ""
        for i in xrange(8):
            ds += "1" if dipsw & (0x80 >> i) else "0"
        print "DIP=", ds
        
    
@setHook(HOOK_GPIN)
def pin_event(pin, is_set):
    if is_set:
        if pin == ACC_INT1:
            print "Motion detected"
    else:
        # Button combinations
        lb = not readPin(BUTTON_LEFT)
        rb = not readPin(BUTTON_RIGHT)
        
        if pin == BUTTON_LEFT:
            print "Left button"
            if rb:
                as1115_write_matrix_symbol(SYM_CHECKERBOARD)
            else:
                as1115_write_matrix_symbol(SYM_ALL_OFF)
        elif pin == BUTTON_RIGHT:
            print "Right button"
            if lb:
                as1115_write_matrix_symbol(SYM_CHECKERBOARD)
            else:
                as1115_write_matrix_symbol(SYM_ALL_ON)
    

def test_sleep(secs):
    """Allow time to measure sleep current"""
    writePin(STATUS_LED, True)
    writePin(LED_PWR_EN, False)
    lis_sleep()

    sleep(2, secs)
    
    lis_wake()
    writePin(LED_PWR_EN, True)
    as1115_init()
    
