import pygame
class dmjoypad:
    def __init__(self, bus):
        bus.readHooks.append(self.ram_read)
        bus.writeHooks.append(self.ram_write)

        self.state = 0
        self.shift_register = 0
        self.strobe = 0

    def update_state(self):
        pressed = pygame.key.get_pressed()

        state = 0
        if pressed[pygame.K_z]: # a
            state |= 1 << 0
        if pressed[pygame.K_x]: # b
            state |= 1 << 1
        if pressed[pygame.K_c]: # select
            state |= 1 << 2
        if pressed[pygame.K_RETURN]: # start
            state |= 1 << 3
        if pressed[pygame.K_UP]:
            state |= 1 << 4
        if pressed[pygame.K_DOWN]:
            state |= 1 << 5
        if pressed[pygame.K_LEFT]:
            state |= 1 << 6
        if pressed[pygame.K_RIGHT]:
            state |= 1 << 7
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