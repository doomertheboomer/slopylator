class dm6502:
    def __init__(self, loglevel = 3):
        self.loglevel = loglevel
        self.loglevels = ["[fatal]", "[error]", "[warn] ", "[info] ", "[debug]", "[trace]"]
        
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
            0x71: [self.__adc71, 2, 5, 1],
            
            0x29: [self.__and29, 2, 2, 0],
            0x25: [self.__and25, 2, 3, 0],
            0x35: [self.__and35, 2, 4, 0],
            0x2D: [self.__and2D, 3, 4, 0],
            0x3D: [self.__and3D, 3, 4, 1],
            0x39: [self.__and39, 3, 4, 1],
            0x21: [self.__and21, 2, 6, 0],
            0x31: [self.__and31, 2, 5, 1],
            
            0x0A: [self.__asl0A, 1, 2, 0],
            0x06: [self.__asl06, 2, 5, 0],
            0x16: [self.__asl16, 2, 6, 0],
            0x0E: [self.__asl0E, 3, 6, 0],
            0x1E: [self.__asl1E, 3, 7, 0],

            0xEA: [self.__nop,   1, 2, 0]
            
        }
        
        self.log("6502 CPU initialized", 3)
        pass
    
    def log(self, str, level = 5):
        if (self.loglevel <= level):
            print(self.loglevels[level], str)
    
    def decodeExecute(self, opcode, params):
        # execute the opcode
        if (opcode in self.__opcodes) and (len(params) == self.__opcodes[opcode][1] - 1): # params len is subtracted by 1
            self.__opcodes[opcode][0](params)
            # TODO: cycle handling
        else:
            self.log(f"Illegal instruction! {hex(opcode)} {len(params)}", 2)
    
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
            self.log("Bad status register flag!", 2)
        pass
    
    # addressing boilerplate
    # immediate - no need because it's in the params
    # zeropage
    def __getZeroPageAddress(self, param):
        return param[0] # kinda redundant but guess i'll include it here
    # zeropage x
    def __getZeroPageXAddress(self, param):
        return (param[0] + self.x) & 0xFF
    # absolute
    def __getAbsoluteAddress(self, param):
        return (param[1] << 8) | param[0]
    # absolute x
    def __getAbsoluteXAddress(self, param):
        return (((param[1] << 8) | param[0]) + self.x) & 0xFFFF # no idea if i should & that or not
    # absolute y
    def __getAbsoluteYAddress(self, param):
        return (((param[1] << 8) | param[0]) + self.y) & 0xFFFF # no idea if i should & that or not
    # indirect x
    def __getIndirectXAddress(self, param):
        # val = PEEK(PEEK((arg + X) % 256) + PEEK((arg + X + 1) % 256) * 256)
        return self.memory[(param[0] + self.x) & 0xFF] + self.memory[(param[0] + self.x + 1) & 0xFF] * 0x100
    # indirect y
    def __getIndirectYAddress(self, param):
        # val = PEEK(PEEK(arg) + PEEK((arg + 1) % 256) * 256 + Y)
        return self.memory[param[0]] + self.memory[(param[0] + 1) & 0xFF] * 0x100 + self.y
    
    # ADC: Add Memory to Accumulator with Carry
    def __adc(self, amount):
        self.log(f"adc {amount}", 5)
        orig_a = self.a
        self.a += amount
    
        # set c flag and correct value
        self.srFlagSet('c', self.a > 255)
        self.a &= 0xFF
    
        # set n flag
        self.srFlagSet('n', bool((self.a >> 7) & 1))
        
        # set z flag
        self.srFlagSet('z', self.a == 0)
    
        # set v flag
        v = ((orig_a ^ self.a) & (amount ^ self.a) & 0x80) != 0
        self.srFlagSet('v', v)
    
    # immediate addressing
    def __adc69(self, params):
        self.__adc(params[0])
    
    # zeropage
    def __adc65(self, params):
        address = self.__getZeroPageAddress(params)
        self.__adc(self.memory[address])
    
    # zeropage x
    def __adc75(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__adc(self.memory[address])
    
    # absolute
    def __adc6D(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__adc(self.memory[address])
        
    # absolute x
    def __adc7D(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__adc(self.memory[address])

    # absolute y
    def __adc79(self, params):
        address = self.__getAbsoluteYAddress(params)
        self.__adc(self.memory[address])
    
    # indirect x
    def __adc61(self, params):
        # val = PEEK(PEEK((arg + X) % 256) + PEEK((arg + X + 1) % 256) * 256)
        address = self.__getIndirectXAddress(params)     
        self.__adc(self.memory[address])

    # indirect y
    def __adc71(self, params):
        # val = PEEK(PEEK(arg) + PEEK((arg + 1) % 256) * 256 + Y)
        address = self.__getIndirectYAddress(params)     
        self.__adc(self.memory[address])
    
    # AND: AND Memory with Accumulator
    def __and(self, value):
        self.log(f"and {value}", 5)
        self.a = self.a & value
        
        # set n and z flag
        self.srFlagSet('n', bool((self.a >> 7) & 1))
        self.srFlagSet('z', self.a == 0)
    
    # immediate
    def __and29(self, params):
        self.__and(params[0])
    
    # zeropage
    def __and25(self, params):
        address = self.__getZeroPageAddress(params)
        self.__and(self.memory[address])

    # zeropage x
    def __and35(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__and(self.memory[address])
    
    # absolute
    def __and2D(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__and(self.memory[address])
    
    # absolute x
    def __and3D(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__and(self.memory[address])

    # absolute y
    def __and39(self, params):
        address = self.__getAbsoluteYAddress(params)
        self.__and(self.memory[address])
    
    # indirect x
    def __and21(self, params):
        address = self.__getIndirectXAddress(params)
        self.__and(self.memory[address])
    
    # indirect y
    def __and31(self, params):
        address = self.__getIndirectYAddress(params)
        self.__and(self.memory[address])
    
    # ASL: Shift Left One Bit (Memory or Accumulator)
    # TODO: set status register flags
    def __asl(self, address):
        pass
    
    # accumulator
    def __asl0A(self, params):
        self.a = self.a << 1
        
    # zeropage
    def __asl06(self, params):
        address = self.__getZeroPageAddress(params)
        self.memory[address] = self.memory[address] << 1
    
    # zeropage x
    def __asl16(self, params):
        address = self.__getZeroPageXAddress(params)
        self.memory[address] = self.memory[address] << 1

    # absolute
    def __asl0E(self, params):
        address = self.__getAbsoluteAddress(params)
        self.memory[address] = self.memory[address] << 1
    
    # absolute x
    def __asl1E(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.memory[address] = self.memory[address] << 1
        
    # NOP: No Operation
    def __nop(self, params):
        self.log("nop", 5)
    
    
cpu = dm6502(0)
cpu.decodeExecute(0x31, [1])