# Copyright (C) 2011 Synapse Wireless, Inc.
"""
This SNAPpy script implements "wakeup on pin change" capability for the ATmega128RFA1
This script works in terms of *IO* pins, not GPIO pins. The following IO pins can wake the processor: 0-11,16,20-23
Note that power consumption will be higher if IO 20-23 are used in Edge mode.
"""

# There are 8 "External Interrupt" pins

# EIMSK - External Interrupt Mask
EIMSK = 0x3D

# EIFR - External Interrupt Flag Register
EIFR = 0x3C

# EICRA - External Interrupt Control Register A
# Controls INT3:0
EICRA = 0x69

# EICRB - External Interrupt Control Register B
# Controls INT7:4
EICRB = 0x6A

# Possible "int_sense" (EICRx) settings (per INTx)
INT_IF_LOW = 0
INT_IF_EDGE = 1
INT_IF_FALLING = 2
INT_IF_RISING = 3

# There are also 9 PCINT pins

# PCICR - Pin Change Interrupt Control Register
PCICR = 0x68

# PCIFR - Pin change Interrupt Flag Register
PCIFR = 0x3B

# Bit positions within the above registers
PCI0 = 1
PCI1 = 2

# PCMSK1 Pin Change Mask 1 (PCINT8)
PCMSK1 = 0x6C

# PCMSK0 Pin Change Mask 0 (PCINT7-0)
PCMSK0 = 0x6B

def wakeup_on(pin, is_enabled, int_sense):
    """Controls "wakeup" feature for the specified "IO" (0-11,16,23).
       int_sense = INT_IF_LOW, INT_IF_EDGE, INT_IF_FALLING, INT_IF_RISING
       Note: pins 0-7 are always EDGE triggered (PCINTs)
    """
    # Precompute masks
    if pin == 0: # PCINT0
        mask = 1
        mask2 = 1
    elif pin == 1: # PCINT1
        mask = 2
        mask2 = 1
    elif pin == 2: # PCINT2
        mask = 4
        mask2 = 1
    elif pin == 3: # PCINT3
        mask = 8
        mask2 = 1
    elif pin == 4: # PCINT4
        mask = 16
        mask2 = 1
    elif pin == 5: # PCINT5
        mask = 32
        mask2 = 1
    elif pin == 6: # PCINT6
        mask = 64
        mask2 = 1
    elif pin == 7: # PCINT7
        mask = 128
        mask2 = 1
    elif pin == 8: # INT0
        shift = 0
        shift2 = 0
    elif pin == 9: # INT1
        shift = 1
        shift2 = 2
    elif pin == 10: # INT2
        shift = 2
        shift2 = 4
    elif pin == 11: # INT3
        shift = 3
        shift2 = 6
    elif pin == 16: # PCINT8
        mask = 1
        mask2 = 2
    elif pin == 20: # INT4
        shift = 0
        shift2 = 0
    elif pin == 21: # INT5
        shift = 1
        shift2 = 2
    elif pin == 22: # INT6
        shift = 2
        shift2 = 4
    elif pin == 23: # INT7
        shift = 3
        shift2 = 6
    else:
        return # only certain IOs can do this trick

    # Disable the interrupt while reconfiguring it
    if (pin >= 0) and (pin <= 7):
        poke(PCMSK0, peek(PCMSK0) & ~mask)
    elif (pin >= 8) and (pin <= 11):
        poke(EIMSK, peek(EIMSK) & ~(1 << shift))
    elif pin == 16:
        poke(PCMSK1, peek(PCMSK1) & ~mask)
    elif (pin >= 20) and (pin <= 23):
        poke(EIMSK, peek(EIMSK) & ~(1 << (4+shift)))

    # Polarity (currently only supporting EDGE interrupts)
    if (pin >= 0) and (pin <= 7):
        pass # PCINT0-7 not configurable
    elif (pin >= 8) and (pin <= 11):
        reg = peek(EICRA)
        reg = (reg & ~(3 << shift2)) | (int_sense << shift2)
        poke(EICRA, reg)
    elif pin == 16:
        pass # PCINT8 not configurable
    elif (pin >= 20) and (pin <= 23):
        reg = peek(EICRB)
        reg = (reg & ~(3 << shift2)) | (int_sense << shift2)
        poke(EICRB, reg)

    # Clear any pending flag
    if (pin >= 0) and (pin <= 7):
        poke(PCIFR, peek(PCIFR) | mask2) # writing to the bit resets it
    elif (pin >= 8) and (pin <= 11):
        poke(EIFR, peek(EIFR) | (1 << shift)) # you WRITE a 1 to reset it
    elif pin == 16:
        poke(PCIFR, peek(PCIFR) | mask2) # writing to the bit resets it
    elif (pin >= 20) and (pin <= 23):
        poke(EIFR, peek(EIFR) | (1 << (4+shift))) # you WRITE a 1 to reset it
    
    # Enable interrupt if requested (unconditionally turned off up above)
    if is_enabled:  
        if (pin >= 0) and (pin <= 7):
            poke(PCMSK0, peek(PCMSK0) | mask)
            poke(PCICR, peek(PCICR) | mask2)
        elif (pin >= 8) and (pin <= 11):
            poke(EIMSK, peek(EIMSK) | (1 << shift))
        elif pin == 16:
            poke(PCMSK1, peek(PCMSK1) | mask)
            poke(PCICR, peek(PCICR) | mask2)
        elif (pin >= 20) and (pin <= 23):
            poke(EIMSK, peek(EIMSK) | (1 << (4+shift)))
    else: # Turn off the SHARED interrupt bit if nobody is left
        if (pin >= 0) and (pin <= 7):
            if peek(PCMSK0) == 0:
                poke(PCICR, peek(PCICR) & ~mask2)
        elif pin == 16:
            if (peek(PCMSK1) & 1) == 0:
                poke(PCICR, peek(PCICR) & ~mask2)
