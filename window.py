import pygame
class dmslopywindow():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 600), pygame.RESIZABLE)
        pygame.display.set_caption("slopylator main")
        
        self.framebuffer = pygame.Surface((256, 240))