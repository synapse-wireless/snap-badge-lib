# (c) Copyright 2011-2016, Synapse Wireless, Inc.
"""ATmega128RFA1 32-bit math library
Since the SNAPpy virtual machine as of version 2.6 only supports signed 2-byte integers
a math library must be used to perform calculations that exceed 65535. Currently all
operations are 32-bit unsigned.

Note: Integers in SNAPpy are two bytes, so 32-bit numbers used by this library must be
      stored in a string data type. The itos() and stoi() functions convert from SNAPpy
      integers to 32-bit integers, and vice versa respetively. All inputs should be in
      big endian format.

The simplest way to print or show the value of the 32-bit number is to use the hex_utilities
script to convert the number from binary into printable hex-ascii.

Ex.
  #Measure an analog voltage on ADC0 and convert to millivolts
  # voltage = ADC/1023 * 1600mV
  from hex_utilities import *
  
  analog_value = readAdc(0)
  analog_value = itos(analog_value)
  analog_value = mult_32(analog_value, '\x00\x00\x06\x40') # 0x640 = 1600 decimal
  analog_value = div_32(analog_value, '\x00\x00\x03\xff')  # 0x3FF = 1023 decimal
  print to_hex(analog_value)    # Print the hex-ascii version
  print stoi(analog_value)      # Convert back to SNAPpy integer and print

"""

def itos(integer):
    """Convert SNAPpy 2-byte integer to math_library 32-bit number"""
    return ("\x00\x00" + chr(integer>>8) + chr(integer&0xFF))

def itos2(integer1, integer2):
    """Convert two 2-byte integers to math_library 32-bit number"""
    return (chr(integer1>>8) + chr(integer1&0xFF) + chr(integer2>>8) + chr(integer2&0xFF))

def stoi(binstring):
    """Convert math_library 32-bit number to SNAPpy 2-byte integer (truncates upper 2 bytes)"""
    return (ord(binstring[2])<<8) | ord(binstring[3])


def add_32(val1, val2):
    """Perform addition on two unsigned 32-bit numbers (val1 + val2)"""
    val1 = flip_string(val1 + val2)
    call(MATH_32BIT_ADD, val1)
    return flip_string(val1[0:4])

def sub_32(val1, val2):
    """Perform subtraction on two unsigned 32-bit numbers (val1 - val2)"""
    val1 = flip_string(val1 + val2)
    call(MATH_32BIT_SUBTRACT, val1)
    return flip_string(val1[0:4])

def mult_32(val1, val2):
    """Perform multiplication on two unsigned 32-bit numbers (val1 * val2)"""
    val1 = flip_string(val1 + val2)
    call(MATH_32BIT_MULTIPLY, val1)
    return flip_string(val1[0:4])

def div_32(val1, val2):
    """Perform division on two unsigned 32-bit numbers (val1 / val2)"""
    val1 = flip_string(val1 + val2)
    call(MATH_32BIT_DIVIDE, val1)
    return flip_string(val1[0:4])

def greater_than(val1, val2):
    """Perform inequality check on two unsigned 32-bit numbers (val1 > val2)"""
    myStr = flip_string(val1) + flip_string(val2)
    call(MATH_32BIT_GREATER_THAN,myStr)
    return (ord(myStr[0]) == 1)

def less_than(val1, val2):
    """Perform inequality check on two unsigned 32-bit numbers (val1 < val2)"""
    myStr = flip_string(val1) + flip_string(val2)
    call(MATH_32BIT_LESS_THAN, myStr)
    return (ord(myStr[0]) != 1)

# Used for flipping strings
def flip_string(string):
    """Perform byte-swap to reverse endianess, we use big endian, but atmel processor is little endian"""
    i = 0
    reverse_string = ''
    string_length = len(string)
    while i < string_length:
        reverse_string += string[string_length-i-1]
        i += 1
    return reverse_string

