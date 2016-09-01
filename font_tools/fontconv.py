"""Convert pixel font binary file to SNAPpy source format

Converts 8x8 pixel font files such as those curated in C64 archives, or editors such as PixelFontEditor
    https://www.min.at/prinz/o/software/pixelfont/

# Output is string-encoded widths (up to 255 chars) and tuple of 128-byte strings (16 8-byte symbols per string)
font_widths = "xNNxNN..."
font_tup = ("xxxx","xxxx","xxxx",)


"""

import argparse
import sys
import time

class ConvertFont(object):
    def __init__(self):
        
        # Define command line args
        parser = argparse.ArgumentParser(description="Convert pixel font binary file to SNAPpy source format")
        parser.add_argument("font_file", help="input font file", type=argparse.FileType('rb'))
        parser.add_argument("-o", "--outfile", type=argparse.FileType('wb'), default=sys.stdout)
        parser.add_argument("-n", "--numchars", type=int, default=128)

        # Parse command line
        self.args = parser.parse_args()
        self.out_fp = self.args.outfile
        self.in_fp = self.args.font_file

    def convert(self):
 
        font_buf = self.in_fp.read()
        if len(font_buf) < self.args.numchars * 8:
            print "Error: input file too small for given numchars"
            exit()

        
        # Determine width of all chars
        width_str = ''
        for i_ch in xrange(self.args.numchars):
            # Flatten char to single row            
            flat = 0 
            for row in xrange(8):
                flat |= ord(font_buf[i_ch * 8 + row])
            # Find width of flattened row
            for bit in xrange(8):
                if flat & (1 << bit):
                    break
            # Build string of widths
            width_str += chr(8 - bit)
            
        self.out_fp.write('"""Font conversion: %s, %s"""\n\n' % (self.in_fp.name, time.ctime()))
        tup_name = self.in_fp.name.split('.')[0]
        
        self.out_fp.write('%s_widths = %s\n' % (tup_name, self.hexrepr(width_str)))
        
        self.out_fp.write('%s = (\n' % tup_name)

        i_tup = 0
        
        for i_ch in xrange(0,self.args.numchars*8,128):
            rec = font_buf[i_ch : i_ch + 128]
            self.out_fp.write('    ' + self.hexrepr(rec) + ',\n')
    
        self.out_fp.write(')\n')
                              
        
    def hexrepr(self, binstr):
        return '"' + ''.join(['\\x%02x' % ord(c) for c in binstr]) + '"'
        
    
    
if __name__ == '__main__':
    cv = ConvertFont()
    cv.convert()
    
    
