"""Pixel manipulation library for SNAP Badge"""
MIN_X = 0
MAX_X = 7
MIN_Y = 0
MAX_Y = 7

def cls():
    global playfield
    playfield = [ 0x00 ] * 8

def invalid_coords(x, y):
    return not ((MIN_X <= x <= MAX_X) and (MIN_Y <= y <= MAX_Y))
    
def set_pixel(x, y):
    global playfield

    if invalid_coords(x, y):
        return

    bit = 0x80 >> x
    playfield[y] = playfield[y] | bit

def reset_pixel(x, y):
    global playfield

    if invalid_coords(x, y):
        return

    bit = 0x80 >> x
    playfield[y] = playfield[y] & ~bit

def test_pixel(x, y):
    global playfield

    if invalid_coords(x, y):
        return False

    bit = 0x80 >> x
    return (playfield[y] & bit) != 0

def refresh_pixels():
    as1115_write_matrix_symbol(chr(playfield)) # library wants a string, not a byte list
