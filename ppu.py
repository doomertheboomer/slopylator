import time
from window import *

bgColors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255)
]

spriteColors = [
    # Palette 0
    [
        None,
        (255, 0, 0),
        (200, 0, 0),
        (150, 0, 0),
    ],

    [
        None,
        (0, 255, 0),
        (0, 200, 0),
        (0, 150, 0),
    ],

    [
        None,
        (0, 0, 255),
        (0, 0, 200),
        (0, 0, 150),
    ],

    [
        None,
        (255, 255, 0),
        (200, 200, 0),
        (150, 150, 0),
    ],
]

class dmppu:
    def __init__(self, rambus, loglevel = 3):
        self.window = dmslopywindow()
        
        self.rambus = rambus
        self.rambus.readHooks.append(self.ram_read)
        self.rambus.writeHooks.append(self.ram_write)
        self.secondWrite = False

        self.oam = [0] * 0x256
        self.patternTable = []
        
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
            'n0': 0,
            'n1': 1,
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
            # print("oam write")
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
            page = value * 0x100
            self.oam[0x00:0xFF] = self.rambus.memoryReadCPU(page, page + 0xFF)
            # print(f"oam dma {hex(page)}")
            return True
    
    # frame render logic
    def renderFrame(self):
        for event in pygame.event.get():
            # print(event)
            pass
        
        self.window.screen.fill(0x400000) # blood red for the blood sweat and tears going into ts

        # RENDER YOUR GAME HERE
        self.renderBackground()
        self.renderSprites()
        
        # flip() the display to put your work on screen
        pygame.display.flip()
        self.lastFrame = time.time() # this line HAS to be last
        
    def buildPatternTable(self):
        address = 0
        patternTable = []

        for i in range(2): # iterate through both pattern tables
            tiles = []
            for j in range(256): # iterate through all tiles in table
                tile = []
                for k in range(8): # 8*2 byte pairs per tile
                    lobyte = self.rambus.memoryReadPPU(address)
                    hibyte = self.rambus.memoryReadPPU(address + 8)
                    address += 1

                    row = []
                    for x in range(8): # for each pixel in the row
                        # decrement, take msb first
                        bit0 = (lobyte >> (7 - x)) & 1
                        bit1 = (hibyte >> (7 - x)) & 1
                        color_index = (bit1 << 1) | bit0
                        #print(color_index)
                        row.append(color_index)
                    tile.append(row)
                address += 8 # already parsed the other 8 hibytes, skip
                tiles.append(tile)
            
            patternTable.append(tiles)
        self.patternTable = patternTable

    def renderBackground(self):
        nametable_start = 0x2000 # TODO: change this dynamically with ppu flags

        # Draw 32x30 tiles
        for y in range(30):
            for x in range(32):

                # tile index from nametable
                address = nametable_start + y * 32 + x # base + y offset + x offset (like a 2d array access)
                tile_index = self.rambus.memoryReadPPU(address)

                # select pattern table
                name = self.patternTable[int(self.ctrlFlagGet('b'))][tile_index]
                
                # iterate per pixel for drawing
                # 8*8 pixel tiles
                screen_y = y * 8
                for row in name:
                    screen_x = x * 8

                    for pixel in row:
                        color = bgColors[pixel] # faster to hardcode 4 colors than indexing attribute table

                        self.window.screen.set_at((screen_x, screen_y), color)
                        screen_x += 1

                    screen_y += 1
                     
    def renderSprites(self):
        pattern_table = self.patternTable[int(self.ctrlFlagGet('s'))]

        # oam fits 64 sprites (256 bytes / 4 bytes per sprite)
        for i in range(64):
            base = i * 4

            # sprite object
            # back in MY DAY we did OOP manually in assembly
            sprite_y = self.oam[base + 0]
            tile_index = self.oam[base + 1]
            attr = self.oam[base + 2]
            sprite_x = self.oam[base + 3]
            palette_id = attr & 0b00000011

            # sprite to render
            tile = pattern_table[tile_index]

            screen_y = sprite_y
            for row in tile:
                screen_x = sprite_x

                for pixel in row:
                    if pixel != 0:
                        color = spriteColors[palette_id][pixel]
                        self.window.screen.set_at((screen_x, screen_y), color)
                    screen_x += 1

                screen_y += 1

                                        
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
            except:
                pass
            self.renderFrame()
            print(f"frame rendered {1/delta} fps")
            # print(self.oam)
        
        self.cycles += 1