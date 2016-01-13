"""AS1115 Driver - i2c LED matrix / keyscan controller"""

# I2C address
AS1115_ADDR = 0x00
AS1115_ADDR_WR = "%c" % AS1115_ADDR
AS1115_ADDR_RD = "%c" % (AS1115_ADDR + 1)

# Digit registers
DIG0 = 0x01
DIG1 = 0x02
DIG2 = 0x03
DIG3 = 0x04
DIG4 = 0x05
DIG5 = 0x06
DIG6 = 0x07
DIG7 = 0x08

# Control registers
DECODE_MODE  = 0x09    # 0 = matrix
GLOB_INTENS  = 0x0A    # Range 0-15
SCAN_LIMIT   = 0x0B
SHUTDOWN     = 0x0C
SELF_ADDR    = 0x0D
FEATURE      = 0x0E    # Bitmask
TEST_MODE    = 0x0F
DIG01_INTENS = 0x10    # Nibble per digit
DIG23_INTENS = 0x11
DIG45_INTENS = 0x12
DIG67_INTENS = 0x13

# Keyscan / Diagnostic registers
DIAG_DIG0 = 0x14
DIAG_DIG1 = 0x15
DIAG_DIG2 = 0x16
DIAG_DIG3 = 0x17
DIAG_DIG4 = 0x18
DIAG_DIG5 = 0x19
DIAG_DIG6 = 0x1A
DIAG_DIG7 = 0x1B
KEYA      = 0x1C
KEYB      = 0x1D

# Shutdown modes (_RST means reset FEATURE register to defaults)
SHUTDOWN_RST  = 0x00
SHUTDOWN_SAVE = 0x80
NORMAL_RST    = 0x01
NORMAL_SAVE   = 0x81

# Matrix operation, D7:D0 correspond to DP,A,B,C,D,E,F,G
NO_DECODE = 0x00

# Feature bitmask (default = 0x00)
AS_CLK_EN = 0x01      # Use external clock
AS_REG_RES = 0x02     # Reset all control registers except Feature reg
AS_DECODE_SEL = 0x04  # 0=Code-B, 1=HEX decoding
AS_BLINK_EN = 0x10    # 1=Enable blinking
AS_BLINK_FREQ = 0x20  # 0=1sec, 1=2sec period (50% duty cycle)
AS_SYNC = 0x40        # Enable multi-device blink sync
AS_BLINK_PHASE = 0x80 # 0=Start with "off", 1=Start with "on"

# Symbols for matrix-mode
SYM_CHECKERBOARD = "\xAA\x55\xAA\x55\xAA\x55\xAA\x55"
SYM_ALL_OFF = "\x00" * 8
SYM_ALL_ON  = "\xFF" * 8

def as1115_init():
    """Initialize AS1115 for matrix-mode operation. Assumes i2c already initialized."""
    as1115_wr(SHUTDOWN, NORMAL_RST)
    as1115_wr(DECODE_MODE, 0)   # Matrix
    as1115_wr(SCAN_LIMIT, 7)    # All digits (rows)
    as1115_wr(GLOB_INTENS, 15)  # Full brightness
    as1115_write_matrix_symbol(SYM_ALL_OFF)
    
def as1115_enable(do_enable):
    as1115_wr(SHUTDOWN, NORMAL_SAVE if do_enable else SHUTDOWN_SAVE)

def as1115_set_matrix_row(row, pix_byte):
    """Set designated row (0-7) to given pixel mask"""
    as1115_wr(row + 1, pix_byte)
    
def as1115_write_matrix_symbol(pix_bytes):
    """Set all matrix rows to given 8-byte 'symbol' string"""
    i2cWrite(AS1115_ADDR_WR + '\x01' + pix_bytes, 1, False)

def as1115_wr(reg, data):
    i2cWrite(AS1115_ADDR_WR + chr(reg) + chr(data), 1, False)

def as1115_rd(reg):
    """Read a single register, return integer value"""
    i2cWrite(AS1115_ADDR_WR + chr(reg), 1, False)
    s = i2cRead(AS1115_ADDR_RD, 1, 1, False)
    return ord(s)

def as1115_rd_multi(start_reg, n_read):
    """Read a block of registers, return as string"""
    i2cWrite(AS1115_ADDR_WR + chr(start_reg), 1, False)
    s = i2cRead(AS1115_ADDR_RD, n_read, 1, False)
    return s

