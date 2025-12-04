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
        self.sp = 0xFF # stack pointer
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
            
            0x90: [self.__bcc,   2, 2, 2],
            0xB0: [self.__bcs,   2, 2, 2],
            0xF0: [self.__beq,   2, 2, 2],
            
            0x24: [self.__bit24, 2, 3, 0],
            0x2C: [self.__bit2C, 3, 4, 0],

            0x30: [self.__bmi,   2, 2, 2],
            0xD0: [self.__bne,   2, 2, 2],
            0x10: [self.__bpl,   2, 2, 2],
            
            0x00: [self.__brk,   1, 7, 0],
            
            0x50: [self.__bvc,   2, 2, 2],
            0x70: [self.__bvs,   2, 2, 2],
            
            0x18: [self.__clc,   1, 2, 0],
            0xD8: [self.__cld,   1, 2, 0],
            0x58: [self.__cli,   1, 2, 0],
            0xB8: [self.__clv,   1, 2, 0],
            
            0xC9: [self.__cmpC9, 2, 2, 0],
            0xC5: [self.__cmpC5, 2, 3, 0],
            0xD5: [self.__cmpD5, 2, 4, 0],
            0xCD: [self.__cmpCD, 3, 4, 0],
            0xDD: [self.__cmpDD, 3, 4, 1],
            0xD9: [self.__cmpD9, 3, 4, 1],
            0xC1: [self.__cmpC1, 2, 6, 0],
            0xD1: [self.__cmpD1, 2, 5, 1],
            
            0xE0: [self.__cpxE0, 2, 2, 0],
            0xE4: [self.__cpxE4, 2, 3, 0],
            0xEC: [self.__cpxEC, 3, 4, 0],

            0xC0: [self.__cpyC0, 2, 2, 0],
            0xC4: [self.__cpyC4, 2, 3, 0],
            0xCC: [self.__cpyCC, 3, 4, 0],
            
            0xC6: [self.__decC6, 2, 5, 0],
            0xD6: [self.__decD6, 2, 6, 0],
            0xCE: [self.__decCE, 3, 6, 0],
            0xDE: [self.__decDE, 3, 7, 0],
            0xCA: [self.__dex,   1, 2, 0],
            0x88: [self.__dey,   1, 2, 0],
            
            0x49: [self.__eor49, 2, 2, 0],
            0x45: [self.__eor45, 2, 3, 0],
            0x55: [self.__eor55, 2, 4, 0],
            0x4D: [self.__eor4D, 3, 4, 0],
            0x5D: [self.__eor5D, 3, 4, 1],
            0x59: [self.__eor59, 3, 4, 1],
            0x41: [self.__eor41, 2, 6, 0],
            0x51: [self.__eor51, 2, 5, 1],
            
            0xE6: [self.__incE6, 2, 5, 0],
            0xF6: [self.__incF6, 2, 6, 0],
            0xEE: [self.__incEE, 3, 6, 0],
            0xFE: [self.__incFE, 3, 7, 0],
            0xE8: [self.__inx,   1, 2, 0],
            0xC8: [self.__iny,   1, 2, 0],
            
            0x4C: [self.__jmp4C, 3, 3, 0],
            0x6C: [self.__jmp6C, 3, 5, 0],
            
            0x20: [self.__jsr,   3, 6, 0],
            
            0xA9: [self.__ldaA9, 2, 2, 0],
            0xA5: [self.__ldaA5, 2, 3, 0],
            0xB5: [self.__ldaB5, 2, 4, 0],
            0xAD: [self.__ldaAD, 3, 4, 0],
            0xBD: [self.__ldaBD, 3, 4, 1],
            0xB9: [self.__ldaB9, 3, 4, 1],
            0xA1: [self.__ldaA1, 2, 6, 0],
            0xB1: [self.__ldaB1, 2, 5, 1],
            
            0xA2: [self.__ldxA2, 2, 2, 0],
            0xA6: [self.__ldxA6, 2, 3, 0],
            0xB6: [self.__ldxB6, 2, 4, 0],
            0xAE: [self.__ldxAE, 3, 4, 0],
            0xBE: [self.__ldxBE, 3, 4, 1],
            
            0xA2: [self.__ldxA2, 2, 2, 0],
            0xA6: [self.__ldxA6, 2, 3, 0],
            0xB6: [self.__ldxB6, 2, 4, 0],
            0xAE: [self.__ldxAE, 3, 4, 0],
            0xBE: [self.__ldxBE, 3, 4, 1],
            
            0xA0: [self.__ldyA0, 2, 2, 0],
            0xA4: [self.__ldyA4, 2, 3, 0],
            0xB4: [self.__ldyB4, 2, 4, 0],
            0xAC: [self.__ldyAC, 3, 4, 0],
            0xBC: [self.__ldyBC, 3, 4, 1],
            
            0x4A: [self.__lsr4A, 1, 2, 0],
            0x46: [self.__lsr46, 2, 5, 0],
            0x56: [self.__lsr56, 2, 6, 0],
            0x4E: [self.__lsr4E, 3, 6, 0],
            0x5E: [self.__lsr5E, 3, 7, 0],
            
            0xEA: [self.__nop,   1, 2, 0],
            
            0x09: [self.__ora09, 2, 2, 0],
            0x05: [self.__ora05, 2, 3, 0],
            0x15: [self.__ora15, 2, 4, 0],
            0x0D: [self.__ora0D, 3, 4, 0],
            0x1D: [self.__ora1D, 3, 4, 1],
            0x19: [self.__ora19, 3, 4, 1],
            0x01: [self.__ora01, 2, 6, 0],
            0x11: [self.__ora11, 2, 5, 1],
            
            0x48: [self.__pha,   1, 3, 0],
            0x08: [self.__php,   1, 3, 0],
            0x68: [self.__pla,   1, 4, 0],
            0x28: [self.__plp,   1, 4, 0],
            
            0x2A: [self.__rol2A, 1, 2, 0],
            0x26: [self.__rol26, 2, 5, 0],
            0x36: [self.__rol36, 2, 6, 0],
            0x2E: [self.__rol2E, 3, 6, 0],
            0x3E: [self.__rol3E, 3, 7, 0],
            
            0x6A: [self.__ror6A, 1, 2, 0],
            0x66: [self.__ror66, 2, 5, 0],
            0x76: [self.__ror76, 2, 6, 0],
            0x6E: [self.__ror6E, 3, 6, 0],
            0x7E: [self.__ror7E, 3, 7, 0],
            
            0x40: [self.__rti,   1, 6, 0],
            0x60: [self.__rts,   1, 6, 0],
            
            0xE9: [self.__sbcE9, 2, 2, 0],
            0xE5: [self.__sbcE5, 2, 3, 0],
            0xF5: [self.__sbcF5, 2, 4, 0],
            0xED: [self.__sbcED, 3, 4, 0],
            0xFD: [self.__sbcFD, 3, 4, 1],
            0xF9: [self.__sbcF9, 3, 4, 1],
            0xE1: [self.__sbcE1, 2, 6, 0],
            0xF1: [self.__sbcF1, 2, 5, 1],
            
            0x38: [self.__sec,   1, 2, 0],
            0xF8: [self.__sed,   1, 2, 0],
            0x78: [self.__sei,   1, 2, 0],
            
            0x85: [self.__sta85, 2, 3, 0],
            0x95: [self.__sta95, 2, 4, 0],
            0x8D: [self.__sta8D, 3, 4, 0],
            0x9D: [self.__sta9D, 3, 5, 0],
            0x99: [self.__sta99, 3, 5, 0],
            0x81: [self.__sta81, 2, 6, 0],
            0x91: [self.__sta91, 2, 6, 0],
            
            0x86: [self.__stx86, 2, 3, 0],
            0x96: [self.__stx96, 2, 4, 0],
            0x8E: [self.__stx8E, 3, 4, 0],
            
            0x84: [self.__sty84, 2, 3, 0],
            0x94: [self.__sty94, 2, 4, 0],
            0x8C: [self.__sty8C, 3, 4, 0],
            
            0xAA: [self.__tax,   1, 2, 0],
            0xA8: [self.__tay,   1, 2, 0],
            0xBA: [self.__tsx,   1, 2, 0],
            0x8A: [self.__txa,   1, 2, 0],
            0x9A: [self.__txs,   1, 2, 0],
            0x98: [self.__tya,   1, 2, 0],
        }
        
        self.log("6502 CPU initialized", 3)
        pass
    
    def log(self, *args):
        level = args[-1]
        va_list = args[0:-1]
        if (self.loglevel <= level):
            print("[cpu]",self.loglevels[level], *va_list)
    
    # address mirroring logic
    def getMemAddy(self, address):
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
    
    def memoryRead(self, address, end = None):
        fixAddy = self.getMemAddy(address)
        if end != None:
            retVal = []
            for i in range(address, end):
                fixAddy = self.getMemAddy(i)
                retVal.append(self.memory[i])
                return retVal
        else:
            return self.memory[fixAddy]
    
    def memoryWrite(self, address, value):
        fixAddy = self.getMemAddy(address)
        self.memory[fixAddy] = value    
    
    def fetch(self, pc = None):
        if pc == None:
            pc = self.pc # cannot access self as default val i hate you python
        
        opcode = self.memoryRead(pc)
        params = []
        # determine params array for opcode
        if (opcode in self.__opcodes):
            paramLen = self.__opcodes[opcode][1]
            # params = self.memory[(pc+1):(pc+paramLen)]
            params = self.memoryRead(pc+1, pc+paramLen) # start from after the instruction and parse remaining instructions (paramLen is already added by 1 by default)
        
        self.decodeExecute(opcode, params)
        
    
    def decodeExecute(self, opcode, params):
        # execute the opcode
        if (opcode in self.__opcodes) and (len(params) == self.__opcodes[opcode][1] - 1): # params len is subtracted by 1
            self.__opcodes[opcode][0](params)
            self.pc += self.__opcodes[opcode][1]
            # TODO: cycle handling
        else:
            self.log(f"Illegal instruction! {hex(opcode)} {len(params)}", 2)
    
    def toSign8(self, val):
        sign = (val >> 7) & 1
        if sign == 0:
            return val & 0xFF
        return (((~val) & 0b01111111) + 1) * -1
        
    def srFlagSet(self, flag, enable):
        # TODO: suggestion from friend to use enums instead
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
    
    def srFlagGet(self, flag):
        # TODO: suggestion from friend to use enums instead
        # 7 6 5 4 3 2 1 0
        # N V x B D I Z C
        if flag[0] in self.__srFlags:
            return bool((self.sr >> self.__srFlags[flag[0]]) & 1)
        else:
            self.log("Bad status register flag!", 2)
            return 0
        
    def stackPush(self, val):
        val &= 0xFF
        self.memoryWrite(self.sp + 0x100, val) # stack is on page 1
        self.sp -= 1
        self.sp &= 0xFF
    
    def stackPull(self):
        retVal = self.memoryRead(self.sp + 0x100)
        self.sp += 1
        self.sp &= 0xFF
        return retVal
    
    # addressing boilerplate
    # immediate - no need because it's in the params
    # accumulator - no need because it's a register
    # relative - no need because it's in the params
    # zeropage
    def __getZeroPageAddress(self, param):
        return param[0] # kinda redundant but guess i'll include it here
    # zeropage x
    def __getZeroPageXAddress(self, param):
        return (param[0] + self.x) & 0xFF
    # zeropage y
    def __getZeroPageYAddress(self, param):
        return (param[0] + self.y) & 0xFF
    # absolute
    def __getAbsoluteAddress(self, param):
        return (param[1] << 8) | param[0]
    # absolute x
    def __getAbsoluteXAddress(self, param):
        return (((param[1] << 8) | param[0]) + self.x) & 0xFFFF # no idea if i should & that or not
    # absolute y
    def __getAbsoluteYAddress(self, param):
        return (((param[1] << 8) | param[0]) + self.y) & 0xFFFF # no idea if i should & that or not
    # indirect
    def __getIndirectAddress(self, param):
        lobyte = param[0] # bb
        hibyte = param[1] # cc
        address = (hibyte << 8) | lobyte # ccbb
        lobyte2 = self.memoryRead(address) # xx
        hibyte2 = self.memoryRead((address + 1) & 0xFF) # yy
        address2 = (hibyte2 << 8) | lobyte2 # yyxx
        return address2 # set pc to this address for jmp
    # indirect x
    def __getIndirectXAddress(self, param):
        # val = PEEK(PEEK((arg + X) % 256) + PEEK((arg + X + 1) % 256) * 256)
        return self.memoryRead((param[0] + self.x) & 0xFF) + self.memoryRead((param[0] + self.x + 1) & 0xFF) * 0x100
    # indirect y
    def __getIndirectYAddress(self, param):
        # val = PEEK(PEEK(arg) + PEEK((arg + 1) % 256) * 256 + Y)
        return self.memoryRead(param[0]) + self.memoryRead((param[0] + 1) & 0xFF) * 0x100 + self.y
    
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
        self.__adc(self.memoryRead(address))
    
    # zeropage x
    def __adc75(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__adc(self.memoryRead(address))
    
    # absolute
    def __adc6D(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__adc(self.memoryRead(address))
        
    # absolute x
    def __adc7D(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__adc(self.memoryRead(address))

    # absolute y
    def __adc79(self, params):
        address = self.__getAbsoluteYAddress(params)
        self.__adc(self.memoryRead(address))
    
    # indirect x
    def __adc61(self, params):
        # val = PEEK(PEEK((arg + X) % 256) + PEEK((arg + X + 1) % 256) * 256)
        address = self.__getIndirectXAddress(params)
        self.__adc(self.memoryRead(address))

    # indirect y
    def __adc71(self, params):
        # val = PEEK(PEEK(arg) + PEEK((arg + 1) % 256) * 256 + Y)
        address = self.__getIndirectYAddress(params)
        self.__adc(self.memoryRead(address))
    
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
        self.__and(self.memoryRead(address))

    # zeropage x
    def __and35(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__and(self.memoryRead(address))
    
    # absolute
    def __and2D(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__and(self.memoryRead(address))
    
    # absolute x
    def __and3D(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__and(self.memoryRead(address))

    # absolute y
    def __and39(self, params):
        address = self.__getAbsoluteYAddress(params)
        self.__and(self.memoryRead(address))
    
    # indirect x
    def __and21(self, params):
        address = self.__getIndirectXAddress(params)
        self.__and(self.memoryRead(address))
    
    # indirect y
    def __and31(self, params):
        address = self.__getIndirectYAddress(params)
        self.__and(self.memoryRead(address))
    
    # ASL: Shift Left One Bit (Memory or Accumulator)
    def __asl(self, address):
        old = self.memoryRead(address)
        # self.memory[address] = self.memory[address] << 1
        self.memoryWrite(address, self.memoryRead(address) << 1)
        # set status flags
        self.srFlagSet('c', bool((old >> 7) & 1))
        self.srFlagSet('n', bool((self.memoryRead(address) >> 7) & 1))
        self.srFlagSet('z', self.memoryRead(address) == 0)
        pass
    
    # accumulator
    def __asl0A(self, params):
        old = self.a
        self.a = self.a << 1
        # set status flags
        self.srFlagSet('c', bool((old >> 7) & 1))
        self.srFlagSet('n', bool((self.a >> 7) & 1))
        self.srFlagSet('z', self.a == 0)
        
    # zeropage
    def __asl06(self, params):
        address = self.__getZeroPageAddress(params)
        self.__asl(address)
    
    # zeropage x
    def __asl16(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__asl(address)

    # absolute
    def __asl0E(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__asl(address)
    
    # absolute x
    def __asl1E(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__asl(address)
    
    # branch wrapper
    def __branch(self, size):
        self.pc += self.toSign8(size)
        self.pc &= 0xFFFF
    
    # BCC: Branch on Carry Clear
    def __bcc(self, params):
        self.log(f"bcc {params[0]}", 5)
        if self.srFlagGet('c') == False:
            self.__branch(params[0]) # function size will be added to pc after exec
    
    # BCS: Branch on Carry Set
    def __bcs(self, params):
        self.log(f"bcs {params[0]}", 5)
        if self.srFlagGet('c'):
            self.__branch(params[0]) # function size will be added to pc after exec
            
    # BEQ: Branch on Result Zero
    def __beq(self, params):
        self.log(f"beq {params[0]}", 5)
        if self.srFlagGet('z'):
            self.__branch(params[0]) # function size will be added to pc after exec
            
    # BIT: Test Bits in Memory with Accumulator
    # zero page
    def __bit24(self, params):
        address = self.__getZeroPageAddress(params)
        result = self.a & self.memoryRead(address)
        self.log(f"bit {result}", 5)

        
        # set bits
        self.srFlagSet('z', result == 0)
        self.srFlagSet('v', bool((self.memoryRead(address) >> 6) & 1))
        self.srFlagSet('n', bool((self.memoryRead(address) >> 7) & 1))
        
    def __bit2C(self, params):
        address = self.__getAbsoluteAddress(params)
        result = self.a & self.memoryRead(address)
        self.log(f"bit {result}", 5)

        # set bits
        self.srFlagSet('z', result == 0)
        self.srFlagSet('v', bool((self.memoryRead(address) >> 6) & 1))
        self.srFlagSet('n', bool((self.memoryRead(address) >> 7) & 1))
        
    # BMI: Branch on Result Minus
    def __bmi(self, params):
        self.log(f"bmi {params[0]}", 5)
        if self.srFlagGet('n'):
            self.__branch(params[0]) # function size will be added to pc after exec
    
    # BNE: Branch on Result Not Zero
    def __bne(self, params):
        self.log(f"bne {params[0]}", 5)
        if self.srFlagGet('z') == False:
            self.__branch(params[0]) # function size will be added to pc after exec
    
    # BPL: Branch on Result Zero
    def __bpl(self, params):
        self.log(f"bpl {params[0]}", 5)
        if self.srFlagGet('n') == False:
            self.__branch(params[0]) # function size will be added to pc after exec
    
    # BRK: Force Break
    def __brk(self, params):
        # push ret ptr to stack
        hibyte = (self.pc >> 8) & 0xFF
        lobyte = self.pc & 0xFF
        
        # push flags (with 2 bits always set to 1) to stack
        flagPush = self.sr | 0b00110000
        
        self.stackPush(hibyte)
        self.stackPush(lobyte)
        self.stackPush(flagPush)
        
        # set i flag according to nesdev
        self.srFlagSet('i', 1)
        
        # set pc to interrupt handler
        self.pc = 0xFFFD # supposed to be FFFE but code will add 1 to pc after
    
    # BVC: Branch on Overflow Clear
    def __bvc(self, params):
        self.log(f"bvc {params[0]}", 5)
        if self.srFlagGet('v') == False:
            self.__branch(params[0]) # function size will be added to pc after exec
            
    # BVS: Branch on Overflow Set
    def __bvs(self, params):
        self.log(f"bvs {params[0]}", 5)
        if self.srFlagGet('v'):
            self.__branch(params[0]) # function size will be added to pc after exec

    # CLC: Clear Carry Flag
    def __clc(self, params):
        self.srFlagSet('c', False)
    
    # CLD: Clear Decimal Mode
    def __cld(self, params):
        self.srFlagSet('d', False)
    
    # CLI: Clear Interrupt Disable Bit
    def __cli(self, params):
        self.srFlagSet('i', False)
    
    # CLV: Clear Overflow Flag
    def __clv(self, params):
        self.srFlagSet('v', False)
        
    # CMP: Compare Memory with Accumulator
    def __cmp(self, memory, register = 0):
        self.log(f"cmp {memory}", 5) # TODO: fix instruction name print for cpx and cpy
        # for other cmps
        if (register == 0):
            register = self.a
        result = (register - memory) & 0xFF # no idea if this should wraparound or not
        # set flags
        self.srFlagSet('c', self.a >= self.memory)
        self.srFlagSet('z', self.a == memory)
        self.srFlagSet('n', bool((result >> 7) & 1))
    
    # immediate
    def __cmpC9(self, params):
        self.__cmp(params[0])
        
    # zeropage
    def __cmpC5(self, params):
        address = self.__getZeroPageAddress(params)
        self.__cmp(self.memoryRead(address))
    
    # zeropage x
    def __cmpD5(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__cmp(self.memoryRead(address))
        
    # absolute
    def __cmpCD(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__cmp(self.memoryRead(address))
        
    # absolute x
    def __cmpDD(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__cmp(self.memoryRead(address))
        
    # absolute y
    def __cmpD9(self, params):
        address = self.__getAbsoluteYAddress(params)
        self.__cmp(self.memoryRead(address))
    
    # indirect x
    def __cmpC1(self, params):
        address = self.__getIndirectXAddress(params)
        self.__cmp(self.memoryRead(address))
    
    # indirect y
    def __cmpD1(self, params):
        address = self.__getIndirectYAddress(params)
        self.__cmp(self.memoryRead(address))
    
    # CPX: Compare Memory and Index X
    # immediate
    def __cpxE0(self, params):
        self.__cmp(params[0], self.x)
    
    # zeropage
    def __cpxE4(self, params):
        address = self.__getZeroPageAddress(params)
        self.__cmp(self.memoryRead(address), self.x)
    
    # absolute
    def __cpxEC(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__cmp(self.memoryRead(address), self.x)
    
    # CPX: Compare Memory and Index Y
    # immediate
    def __cpyC0(self, params):
        self.__cmp(params[0], self.y)
    
    # zeropage
    def __cpyC4(self, params):
        address = self.__getZeroPageAddress(params)
        self.__cmp(self.memoryRead(address), self.y)
    
    # absolute
    def __cpyCC(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__cmp(self.memoryRead(address), self.y)
        
    # DEC: Decrement Memory by One
    def __dec(self, address):
        self.log(f"dec {address}", 5)
        
        # self.memory[address] -= 1
        # self.memory[address] &= 0xFF        
        self.memoryWrite(address, (self.memoryRead(address) - 1) & 0xFF)
        
        # update flags
        self.srFlagSet('z', self.memoryRead(address) == 0)
        self.srFlagSet('n', bool((self.memoryRead(address) >> 7) & 1))
        
    # zeropage
    def __decC6(self, params):
        address = self.__getZeroPageAddress(params)
        self.__dec(address)
        
    # zeropage x
    def __decD6(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__dec(address)
        
    # absolute
    def __decCE(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__dec(address)
        
    # absolute x
    def __decDE(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__dec(address)
    
    # DEX: Decrement Index X by One
    def __dex(self, params):
        self.log(f"dex", 5)
        self.x -= 1
        self.x &= 0xFF
        # update flags
        self.srFlagSet('z', self.x == 0)
        self.srFlagSet('n', bool((self.x >> 7) & 1))

    # DEY: Decrement Index Y by One
    def __dey(self, params):
        self.log(f"dey", 5)
        self.y -= 1
        self.y &= 0xFF
        # update flags
        self.srFlagSet('z', self.y == 0)
        self.srFlagSet('n', bool((self.y >> 7) & 1))
        
    # EOR: Exclusive-OR Memory with Accumulator
    def __eor(self, memory):
        self.log(f"eor {memory}", 5)
        self.a ^= memory
        # set flags
        self.srFlagSet('z', self.a == 0)
        self.srFlagSet('n', bool((self.a >> 7) & 1))
        
    # immediate
    def __eor49(self, params):
        self.__eor(params[0])
        
    # zeropage
    def __eor45(self, params):
        address = self.__getZeroPageAddress(params)
        self.__eor(self.memoryRead(address))
        
    # zeropage x
    def __eor55(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__eor(self.memoryRead(address))
        
    # absolute
    def __eor4D(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__eor(self.memoryRead(address))
        
    # absolute x
    def __eor5D(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__eor(self.memoryRead(address))
        
    # absolute y
    def __eor59(self, params):
        address = self.__getAbsoluteYAddress(params)
        self.__eor(self.memoryRead(address))
        
    # indirect x
    def __eor41(self, params):
        address = self.__getIndirectXAddress(params)
        self.__eor(self.memoryRead(address))
        
    # indirect y
    def __eor51(self, params):
        address = self.__getIndirectYAddress(params)
        self.__eor(self.memoryRead(address))
        
    # INC: Incrament Memory by One
    def __inc(self, address):
        self.log(f"inc {address}", 5)
        # self.memory[address] += 1
        # self.memory[address] &= 0xFF
        self.memoryWrite(address, (self.memoryRead(address) + 1) & 0xFF)
        # update flags
        self.srFlagSet('z', self.memoryRead(address) == 0)
        self.srFlagSet('n', bool((self.memoryRead(address) >> 7) & 1))
        
    # zeropage
    def __incE6(self, params):
        address = self.__getZeroPageAddress(params)
        self.__inc(address)
        
    # zeropage x
    def __incF6(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__inc(address)
        
    # absolute
    def __incEE(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__inc(address)
        
    # absolute x
    def __incFE(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__inc(address)
    
    # INX: Increment Index X by One
    def __inx(self, params):
        self.log(f"inx", 5)
        self.x += 1
        self.x &= 0xFF
        # update flags
        self.srFlagSet('z', self.x == 0)
        self.srFlagSet('n', bool((self.x >> 7) & 1))

    # INY: Increment Index Y by One
    def __iny(self, params):
        self.log(f"iny", 5)
        self.y += 1
        self.y &= 0xFF
        # update flags
        self.srFlagSet('z', self.y == 0)
        self.srFlagSet('n', bool((self.y >> 7) & 1))
        
    # JMP: Jump to New Location
    def __jmp(self, address):
        self.log(f"jmp {address}")
        self.pc = address - 3 # function size will be added to pc after exec
    
    # absolute
    def __jmp4C(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__jmp(address)
        
    # indirect
    def __jmp6C(self, params):
        address = self.__getIndirectAddress(params)
        self.__jmp(address)
        
    # JSR: Jump to New Location Saving Return Address
    def __jsr(self, params):
        self.log(f"jsr {address}")
        address = self.__getAbsoluteAddress(params)
        # this is pretty much a call, pushes return address to top of stack for later
        ret = self.pc+2
        hibyte = (ret >> 8) & 0xFF
        lobyte = ret & 0xFF
        self.stackPush(hibyte)
        self.stackPush(lobyte)
        self.pc = address - 3 # function size will be added to pc after exec
        
    # LDA: Load Accumulator with Memory
    def __lda(self, memory):
        self.log(f"lda {memory}", 5)
        self.a = memory
        # set flags
        self.srFlagSet('z', memory == 0)
        self.srFlagSet('n', bool((memory >> 7) & 1))
        
    # immediate
    def __ldaA9(self, params):
        self.__lda(params[0])
    
    # zeropage
    def __ldaA5(self, params):
        address = self.__getZeroPageAddress(params)
        self.__lda(self.memoryRead(address))
    
    # zeropage x
    def __ldaB5(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__lda(self.memoryRead(address))
    
    # absolute
    def __ldaAD(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__lda(self.memoryRead(address))
        
    # absolute x
    def __ldaBD(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__lda(self.memoryRead(address))

    # absolute y
    def __ldaB9(self, params):
        address = self.__getAbsoluteYAddress(params)
        self.__lda(self.memoryRead(address))
    
    # indirect x
    def __ldaA1(self, params):
        address = self.__getIndirectXAddress(params)
        self.__lda(self.memoryRead(address))

    # indirect y
    def __ldaB1(self, params):
        # val = PEEK(PEEK(arg) + PEEK((arg + 1) % 256) * 256 + Y)
        address = self.__getIndirectYAddress(params)
        self.__lda(self.memoryRead(address))
        
    # LDX: Load Index X with Memory
    def __ldx(self, memory):
        self.log(f"ldx {memory}", 5)
        self.x = memory
        # set flags
        self.srFlagSet('z', memory == 0)
        self.srFlagSet('n', bool((self.memory >> 7) & 1))
    
    # immediate
    def __ldxA2(self, params):
        self.__ldx(params[0])
    
    # zeropage
    def __ldxA6(self, params):
        address = self.__getZeroPageAddress(params)
        self.__ldx(self.memoryRead(address))
        
    # zeropage y
    def __ldxB6(self, params):
        address = self.__getZeroPageYAddress(params)
        self.__ldx(self.memoryRead(address))
    
    # absolute
    def __ldxAE(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__ldx(self.memoryRead(address))
    
    # absolute y
    def __ldxBE(self, params):
        address = self.__getAbsoluteYAddress(params)
        self.__ldx(self.memoryRead(address))
    
    # LDY: Load Index Y with Memory
    def __ldy(self, memory):
        self.log(f"ldy {memory}", 5)
        self.y = memory
        # set flags
        self.srFlagSet('z', memory == 0)
        self.srFlagSet('n', bool((self.memory >> 7) & 1))
    
    # immediate
    def __ldyA0(self, params):
        self.__ldy(params[0])
    
    # zeropage
    def __ldyA4(self, params):
        address = self.__getZeroPageAddress(params)
        self.__ldy(self.memoryRead(address))
        
    # zeropage x
    def __ldyB4(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__ldy(self.memoryRead(address))
    
    # absolute
    def __ldyAC(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__ldy(self.memoryRead(address))
    
    # absolute x
    def __ldyBC(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__ldy(self.memoryRead(address))
    
    # LSR: Shift One Bit Right (Memory or Accumulator)
    def __lsr(self, address):
        self.log(f"lsr {address}", 5)
        old = self.memoryRead(address)
        # self.memory[address] = self.memory[address] >> 1
        self.memoryWrite(address, self.memoryRead(address) >> 1)
        # set status flags
        self.srFlagSet('c', bool(old & 1))
        self.srFlagSet('n', False)
        self.srFlagSet('z', self.memoryRead(address) == 0)
        
    # accumulator
    def __lsr4A(self, params):
        self.log(f"lsr {params}", 5)
        old = self.a
        self.a = self.a >> 1
        # set status flags
        self.srFlagSet('c', bool(old & 1))
        self.srFlagSet('n', False)
        self.srFlagSet('z', self.a == 0)
        
    # zeropage
    def __lsr46(self, params):
        address = self.__getZeroPageAddress(params)
        self.__lsr(address)
        
    # zeropage x
    def __lsr56(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__lsr(address)
    
    # absolute
    def __lsr4E(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__lsr(address)
    
    # absolute x
    def __lsr5E(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__lsr(address)
    
    # NOP: No Operation
    def __nop(self, params):
        self.log("nop", 5)
    
    # ORA: OR Memory with Accumulator
    def __ora(self, memory):
        self.log(f"ora {memory}", 5)
        self.a |= memory
        # set cpu flags
        self.srFlagSet('z', self.a == 0)
        self.srFlagSet('n', bool((self.a >> 7) & 1))
    
    # immediate
    def __ora09(self, params):
        self.__ora(params[0])
        
    # zeropage
    def __ora05(self, params):
        address = self.__getZeroPageAddress(params)
        self.__ora(self.memoryRead(address))
        
    # zeropage x
    def __ora15(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__ora(self.memoryRead(address))
        
    # absolute
    def __ora0D(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__ora(self.memoryRead(address))
        
    # absolute x
    def __ora1D(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__ora(self.memoryRead(address))
        
    # absolute y
    def __ora19(self, params):
        address = self.__getAbsoluteYAddress(params)
        self.__ora(self.memoryRead(address))
        
    # indirect x
    def __ora01(self, params):
        address = self.__getIndirectXAddress(params)
        self.__ora(self.memoryRead(address))
    
    # indirect y
    def __ora11(self, params):
        address = self.__getIndirectYAddress(params)
        self.__ora(self.memoryRead(address))
    
    # PHA: Push Accumulator on Stack
    def __pha(self, params):
        self.log(f"pha {self.a}", 5)
        self.stackPush(self.a)
    
    # PHP: Push Processor Status on Stack
    def __php(self, params):
        self.log(f"php {self.sr}", 5)
        res = self.sr | 0b00110000 # modified before push
        self.stackPush(res)
        
    # PLA: Pull Accumulator from Stack
    def __pla(self, params):
        self.a = self.stackPull()
        self.log(f"pla {self.a}", 5)
        
        # set cpu flags
        self.srFlagSet('z', self.a == 0)
        self.srFlagSet('n', bool((self.a >> 7) & 1))
        
    # PLP: Pull Processor Status from Stack
    def __plp(self, params):
        old = (self.sr & 0b00110000) # save old bits
        self.sr = self.stackPull() # set the status register
        self.sr |= old # restore old bits
        self.log(f"plp {self.sr}", 5)
        
    # ROL: Rotate One Bit Left (Memory or Accumulator)
    def __rol(self, address):
        # Move each of the bits in either A or M one place to the left. Bit 0 is filled with the current value of the carry flag whilst the old bit 7 becomes the new carry flag value.
        self.log(f"rol {address}")
        old = self.memoryRead(address)
        # self.memory[address] = self.memory[address] << 1 # Move each of the bits in either A or M one place to the left
        # self.memory[address] |= int(self.srFlagGet('c')) # Bit 0 is filled with the current value of the carry flag
        self.memoryWrite(address, self.memoryRead(address) << 1) # Move each of the bits in either A or M one place to the left
        self.memoryWrite(address, self.memoryRead(address) | int(self.srFlagGet('c'))) # Bit 0 is filled with the current value of the carry flag
        # set all da flags
        self.srFlagSet('c', bool((old >> 7) & 1)) # the old bit 7 becomes the new carry flag value
        self.srFlagSet('z', self.memoryRead(address) == 0)
        self.srFlagSet('n', bool((self.memoryRead(address) >> 7) & 1))
    
    # accumulator
    def __rol2A(self, params):
        # Move each of the bits in either A or M one place to the left. Bit 0 is filled with the current value of the carry flag whilst the old bit 7 becomes the new carry flag value.
        self.log(f"rol A")
        old = self.a
        self.a = self.a << 1 # Move each of the bits in either A or M one place to the left
        self.a |= int(self.srFlagGet('c')) # Bit 0 is filled with the current value of the carry flag
        # set all da flags
        self.srFlagSet('c', bool((old >> 7) & 1)) # the old bit 7 becomes the new carry flag value
        self.srFlagSet('z', self.a == 0)
        self.srFlagSet('n', bool((self.a >> 7) & 1))
        
    # zeropage
    def __rol26(self, params):
        addr = self.__getZeroPageAddress(params)
        self.__rol(addr)
        
    # zeropage x
    def __rol36(self, params):
        addr = self.__getZeroPageXAddress(params)
        self.__rol(addr)
    
    # absolute
    def __rol2E(self, params):
        addr = self.__getAbsoluteAddress(params)
        self.__rol(addr)
    
    # absolute x
    def __rol3E(self, params):
        addr = self.__getAbsoluteXAddress(params)
        self.__rol(addr)
        
    # ROL: Rotate Right Bit Left (Memory or Accumulator)
    def __ror(self, address):
        # Move each of the bits in either A or M one place to the right. Bit 7 is filled with the current value of the carry flag whilst the old bit 0 becomes the new carry flag value. 
        self.log(f"rol {address}")
        old = self.memoryRead(address)
        # self.memory[address] = self.memory[address] >> 1 # Move each of the bits in either A or M one place to the right
        # self.memory[address] |= ((int(self.srFlagGet('c'))) << 7) # Bit 7 is filled with the current value of the carry flag
        self.memoryWrite(address, self.memoryRead(address) >> 1) # Move each of the bits in either A or M one place to the right
        self.memoryWrite(address, self.memoryRead(address) | ((int(self.srFlagGet('c'))) << 7)) # Bit 7 is filled with the current value of the carry flag
        
        # set all da flags
        self.srFlagSet('c', bool(old & 1)) # the old bit 0 becomes the new carry flag value
        self.srFlagSet('z', self.memoryRead(address) == 0)
        self.srFlagSet('n', bool((self.memoryRead(address) >> 7) & 1))
        
    # accumulator
    def __ror6A(self, params):
        # Move each of the bits in either A or M one place to the right. Bit 7 is filled with the current value of the carry flag whilst the old bit 0 becomes the new carry flag value. 
        self.log(f"ror A")
        old = self.a
        self.a = self.a >> 1 # Move each of the bits in either A or M one place to the right
        self.a |= ((int(self.srFlagGet('c'))) << 7) # Bit 7 is filled with the current value of the carry flag
        # set all da flags
        self.srFlagSet('c', bool(old & 1)) # the old bit 0 becomes the new carry flag value
        self.srFlagSet('z', self.a == 0)
        self.srFlagSet('n', bool((self.a >> 7) & 1))
        
    # zeropage
    def __ror66(self, params):
        addr = self.__getZeroPageAddress(params)
        self.__ror(addr)
    
    # zeropage x
    def __ror76(self, params):
        addr = self.__getZeroPageXAddress(params)
        self.__ror(addr)
    
    # absolute
    def __ror6E(self, params):
        addr = self.__getAbsoluteAddress(params)
        self.__ror(addr)
        
    # absolute x
    def __ror7E(self, params):
        addr = self.__getAbsoluteXAddress(params)
        self.__ror(addr)
    
    # RTI: Return from Interrupt
    def __rti(self, params):
        flags = (self.stackPull()) & 0b11001111 # 2 flags are ignored
        lobyte = self.stackPull()
        hibyte = self.stackPull()
        
        # set the stuff
        self.sr |= flags
        self.pc = (lobyte & 0xFF) | ((hibyte << 8) & 0xFF)
        self.log(f"rti {self.pc}", 5)
        
    # RTS: Return from Subroutine
    def __rts(self, params):
        lobyte = self.stackPull()
        hibyte = self.stackPull()
        self.pc = (((lobyte & 0xFF) | ((hibyte << 8) & 0xFF)) + 1) & 0xFFFF # add 1 and limit to 16 bit address space
        self.log(f"rts {self.pc}", 5)

    
    # SBC: Subtract Memory from Accumulator with Borrow
    def __sbc(self, memory):
        # initial operation
        oldA = self.a
        self.a = self.a + ~memory + int(self.srFlagGet('c'))
        
        # weird flagset
        self.srFlagSet('c', bool(~(self.a < 0))) # ~(result < $00)
        
        # do 8bit wrap to val and do rest of flags
        self.a &= 0xFF
        self.srFlagSet('v', bool((self.a ^ oldA) & (self.a ^ ~memory) & 0x80)) # (result ^ A) & (result ^ ~memory) & $80
        self.srFlagSet('z', self.a == 0) # result == 0
        self.srFlagSet('n', bool((self.a >> 7) & 1))
        self.log(f"sbc {self.a}", 5)
        
    # immediate
    def __sbcE9(self, params):
        self.__sbc(params[0])
    
    # zeropage
    def __sbcE5(self, params):
        address = self.__getZeroPageAddress(params)
        self.__sbc(self.memoryRead(address))
        
    # zeropage x
    def __sbcF5(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__sbc(self.memoryRead(address))
    
    # absolute
    def __sbcED(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__sbc(self.memoryRead(address))
    
    # absolute x
    def __sbcFD(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__sbc(self.memoryRead(address))
        
    # absolute y
    def __sbcF9(self, params):
        address = self.__getAbsoluteYAddress(params)
        self.__sbc(self.memoryRead(address))
        
    # indirect x
    def __sbcE1(self, params):
        address = self.__getIndirectXAddress(params)
        self.__sbc(self.memoryRead(address))
        
    # indirect y
    def __sbcF1(self, params):
        address = self.__getIndirectYAddress(params)
        self.__sbc(self.memoryRead(address))
    
    # SEC: Set Carry Flag
    def __sec(self, params):
        self.log("sec", 5)
        self.srFlagSet('c', True)
    
    # SED: Set Decimal Flag
    def __sed(self, params):
        self.log("sed", 5)
        self.srFlagSet('d', True)
        
    # SEI: Set Interrupt Disable Status
    def __sei(self, params):
        self.log("sei", 5)
        self.srFlagSet('i', True) # TODO: this is delayed by 1 instruction
    
    # STA: Store Accumulator in Memory
    def __sta(self, address):
        # self.memory[address] = self.a
        self.memoryWrite(address, self.a)
        self.log(f"sta {self.a}", 5)
        
    # zeropage
    def __sta85(self, params):
        address = self.__getZeroPageAddress(params)
        self.__sta(address)
    
    # zeropage x
    def __sta95(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__sta(address)
    
    # absolute
    def __sta8D(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__sta(address)
        
    # absolute x
    def __sta9D(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__sta(address)
    
    # absolute y
    def __sta99(self, params):
        address = self.__getAbsoluteYAddress(params)
        self.__sta(address)
        
    # indirect x
    def __sta81(self, params):
        address = self.__getIndirectXAddress(params)
        self.__sta(address)
        
    # indirect y
    def __sta91(self, params):
        address = self.__getIndirectYAddress(params)
        self.__sta(address)
        
    # STX: Store Index X in Memory
    def __stx(self, address):
        # self.memory[address] = self.x
        self.memoryWrite(address, self.x)
        self.log(f"stx {self.x}", 5)
        
    # zeropage
    def __stx86(self, params):
        address = self.__getZeroPageAddress(params)
        self.__stx(address)
    
    # zeropage y
    def __stx96(self, params):
        address = self.__getZeroPageYAddress(params)
        self.__stx(address)
    
    # absolute
    def __stx8E(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__stx(address)
        
    # STY: Store Index Y in Memory
    def __sty(self, address):
        # self.memory[address] = self.y
        self.memoryWrite(address, self.y)
        self.log(f"sty {self.y}", 5)
    
    # zeropage
    def __sty84(self, params):
        address = self.__getZeroPageAddress(params)
        self.__sty(address)
    
    # zeropage x
    def __sty94(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__sty(address)
    
    # absolute
    def __sty8C(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__sty(address)
        
    # TAX: Transfer Accumulator to Index X
    def __tax(self, params):
        self.x = self.a
        # set flags
        self.srFlagSet('z', self.x == 0)
        self.srFlagSet('n', bool((self.x >> 7) & 1))
        self.log(f"tax {self.x}", 5)
    
    # TAY: Transfer Accumulator to Index Y
    def __tay(self, params):
        self.y = self.a
        # set flags
        self.srFlagSet('z', self.y == 0)
        self.srFlagSet('n', bool((self.y >> 7) & 1))
        self.log(f"tay {self.y}", 5)
    
    # TSX: Transfer Stack Pointer to Index X
    def __tsx(self, params):
        self.x = self.sp
        # set flags
        self.srFlagSet('z', self.x == 0)
        self.srFlagSet('n', bool((self.x >> 7) & 1))
        self.log(f"tsx {self.x}", 5)
        
    # TXA: Transfer Index X to Accumulator
    def __txa(self, params):
        self.a = self.x
        # set flags
        self.srFlagSet('z', self.x == 0)
        self.srFlagSet('n', bool((self.x >> 7) & 1))
        self.log(f"txa {self.x}", 5)
    
    # TXS: Transfer Index X to Stack Pointer
    def __txs(self, params):
        self.sp = self.x
        self.log(f"txs {self.x}", 5)
    
    # TYA: Transfer Index Y to Accumulator
    def __tya(self, params):
        self.a = self.y
        # set flags
        self.srFlagSet('z', self.y == 0)
        self.srFlagSet('n', bool((self.y >> 7) & 1))
        self.log(f"tya {self.y}", 5)