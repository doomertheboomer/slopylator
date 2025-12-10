import time
from window import *

class dmppu:
    def __init__(self, rambus, loglevel = 3):
        # self.window = dmslopywindow()
        
        self.rambus = rambus
        self.oam = [0] * 0x256
        
        # init state
        self.rambus.cpumem[0x2000] = 0 # ctrl
        self.rambus.cpumem[0x2001] = 0 # mask
        self.rambus.cpumem[0x2002] = 0 # status
        self.rambus.cpumem[0x2003] = 0 # oamaddr
        self.rambus.cpumem[0x2004] = 0 # oamdata
        self.rambus.cpumem[0x2005] = 0 # scroll (internal 2 byte)
        
        self.cycles = 0
        self.lastFrame = time.time()
        
        # read from PPU memory?
        # 2 byte internal register for addr
        self.intlAddr = 0
        self.__intlDataBuf = 0
        self.rambus.cpumem[0x2006] = 0 # addr
        self.rambus.cpumem[0x2007] = 0 # data
        
        # skibidi dma
        self.rambus.cpumem[0x4014] = 0 # oamdma
        self.readRegisters()
        
        # constants
        self.__ctrlFlags = {
            'i': 2, # ppudata address incrament
            's': 3, # sprite pattern table addr
            'b': 4, # bg pattern table addr
            'h': 5, # sprite size
            'p': 6, # ppu master/slave
            'v': 7 # vblank NMI (INTERRUPT!!!)
        }
        self.__maskFlags = {
            'g': 0,
            'm': 1,
            'M': 2,
            'b': 3,
            's': 4,
            'R': 5,
            'G': 6,
            'B': 7
        }
        self.__statusFlags = {
            'o': 5,
            's': 6,
            'v': 7
        }
    
    def readRegisters(self):
        self.ctrl = self.rambus.cpumem[0x2000] # done
        self.mask = self.rambus.cpumem[0x2001]
        self.status = self.rambus.cpumem[0x2002]
        self.oamaddr = self.rambus.cpumem[0x2003] # done
        self.oamdata = self.rambus.cpumem[0x2004] # done
        self.scroll = self.rambus.cpumem[0x2005]
        self.addr = self.rambus.cpumem[0x2006] # done
        self.data = self.rambus.cpumem[0x2007] # done
        self.oamdma = self.rambus.cpumem[0x4014] # done
        
    def writeRegisters(self):
        self.rambus.cpumem[0x2000] = self.ctrl
        self.rambus.cpumem[0x2001] = self.mask
        self.rambus.cpumem[0x2002] = self.status
        self.rambus.cpumem[0x2003] = self.oamaddr
        self.rambus.cpumem[0x2004] = self.oamdata
        self.rambus.cpumem[0x2005] = self.scroll
        self.rambus.cpumem[0x2006] = self.addr
        self.rambus.cpumem[0x2007] = self.data
        self.rambus.cpumem[0x4014] = self.oamdma # in case something goes wrong chop it
    
    def __updateAddr(self):
        highptr = int(self.rambus.ppuintlAddrHigh) * 8
        
        # reset bytes to write first
        self.intlAddr &= (0b1111111100000000 >> highptr) # shift right to reset high ptr, no shift to reset low ptr
        
        # write new bytes to high/low ptr
        self.intlAddr |= (self.addr << highptr)
    
    def ctrlFlagGet(self, flag):
        # return an int for this
        if flag == 'n':
            return self.ctrl & 0b00000011
        if flag[0] in self.__ctrlFlags:
            return bool((self.ctrl >> self.__ctrlFlags[flag[0]]) & 1)
        
    def ctrlFlagSet(self, flag, enable):
        # TODO: writing to N flag lol
        if flag == 'n':
            pass
        if flag[0] in self.__ctrlFlags:
            mask = 1 << self.__ctrlFlags[flag[0]]
            if enable:
                self.ctrl |= mask
            else:
                self.ctrl &= ~mask
                
    def maskFlagGet(self, flag):
        if flag[0] in self.__maskFlags:
            return bool((self.mask >> self.__maskFlags[flag[0]]) & 1)
        
    def maskFlagSet(self, flag, enable):
        if flag[0] in self.__maskFlags:
            mask = 1 << self.__maskFlags[flag[0]]
            if enable:
                self.mask |= mask
            else:
                self.mask &= ~mask
    
    def statusFlagGet(self, flag):
        if flag[0] in self.__statusFlags:
            return bool((self.status >> self.__statusFlags[flag[0]]) & 1)
        
    def statusFlagSet(self, flag, enable):
        if flag[0] in self.__statusFlags:
            mask = 1 << self.__statusFlags[flag[0]]
            if enable:
                self.status |= mask
            else:
                self.status &= ~mask             
    
    # dummy frame render logic
    def renderFrame(self):
        # for event in pygame.event.get():
        #     # print(event)
        #     pass
        
        # self.window.screen.fill("purple")

        # RENDER YOUR GAME HERE

        # flip() the display to put your work on screen
        # pygame.display.flip()
        self.lastFrame = time.time() # this line HAS to be last
                    
    def fetch(self):
        self.readRegisters()
        
        # address register operations
        # TODO: internal state IF it breaks
        # update address if the cpu writes to ppuaddr
        if self.rambus.cpuLastWrite == 0x2006:
            self.__updateAddr() # weird internal state update for addr register
        
        # if accessing palette data, upload immediately instead of on next cycle
        # this will probably break but if it doesnt im the best programmer on earth
        if (self.intlAddr >= 0x3F00) and (self.intlAddr <= 0x3FFF):
            self.data = self.rambus.memoryReadPPU(self.intlAddr)
        
        # only update data AFTER 2007 was read to. this happens after next cpu cycle
        if self.rambus.cpuLastRead == 0x2007:
            self.data = self.rambus.memoryReadPPU(self.intlAddr)
            self.intlAddr += (int(self.ctrlFlagGet('i')) * 31 + 1)
            self.rambus.cpuLastRead = 0xFFFFF
        elif self.rambus.cpuLastWrite == 0x2007:
            self.rambus.memoryWritePPU(self.intlAddr, self.data)
            self.intlAddr += (int(self.ctrlFlagGet('i')) * 31 + 1)
            self.rambus.cpuLastWrite = 0xFFFFF          
            
        # oam operations
        self.oamdata = self.oam[self.oamaddr] # immediate
        if self.rambus.cpuLastWrite == 0x2004:
            self.oam[self.oamaddr] = self.oamdata
            self.rambus.cpuLastWrite = 0xFFFFF
        elif self.rambus.cpuLastWrite == 0x4014:
            page = self.oamdma * 0x100
            self.oam[0x00:0xFF] = self.rambus.memoryReadCPU(page, page + 0xFF)
        
        # vblank flag is reset on read
        if self.rambus.cpuLastRead == 0x2002:
            self.statusFlagSet('v', False)
            self.rambus.cpuLastRead = 0xFFFFF
        
        # frame timing stuff
        cycle = self.cycles % 89342
        
        # handling vblank with NMI
        if (cycle) == 82181:
            self.statusFlagSet('v', True)
            self.ctrlFlagSet('v', True)
            self.rambus.ppuInterrupt = True
        elif (cycle) == 0:
            self.statusFlagSet('v', False)
            
            # rendering new frames
            delta = time.time() - self.lastFrame
            # dont sleep if fps is less than 60 LOL
            try:
                time.sleep(0.0167 - delta)
                pass
            except:
                pass
            self.renderFrame()
            print(f"frame rendered {1/delta} fps")
            print(self.rambus.cpumem[0x200:0x300])

        self.writeRegisters()
        
        self.cycles += 1