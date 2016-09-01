"""Test script for SNAP Badge

Next steps:
  When no buttons pressed, display reflects DIP switch (columns) and accelerometer (height) bar-graph.
  Left hold = All off, Right hold = All on, Both = Checker
"""

from drivers.snap_badge import *
from synapse.switchboard import *

# Latest DIP switch value
dipsw = 0x00

# Packetserial control via USB port
packetserial_enabled = True
#packetserial_countdown = 5  # seconds grace period before disconnect
packetserial_countdown = 0  # seconds grace period before disconnect

@setHook(HOOK_STARTUP)
def start():
    badge_start()
    
    monitorPin(BUTTON_LEFT, True)
    monitorPin(BUTTON_RIGHT, True)
    monitorPin(ACC_INT1, True)
    
@setHook(HOOK_1S)
def tick_1s():
    global dipsw, packetserial_countdown
    pulsePin(STATUS_LED, 200, False)
    
    # Poll DIP switch
    sw = as1115_rd(KEYB)
    if sw != dipsw:
        dipsw = sw
        ds = ""
        for i in xrange(8):
            ds += "1" if dipsw & (0x80 >> i) else "0"
        print "DIP=", ds
        
    # Disable packetserial after grace period
    if packetserial_countdown:
        packetserial_countdown -= 1
        if packetserial_countdown == 0:
            enable_packet_serial(False)
    
    
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
            if rb:
                print "Both buttons (checker)"
                as1115_write_matrix_symbol(SYM_CHECKERBOARD)
            else:
                print "Left button (all off)"
                as1115_write_matrix_symbol(SYM_ALL_OFF)
        elif pin == BUTTON_RIGHT:
            if lb:
                print "Both buttons (checker)"
                as1115_write_matrix_symbol(SYM_CHECKERBOARD)
            else:
                print "Right button (all on)"
                as1115_write_matrix_symbol(SYM_ALL_ON)
    

def enable_packet_serial(do_enable):
    global packetserial_enabled
    packetserial_enabled = do_enable
    
    if do_enable:
        crossConnect(DS_PACKET_SERIAL, DS_UART1)
        initUart(1, 38400)
    else:
        crossConnect(DS_PACKET_SERIAL, DS_NULL)
        initUart(1, 0)
