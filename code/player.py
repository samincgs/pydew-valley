import pygame
from settings import *
from os.path import join
from support import import_folder, import_music
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, tree_sprites, interaction, soil_layer, toggle_shop):
        super().__init__(groups)
        
        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0
        
        #general setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        self.hitbox = self.rect.copy().inflate((-126, -70))
        self.z = LAYERS['main']
        
        # movement
        self.direction = pygame.Vector2()
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 400
        
        self.collision_sprites = collision_sprites
        
        #timers
        self.timers = {
           'tool use' : Timer(350, self.use_tool),
           'tool switch': Timer(200),
           'seed use': Timer(300, self.use_seed),
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
        
        #interaction
        self.tree_sprites = tree_sprites
        self.interaction = interaction
        self.sleep = False
        self.soil_layer = soil_layer
        self.toggle_shop = toggle_shop
        
        # inventory
        self.item_inventory = {
            'wood':   20,
            'apple':  20,
            'corn':   20,
            'tomato': 20
        }
        
        self.seed_inventory = {
            'corn': 5,
            'tomato': 5,
        }
        
        self.money = 150
        
        # sound
        self.water_sound = import_music('audio', 'water.mp3')
    
    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
     
    def use_seed(self):
        if self.seed_inventory[self.selected_seed] > 0:
            self.seed_inventory[self.selected_seed] -= 1
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
    
    def use_tool(self):
        print('use tool')
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)
        if self.selected_tool == 'axe':
            for tree in self.tree_sprites:
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        if self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)
            self.water_sound.play()
            
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
        recent_keys = pygame.key.get_just_pressed()
        
        if not self.timers['tool use'].active and not self.sleep:
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
            if recent_keys[pygame.K_SPACE]:
                # timer for the tool use
                self.timers['tool use'].activate()
                self.direction = pygame.Vector2()
                self.frame_index = 0
                
            # change tool
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                print('tool switch')
                self.timers['tool switch'].activate()
                self.tool_index += 1
                if self.tool_index >= len(self.tools):
                    self.tool_index = 0
                self.selected_tool = self.tools[self.tool_index]
                
            # seed use
            if recent_keys[pygame.K_LSHIFT]:
                self.timers['seed use'].activate()
                self.direction = pygame.Vector2()
                self.frame_index = 0
                
            # seed switch
            if keys[pygame.K_e] and not self.timers['seed switch'].active:
                print('seed switch')
                self.timers['seed switch'].activate()
                self.seed_index += 1 
                if self.seed_index >= len(self.seeds):
                    self.seed_index = 0
                self.selected_seed = self.seeds[self.seed_index]
                
            # interact with bed and trader
            if keys[pygame.K_RETURN]:
                collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, False)
                if collided_interaction_sprite:
                    if collided_interaction_sprite[0].name == 'Trader':
                        self.toggle_shop()
                    if collided_interaction_sprite[0].name == 'Bed':
                        self.status = 'left_idle'
                        self.sleep = True
                       
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
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        
        #vertical movement  
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')
    
    def collision(self, direction):
        for sprite in self.collision_sprites:
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        self.pos.x = self.hitbox.centerx
                        self.rect.centerx = self.hitbox.centerx   
                    if direction == 'vertical':
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        self.pos.y = self.hitbox.centery
                        self.rect.centery = self.hitbox.centery           

    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]
    
    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        
        self.move(dt)
        self.animate(dt)