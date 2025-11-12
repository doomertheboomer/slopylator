class dm6502:
    def __init__(self):
        # general purpose registers
        self.a = 0  # accumulator
        self.x = 0  # x register
        self.y = 0  # y register
        # special registers
        self.pc = 0 # program counter
        self.sp = 0 # stack pointer
        self.sr = 0 # status register
        
        self.memory = [0] * 0x10000 # up to 0x10000
        print("6502 CPU initialized")
        pass
    
    def __fetchDecode(self):
        print("test")
        pass
    
cpu = dm6502()