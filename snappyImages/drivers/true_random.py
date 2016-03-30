"""True random number access for ATmega128RFA1 based hardware.
   Not needed for SNAP Core v2.7+ since this is implemented in core.
"""

PHY_RSSI = 0x146
def true_random():
    value = 0
    for i in xrange(0,6):
        value <<= 2
        value |= (peek(PHY_RSSI)>>5)&0x3
    return value

