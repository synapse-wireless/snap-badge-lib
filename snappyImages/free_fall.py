from drivers.atmega128rfa1_math import *
from drivers.atmega128rfa1_timers import *

def init_free_fall_timer():
    timer_init(TMR5, WGM_NORMAL, CLK_FOSC_DIV1024, 0)
    

# Gravity inches per timebase**2
# Timebase = 64uS
gravity_per_timebase = '\x00\x01\xEE\x05'

def calc_fall_height(fall_time):
    """Calculate free-fall distance by measuring elapsed time from zero-g event to high-g event"""
    fall_time = itos(fall_time)
    fall_time = mult_32(fall_time, fall_time)
    fall_height = div_32(fall_time, gravity_per_timebase)
    
    return stoi(fall_height)