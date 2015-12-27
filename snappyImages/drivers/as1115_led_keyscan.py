"""AS1115 Driver - i2c LED matrix / keyscan controller"""

# I2C address
AS1115_ADDR = 0x00
AS1115_ADDR_WR = "%c" % AS1115_ADDR
AS1115_ADDR_RD = "%c" % (AS1115_ADDR + 1)

# Device registers





def as1115_init():
    pass

