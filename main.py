# builtin modules import


# my own modules import
from cpu import *
from ppu import *

# this is the bus i guess
cpu = dm6502() # has ram mirrored by bus (done inside the obj)
ppu = dmppu() # has its own ram too

# load the rom
with open("rom.nes", "rb") as file:
    romfile = list(file.read())
prgRom = romfile[4] # number of code banks (*16kb)
chrRom = romfile[5] # number of graphics banks (*8kb)

# control bytes bitmask
ctrl1 = romfile[6] # six
ctrl2 = romfile[7] # sevennnnnnnn
hasTrainer = (ctrl1 >> 2) & 1 # need to skip 512 bytes if this is present
isVertical = bool(ctrl1 & 1) # if false then game mirrors horizontal
is4Screen = bool((ctrl1 >> 3) & 1)

prgStart = 16 + (hasTrainer * 512)
chrStart = prgStart + (16384 * prgRom)

