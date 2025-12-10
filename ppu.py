import time
from window import *

class dmppu:
    def __init__(self, rambus, loglevel = 3):
        self.window = dmslopywindow()
        
        self.rambus = rambus
        self.rambus.readHooks.append(self.ram_read)
        self.rambus.writeHooks.append(self.ram_write)

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
        
        # readregisters
        self.ctrl = self.rambus.cpumem[0x2000] # done
        self.mask = self.rambus.cpumem[0x2001]
        self.status = self.rambus.cpumem[0x2002]
        self.oamaddr = self.rambus.cpumem[0x2003] # done
        self.oamdata = self.rambus.cpumem[0x2004] # done
        self.scroll = self.rambus.cpumem[0x2005]
        self.addr = self.rambus.cpumem[0x2006] # done
        self.data = self.rambus.cpumem[0x2007] # done
        self.oamdma = self.rambus.cpumem[0x4014] # done
        
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
    
    def ctrlFlagGet(self, flag):
        # return an int for this
        if flag == 'n':
            return self.ctrl & 0b00000011
        if flag[0] in self.__ctrlFlags:
            return bool((self.ctrl >> self.__ctrlFlags[flag[0]]) & 1)
        
    def ctrlFlagSet(self, flag, enable):
        if flag == 'n':
            self.ctrlFlagSet('n0', bool(enable & 1))
            self.ctrlFlagSet('n1', bool(enable & 2))
            return
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
    
    def ram_read(self, address):
        if address == 0x2000:
            return self.ctrl
        if address == 0x2001:
            return self.mask
        if address == 0x2002:
            status = self.status

            # reset vblank on read
            self.statusFlagSet('v', False)

            #read resets write pair for $2005/$2006
            self.secondWrite = False

            return status
        if address == 0x2003:
            return self.oamaddr
        if address == 0x2004:
            return self.oam[self.oamaddr]
        if address == 0x2005:
            return self.scroll
        if address == 0x2006:
            return self.addr
        if address == 0x2007:
            print(f"vram read {hex(self.intlAddr)}")

            # directly read from vram for palette data
            if (self.intlAddr >= 0x3F00) and (self.intlAddr <= 0x3FFF):
                return_value = self.rambus.memoryReadPPU(self.intlAddr)
                # buffer the data "underneath"
                self.data = self.rambus.memoryReadPPU(self.intlAddr - 0x1000)
            else:
                return_value = self.data
                self.data = self.rambus.memoryReadPPU(self.intlAddr)
            self.intlAddr += (int(self.ctrlFlagGet('i')) * 31 + 1)
            return return_value

    def ram_write(self, address, value):
        if address == 0x2000:
            self.ctrl = value
            return True
        if address == 0x2001:
            self.mask = value
            return True
        if address == 0x2002:
            self.status = value
            return True
        if address == 0x2003:
            self.oamaddr = value
            return True
        if address == 0x2004:
            self.oam[self.oamaddr] = value
            self.oamaddr = (self.oamaddr + 1) & 0xFF
            return True
        if address == 0x2005:
            self.scroll = value

            self.secondWrite = not self.secondWrite
            return True
        if address == 0x2006:
            self.addr = value

            if self.secondWrite:
                self.intlAddr = (self.intlAddr & 0xFF00) + value
            else:
                self.intlAddr = (self.intlAddr & 0x00FF) + (value << 8)
                
            self.secondWrite = not self.secondWrite
            return True
        if address == 0x2007:
            self.rambus.memoryWritePPU(self.intlAddr, value)
            self.intlAddr += (int(self.ctrlFlagGet('i')) * 31 + 1)
            return True
        if address == 0x4014:
            # TODO: 513-514 cycle delay
            page = self.oamdma * 0x100
            self.oam[0x00:0xFF] = self.rambus.memoryReadCPU(page, page + 0xFF)
            return True
    
    # dummy frame render logic
    def renderFrame(self):
        for event in pygame.event.get():
            # print(event)
            pass
        
        self.window.screen.fill("purple")

        # RENDER YOUR GAME HERE

        # flip() the display to put your work on screen
        pygame.display.flip()
        self.lastFrame = time.time() # this line HAS to be last
                    
    def fetch(self):
        # frame timing stuff
        cycle = self.cycles % 89342
        
        # handling vblank with NMI
        if (cycle) == 82181:
            self.statusFlagSet('v', True)
            # self.ctrlFlagSet('v', True)
            self.rambus.ppuInterrupt = True
        elif (cycle) == 0:
            # self.statusFlagSet('v', False)
            
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
        
        self.cycles += 1