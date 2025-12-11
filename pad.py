class dmjoypad:
    def __init__(self, bus):
        bus.readHooks.append(self.ram_read)
        bus.writeHooks.append(self.ram_write)

        self.state = 0
        self.shift_register = 0
        self.strobe = 0

    def update_state(self):
        state = 0
        self.state = state

    def ram_read(self, address):
        if address == 0x4016:
            self.update_state()

            bit = (self.state >> self.bit) & 1
            self.bit += 1

            # https://github.com/jameskmurphy/nes
            return (bit & 0b00011111) + (0x40 & 0b11100000)
        if address == 0x4017:
            return 0
    
    def ram_write(self, address, value):
         if address == 0x4016:
            if value & 1:
                self.bit = 0
            return True
         if address == 0x4017:
            return True