# Define Embedded C code for 32-bit math operations
MATH_32BIT_ADD = '\x0d\x01\x22\x50\x30\x40\xf9\x01\xf1\x81\xd9\x01\xec\x91\x05\x81\x16\x81\x27\x81\x30\x85\x41\x81\x52\x81\x63\x81\x74\x81\x40\x0f\x51\x1f\x62\x1f\x73\x1f\x41\x83\x52\x83\x63\x83\x74\x83\xd0\x01\x08\x95'
MATH_32BIT_SUBTRACT = '\x0d\x01\x22\x50\x30\x40\xf9\x01\xf1\x81\xd9\x01\xec\x91\x05\x81\x16\x81\x27\x81\x30\x85\x41\x81\x52\x81\x63\x81\x74\x81\x04\x1b\x15\x0b\x26\x0b\x37\x0b\x01\x83\x12\x83\x23\x83\x34\x83\xd0\x01\x08\x95'
MATH_32BIT_MULTIPLY = '\xba\x93\x3a\x2e\x22\x50\x30\x40\xf9\x01\xf1\x81\xd9\x01\xec\x91\x41\x81\x52\x81\x63\x81\x74\x81\x05\x81\x16\x81\x27\x81\x30\x85\x31\x96\x22\x24\x34\x9f\x30\x2d\x25\x9f\x30\x0d\x16\x9f\x30\x0d\x07\x9f\x30\x0d\x24\x9f\x20\x2d\x31\x0d\x15\x9f\x20\x0d\x31\x1d\x06\x9f\x20\x0d\x31\x1d\x14\x9f\x10\x2d\x21\x0d\x32\x1d\x05\x9f\x10\x0d\x21\x1d\x32\x1d\x04\x9f\x11\x0d\x22\x1d\x32\x1d\x00\x82\x11\x83\x22\x83\x33\x83\xa3\x2d\xb9\x91\x08\x95'
MATH_32BIT_DIVIDE = '\xba\x93\xaa\x93\xf9\x01\x32\x97\xb1\x81\xa0\xe0\x00\x81\xa0\x2b\x11\x96\xfd\x01\x04\x81\x15\x81\x26\x81\x37\x81\x4d\x91\x5d\x91\x6d\x91\x7c\x91\x13\x97\x00\x24\x11\x24\x10\x01\xe0\xe2\xea\x95\x92\xf0\x00\x1f\x11\x1f\x22\x1f\x33\x1f\x00\x1c\x11\x1c\x22\x1c\x33\x1c\x04\x16\x15\x06\x26\x06\x37\x06\x88\xf3\x04\x1a\x15\x0a\x26\x0a\x37\x0a\xec\xcf\x00\x1f\x11\x1f\x22\x1f\x33\x1f\xa0\x01\xb1\x01\x00\x95\x10\x95\x20\x95\x30\x95\x0d\x93\x1d\x93\x2d\x93\x3c\x93\xa9\x91\xb9\x91\x08\x95'
MATH_32BIT_GREATER_THAN = '\x0d\x01\x22\x50\x30\x40\xf9\x01\xf1\x81\xd9\x01\xec\x91\x05\x81\x16\x81\x27\x81\x30\x85\x41\x81\x52\x81\x63\x81\x74\x81\x31\x96\x04\x17\x15\x07\x26\x07\x37\x07\x10\xf4\x01\xe0\x01\xc0\x00\xe0\x00\x83\xd0\x01\x08\x95'
MATH_32BIT_LESS_THAN = '\x0d\x01\x22\x50\x30\x40\xf9\x01\xf1\x81\xd9\x01\xec\x91\x01\x81\x12\x81\x23\x81\x34\x81\x45\x81\x56\x81\x67\x81\x70\x85\x31\x96\x04\x17\x15\x07\x26\x07\x37\x07\x10\xf4\x00\xe0\x01\xc0\x01\xe0\x00\x83\xd0\x01\x08\x95'
