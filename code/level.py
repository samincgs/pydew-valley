from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree
from support import *

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        
        #groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        
        self.setup()
        self.overlay = Overlay(self.player)
    
    def setup(self):
        tmx_data = load_pygame(join('data', 'map.tmx'))
        
        #house
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x,y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE,y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])
        
        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x,y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)
        
        #fence
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites))
            
        #water
        water_frames = import_folder(join('graphics', 'water'))
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)
        #trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites), obj.name)
        
        #wildflowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
        
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player((obj.x, obj.y),self.all_sprites, self.collision_sprites)
                
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
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)