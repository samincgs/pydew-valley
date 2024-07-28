import pygame
from settings import *
from os.path import join
from pytmx.util_pygame import load_pygame
from support import import_folder_dict, import_folder, import_music
from random import choice

class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type, groups, soil, check_watered):
        super().__init__(groups)
        self.plant_type = plant_type
        self.frames = import_folder(join('graphics', 'fruit', plant_type))
        self.soil = soil
        self.check_watered = check_watered
        
        # plant growing
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[plant_type]
        self.harvestable = False
        
        # sprites
        self.image = self.frames[self.age]
        self.y_offset = -16 if plant_type == 'corn' else -8
        self.rect = self.image.get_rect(midbottom = soil.rect.midbottom + pygame.Vector2(0, self.y_offset))
        self.z = LAYERS['ground plant']
        
    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed
            
            if int(self.age) > 0:
                self.z = LAYERS['main']
                self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * 0.4)
            
            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True
            
            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom = self.soil.rect.midbottom + pygame.Vector2(0, self.y_offset))

class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil']

class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf , groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil water']

class SoilLayer:
    def __init__(self, all_sprites, collision_sprites):
        
        # sprite groups
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()
        
        # graphics
        self.soil_surfs = import_folder_dict(join('graphics', 'soil'))
        self.water_surfs = import_folder(join('graphics', 'soil_water'))
        
        self.create_soil_grid()
        self.create_hit_rects()
        
        # sounds
        self.hoe_sound = import_music('audio', 'hoe.wav')
        self.hoe_sound.set_volume(0.1)
        
    def create_soil_grid(self):
        ground = pygame.image.load(join('graphics', 'world', 'ground.png'))
        h_tiles = ground.get_width() // TILE_SIZE
        v_tiles = ground.get_height() // TILE_SIZE
        
        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        tmx_map = load_pygame(join('data', 'map.tmx' ))
        for x, y, _ in tmx_map.get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')
            
    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row): 
                if 'F' in cell:
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)
                    
    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                self.hoe_sound.play()
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE
                
                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
                    if self.raining:
                        self.water_all()
    
    def plant_seed(self, target_pos, seed):
        for soil_sprite in self.soil_sprites:
            if soil_sprite.rect.collidepoint(target_pos):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                
                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')
                    Plant(seed, (self.all_sprites, self.plant_sprites, self.collision_sprites), soil_sprite, self.check_watered)
                    
    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:
                    
                    # autotiling
                    
                    # tile options
                    t = 'X' in self.grid[index_row - 1][index_col]
                    b = 'X' in self.grid[index_row + 1][index_col]
                    r = 'X' in row[index_col + 1]
                    l = 'X' in row[index_col - 1]
                    
                    tile_type = 'o'
                    
                    # all sides
                    if all((t,b,r,l)): tile_type = 'x'
                    
                    # horizontal tiles only
                    if l and not any((t,r,b)): tile_type = 'r' 
                    if r and not any((t,l,b)): tile_type = 'l'
                    if r and l and not any((t,b)): tile_type = 'lr'
                    
                    # vertical tiles only
                    if t and not any((l,r,b)): tile_type = 'b'
                    if b and not any((l,r,t)): tile_type = 't'
                    if t and b and not any((l,r)): tile_type = 'tb'
                    
                    # corners
                    if l and b and not any((t, r)): tile_type = 'tr' #topright
                    if b and r and not any((t, l)): tile_type = 'tl' #topleft
                    if l and t and not any((b, r)): tile_type = 'br' #bottom right
                    if t and r and not any((l, b)): tile_type = 'bl' #bottom left
                    
                    # T shapes
                    if all((t,b,r)) and not l: tile_type = 'tbr' #in the middle of top, bottom and right
                    if all((t,b,l)) and not r: tile_type = 'tbl' #in the middle of top, bottom and left
                    if all((l, r, t)) and not b: tile_type = 'lrb' #in the middle of left, right and top
                    if all((l, r, b)) and not t: tile_type = 'lrt' #in the middle of left, right and top
                        
                    SoilTile((index_col * TILE_SIZE, index_row * TILE_SIZE), self.soil_surfs[tile_type], (self.all_sprites, self.soil_sprites))
    
    def update_plants(self):
        for plant in self.plant_sprites:
            plant.grow()
    
    def check_watered(self, pos):
        x = pos[0] // TILE_SIZE
        y = pos[1] // TILE_SIZE 
        cell = self.grid[y][x]
        is_watered = 'W' in cell
        return is_watered
    
    def remove_water(self):
        
        # destroy all water sprites
        for sprite in self.water_sprites:
            sprite.kill()
        
        # clean up the grid
        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')
    
    def water_all(self):
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    surf = choice(self.water_surfs)
                    WaterTile(pos=(x, y),
                          surf=surf,
                          groups=(self.all_sprites, self.water_sprites))
                    
    def water(self, target_pos):
        for soil_sprite in self.soil_sprites:
            if soil_sprite.rect.collidepoint(target_pos):
                
                # add an entry to the soil grid -> 'W'
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                self.grid[y][x].append('W')
                
                # create a water sprite
                pos = soil_sprite.rect.topleft
                surf = choice(self.water_surfs)
                WaterTile(pos=pos,
                          surf=surf,
                          groups=(self.all_sprites, self.water_sprites))