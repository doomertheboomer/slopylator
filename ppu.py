class dmppu:
    def __init__(self, rambus, loglevel = 3):
        self.rambus = rambus
        
        # init state
        self.rambus.cpumem[0x2000] = 0 # ctrl
        self.rambus.cpumem[0x2001] = 0 # mask
        self.rambus.cpumem[0x2002] = 0 # status
        self.rambus.cpumem[0x2003] = 0 # oamaddr
        self.rambus.cpumem[0x2004] = 0 # oamdata
        self.rambus.cpumem[0x2005] = 0 # scroll (internal 2 byte)
        
        # read from PPU memory?
        # 2 byte internal register for addr
        self.__intlAddr = 0
        self.__intlDataBuf = 0
        self.rambus.cpumem[0x2006] = 0 # addr
        self.rambus.cpumem[0x2007] = 0 # data
        
        # skibidi dma
        self.rambus.cpumem[0x4014] = 0 # oamdma
        self.readRegisters()
        
        # constants
        self.ctrlFlags = {
            'i': 2, # ppudata address incrament
            's': 3, # sprite pattern table addr
            'b': 4, # bg pattern table addr
            'h': 5, # sprite size
            'p': 6, # ppu master/slave
            'v': 7 # vblank NMI (INTERRUPT!!!)
        }
    
    def readRegisters(self):
        self.ctrl = self.rambus.cpumem[0x2000]
        self.mask = self.rambus.cpumem[0x2001]
        self.status = self.rambus.cpumem[0x2002]
        self.oamaddr = self.rambus.cpumem[0x2003]
        self.oamdata = self.rambus.cpumem[0x2004]
        self.scroll = self.rambus.cpumem[0x2005]
        self.addr = self.rambus.cpumem[0x2006]
        self.data = self.rambus.cpumem[0x2007]
        self.oamdma = self.rambus.cpumem[0x4014]
        
    def writeRegisters(self):
        self.rambus.cpumem[0x2000] = self.ctrl
        self.rambus.cpumem[0x2001] = self.mask
        self.rambus.cpumem[0x2002] = self.status
        self.rambus.cpumem[0x2003] = self.oamaddr
        self.rambus.cpumem[0x2004] = self.oamdata
        self.rambus.cpumem[0x2005] = self.scroll
        self.rambus.cpumem[0x2006] = self.addr
        self.rambus.cpumem[0x2007] = self.data
        self.rambus.cpumem[0x4014] = self.oamdma
    
    def __updateAddr(self):
        highptr = int(self.rambus.ppuintlAddrHigh) * 8
        
        # reset bytes to write first
        self.__intlAddr &= (0b1111111100000000 >> highptr) # shift right to reset high ptr, no shift to reset low ptr
        
        # write new bytes to high/low ptr
        self.__ppuintlAddr |= (self.addr << highptr)
    
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
                    
    def fetch(self):
        self.readRegisters()
        
        # address bus operations
        
        # upload current byte in header first before processing the rest
        if self.rambus.ppu2007Read: # only update data when 2007 is read from the CPU
            self.data = self.rambus.memoryReadPPU(self.__intlAddr)
        
        # do not update if read
        if not (self.rambus.ppu2007Read or self.rambus.ppu2007Write):
            self.__updateAddr() # weird internal state update for addr register
        
        # if accessing palette data, upload immediately instead of on next cycle
        if self.rambus.ppu2007Read:
            if (self.__intlAddr >= 0x3F00) and (self.__intlAddr <= 0x3FFF):
                self.data = self.rambus.memoryReadPPU(self.__intlAddr)
            self.rambus.ppu2007Read = False
        elif self.rambus.ppu2007Write:
            self.rambus.memoryWritePPU(self.__intlAddr, self.data)
            self.rambus.ppu2007Write = False
        
        # incrament after read
        if self.rambus.ppu2007Read or self.rambus.ppu2007Write:
            self.__intlAddr += (int(self.ctrlFlagGet('i')) * 31 + 1)
        
        self.writeRegisters()
        
        