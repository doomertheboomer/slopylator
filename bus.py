class dmrambus:
    def __init__(self, isVertical):
        # up to 0x10000 for both cpu and ppu
        self.cpumem = [0] * 0x10000
        self.ppumem = [0] * 0x4000

        self.ppuNameTableMemory = [0] * 0xffff
        
        # bus rw log, can be reset by PPU/CPU i guess
        self.cpuLastRead = 0xFFFFF
        self.cpuLastWrite = 0xFFFFF
        
        # internal PPU flip flops
        self.ppuintlAddrHigh = True
        self.isVertical = False
        self.ppuInterrupt = False
        
        self.isVertical = isVertical

        self.readHooks = []
        self.writeHooks = []
        
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

        for f in self.readHooks:
            v = f(fixAddy)
            if v is not None:
                return v
        
        # handle weird PPU edge cases (prepare for yandev quality code)
        # if fixAddy == 0x2002:
        #     self.ppuintlAddrHigh = False
        # elif fixAddy == 0x2006:
        #     # for double address reads
        #     self.ppuintlAddrHigh = (not self.ppuintlAddrHigh)
        
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
        self.cpuLastWrite = fixAddy
        
        for f in self.writeHooks:
            if f(fixAddy, value) is not None:
                return

        self.cpumem[fixAddy] = value
        
        # handle weird PPU edge cases (prepare for yandev quality code)
        # if fixAddy == 0x2006:
        #     # for double address writes
        #     self.ppuintlAddrHigh = (not self.ppuintlAddrHigh)
        
    # address mirroring logic for PPU
    def getMemAddyPPU(self, address):
        address &= 0x3FFF
        if address >= 0 and address <= 0x1FFF:
            return self.ppumem, address
                
        # $3000-3EFF is usually a mirror of the 2kB region from $2000-2EFF. The PPU does not render from this address range, so this space has negligible utility.
        #if (address >= 0x3000) and (address <= 0x3EFF):
        #    address -= 0x1000
        
        # horizontal and vertical mirroring
        # given A is 0-3ff and B is 400-7ff
        # these need to be mirrored to 2000-3000
        # hori is AABB and vert is ABAB
        if (address >= 0x2000) and (address <= 0x2FFF):
            if self.isVertical:
                return self.ppuNameTableMemory, address & 0x7FF
            else:
                offset = address & 0x3FF
                quartile = (address - 0x2000) // 0x400
                newAddress = offset + ((quartile // 2) * 0x400)
                return self.ppuNameTableMemory, newAddress
        return self.ppumem, address
        
    def memoryReadPPU(self, address, end = None):
        data, addr = self.getMemAddyPPU(address)
        if end != None:
            retVal = []
            for i in range(address, end):
                data, addr = self.getMemAddyPPU(i)
                retVal.append(data[addr])
        else:
            return data[addr]
        return retVal
    
    def memoryWritePPU(self, address, value):
        data, addr = self.getMemAddyPPU(address)
        # print(hex(addr))
        data[addr] = value
