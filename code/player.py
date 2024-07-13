from settings import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        #setup
        self.import_assets()
        self.status = 'down'
        self.frame_index = 0
        
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        self.z = LAYERS['main']
        
        #movement
        self.pos = Vector2(self.rect.center)
        self.direction = Vector2()
        self.speed = 500
        
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
    
    def use_tool(self):
        pass
        # print(self.selected_tool)
    
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
        #vertical
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
    
    def animate(self, dt):
        current_animation = self.animations[self.status]
        self.frame_index += 4 * dt
        
        if self.frame_index > len(current_animation):
            self.frame_index = 0
        self.image = current_animation[int(self.frame_index)]
    
    def update_timers(self):
        for timers in self.timers.values():
            timers.update()
          
    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.move(dt)
        self.animate(dt)
        
        