"""This file defines some 8x8 glyphs for things such as directional remotes.

Note: This could be accomplished with fonts_8x8.py which allows using external tools to define symbols.
      However, the code below illustrates the simplicity of creating LED matrix symbols directly and
      thus stands as a useful example.
"""

# OOOOOOOO
# OOOOOOOO
# OOOOOOOO
# OOO**OOO
# OOO**OOO
# OOOOOOOO
# OOOOOOOO
# OOOOOOOO
CENTER_SQUARE = "\x00\x00\x00\x18\x18\x00\x00\x00"

# OOO**OOO
# OO****OO
# O******O
# OOO**OOO
# OOO**OOO
# OOOOOOOO
# OOOOOOOO
# OOOOOOOO
UP_ARROW = "\x18\x3C\x7E\x18\x18\x00\x00\x00"

# OOOO****
# OOOOO***
# OOOO****
# OOO***O*
# OOO**OOO
# OOOOOOOO
# OOOOOOOO
# OOOOOOOO
UP_RIGHT_ARROW = "\x0F\x07\x0F\x1D\x18\x00\x00\x00"

# ****OOOO
# ***OOOOO
# ****OOOO
# *O***OOO
# OOO**OOO
# OOOOOOOO
# OOOOOOOO
# OOOOOOOO
UP_LEFT_ARROW = "\xF0\xE0\xF0\xB8\x18\x00\x00\x00"

# OOOOOOOO
# OOOOOOOO
# OOOOOOOO
# OOO**OOO
# OOO**OOO
# O******O
# OO****OO
# OOO**OOO
DOWN_ARROW = "\x00\x00\x00\x18\x18\x7E\x3C\x18"

# OOOOOOOO
# OOOOOOOO
# OOOOOOOO
# OOO**OOO
# OOO***O*
# OOOO****
# OOOOO***
# OOOO****
DOWN_RIGHT_ARROW = "\x00\x00\x00\x18\x1D\x0F\x07\x0F"

# OOOOOOOO
# OOOOOOOO
# OOOOOOOO
# OOO**OOO
# *O***OOO
# ****OOOO
# ***OOOOO
# ****OOOO
DOWN_LEFT_ARROW = "\x00\x00\x00\x18\xB8\xF0\xE0\xF0"

# OOOOOOOO
# OO*OOOOO
# O**OOOOO
# *****OOO
# *****OOO
# O**OOOOO
# OO*OOOOO
# OOOOOOOO
LEFT_ARROW = "\x00\x20\x60\xF8\xF8\x60\x20\x00"

# OOOOOOOO
# OOOOO*OO
# OOOOO**O
# OOO*****
# OOO*****
# OOOOO**O
# OOOOO*OO
# OOOOOOOO
RIGHT_ARROW = "\x00\x04\x06\x1F\x1F\x06\x04\x00"
