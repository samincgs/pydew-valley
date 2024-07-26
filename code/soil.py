import pygame
from settings import *
from os.path import join
from pytmx.util_pygame import load_pygame
from support import import_folder_dict

class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil']

class SoilLayer:
    def __init__(self, all_sprites):
        
        # sprite groups
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        
        # graphics
        self.soil_surf = pygame.image.load(join('graphics', 'soil', 'o.png')).convert_alpha()
        self.soil_surfs = import_folder_dict(join('graphics', 'soil'))
        print(self.soil_surfs)
        
        self.create_soil_grid()
        self.create_hit_rects()
        
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
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE
                
                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
                    
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
                    if t and l and not any((b, r)): tile_type = 'br' #bottom right
                    if t and r and not any((l, b)): tile_type = 'bl' #bottom left
                        
                    
                    SoilTile((index_col * TILE_SIZE, index_row * TILE_SIZE), self.soil_surfs[tile_type], (self.all_sprites, self.soil_sprites))