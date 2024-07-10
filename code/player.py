from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        
        self.image = pygame.Surface((32, 64))
        self.image.fill('green')
        self.rect = self.image.get_frect(center = pos)