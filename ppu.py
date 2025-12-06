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
        self.__intlAddrHigh = True
        self.rambus.cpumem[0x2006] = 0 # addr
        self.rambus.cpumem[0x2007] = 0 # data
        
        # skibidi dma
        self.rambus.cpumem[0x4014] = 0 # oamdma
        self.readRegisters()
    
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
    
    def fetch(self):
        self.readRegisters()
        
        # TODO: do the PPU operation
        
        
        self.writeRegisters()
        
        