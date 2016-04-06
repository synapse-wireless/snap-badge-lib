"""Font utilities for 8x8 display support in SNAPpy.

   Use the 'fontconv.py' utility to convert binary 8x8 pixel fonts into SNAPpy fontsets
   compatible with this library.
"""

# Current loaded fontset / widths
cur_fontset = None
cur_fontwidth = None

# Scrolling text state
stext_i_ch = 0
stext_i_pix = 0
stext_str = ''
cur_next_width = 0  # width of symbol being scrolled-in

# Current displayed symbol, in 8-byte string format
BLANK_DISP = "\x00" * 8
cur_disp_sym = BLANK_DISP

# Display driver is a function which takes a single symbol (8-byte string) parameter
display_drv = None

rotate_scroll = 0  # Support 0, 90, 180, 270 rotations

def set_display_driver(drv):
    """Set destination for symbol output"""
    global display_drv
    display_drv = drv

def load_font(fontset, fontwidth):
    """Load a font-set. Takes effect for all subsequent symbol operations."""
    global cur_fontset, cur_fontwidth
    cur_fontset = fontset
    cur_fontwidth = fontwidth

def get_indexed_sym(ch_code):
    """Return binary symbol string for indexed character in current fontset. Symbol itself is 
       an 8-byte string.
    """
    i_str = ch_code >> 4  # fontsets are stored as 16-char strings
    i_sym = (ch_code & 0x0F) << 3  # strings are composed of 8-byte symbols
    return cur_fontset[i_str][i_sym : i_sym + 8]

def get_indexed_width(ch_code):
    """Return pixel-width of indexed character"""
    return ord(cur_fontwidth[ch_code])

def set_scroll_rotation(deg):
    global rotate_scroll
    rotate_scroll = deg

def scroll_right(disp_sym, next_sym, ipix):
    """Return scrolled version of disp_sym, shifting in new columns from the right"""
    sym = ''
    
    # Note: speed optimized, deliberately redundant.
    if ipix < 0:
        for row in xrange(8):
            r = ord(disp_sym[row]) << 1
            sym += chr(r & 0xFF)
    else:
        pix_mask = 0x80 >> ipix
        for row in xrange(8):
            r = ord(disp_sym[row]) << 1
            if (pix_mask & ord(next_sym[row])):
                r |= 0x01
            sym += chr(r & 0xFF)
        
    return sym
    
def set_scroll_text(text):
    """Start scrolling text"""
    global stext_i_ch, stext_i_pix, stext_str, cur_next_width, cur_disp_sym
    stext_i_ch = 0
    stext_i_pix = 0
    stext_str = text
    cur_next_width = 0
    cur_disp_sym = BLANK_DISP

def stop_scroll_text():
    """Stop scrolling text"""
    global stext_str
    stext_str = ''
    
def set_scroll_index(i_ch):
    global stext_i_ch
    if i_ch < len(stext_str):
        stext_i_ch = i_ch
    
def update_scroll_text(char_gap):
    """Call periodically to update scroll text position.
       Intercharacter pixel space set by char_gap.
       Returns True when new character is about to scroll in.
    """
    global stext_i_ch, stext_i_pix, cur_disp_sym, cur_next_sym, cur_next_width
    
    if not stext_str:
        # Nothing to do if no text to display
        return

    is_start = (stext_i_pix == 0)
    
    if stext_i_pix == cur_next_width:
        # Start shifting in a new character
        c = ord(stext_str[stext_i_ch])
        cur_next_sym = get_indexed_sym(c)
        cur_next_width = ord(cur_fontwidth[c])
        stext_i_pix = -char_gap

        stext_i_ch += 1
        if stext_i_ch == len(stext_str):
            # Wrap text
            stext_i_ch = 0

    # Scroll
    cur_disp_sym = scroll_right(cur_disp_sym, cur_next_sym, stext_i_pix)
    stext_i_pix += 1

    # Write to display
    ds = rotate_sym(cur_disp_sym, rotate_scroll)
    display_drv(ds)
    
    return is_start


def rotate_sym(sym, deg):
    """# Support 0, 90, 180, 270 rotations"""
    if deg == 0:
        return sym
    
    rot = [0] * 8
    
    if deg == 90:
        for i in xrange(8):
            r = ord(sym[i])   # this row of sym rotates to...
            b = 1 << i        # this bit position in rows of rot
            for j in xrange(8):
                if (1 << j) & r:
                    val = rot[7-j]
                    rot[7-j] = val | b
                    
    elif deg == 180:
        for i in xrange(8):
            r = ord(sym[i])
            t = 0
            for j in xrange(8):
                if (r & (1 << j)):
                    t |= (0x80 >> j)
            rot[7-i] = t
            
    elif deg == 270:
        for i in xrange(8):
            r = ord(sym[i])   # this row of sym rotates to...
            b = 0x80 >> i     # this bit position in rows of rot
            for j in xrange(8):
                if (1 << j) & r:
                    val = rot[j]
                    rot[j] = val | b
                    
    else:
        return sym
    
    return chr(rot)

def test_display_driver_print(sym):
    """Simulate 8x8 display with print statements. Doesn't display very well on Portal's event log."""
    dsp = '--------\n'
    for c in sym:
        row = ord(c)
        for i in xrange(8):
            ch = '*' if (0x80 >> i) & row else ' '
            dsp += ch
        dsp += '\n'
    dsp += '--------'
    print dsp

def test_display_driver_mcast(sym):
    """Send symbol over the air for simulated display"""
    mcastRpc(1, 1, 'disp8x8', sym)

