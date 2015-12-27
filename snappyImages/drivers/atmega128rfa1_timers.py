# (c) Copyright 2011-2015, Synapse Wireless, Inc.
"""ATmega128RFA1 timer support
Currently covers setup for basic timing and PWM operation.

Currently supports 16-bit Timers 1,3,4,5 as well as 8-bit Timers 0,2.

Note: Timer 0/2 functions/constants are separate, but share the Clock Select (CS)
      and Compare Output Mode (COM) constants.

Note: Timer4 is used as SNAP's 1ms timer, and Timer5 is used by some sleep modes.

Ex.
  #Setup timer1 as 2MHz free-running counter (assumes 16MHz system clock)
  timer_init(TMR1, WGM_NORMAL, CLK_FOSC_DIV8, 0)

Ex.
  #Setup OC3C for 8-bit PWM at 2MHz, 50% duty cycle
  timer_init(TMR3, WGM_FASTPWM8, CLK_FOSC_DIV8, 0)
  set_tmr_ocr(TMR3, OCRxC, 127)  # Set C output duty cycle (127/255)
  set_tmr_output(TMR3, OCRxC, TMR_OUTP_CLR)  # Enable PWM on pin
  # ...
  set_tmr_output(TMR3, OCRxC, TMR_OUTP_OFF)  # Restore pin to regular I/O
  
Ex.
  #Generate a 500uS one-shot pulse on OC0B
  timer8_init(TMR0, WGM0_FASTPWM8_TOP_OCRA, CLK_FOSC_DIV256)  # 16us period
  set_tmr8_output(TMR0, OCR0B, TMR_OUTP_SET)   # Set on match
  set_tmr8_ocr(TMR0, OCR0A, 0)                 # Top=Bottom (one-shot mode)
  match = 256 - 31                       # 31 * 16us = 496us
  set_tmr8_ocr(TMR0, OCR0B, match)
  # Generate pulse, by setting count just below match (will end at overflow)
  set_tmr8_count(TMR0, match - 1)
  
  
  http://www.atmel.com/Images/Atmel-8266-MCU_Wireless-ATmega128RFA1_Datasheet.pdf

"""

# Base address for Timers
TMR1 = 0x80
TMR3 = 0x90
TMR4 = 0xA0
TMR5 = 0x120

# ATmega128RFA1 Timer register offsets
TCCRxA = 0x00  # Timer/Counter Control Register  A
TCCRxB = 0x01  # Timer/Counter Control Register  B
TCCRxC = 0x02  # Timer/Counter Control Register  C
TCNTx = 0x04  # Timer/Counter Low Order Byte (+1 for High Byte)
ICRx = 0x06   # Input Capture Registers Low Order Byte (+1 for High Byte)
OCRxA = 0x08   # Output Compare Registers A Low Order Byte (+1 for High Byte)
OCRxB = 0x0A   # Output Compare Registers B Low Order Byte (+1 for High Byte)
OCRxC = 0x0C   # Output Compare Registers C Low Order Byte (+1 for High Byte)

# Compare Output Modes (COM)
TMR_OUTP_OFF = 0
TMR_OUTP_TGL = 1
TMR_OUTP_CLR = 2
TMR_OUTP_SET = 3

# Common Waveform Generation Modes
WGM_NORMAL = 0
WGM_FASTPWM8 = 5
WGM_FASTPWM16_TOP_ICR = 14
WGM_FASTPWM16_TOP_OCR = 15

# Clock Select
CLK_FOSC = 1
CLK_FOSC_DIV8 = 2
CLK_FOSC_DIV64 = 3
CLK_FOSC_DIV256 = 4
CLK_FOSC_DIV1024 = 5
CLK_EXT_FALLING = 6
CLK_EXT_RISING = 7

# TMR0 register base and offsets
TMR0 = 0x44
TCCR0A = 0x00  # Timer/Counter Control Register  A
TCCR0B = 0x01  # Timer/Counter Control Register  A
TCNT0  = 0x02  # Timer0 Count
OCR0A  = 0x03  # Output Compare Register A
OCR0B  = 0x04  # Output Compare Register B
WGM0_NORMAL = 0
WGM0_FASTPWM8 = 3  # TOP=0xFF
WGM0_FASTPWM8_TOP_OCRA = 7

