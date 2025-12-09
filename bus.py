class dmrambus:
    def __init__(self, isVertical):
        # up to 0x10000 for both cpu and ppu
        self.cpumem = [0] * 0x10000
        self.ppumem = [0] * 0x10000
        
        # bus rw log, can be reset by PPU/CPU i guess
        self.cpuLastRead = 0xFFFFF
        self.cpuLastWrite = 0xFFFFF
        
        # internal PPU flip flops
        self.ppuintlAddrHigh = True
        self.isVertical = False
        self.ppuInterrupt = False
        
        self.isVertical = isVertical
        
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
        self.cpuLastRead = fixAddy
        
        # handle weird PPU edge cases (prepare for yandev quality code)
        if fixAddy == 0x2002:
            self.ppuintlAddrHigh = False
        elif fixAddy == 0x2006:
            # for double address reads
            self.ppuintlAddrHigh = (not self.ppuintlAddrHigh)
        
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
        self.cpuLastWrite = fixAddy
        
        # handle weird PPU edge cases (prepare for yandev quality code)
        if fixAddy == 0x2006:
            # for double address writes
            self.ppuintlAddrHigh = (not self.ppuintlAddrHigh)
        
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
        
        # horizontal and vertical mirroring
        # given A is 0-3ff and B is 400-7ff
        # these need to be mirrored to 2000-3000
        # hori is AABB and vert is ABAB
        if (address >= 0x2000) and (address <= 0x2FFF):
            if self.isVertical:
                address &= 0x7FF
            else:
                offset = address & 0x3FF
                quartile = (address - 0x2000) // 0x400
                address = offset + ((quartile // 2) * 0x400)
        
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
