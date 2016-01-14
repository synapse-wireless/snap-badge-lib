MIN_X = 0
MAX_X = 7
MIN_Y = 0
MAX_Y = 7

def cls():
    global playfield
    playfield = [ 0x00 ] * 8

def invalid_coords(x, y):
    if x < MIN_X:
        return True
    if x > MAX_X:
        return True
    if y < MIN_Y:
        return True
    if y > MAX_Y:
        return True
    return False

def set_pixel(x, y):
    global playfield

    if invalid_coords(x, y):
        return

    bit = 1 << (7-x)
    playfield[y] = playfield[y] | bit

def reset_pixel(x, y):
    global playfield

    if invalid_coords(x, y):
        return

    bit = 1 << (7-x)
    playfield[y] = playfield[y] & ~bit

def test_pixel(x, y):
    global playfield

    if invalid_coords(x, y):
        return False

    bit = 1 << (7-x)
    return (playfield[y] & bit) != 0

def refresh_pixels():
    as1115_write_matrix_symbol(chr(playfield)) # library wants a string, not a byte list
