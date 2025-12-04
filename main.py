# builtin modules import


# my own modules import
from cpu import *
from ppu import *

# this is the bus i guess
cpu = dm6502() # has ram mirrored by bus (done inside the obj)
ppu = dmppu() # has its own ram too

# load the rom
