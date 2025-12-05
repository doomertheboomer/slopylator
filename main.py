# builtin modules import
import sys

# my own modules import
from cpu import *
from ppu import *

# this is the bus i guess
cpu = dm6502(5) # has ram mirrored by bus (done inside the obj)
ppu = dmppu() # has its own ram too

# python should let this var be used out of the if block
if len(sys.argv) == 1:
    filename = input("Enter the romfile name: ")
else:
    filename = sys.argv[1]

# load the rom
with open(filename, "rb") as file:
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

prg = romfile[prgStart:chrStart]
if prgRom == 1:
    prg += prg # mirroring if only 1 rom

chr = romfile[chrStart:chrStart+8192] # best if i limit this for sanity

# load prgrom into cpu
cpu.memory[0x8000:0x10000] = prg
cpu.pc = cpu.getIndirectAddress([0xfc, 0xff]) # needs to point to reset vector
print(f"Program ROM loaded at entrypoint {hex(cpu.pc)}")
input("Press ENTER to start emulation!")

# TODO: load chrrom into ppu

breakpoint = 0xdbb5f
stepping = False
# main loop
while True:
    cpu.fetch()
    if stepping:
        input()
        print(f"A {hex(cpu.a)} X {hex(cpu.x)} Y {hex(cpu.y)} SR {hex(cpu.sr)} SP {hex(cpu.sp)}")
    if (cpu.pc == breakpoint):
        print(f"Breakpoint hit! A {hex(cpu.a)} X {hex(cpu.x)} Y {hex(cpu.y)} SR {hex(cpu.sr)} SP {hex(cpu.sp)}")
        stepping = True