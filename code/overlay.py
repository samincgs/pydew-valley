import pygame
from settings import *
from os.path import join

class Overlay:
    def __init__(self, player):
        
        # general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player
        
        # imports
        self.tools_surf = {tool: pygame.image.load(join('graphics', 'overlay', f'{tool}.png')).convert_alpha() for tool in player.tools}
        self.seeds_surf = {seed: pygame.image.load(join('graphics', 'overlay', f'{seed}.png')).convert_alpha() for seed in player.seeds}
       