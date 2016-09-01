# Copyright (C) 2014 Synapse Wireless, Inc.
"""LIS3DH Driver - i2c Accelerometer

Functions exposed in this driver are aimed at 2 primary use-cases:
1. Read current XYZ orientation
2. Toggle external interrupt pin on motion (wake on motion)
3. Portrait/Landscape detection - wake on change

"""

# I2C address
ACCEL_ADDR = 0x30
LIS_ADDR_WR = "%c" % ACCEL_ADDR
LIS_ADDR_RD = "%c" % (ACCEL_ADDR + 1)

# Device registers
LIS_ADC1 = '\x08'          # 10-bit 2's complement ADC
LIS_ADC2 = '\x0a'
LIS_ADC3 = '\x0c'          # Also temperature value
LIS_INT_COUNTER = '\x0e'   # Interrupt counter
LIS_DEV_ID = '\x0f'        # hardcoded WHO_AM_I ID
LIS_TEMP_CFG = '\x1f'      # Enable temperature sensor / ADC
LIS_CTRL_REG1 = '\x20'     # Data rate, axis enables
LIS_CTRL_REG2 = '\x21'     # High pass filter
LIS_CTRL_REG3 = '\x22'     # IRQ config
LIS_CTRL_REG4 = '\x23'     # Endianness, sensitivity/rez
LIS_CTRL_REG5 = '\x24'     # Fifo/ IRQ latch
LIS_CTRL_REG6 = '\x25'
LIS_STATUS_REG = '\x27'    # Data available
LIS_OUT_REG_MULTI = '\xa8' # 3 axes XYZ, each 16bit 2's complement (Note: msb set for multibyte read)
LIS_FIFO_CTRL_REG = '\x2e'
LIS_INT1_CFG = '\x30'
LIS_INT1_SRC = '\x31'
LIS_INT1_THRESHOLD = '\x32'
LIS_INT1_DURATION = '\x33'

LIS_VFY_DEV_ID  = '\x33'
LIS_CMD_TEMP_EN = '\x40'    # Enable temperature sensor

lis_axis_x = 0
lis_axis_y = 0
lis_axis_z = 0

# Default values for specified driver use-case
#LIS_CTRL_VAL1 = 0x27   # ODR=10Hz, Normal mode, all axes enabled (4uA mode)
LIS_CTRL_VAL1 = 0x27   # ODR=10Hz, Normal mode, XY axes enabled (4uA mode)
LIS_CTRL_VAL2 = 0x01   # High pass filter enabled for AOI1 interrupt (data reg not filtered)
LIS_CTRL_VAL3 = 0x40   # AOI1 interrupt on INT1 pad
LIS_CTRL_VAL4 = 0xc8   # Force byte consistency, big endian, 2G sens, HiRez mode
#LIS_CTRL_VAL5 = 0x00   # No fifo, no latch IRQ (default)
LIS_CTRL_VAL5 = 0x04   # No fifo, no latch IRQ (default), 4D enable
LIS_CTRL_VAL6 = 0x00   # Nothing on INT2 pad, Active High interrupt
#LIS_INT1_CFG_VAL   = 0x2a  # Enable XYZ high events
LIS_INT1_CFG_VAL   = 0xca  # Enable XY high events, orientation (6D) mode with AND/OR interrupt logic
LIS_INT1_THRESH_VAL = 0x04 # This threshold will generate interrupts when device is gently moving
LIS_INT1_DUR_VAL  = 0x00

def lis_init():
    """First time initialization"""
    sleep(2, -5) # Wait 5ms for LIS3DH boot procedure (power-on trim)
    lis_ctrl(1, LIS_CTRL_VAL1)
    lis_ctrl(2, LIS_CTRL_VAL2)
    lis_ctrl(3, LIS_CTRL_VAL3)
    lis_ctrl(4, LIS_CTRL_VAL4)
    lis_ctrl(5, LIS_CTRL_VAL5)
    lis_ctrl(6, LIS_CTRL_VAL6)
    lis_int1(LIS_INT1_CFG_VAL, LIS_INT1_THRESH_VAL, LIS_INT1_DUR_VAL)

def lis_ctrl(reg, cmd):
    """Set control registers"""
    i2cWrite(LIS_ADDR_WR + chr(0x1f + reg) + chr(cmd) , 1, False)

def lis_int1(cfg, thresh, duration):
    """Set interrupt1 configuration"""
    i2cWrite(LIS_ADDR_WR + LIS_INT1_CFG + chr(cfg), 1, False)
    i2cWrite(LIS_ADDR_WR + LIS_INT1_THRESHOLD + chr(thresh), 1, False)
    i2cWrite(LIS_ADDR_WR + LIS_INT1_DURATION + chr(duration), 1, False)

def lis_vfy_mfg_dev():
    """Verify device ID - return True if correct"""
    i2cWrite(LIS_ADDR_WR + LIS_DEV_ID , 1, False)
    s = i2cRead(LIS_ADDR_RD, 1, 1, False)
    return s == LIS_VFY_DEV_ID

def lis_read():
    """Read current XYZ axis values and update global 'lis_axis_*' variables"""
    global lis_axis_x, lis_axis_y, lis_axis_z
    
    i2cWrite(LIS_ADDR_WR + LIS_OUT_REG_MULTI , 1, False)
    s = i2cRead(LIS_ADDR_RD, 6, 1, False)
    lis_axis_x = (ord(s[0]) << 8) | ord(s[1])
    lis_axis_y = (ord(s[2]) << 8) | ord(s[3])
    lis_axis_z = (ord(s[4]) << 8) | ord(s[5])

def lis_wake():
    """Recover from sleep"""
    lis_ctrl(1, LIS_CTRL_VAL1)

def lis_sleep():
    """Shutdown operation - draws <1uA"""
    lis_ctrl(1, 0x00)   # ODR=0 is power down

def dump_axes():
    """Debug - send axis values to stdout"""
    lis_read()
    print "X=", lis_axis_x, ", Y=", lis_axis_y, ", Z=", lis_axis_z
    


