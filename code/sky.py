import pygame
from settings import *
from support import import_folder
from os.path import join
from sprites import Generic
from random import randint, choice

class Drop(Generic):
    def __init__(self, pos, surf, moving, groups , z):
        
        # general setup
        super().__init__(pos, surf, groups, z)
        self.lifetime = randint(300, 500)
        self.start_time = pygame.time.get_ticks()
        
        #moving
        self.moving = moving
        if self.moving:
            self.pos = pygame.Vector2(self.rect.topleft)
            self.direction = pygame.Vector2(-2, 4)
            self.speed = randint(200,300)
            
    def update(self, dt):
        # movement
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        
        #timer
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.lifetime:
            self.kill()
            
class Rain:
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites
        self.rain_drops = import_folder(join('graphics', 'rain', 'drops'))
        self.rain_floor = import_folder(join('graphics', 'rain', 'floor'))
        self.floor_w, self.floor_h = pygame.image.load(join('graphics', 'world', 'ground.png')).get_size()
        print(self.floor_w, self.floor_h)
        
    def create_floor(self):
        x = randint(0, self.floor_w) 
        y = randint(0, self.floor_h)
        surf = choice(self.rain_floor)
        Drop((x, y), surf, False, self.all_sprites, LAYERS['rain floor'])

    def create_drops(self):
        x = randint(0, self.floor_w) 
        y = randint(0, self.floor_h)
        surf = choice(self.rain_drops)
        Drop((x, y), surf, True, self.all_sprites, LAYERS['rain drops'])
    
    def update(self):
        self.create_floor()
        self.create_drops()