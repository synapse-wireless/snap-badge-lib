"""AppSwitch - allow runtime switching between hooked-in script applications.

Usage:
  # In your main application script, import and initialize as follows
  from app_switch import *
  app_switch_hooks(snappyGen.setHook)

"""

# Import HOOK_* constants
from snappy.hooks import *

current_context = None

def app_hook_init(setHook):
    """Compile-time: intercept SNAPpy system HOOKs for switching between application scripts"""
    setHook(HOOK_1MS, _tick1ms)
    setHook(HOOK_10MS, _tick10ms)
    setHook(HOOK_100MS, _tick100ms)
    setHook(HOOK_1S, _tick1s)
    setHook(HOOK_GPIN, _pin_event)
    
def app_switch(new_context):
    """Switch all hooks per new_context tuple. Tuple elements can be '0' or 'None' to retain prior
       callback or insert empty one respectively.
       
       new_context tuple format:
         (INIT, 1MS, 10MS, 100MS, 1S, GPIN)
    """
    global as_init, as_tick1ms, as_tick10ms, as_tick100ms, as_tick1s, as_pin_event, current_context
    
    current_context = new_context
    
    h = app_context(new_context[0])
    if h:
        as_init = h
        
    h = app_context(new_context[1])
    if h:
        as_tick1ms = h
        
    h = app_context(new_context[2])
    if h:
        as_tick10ms = h

    h = app_context(new_context[3])
    if h:
        as_tick100ms = h

    h = app_context(new_context[4])
    if h:
        as_tick1s = h

    h = app_context(new_context[5])
    if h:
        as_pin_event = h

    if as_init:
        as_init()


def app_switch_set_exit(exit_func):
    """Set an exit function - to be called by app when it has completed"""
    global app_exit
    app_exit = exit_func

def app_switch_set_background_1s(bg_func):
    """Set a background function - called regardless of which app is loaded"""
    global as_background_1s
    as_background_1s = bg_func

def app_context(func):
    if func:
        return func
    elif func == None:
        return fpass
    else:
        return False

def fpass():
    pass

def _tick1ms():
    as_tick1ms()
    
def _tick10ms():
    as_tick10ms()
    
def _tick100ms():
    as_tick100ms()
    
def _tick1s():
    as_background_1s()
    as_tick1s()
    
def _pin_event(pin, is_set):
    as_pin_event(pin, is_set)


app_exit = fpass    
as_init = fpass
as_tick1ms = fpass
as_tick10ms = fpass
as_tick100ms = fpass
as_tick1s = fpass
as_pin_event = fpass
as_background_1s = fpass

app_switch_pass = (fpass, fpass, fpass, fpass, fpass, fpass)

