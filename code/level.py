import pygame
from os.path import join
from pytmx.util_pygame import load_pygame
from random import randint
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from support import import_folder
from transition import Transition
from soil import SoilLayer
from sky import Rain
 

class Level:
    def __init__(self):
        
        # getting the display surface
        self.display_surface = pygame.display.get_surface()
        
        #groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()
        
        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)
        
        #sky
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0, 10) > 7
        self.soil_layer.raining = self.raining
    
    def player_add(self, item):
        self.player.item_inventory[item] += 1
    
    def setup(self):
        tmx_map = load_pygame(join('data', 'map.tmx'))
        
        # house
        for layer in ['HouseFloor','HouseFurnitureBottom']:
            for x,y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])
        
        # house walls        
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
                self.player = Player(pos=(obj.x, obj.y), 
                                     groups=self.all_sprites, 
                                     collision_sprites=self.collision_sprites, 
                                     tree_sprites=self.tree_sprites,
                                     interaction = self.interaction_sprites,
                                     soil_layer = self.soil_layer)
            if obj.name == 'Bed':
                Interaction(pos=(obj.x, obj.y), 
                            size=(obj.width, obj.height), 
                            groups=self.interaction_sprites, 
                            name=obj.name)
        
        # collision walls
        for x,y, surf in tmx_map.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((surf.get_width(), surf.get_height())), self.collision_sprites)
           
        Generic((0, 0), pygame.image.load(join('graphics', 'world', 'ground.png')), self.all_sprites, LAYERS['ground'])
    
    def reset(self):
        
        # plants
        self.soil_layer.update_plants()
        
        # soil
        self.soil_layer.remove_water()
        
        # randomize rain
        self.raining = randint(0, 10) < 3
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()
        
        #apples on the trees
        for tree in self.tree_sprites:
            for apple in tree.apple_sprites:
                apple.kill()
            if tree.alive:
                tree.create_fruit()
    
    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites:
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    Particle((plant.rect.topleft), plant.image, self.all_sprites, LAYERS['main'])  
                    row = plant.rect.centery // TILE_SIZE
                    col = plant.rect.centerx // TILE_SIZE                  
                    self.soil_layer.grid[row][col].remove('P')
                    plant.kill()
       
    def run(self, dt):
        self.display_surface.fill('black')
        # self.all_sprites.draw(self.display_surface)
        self.all_sprites.customize_draw(self.player)
        self.all_sprites.update(dt)
        self.plant_collision()
        
        self.overlay.display()
        
        # rain
        if self.raining:
            self.rain.update()
        
        # transition overlay
        if self.player.sleep:
            self.transition.play()
            
    

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