import pygame
from settings import *
from os.path import join
from support import import_folder
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        
        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0
        
        #general setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        self.z = LAYERS['main']
        
        # movement
        self.direction = pygame.Vector2()
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 400
        
        #timers
        self.timers = {
           'tool use' : Timer(350, self.use_tool),
           'tool switch': Timer(200),
           'seed use': Timer(350, self.use_seed),
           'seed switch': Timer(200),
        }
        
        # tools
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]
        
        #seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]
    
    def use_seed(self):
        pass
    
    def use_tool(self):
        pass
    
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
        
        if not self.timers['tool use'].active:
            #directions
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
                
            #tool use
            if keys[pygame.K_SPACE]:
                # timer for the tool use
                self.timers['tool use'].activate()
                self.direction = pygame.Vector2()
                self.frame_index = 0
                
            # change tool
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tool_index += 1
                if self.tool_index >= len(self.tools):
                    self.tool_index = 0
                self.selected_tool = self.tools[self.tool_index]
                
            # seed use
            if keys[pygame.K_LCTRL]:
                self.timers['seed use'].activate()
                self.direction = pygame.Vector2()
                self.frame_index = 0
                
            # seed switch
            if keys[pygame.K_e] and not self.timers['seed switch'].active:
                self.timers['seed switch'].activate()
                self.seed_index += 1 
                if self.seed_index >= len(self.seeds):
                    self.seed_index = 0
                self.selected_seed = self.seeds[self.seed_index]
                
        
    def get_status(self):
        
        # idle movement
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'
        
        #tool use
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + f'_{self.selected_tool}' 
    
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()
    
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
        self.get_status()
        self.update_timers()
        
        self.move(dt)
        self.animate(dt)