# builtin modules import
import sys

# my own modules import
from cpu import *
from ppu import *

# this is the bus i guess
class dmrambus:
    def __init__(self):
        # up to 0x10000 for both cpu and ppu
        self.cpumem = [0] * 0x10000
        self.ppumem = [0] * 0x10000
        
    # address mirroring logic for CPU
    def getMemAddyCPU(self, address):
        address &= 0xFFFF
        
        # first mirror 0x800-0x1FFF
        if (address >= 0x800) and (address <= 0x1FFF):
            address %= 0x800
            return address
            
        # second mirror 0x2008-0x4000
        if (address >= 0x2008) and (address <= 0x3FFF):
            address = ((address - 0x2000) % 0x8) + 0x2000
            return address
            
        # default case
        return address
    
    def memoryReadCPU(self, address, end = None):
        fixAddy = self.getMemAddyCPU(address)
        if end != None:
            retVal = []
            for i in range(address, end):
                fixAddy = self.getMemAddyCPU(i)
                retVal.append(self.cpumem[fixAddy])
        else:
            return self.cpumem[fixAddy]
        return retVal
    
    def memoryWriteCPU(self, address, value):
        fixAddy = self.getMemAddyCPU(address)
        self.cpumem[fixAddy] = value
        
    # address mirroring logic for PPU
    def getMemAddyPPU(self, address):
        # mirrors are nested so better substitute high addresses for this
        address = (address % 0x4000)
        
        # first mirror
        if (address >= 0x3000) and (address <= 0x3EFF):
            address = (address & 0x3000) + 0x2000 # only one mirror so no need to do weird things
            return address
        
        # second mirror
        if (address >= 0x3F20) and (address <= 0x3FFF):
            address = ((address - 0x3F00) % 0x20) + 0x3F00
            return address
        
    def memoryReadPPU(self, address, end = None):
        fixAddy = self.getMemAddyPPU(address)
        if end != None:
            retVal = []
            for i in range(address, end):
                fixAddy = self.getMemAddyPPU(i)
                retVal.append(self.ppumem[fixAddy])
        else:
            return self.ppumem[fixAddy]
        return retVal
    
    def memoryWritePPU(self, address, value):
        fixAddy = self.getMemAddyPPU(address)
        self.ppumem[fixAddy] = value
        
bus = dmrambus()
cpu = dm6502(bus, 5) # has ram mirrored by bus
ppu = dmppu(bus, 5) # has its own ram too

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
bus.cpumem[0x8000:0x10000] = prg
cpu.pc = cpu.getIndirectAddress([0xfc, 0xff]) # needs to point to reset vector
print(f"Program ROM loaded with entrypoint {hex(cpu.pc)}")

# TODO: load chrrom into ppu


input("Press ENTER to start emulation!")


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