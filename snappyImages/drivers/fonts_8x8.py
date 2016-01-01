"""Font utilities for 8x8 displays"""

# Current loaded fontset / widths
cur_fontset = None
cur_fontwidth = None

# Scrolling text state
stext_i_ch = 0
stext_i_pix = 0
stext_str = ''

# Display driver is a function which takes a single symbol (8-byte string) parameter
display_drv = None

def set_display_driver(drv):
    global display_drv
    display_drv = drv

def load_font(fontset, fontwidth):
    global cur_fontset, cur_fontwidth
    cur_fontset = fontset
    cur_fontwidth = fontwidth

def get_indexed_sym(ch_code):
    """Return binary symbol string for indexed character in current fontset. Symbol itself is 
       an 8-byte string.
    """
    print "get_i_sym(", ch_code, ')'
    i_str = ch_code >> 4  # fontsets are stored as 16-char strings
    i_sym = (ch_code & 0x0F) << 3  # strings are composed of 8-byte symbols
    return cur_fontset[i_str][i_sym : i_sym + 8]

def get_indexed_width(ch_code):
    return ord(cur_fontwidth[ch_code >> 4])

def scroll_right(sym1, sym2, width1, nscroll, gap):
    """Return scrolled symbol composed of sym1/gap/sym2"""
    sym = ''
    for row in xrange(8):
        r = (ord(sym1[row]) << nscroll) | (ord(sym2[row]) >> (width1 + gap - nscroll))
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
    
    
def update_scroll_text():
    """Call periodically to update scroll text position"""
    global stext_i_ch, stext_i_pix, cur_scroll_sym1, cur_scroll_sym2, cur_scroll_width1
    
    CHAR_GAP = 1                # Intercharacter pixel space
    SCROLL_PIX_INCREMENT = 1    # Pixels scrolled per update
    
    if not stext_str:
        # Nothing to do if no text to display
        return
    
    if stext_i_pix == 0:
        # Starting a new character
        c = ord(stext_str[stext_i_ch])
        cur_scroll_sym1 = get_indexed_sym(c)
        cur_scroll_width1 = ord(cur_fontwidth[c])
        next_i_ch = stext_i_ch + 1
        if next_i_ch == len(stext_str):
            next_i_ch = 0
        c = ord(stext_str[next_i_ch])
        cur_scroll_sym2 = get_indexed_sym(c)
        
    # Get scrolled symbol, and send to display
    sym = scroll_right(cur_scroll_sym1, cur_scroll_sym2, cur_scroll_width1, stext_i_pix, CHAR_GAP)
    display_drv(sym)
    
    # Increment scroll index
    stext_i_pix += SCROLL_PIX_INCREMENT
    if stext_i_pix == cur_scroll_width1 + CHAR_GAP:
        stext_i_pix = 0
        stext_i_ch += 1
        if stext_i_ch == len(stext_str):
            # Wrap text
            stext_i_ch = 0
        
    
    
def test_display_driver1(sym):
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

def test_display_driver2(sym):
    """Send symbol over the air for simulated display"""
    mcastRpc(1, 1, 'disp8x8', sym)



