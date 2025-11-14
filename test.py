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
            
            0xEA: [self.__nop,   1, 2, 0]
            
        }
        
        self.log("6502 CPU initialized", 3)
        pass
    
    def log(self, *args):
        level = args[-1]
        va_list = args[0:-1]
        if (self.loglevel <= level):
            print("[cpu]",self.loglevels[level], *va_list)
    
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
        self.memory[self.sp + 0x100] = val # stack is on page 1
        self.sp -= 1
        self.sp &= 0xFF
    
    def stackPull(self):
        retVal = self.memory[self.sp + 0x100]
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
    def __asl(self, address):
        old = self.memory[address]
        self.memory[address] = self.memory[address] << 1
        # set status flags
        self.srFlagSet('c', bool((old >> 7) & 1))
        self.srFlagSet('n', bool((self.memory[address] >> 7) & 1))
        self.srFlagSet('z', self.memory[address] == 0)
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
    
    # TODO: wraparound branches and branch internal func
    # BCC: Branch on Carry Clear
    def __bcc(self, params):
        self.log(f"bcc {params[0]}", 5)
        if self.srFlagGet('c') == False:
            self.pc += self.toSign8(params[0]) # function size will be added to pc after exec
    
    # BCS: Branch on Carry Set
    def __bcs(self, params):
        self.log(f"bcs {params[0]}", 5)
        if self.srFlagGet('c'):
            self.pc += self.toSign8(params[0]) # function size will be added to pc after exec
            
    # BEQ: Branch on Result Zero
    def __beq(self, params):
        self.log(f"beq {params[0]}", 5)
        if self.srFlagGet('z'):
            self.pc += self.toSign8(params[0]) # function size will be added to pc after exec
            
    # BIT: Test Bits in Memory with Accumulator
    # zero page
    def __bit24(self, params):
        address = self.__getZeroPageAddress(params)
        result = self.a & self.memory[address]
        self.log(f"bit {result}", 5)

        
        # set bits
        self.srFlagSet('z', result == 0)
        self.srFlagSet('v', bool((self.memory[address] >> 6) & 1))
        self.srFlagSet('n', bool((self.memory[address] >> 7) & 1))
        
    def __bit2C(self, params):
        address = self.__getAbsoluteAddress(params)
        result = self.a & self.memory[address]
        self.log(f"bit {result}", 5)

        # set bits
        self.srFlagSet('z', result == 0)
        self.srFlagSet('v', bool((self.memory[address] >> 6) & 1))
        self.srFlagSet('n', bool((self.memory[address] >> 7) & 1))
        
    # BMI: Branch on Result Minus
    def __bmi(self, params):
        self.log(f"bmi {params[0]}", 5)
        if self.srFlagGet('n'):
            self.pc += self.toSign8(params[0]) # function size will be added to pc after exec
    
    # BNE: Branch on Result Not Zero
    def __bne(self, params):
        self.log(f"bne {params[0]}", 5)
        if self.srFlagGet('z') == False:
            self.pc += self.toSign8(params[0]) # function size will be added to pc after exec
    
    # BPL: Branch on Result Zero
    def __bpl(self, params):
        self.log(f"bpl {params[0]}", 5)
        if self.srFlagGet('n') == False:
            self.pc += self.toSign8(params[0]) # function size will be added to pc after exec
    
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
            self.pc += self.toSign8(params[0]) # function size will be added to pc after exec
            
    # BVS: Branch on Overflow Set
    def __bvs(self, params):
        self.log(f"bvs {params[0]}", 5)
        if self.srFlagGet('v'):
            self.pc += self.toSign8(params[0]) # function size will be added to pc after exec

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
        self.__cmp(self.memory[address])
    
    # zeropage x
    def __cmpD5(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__cmp(self.memory[address])
        
    # absolute
    def __cmpCD(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__cmp(self.memory[address])
        
    # absolute x
    def __cmpDD(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__cmp(self.memory[address])
        
    # absolute y
    def __cmpD9(self, params):
        address = self.__getAbsoluteYAddress(params)
        self.__cmp(self.memory[address])
    
    # indirect x
    def __cmpC1(self, params):
        address = self.__getIndirectXAddress(params)
        self.__cmp(self.memory[address])
    
    # indirect y
    def __cmpD1(self, params):
        address = self.__getIndirectYAddress(params)
        self.__cmp(self.memory[address])
    
    # CPX: Compare Memory and Index X
    # immediate
    def __cpxE0(self, params):
        self.__cmp(params[0], self.x)
    
    # zeropage
    def __cpxE4(self, params):
        address = self.__getZeroPageAddress(params)
        self.__cmp(self.memory[address], self.x)
    
    # absolute
    def __cpxEC(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__cmp(self.memory[address], self.x)
    
    # CPX: Compare Memory and Index Y
    # immediate
    def __cpyC0(self, params):
        self.__cmp(params[0], self.y)
    
    # zeropage
    def __cpyC4(self, params):
        address = self.__getZeroPageAddress(params)
        self.__cmp(self.memory[address], self.y)
    
    # absolute
    def __cpyCC(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__cmp(self.memory[address], self.y)
        
    # DEC: Decrement Memory by One
    def __dec(self, address):
        self.log(f"dec {address}", 5)
        self.memory[address] -= 1
        self.memory[address] &= 0xFF
        # update flags
        self.srFlagSet('z', self.memory[address] == 0)
        self.srFlagSet('n', bool((self.memory[address] >> 7) & 1))
        
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
        self.__eor(self.memory[address])
        
    # zeropage x
    def __eor55(self, params):
        address = self.__getZeroPageXAddress(params)
        self.__eor(self.memory[address])
        
    # absolute
    def __eor4D(self, params):
        address = self.__getAbsoluteAddress(params)
        self.__eor(self.memory[address])
        
    # absolute x
    def __eor5D(self, params):
        address = self.__getAbsoluteXAddress(params)
        self.__eor(self.memory[address])
        
    # absolute y
    def __eor59(self, params):
        address = self.__getAbsoluteYAddress(params)
        self.__eor(self.memory[address])
        
    # indirect x
    def __eor41(self, params):
        address = self.__getIndirectXAddress(params)
        self.__eor(self.memory[address])
        
    # indirect y
    def __eor51(self, params):
        address = self.__getIndirectYAddress(params)
        self.__eor(self.memory[address])
        
    # NOP: No Operation
    def __nop(self, params):
        self.log("nop", 5)
    
cpu = dm6502(0)
cpu.decodeExecute(0x31, [1])