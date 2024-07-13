from settings import *
from random import randint

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z = LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)

class Water(Generic):
    def __init__(self, pos, frames, groups):
        
        #animation setup
        self.frames = frames
        self.frame_index = 0
        
        super().__init__(pos, self.frames[self.frame_index], groups, LAYERS['water'])
        
    def animate(self, dt):
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames): self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        
    def update(self, dt):
        self.animate(dt)
        
class WildFlower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)
        
class Tree(Generic):
    def __init__(self, pos, surf, groups, name):
        super().__init__(pos, surf, groups)
        
        self.apple_surf = pygame.image.load(join('graphics', 'fruit', 'apple.png')).convert_alpha()
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()
        
    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0, 10) < 2:
                x = self.rect.left + pos[0]
                y = self.rect.top + pos[1]
                Generic((x, y), self.apple_surf, (self.apple_sprites, self.groups()[0]), LAYERS['fruit'])

        