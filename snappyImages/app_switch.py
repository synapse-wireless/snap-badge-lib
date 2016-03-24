"""AppSwitch - allow runtime switching between hooked-in scripapplications"""

as_init = None
as_tick1ms = None
as_tick10ms = None
as_tick100ms = None
as_tick1s = None

def app_switch(new_context):
    global as_init, as_tick1ms, as_tick10ms, as_tick100ms, as_tick1s
    
    h = new_context[0]
    if h:
        as_init = h
    h = new_context[1]
    if h:
        as_tick1ms = h
    h = new_context[2]
    if h:
        as_tick10ms = h

    h = new_context[3]
    if h:
        as_tick100ms = h

    h = new_context[4]
    if h:
        as_tick1s = h

    if as_init:
        as_init()


def fpass():
    pass

app_switch_dummy_context = (fpass, fpass, fpass, fpass, fpass)

def app_switch_init():
    app_switch(app_switch_dummy_context)

    
#snappyGen.setHook(SnapConstants.HOOK_1S, as_tick1s)
