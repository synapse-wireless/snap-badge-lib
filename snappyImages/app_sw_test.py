from drivers.snap_badge import *

from app_switch import *
app_hook_init(snappyGen.setHook)

from snake import *

led_state = False
context = 0

@setHook(HOOK_STARTUP)
def start():
    app_switch(context0)

def pin_event(pin, is_set):
    global context
    if not is_set:
        # Button pressed
        
        if context == 0:
            app_switch(context1)
            context = 1
        elif context == 1:
            app_switch(snake_context)
            context = 2
        elif context == 2:
            app_switch(context0)
            context = 0
            
def init_pins():
    setPinDir(STATUS_LED, True)
    setPinDir(BUTTON_LEFT, False)
    setPinPullup(BUTTON_LEFT, True)
    monitorPin(BUTTON_LEFT, True)

def toggle():
    global led_state
    led_state = not led_state
    writePin(STATUS_LED, led_state)

# Context: (INIT, 1MS, 10MS, 100MS, 1S, GPIN)
context0 = (init_pins, None, None, toggle, None, pin_event)
context1 = (init_pins, None, None, None, toggle, pin_event)

