import pygame
from os.path import join
from pytmx.util_pygame import load_pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree
from support import import_folder
 

class Level:
    def __init__(self):
        
        # getting the display surface
        self.display_surface = pygame.display.get_surface()
        
        #groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        
        self.setup()
        self.overlay = Overlay(self.player)
    
    def player_add(self, item):
        self.player.item_inventory[item] += 1
    
    def setup(self):
        tmx_map = load_pygame(join('data', 'map.tmx'))
        
        
        # house
        for layer in ['HouseFloor','HouseFurnitureBottom']:
            for x,y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])
                
        for layer in ['HouseWalls','HouseFurnitureTop']:
            for x,y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)
                
        # fence
        for x,y, surf in tmx_map.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites))
            
        # water
        water_frames = import_folder(join("graphics", "water"))
        for x,y,surf in tmx_map.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)
        
        # trees
        for obj in tmx_map.get_layer_by_name('Trees'):
            Tree(pos =(obj.x, obj.y), 
                 surf=obj.image, 
                 groups=(self.all_sprites, self.collision_sprites, self.tree_sprites), 
                 name=obj.name,
                 player_add = self.player_add)   
        
        # wildflowers
        for obj in tmx_map.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))      
        
        # player
        for obj in tmx_map.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.tree_sprites)
        
        # collision walls
        for x,y, surf in tmx_map.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((surf.get_width(), surf.get_height())), self.collision_sprites)
           
        Generic((0, 0), pygame.image.load(join('graphics', 'world', 'ground.png')), self.all_sprites, LAYERS['ground'])
        
    def run(self, dt):
        self.display_surface.fill('black')
        # self.all_sprites.draw(self.display_surface)
        self.all_sprites.customize_draw(self.player)
        self.all_sprites.update(dt)
        
        self.overlay.display()
        
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
        
    def customize_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
        
        
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key= lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
                    
                    #draw target postion of player to easily visualize player tool position
                    # if sprite == player:
                    #     pygame.draw.rect(self.display_surface, 'red', offset_rect, 5)
                    #     hitbox_rect = player.hitbox.copy()
                    #     hitbox_rect.center = offset_rect.center
                    #     pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)
                    #     target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
                    #     pygame.draw.circle(self.display_surface, 'blue', target_pos, 5)