"""Gesture detection for SNAP Badge, using the LIS3DH accelerometer.
Note: this could be enhanced to use the LIS3D hardware for detection, with the advantage of much lower
      cpu utilization and better performance including wake on interrupt. The initial software based
      implementation has the advantage of being easy to understand and experiment with.
"""

from drivers.lis3dh_accel import *

# Detected gestures
GESTURE_DOWN = 0

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
        if dz > 10000:
            if gesture_cb:
                gesture_cb(GESTURE_DOWN)
            gesture_debounce = 20
    
    gesture_update_accel()
