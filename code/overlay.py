from settings import *

class Overlay:
    def __init__(self, player):
        # general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player
        
        #imports
        self.tools_surf = {tool: pygame.image.load(join('graphics', 'overlay', tool) + '.png').convert_alpha() for tool in player.tools}
        self.seeds_surf = {seed: pygame.image.load(join('graphics', 'overlay', seed) + '.png').convert_alpha() for seed in player.seeds}
    
    def display(self):
        
        #tool
        tool_surf = self.tools_surf[self.player.selected_tool]
        tool_rect = tool_surf.get_frect(midbottom = OVERLAY_POSITIONS['tool'])
        self.display_surface.blit(tool_surf, tool_rect)
        
        #seed
        seed_surf = self.seeds_surf[self.player.selected_seed]
        seed_rect = seed_surf.get_frect(midbottom = OVERLAY_POSITIONS['seed'])
        self.display_surface.blit(seed_surf, seed_rect)