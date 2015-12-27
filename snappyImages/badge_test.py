"""Test script for SNAP Badge"""

from drivers.snap_badge import *
from drivers.lis3dh_accel import *

@setHook(HOOK_STARTUP)
def start():
    badge_init_pins()
    
    monitorPin(BUTTON_LEFT, True)
    monitorPin(BUTTON_RIGHT, True)
    
    
@setHook(HOOK_1S)
def tick_1s():
    pulsePin(STATUS_LED, 200, False)
    
    
@setHook(HOOK_GPIN)
def pin_event(pin, is_set):
    if not is_set:
        if pin == BUTTON_LEFT:
            print "Left button"
        else:
            print "Right button"
            

def test_sleep(secs):
    """Allow time to measure sleep current"""
    writePin(STATUS_LED, True)
    sleep(2, secs)
    
