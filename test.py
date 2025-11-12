class dm6502:
    def __init__(self, loglevel = 5):
        self.loglevel = loglevel
        self.loglevels = ["[fatal]", "[error]", "[warning]", "[information]", "[debug]", "[trace]"]
        
        # general purpose registers
        self.a = 0  # accumulator
        self.x = 0  # x register
        self.y = 0  # y register
        # special registers
        self.pc = 0 # program counter
        self.sp = 0 # stack pointer
        self.sr = 0 # status register
        self.__srFlags = {
            'n': 7,
            'v': 6,
            'b': 4,
            'd': 3,
            'i': 2,
            'z': 1,
            'c': 0
        }
        
        self.memory = [0] * 0x10000 # up to 0x10000
        
        # master list of all opcodes
        # opcode: [func, size (including first byte), cycles, stars]
        self.__opcodes = {
            0x69: [self.__adc69, 2, 2, 0],
            0x65: [self.__adc65, 2, 3, 0],
            0x75: [self.__adc75, 2, 4, 0],
            0x6D: [self.__adc6D, 3, 4, 0],
            0x7D: [self.__adc7D, 3, 4, 1],
            0x79: [self.__adc79, 3, 4, 1],
            0x61: [self.__adc61, 2, 6, 0],
            # 0x71: [self.__adc71, 2, 5, 1],
            0xEA: [self.__nop,   1, 2, 0]
        }
        
        self.log("6502 CPU initialized")
        pass
    
    def log(self, str, level = 5):
        # TODO: proper debug print impl
        print(str)
        pass
    
    def decodeExecute(self, opcode, params):
        # execute the opcode
        if (opcode in self.__opcodes) and (len(params) == self.__opcodes[opcode][1] - 1): # params len is subtracted by 1
            self.__opcodes[opcode][0](params)
            # TODO: cycle handling
        else:
            self.log("Illegal instruction!")
        pass
    
    def srFlagSet(self, flag, enable):
        # TODO: suggestion from friend to use enums instead
        flag = flag.lower()
        # 7 6 5 4 3 2 1 0
        # N V x B D I Z C
        if flag[0] in self.__srFlags:
            mask = 1 << self.__srFlags[flag[0]]
            if enable:
                self.sr |= mask
            else:
                self.sr &= ~mask
        else:
            self.log("Bad status register flag!")
        pass
    
    # TODO: addressing boilerplate
    
    # ADC: Add Memory to Accumulator with Carry
    def __adc(self, amount):
        self.a += amount
    
        # set c flag and correct value
        if self.a > 255:
            self.srFlagSet('c', True)
            self.a &= 0xFF
        else:
            self.srFlagSet('c', False)
    
        # set n flag
        self.srFlagSet('n', bool((self.a >> 7) & 1))
        
        # set z flag
        self.srFlagSet('z', int(self.a == 0))
    
        # set v flag
    
    # immediate addressing
    def __adc69(self, params):
        self.__adc(params[0])
        pass
    
    # zeropage
    def __adc65(self, params):
        self.__adc(self.memory[params[0]])
        
    # zeropage x
    def __adc75(self, params):
        address = (params[0] + self.x) & 0xFF
        self.__adc(self.memory[address])
        
    # absolute
    def __adc6D(self, params):
        address = (params[1] << 8) | params[0]
        self.__adc(self.memory[address])
        
    # absolute x
    def __adc7D(self, params):
        address = (((params[1] << 8) | params[0]) + self.x) & 0xFFFF # no idea if i should & that or not
        self.__adc(self.memory[address])
    
    # absolute y
    def __adc79(self, params):
        address = (((params[1] << 8) | params[0]) + self.y) & 0xFFFF # no idea if i should & that or not
        self.__adc(self.memory[address])
    
    # indirect x
    def __adc61(self, params):
        # val = PEEK(PEEK((arg + X) % 256) + PEEK((arg + X + 1) % 256) * 256)
        address = self.memory[(params[0] + self.x) & 0xFF] + self.memory[(params[0] + self.x + 1) & 0xFF] * 0x100        
        self.__adc(self.memory[address])
        
    # indirect y
    def __adc71(self, params):
        # val = PEEK(PEEK(arg) + PEEK((arg + 1) % 256) * 256 + Y)
        address = self.memory[params[0]] + self.memory[(params[0] + 1) & 0xFF] * 0x100 + self.y
        self.__adc(self.memory[address])
        
    # NOP: No Operation
    def __nop(self, params):
        self.log("nop")
        pass
    
    
cpu = dm6502()
cpu.decodeExecute(0xEA, [])