import pygame
from settings import *
from os.path import join
from support import import_folder

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        
        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0
        #general setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos) 
        
        # movement
        self.direction = pygame.Vector2()
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 400
    
    def import_assets(self):
        self.animations = {'up' : [],'down' : [], 'left' : [],'right' : [],
                           'up_idle' : [],'down_idle' : [],'left_idle' : [], 'right_idle' : [],
                           'up_axe' : [],'down_axe' : [],'left_axe' : [], 'right_axe' : [],
                           'up_hoe' : [],'down_hoe' : [],'left_hoe' : [], 'right_hoe' : [],
                           'up_water' : [],'down_water' : [],'left_water' : [], 'right_water' : [],
                           }
        for animation in self.animations.keys():
            full_path = join('graphics', 'character', animation)
            self.animations[animation] = import_folder(full_path)
          
    def input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.status = 'down'
        else:
            self.direction.y = 0
            
        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.status = 'right'
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.status = 'left'
        else:
            self.direction.x = 0
 
    def move(self, dt):
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
        #horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = self.pos.x
        
        #vertical movement  
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = self.pos.y
        
    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]
    
    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)