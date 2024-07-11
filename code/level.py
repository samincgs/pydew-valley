from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        
        #groups
        self.all_sprites = CameraGroup()
        
        self.setup()
        self.overlay = Overlay(self.player)
    
    def setup(self):
        self.player = Player((640, 360),self.all_sprites)
        Generic((0,0), pygame.image.load(join('graphics', 'world', 'ground.png')).convert_alpha(), self.all_sprites, LAYERS['ground'])
      
    def run(self, dt):
       self.display_surface.fill('black')
       self.all_sprites.customized_draw(self.player)
       self.all_sprites.update(dt)
       
       self.overlay.display()
       
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = Vector2()
        
    def customized_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT/ 2
        for layer in LAYERS.values():
            for sprite in self.sprites():
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)