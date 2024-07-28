import pygame
from settings import *

class Menu:
    def __init__(self, player, toggle_menu):
        
        #general setup
        self.display_surface = pygame.display.get_surface() 
        self.player = player
        self.toggle_menu = toggle_menu
        self.font = pygame.font.Font('font/LycheeSoda.ttf', 30)
        
        # options
        self.width = 400
        self.space = 10
        self.padding = 8
        
        # entries
        self.options = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys())
        self.sell_border = len(self.player.item_inventory) - 1
        self.setup()
        
        # movement
        self.index = 0
    
    def setup(self):
        
        # create the text surfs
        self.text_surfs = []
        self.total_height = 0
        for item in self.options:
            text_surf = self.font.render(item, False, 'Black')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)
        
        self.total_height += (len(self.text_surfs) - 1) * self.space
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        
        left = SCREEN_WIDTH / 2 - self.width / 2
        self.main_rect = pygame.Rect(left,self.menu_top,self.width,self.total_height)
        
        # buy/sell text surface
        self.buy_text = self.font.render('buy', False, 'Black')
        self.sell_text = self.font.render('sell', False, 'Black')
    
    def input(self):
        keys = pygame.key.get_just_pressed()
        
        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()
            
        if keys[pygame.K_UP]:
            self.index -= 1
        if keys[pygame.K_DOWN]:
            self.index += 1
        
        if keys[pygame.K_SPACE]:
            current_item = self.options[self.index]
            print(current_item)
            
            # sell or buy
            if self.index <=self.sell_border:
                if self.player.item_inventory[current_item] > 0:
                    self.player.item_inventory[current_item] -= 1
                    self.player.money += SALE_PRICES[current_item]
            
            else:
                seed_price = PURCHASE_PRICES[current_item]
                if self.player.money >= seed_price:
                    self.player.seed_inventory[current_item] += 1
                    self.player.money -= seed_price
        
        # clamp the values
        if self.index < 0:
            self.index = len(self.options) - 1
        if self.index > len(self.options) - 1:
            self.index = 0
    
    def display_money(self):
        money_font = pygame.font.Font('font/LycheeSoda.ttf', 35)
        text_surf = money_font.render(f'${self.player.money}',False, 'Black')
        text_rect = text_surf.get_rect(midbottom = (70, 70))
        
        pygame.draw.rect(self.display_surface, 'white', text_rect.inflate(10, 10), 0, 6)
        
        self.display_surface.blit(text_surf, text_rect)
    
    def show_entry(self, text_surf, amount, top, selected):
        # background
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + (self.padding * 2))
        pygame.draw.rect(self.display_surface, 'white', bg_rect, 0, 4)
        
        # text
        text_rect = text_surf.get_rect(midleft = (self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)
        
        # amount
        amount_surf = self.font.render(str(amount), False, 'Black')
        amount_rect = amount_surf.get_rect(midright = (self.main_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)
        
        # selected
        
        if selected:
            pygame.draw.rect(self.display_surface, 'black', bg_rect, 4, 4)
            pos_rect = self.sell_text.get_rect(midleft = (self.main_rect.left + 200, bg_rect.centery))
            if self.index <= self.sell_border: # sell
                self.display_surface.blit(self.sell_text, pos_rect)
            else:
                self.display_surface.blit(self.buy_text, pos_rect)
                
                
                
    
    def update(self):
        self.input()
        self.display_money()
        
        for text_index, text_surf in enumerate(self.text_surfs):
            top = self.main_rect.top + text_index * (text_surf.get_height() + (self.padding * 2) + self.space)
            amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())
            amount = amount_list[text_index]
            self.show_entry(text_surf,amount, top, self.index == text_index)
            
            