# builtin modules import
import sys

# my own modules import
from cpu import *
from ppu import *
from bus import *
from pad import *

# python should let this var be used out of the if block
if len(sys.argv) == 1:
    filename = input("Enter the romfile name (enter \"testrom\" for test rom): ")
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

chr = romfile[chrStart:] # best if i limit this for sanity

bus = dmrambus(isVertical)
cpu = dm6502(bus, 0) # has ram mirrored by bus
ppu = dmppu(bus, 5) # has its own ram too
pad = dmjoypad(bus)

# load prgrom into cpu
bus.cpumem[0x8000:0x10000] = prg
cpu.pc = cpu.getIndirectAddress([0xfc, 0xff]) # needs to point to reset vector
if filename == "testrom":
    cpu.pc = 0xC000
    cpu.testmode = True
print(f"Program ROM loaded with entrypoint {hex(cpu.pc)}")

# TODO: load chrrom into ppu
bus.ppumem[0x0:0x2000] = chr[0x0:0x2000]
bus.isVertical = isVertical
ppu.buildPatternTable()
print(f"CHR ROM and mirror data loaded into PPU")

# input("Press ENTER to start emulation!")

breakpoints = []
stepping = False

# testcase generator
if cpu.testmode:
    log = open("testoutput.txt", "w")
    log.write("")
    log = open("testoutput.txt", "a")
    lines = []

# main loop
cpuCyclesOld = 0
while True:
    if (cpu.pc in breakpoints):
        print(f"Breakpoint {hex(cpu.pc)} hit! A {hex(cpu.a)} X {hex(cpu.x)} Y {hex(cpu.y)} SR {hex(cpu.sr)} SP {hex(cpu.sp)}")
        stepping = True
    if stepping:
        t = input()
        print(f"A {hex(cpu.a)} X {hex(cpu.x)} Y {hex(cpu.y)} SR {hex(cpu.sr)} SP {hex(cpu.sp)}")
        if len(t) > 0:
            stepping = False
    
    if bus.ppuInterrupt:
        # print(hex(cpu.pc)) # TEMP
        # this needs to be nested
        if ppu.ctrlFlagGet('v'):
            # stepping = True
            # print("NMI enable")
            cpu.interrupt(0xFFFA)
        bus.ppuInterrupt = False
        
    if cpu.testmode:
        log.write(f"{cpu.pc:04X} {cpu.a:02X} {cpu.x:02X} {cpu.y:02X} {cpu.sp:02X} {cpu.sr:08b}\n")
        
    cpu.fetch()
    
    # ppu is 3x faster than cpu
    for i in range((cpu.cycles - cpuCyclesOld) * 3):
        ppu.fetch()
    cpuCyclesOld = cpu.cycles
    