import pygame
class dmslopywindow():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((256, 240))
        pygame.display.set_caption("slopylator main")