"""Hardware definitions for SNAP Badge"""

from lis3dh_accel import *
from as1115_led_keyscan import *

ACC_INT1 = 4      # Accelerometer interrupt 1 (PB4, PCINT4)
ACC_INT2 = 14     # Accelerometer interrupt 2 (PD6, T1)
IS_USB = 15       # Tied low when switched to USB power (PD7)
STATUS_LED =  37  # Active low status LED (PG5, OC0B)
BUTTON_LEFT = 0   # Active low momentary pushbutton (PB0, PCINT0)
BUTTON_RIGHT = 22 # Active low momentary pushbutton (PE6, T3, INT6)
LED_PWR_EN = 13   # Enable LED and DIP-SW matrix driver (PD5)
I2C_SCL = 8       # I2C clock (PD0, SCL)
I2C_SDA = 9       # I2C data (PD1, SDA)
USB_TXD = 10      # SM220 UART RX
USB_RXD = 11      # SM220 UART TX

# Arduino headers
D0	= 16
D1	= 17
D2	= 20
D3	= 5
D4	= 23
D5	= 6
D6	= 7
D7	= 12
D8	= 0
D9	= 19
D10	= 21
D11	= 2   # Differs from Pyduino (MOSI)
D12	= 3   # Differs from Pyduino (MISO)
D13	= 1   # Differs from Pyduino (SCK)
SDA = 9
SCL = 8
# Analog I/O pins
AD0 = 24
AD1 = 25
AD2 = 28
AD3 = 29
AD4 = 30   # Some shields tie this to SDA
AD5 = 31   # Some shields tie this to SCL
# Analog ADC channels
A0 = 0
A1 = 1
A2 = 4
A3 = 5
A4 = 6
A5 = 7

# DIP Switch Positions
DIP_STEM     = 0x01
DIP_ANALOG   = 0x02
DIP_DIGITAL  = 0x04
DIP_HARDWARE = 0x08
DIP_SOFTWARE = 0x10
DIP_IOT      = 0x20
DIP_S7       = 0x40
DIP_S8       = 0x80

# Exclude pins used by badge, and internally by SM220, from initialization defaults
BADGE_EXCL_PINS = (ACC_INT1, ACC_INT2, IS_USB, STATUS_LED, BUTTON_LEFT, BUTTON_RIGHT, LED_PWR_EN, I2C_SCL,
                   I2C_SDA, USB_RXD, USB_TXD, AD4, AD5)
SM220_EXCL_PINS = (27,32,33,34,35,36)

def badge_start():
    badge_init_pins(None)
    lis_init()
    badge_led_array_enable(True)

def badge_init_pins(user_excludes):
    """Initialize all badge pins default for low-power operation (assuming no shield attached)"""
    
    # Init onboard HW
    setPinDir(ACC_INT1, False)
    setPinDir(ACC_INT2, False)
    setPinDir(IS_USB, False)
    setPinDir(BUTTON_LEFT, False)
    setPinPullup(BUTTON_LEFT, True)
    setPinDir(BUTTON_RIGHT, False)
    setPinPullup(BUTTON_RIGHT, True)
    
    writePin(LED_PWR_EN, False)
    setPinDir(LED_PWR_EN, True)
    writePin(STATUS_LED, True)
    setPinDir(STATUS_LED, True)
    
    # Since some shields tie AD4/5 to I2C lines, let them float.
    setPinDir(AD4, False)
    setPinDir(AD5, False)

    i2cInit(False, I2C_SCL, I2C_SDA)
    
    # Init all other non-excluded pins
    for pin in xrange(38):
        if (pin in SM220_EXCL_PINS) or (pin in BADGE_EXCL_PINS) or (user_excludes and (pin in user_excludes)):
            continue
        
        # Set pin to output/low for lowest power consumption
        setPinDir(pin, True)
        writePin(pin, False)
        
def badge_led_array_enable(do_enable):
    writePin(LED_PWR_EN, do_enable)
    if do_enable:
        sleep(2, -2) # Wait 2ms for switching power supply to startup
        as1115_init()
        

def badge_sleep(secs):
    writePin(STATUS_LED, True)
    badge_led_array_enable(False)
    lis_sleep()
    
    # What about button pullups?  And AD4/5?

    sleep(2, secs)
    
    lis_wake()
    badge_led_array_enable(True)
    
