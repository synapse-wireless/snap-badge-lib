"""Gesture detection for SNAP Badge, using the LIS3DH accelerometer.
Note: this could be enhanced to use the LIS3D hardware for detection, with the advantage of much lower
      cpu utilization and better performance including wake on interrupt. The initial software based
      implementation has the advantage of being easy to understand and experiment with.
"""

from drivers.lis3dh_accel import *

# Detected gestures
GESTURE_DOWN = 0     # Badge held vertical, then flipped down face-up
GESTURE_ZERO_G = 1   # Badge experienced zero-g condition
GESTURE_HIGH_G = 2   # Badge experienced high-g condition

# Double tap configuration parameters  
DT_CFG1 = 0x77      # ODR = 400Hz
DT_CFG2 = 0x84      # Enable High-pass filter
DT_CFG3 = 0xc0      # Set INT1 pin
DT_SRC = 0x20
DT_THRESHOLD = 0x50
DT_CFG = 0x20
DT_LIMIT = 0x17     # 57.5ms
DT_LATENCY = 0x25   # 92.5ms
DT_WINDOW = 0x30    # 120ms

gesture_debounce = 20
gesture_cb = None

def gesture_set_callback(cb):
    """Set callback when gesture detected. Callback receives detected gesture type as parameter.
         ex: def my_gestures(gesture_type): ...
    """
    global gesture_cb
    gesture_cb = cb

def gesture_update_accel():
    """Track accelerometer position readings from last poll. Enables determining inertial 'diffs' of each axis"""
    global gest_last_x, gest_last_y, gest_last_z
    gest_last_x = lis_axis_x
    gest_last_y = lis_axis_y
    gest_last_z = lis_axis_z


def gesture_poll_10ms():
    """Called by system every 10ms"""
    global gesture_debounce

    # Poll the accelerometer
    lis_read()
    
    # Debounce gesture detection
    if gesture_debounce:
        gesture_debounce -= 1
    else:
        #print lis_axis_x, ",", lis_axis_y, ",", lis_axis_z
        #print "dxyz=", lis_axis_x - rps_last_x, ",",lis_axis_y - rps_last_y, ",",lis_axis_z - rps_last_z
        
        # Detect GESTURE_DOWN event
        dz = lis_axis_z - gest_last_z
        if dz > 6000:
            if gesture_cb:
                gesture_cb(GESTURE_DOWN)
            gesture_debounce = 20
    
    gesture_update_accel()
    
def gesture_set_zero_g():
    """Configure accelerometer to detect zero-g condition and set interrupt"""
    lis_int1(0x95, 0x10, 0x10)
    
def gesture_set_high_g():
    """Configure accelerometer to detect high-g condition and set interrupt"""
    lis_int1(0x2a, 0x30, 0x00)
    
def gesture_set_double_tap():
    """Configure accelerometer to detect double tap and set interrupt"""
    lis_ctrl(1, DT_CFG1)
    lis_ctrl(2, DT_CFG2)
    lis_ctrl(3, DT_CFG3)
    lis_tap_cfg(DT_SRC, DT_THRESHOLD, DT_CFG, DT_LIMIT, DT_LATENCY, DT_WINDOW)
    