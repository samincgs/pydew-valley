from settings import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, tree_sprites):
        super().__init__(groups)
        #setup
        self.import_assets()
        self.status = 'down'
        self.frame_index = 0
        self.collision_sprites = collision_sprites
        
        
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        self.hitbox = self.rect.copy().inflate((-126, -70))
        self.z = LAYERS['main']
        
        #movement
        self.pos = Vector2(self.rect.center)
        self.direction = Vector2()
        self.speed = 300
        
        #timers
        self.timers = {
            'tool use' : Timer(350, self.use_tool),
            'tool switch' : Timer(200),
            'seed use': Timer(350, self.use_seed),
            'seed switch' : Timer(200)
        }
        
        #tools
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]
        
        #seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]
        
        #interaction
        self.tree_sprites = tree_sprites
    
    def use_tool(self):
        print('tool use')
        if self.selected_tool == 'hoe':
            pass
        if self.selected_tool == 'axe':
            for tree in self.tree_sprites:
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
                
        if self.selected_tool == 'water':
            pass
    
    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
    
    def use_seed(self):
        pass
       
    def import_assets(self):
        self.animations = {}
        for folder_path, _, file_names in walk(join('graphics', 'character')):
            if file_names:
                self.animations[path.basename(folder_path)] = []
        
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
            
            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0
        
            #tool_use
            if keys[pygame.K_SPACE]:
                # timer for the tool use
                self.timers['tool use'].activate()
                self.direction = Vector2()
                self.frame_index = 0
            
            #change tool
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tool_index += 1
                if self.tool_index >= len(self.tools): self.tool_index = 0
                self.selected_tool = self.tools[self.tool_index]
                
            #seed use
            if keys[pygame.K_LCTRL]:
                self.timers['seed use'].activate()
                self.direction = Vector2()
                self.frame_index = 0
                print('seed use')
            
            #change seed
            if keys[pygame.K_e] and not self.timers['seed switch'].active:
                self.timers['seed switch'].activate()
                self.seed_index += 1
                if self.seed_index >= len(self.seeds): self.seed_index = 0
                self.selected_seed = self.seeds[self.seed_index]  
              
    def get_status(self):
        #idle
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'      
         
        # tool use
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool
               
    def move(self, dt):
        
        if self.direction.magnitude() > 0: self.direction = self.direction.normalize()
        #horizontal
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        #vertical
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')
        
    
    def animate(self, dt):
        current_animation = self.animations[self.status]
        self.frame_index += 4 * dt
        
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
        self.image = current_animation[int(self.frame_index)]
    
    def update_timers(self):
        for timers in self.timers.values():
            timers.update()
    
    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0: # moving right
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0: # moving left
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

                    if direction == 'vertical':
                        if self.direction.y > 0: # moving down
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0: # moving up
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery
        
        
        
    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        self.move(dt)
        self.animate(dt)
        
        