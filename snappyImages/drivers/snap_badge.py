"""Hardware definitions for SNAP Badge"""

ACC_INT1 = 4      # Accelerometer interrupt 1 (PB4, PCINT4)
ACC_INT2 = 14     # Accelerometer interrupt 2 (PD6, T1)
IS_USB = 15       # Tied low when switched to USB power (PD7)
STATUS_LED =  37  # Active low status LED (PG5, OC0B)
BUTTON_LEFT = 0   #  (PB0, PCINT0)
BUTTON_RIGHT = 22 # (PE6, T3, INT6)
LED_PWR_EN = 13   # Enable LED and DIP-SW matrix driver (PD5)
I2C_SCL = 8       # (PD0, SCL)
I2C_SDA = 9       # (PD1, SDA)

BADGE_EXCL_PINS = (ACC_INT1, ACC_INT2, IS_USB, STATUS_LED, BUTTON_LEFT, BUTTON_RIGHT, LED_PWR_EN, I2C_SCL, I2C_SDA)
SM220_EXCL_PINS = (27,32,33,34,35,36)


def badge_init_pins(user_excludes):
    """Initialize all badge pins for low-power operation (assuming no shield attached)"""
    
    # Init onboard HW
    setPinDir(ACC_INT1, False)
    setPinDir(ACC_INT2, False)
    setPinDir(IS_USB, False)
    setPinDir(BUTTON_LEFT, False)
    setPinDir(BUTTON_RIGHT, False)
    
    writePin(LED_PWR_EN, False)
    setPinDir(LED_PWR_EN, True)
    writePin(STATUS_LED, True)
    setPinDir(STATUS_LED, True)

    i2cInit(False, I2C_SCL, I2C_SDA)
    
    # Init all other non-excluded pins
    for pin in xrange(38):
        if pin in SM220_EXCL_PINS or pin in BADGE_EXCL_PINS or (user_excludes and pin in user_excludes):
            continue
        
        # Set pin to output/low for lowest power consumption
        setPinDir(pin, True)
        writePin(pin, False)
