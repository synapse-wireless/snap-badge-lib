# Copyright (C) 2014 Synapse Wireless, Inc.
"""ATmega128RFA1 internal battery monitor support
The Battery Monitor can be configured using the BATMON register. Register subfield
BATMON_VTH sets the threshold voltage. It is configurable with a resolution of 75 mV
in the upper voltage range (BATMON_HR = 1) and with a resolution of 50 mV in the
lower voltage range (BATMON_HR = 0).
"""

BATMON_REG = 0x151
BATMON_HR = 0x10    # select high/low range
BATMON_OK = 0x20    # set if batt voltage is above Vth
BATMON_SNAP_DEFAULT = 0x06

low_range = (1700, 1750, 1800, 1850, 1900, 1950, 2000, 2050, 2100, 2150, 2200, 2250, 2300, 2350, 2400, 2450)
high_range = (2550, 2625, 2700, 2775, 2850, 2925, 3000, 3075, 3150, 3225, 3300, 3375, 3450, 3525, 3600, 3675)

def batmon_mv():
    
    i = 16
    while i > 0:
        i = i - 1
        poke(BATMON_REG, BATMON_HR | i)
        if peek(BATMON_REG) & BATMON_OK:
            poke(BATMON_REG, BATMON_SNAP_DEFAULT)
            return high_range[i]

    i = 16
    while i > 0:
        i = i - 1
        poke(BATMON_REG, i)
        if peek(BATMON_REG) & BATMON_OK:
            poke(BATMON_REG, BATMON_SNAP_DEFAULT)
            return low_range[i]

    return 0
 