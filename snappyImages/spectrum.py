"""
Tool - Low Resolution (only 8 bars for 16 channels) Wireless Spectrum Analyzer
"""

from drivers.snap_badge import *
from pixel_lib import *

#
# Screen refreshes are triggered from the 100 ms timebase
# During development, I found this to be "flickery" so
# I added the ability to skip ticks. You can change the
# default value (below), plus you can change it on-the-fly
# using the buttons.
#
MIN_SKIP = 0
MAX_SKIP = 10

DEFAULT_SKIP = 5

skip_reload = DEFAULT_SKIP
skip_counter = DEFAULT_SKIP

def spectrum_start():
    badge_start()
    monitorPin(BUTTON_LEFT, True)
    monitorPin(BUTTON_RIGHT, True)

def spectrum_tick_100ms():
    global skip_counter
    skip_counter -= 1
    if skip_counter < 0:
        skip_counter = skip_reload
        scan_and_plot_channels()

def spectrum_pin_event(pin, is_set):
    global skip_reload
    if not is_set:
        if pin == BUTTON_RIGHT:
            skip_reload -= 1
            if skip_reload < MIN_SKIP:
                skip_reload = MIN_SKIP
        elif pin == BUTTON_LEFT:
            skip_reload += 1
            if skip_reload > MAX_SKIP:
                skip_reload = MAX_SKIP
#
# Generic "8 bar" plotter (use divisor=1 and offset=0 if your data is already 0-7)
#
def plot_bars(values, divisor, offset):
    values = [ values ] # SNAPpy str => byte-list
    cls()
    column = 0
    for value in values:
        # Scale the value per the callers wishes
        scaled_value = value / divisor
        adjusted_value = scaled_value + offset
        # Flip it so 0 is at the bottom of the display, 7 is at the top
        final_value = MAX_Y - adjusted_value
        # I chose clipping here, other choices are possible
        if final_value > MAX_Y:
            final_value = MAX_Y
        if final_value < MIN_Y:
            final_value = MIN_Y
        # Draw the bar (note that we chose a one-pixel minimum height)
        y = MAX_Y
        set_pixel(column, y)
        while y > final_value:
            y -= 1
            set_pixel(column, y)
        column += 1
    refresh_pixels()

#
# Map SNAPpy RSSI values onto 1-8 pixels
#
def plot_channels(channels):
    # Map RSSI Values of 90 (weak) to 20 (strong)
    #   onto Bargraph Bars of 0 to 7
    plot_bars(channels, -10, 9)

#
# Map 16 channels of RSSI data onto 8 columns.
# We chose to show the PEAK value of the two channels, rather
# than the AVERAGE of the two channel values.
#
def compress_with_peak(real_channels):
    starting_data = [ real_channels ] # SNAPpy str => byte-list
    # Display only has 8 columns, so do a 2:1 compression,
    # BUT keep the peak values rather than averaging
    peak_data = []
    count = 0
    while count < 8:
        left_channel = starting_data[count * 2]
        right_channel = starting_data[count * 2 + 1]
        # In this case, LOWER values correspond to STRONGER signals
        if left_channel < right_channel:
            peak_data += [left_channel]
        else:
            peak_data += [right_channel]
        count += 1
    peak_data = chr(peak_data) # SNAPpy byte-list => str, so it can be sent over-the-air for debug purposes
    return peak_data

def scan_and_plot_channels():
    raw_data = scanEnergy()
    compressed_data = compress_with_peak(raw_data)
    plot_channels(compressed_data)

# Hook context, for multi-app switching via app_switch.py
spectrum_context = (spectrum_start, None, None, spectrum_tick_100ms, None, spectrum_pin_event)

# Set hooks if running app standalone
if "setHook" in globals():
    snappyGen.setHook(SnapConstants.HOOK_STARTUP, spectrum_start)
    snappyGen.setHook(SnapConstants.HOOK_100MS, spectrum_tick_100ms)
    snappyGen.setHook(SnapConstants.HOOK_GPIN, spectrum_pin_event)
