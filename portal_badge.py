"""Portal script helper for SNAP Badge
   
   Provides a simulated LED matrix display for testing in the absence of physical hardware.
"""

import wx

frame = None

def disp8x8(sym):
    """Display symbol on simulated 8x8 LED matrix"""
    sim_display_wx(sym)
    
def sim_display_print(sym):
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

def sim_display_wx(sym):
    """Simulate 8x8 display using wx graphics library"""
    global frame
    if not frame:
        frame = BadgeFrame(root)
    frame.display8x8(sym)
        
class BadgeFrame(wx.Frame):
    """Main window frame"""
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "SNAP Badge", size=(330,710), style = wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.panel = BadgePanel(self)
        self.Show(True)

    def onClose(self, event):
        self.Destroy()

    def display8x8(self, sym):
        self.panel.cur_sym = sym
        self.Refresh()
        
        
class BadgePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.badge_frame = parent
        self.cur_sym = None
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)   # required for BufferedPaintDC

        self.badge_bmp = wx.Bitmap('badge.png')
        self.badge_bmp_sz = self.badge_bmp.GetSize()
        self.led_bmp = wx.Bitmap('led.png')
        self.led_bmp_sz = self.led_bmp.GetSize()
        
    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        assert isinstance(gc, wx.GraphicsContext)
        dc.SetBackground(wx.Brush("white"))
        dc.Clear()

        # Draw badge
        gc.PushState()

        gc.DrawBitmap(self.badge_bmp, 0,0, self.badge_bmp_sz.width, self.badge_bmp_sz.height)

        # Draw LEDs
        if self.cur_sym:
            y = 0
            for c in self.cur_sym:
                row = ord(c)
                for x in xrange(8):
                    if (0x80 >> x) & row:
                        self.led_on(gc, x, y)
                y += 1
        
        gc.PopState()
        
    def led_on(self, gc, x, y):
        """Draw LED at specified matrix coords"""
        # LED pixel positions, from badge.png
        x_org = 63
        y_org = 51
        x_step = 23.7
        y_step = 26.14
        x_pix = x_org + x * x_step
        y_pix = y_org + y * y_step
        gc.DrawBitmap(self.led_bmp, x_pix, y_pix, self.led_bmp_sz.width, self.led_bmp_sz.height)
        

if __name__ == '__main__':
    """Test - run standalone view""" 
    class MyApp(wx.App):
        def OnInit(self):
            self.frame = BadgeFrame(None)
            self.SetTopWindow(self.frame)
            return True


    app = MyApp(0)
    app.MainLoop()

        