# TMR2 runs on 32kHz crystal, has different prescaler consts
TMR2 = 0xB0  # Register offsets and WGMs are same as TMR0
CLK2_FOSC = 1
CLK2_FOSC_DIV8 = 2
CLK2_FOSC_DIV32 = 3
CLK2_FOSC_DIV64 = 4
CLK2_FOSC_DIV128 = 5
CLK2_FOSC_DIV256 = 6
CLK2_FOSC_DIV1024 = 7

# Synchronization control (All timers)
GTCCR  = 0x43  # General Timer Counter Control Register


def set_tmr_ocr(tmr, ocr, val):
    """Set OCR register. This controls the duty cycle (duty/TOP) in some
    PWM modes"""
    poke(tmr + ocr + 1, (val >> 8) & 0xFF)  # high byte
    poke(tmr + ocr, val & 0xff)  # low byte


def set_tmr_output(tmr, ocr, mode):
    """Set output mode"""
    shift = 14 - ocr
    mask = ~(0x03 << shift)
    val = peek(tmr)
    val = (val & mask) | (mode << shift)
    poke(tmr, val)


def get_tmr_count(tmr):
    """Read immediate count value"""
    return peek(tmr + TCNTx) | (peek(tmr + TCNTx + 1) << 8)


def set_tmr_count(tmr, count):
    """Set immediate count value"""
    poke(tmr + TCNTx + 1, (count >> 8) & 0xFF)  # high byte
    poke(tmr + TCNTx, count & 0xff)  # low byte


def timer_init(tmr, wgm_mode, clk_sel, icr):
    """Initialize waveform generation mode, clock select, and input-capture"""
    # TCCRxA
    value = wgm_mode & 0x03  # Set COMxA/B/C = O (off), and LSBs of WGM
    poke(tmr + TCCRxA, value)

    # TCCRxB
    value = (wgm_mode & 0x0C) << 1
    value |= clk_sel & 0x07
    poke(tmr + TCCRxB, value)

    # ICRx
    poke(tmr + ICRx + 1, (icr >> 8) & 0xFF)  # high byte
    poke(tmr + ICRx, icr & 0xff)  # low byte
    
def set_icp_mode(tmr, is_positive, do_filter):
    """Set edge and filter (noise cancel) mode for input capture unit"""
    tccrXb = peek(tmr + TCCRxB)
    tccrXb &= 0x3F
    if is_positive:
        tccrXb |= 0x40
    if do_filter:
        tccrXb |= 0x80
    poke(tmr + TCCRxB, tccrXb)

def get_icp_val(tmr):
    """Read input capture value"""
    return peek(tmr + ICRx) | (peek(tmr + ICRx + 1) << 8)


#---- Timer 0 operations ----
def timer8_init(tmr, wgm_mode, clk_sel):
    """Initialize WGM0 waveform generation mode and clock select"""
    # TCCR0A
    value = wgm_mode & 0x03  # Set COM0A/B = O (off), and LSBs of WGM
    poke(tmr + TCCR0A, value)

    # TCCR0B
    value = (wgm_mode & 0x04) << 1
    value |= clk_sel & 0x07
    poke(tmr + TCCR0B, value)

def set_tmr8_output(tmr, ocr, mode):
    """Set output mode"""
    reg = tmr + TCCR0A
    
    shift = 6 if ocr == OCR0A else 4
    mask = ~(0x03 << shift)
    val = peek(reg)
    val = (val & mask) | (mode << shift)
    poke(reg, val)

def set_tmr8_count(tmr, count):
    """Set 8-bit immediate count value"""
    poke(tmr + TCNT0, count)

def get_tmr8_count(tmr):
    """Read 8-bit immediate count value"""
    return peek(tmr + TCNT0)

def set_tmr8_ocr(tmr, ocr, val):
    """Set 8-bit OCR register. This controls the duty cycle (duty/TOP) in some PWM modes"""
    poke(tmr + ocr, val)


#---- Global timer operations ----
def timer_sync_halt(do_halt):
    """Halt timers (and reset prescaler). TCNT values can be modified while halted, so timers will
       remain synchronized when counting resumed"""
    if do_halt:
        poke(GTCCR, 0x83)
    else:
        poke(GTCCR, 0)
