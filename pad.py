class dmjoypad:
    def __init__(self, bus):
        bus.readHooks.append(self.ram_read)
        bus.writeHooks.append(self.ram_write)

    # TODO: proper implementation
    def ram_read(self, address):
         if address == 0x4016:
            return 0xFF
    
    def ram_write(self, address, value):
         if address == 0x4016:
            return True