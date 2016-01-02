"""Font utilities for 8x8 displays"""

# Current loaded fontset / widths
cur_fontset = None
cur_fontwidth = None

# Scrolling text state
stext_i_ch = 0
stext_i_pix = 0
stext_str = ''
cur_next_width = 0  # width of symbol being scrolled-in

# Current displayed symbol, in 8-byte string format
cur_disp_sym = "\x00" * 8

# Display driver is a function which takes a single symbol (8-byte string) parameter
display_drv = None

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
    global stext_i_ch, stext_i_pix, stext_str
    stext_i_ch = 0
    stext_i_pix = 0
    stext_str = text

def stop_scroll_text():
    """Stop scrolling text"""
    global stext_str
    stext_str = ''
    
def update_scroll_text(char_gap):
    """Call periodically to update scroll text position.
       Intercharacter pixel space set by char_gap.    
    """
    global stext_i_ch, stext_i_pix, cur_disp_sym, cur_next_sym, cur_next_width
    
    if not stext_str:
        # Nothing to do if no text to display
        return
    
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
    display_drv(cur_disp_sym)

            
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

