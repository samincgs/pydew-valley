import pygame
from os import walk
from os.path import join

def import_folder(path):
    surface_list = []
    
    for _, _, img_files in walk(path):
        for image in img_files:
            full_path = join(path, image)
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
    
    return surface_list

def import_folder_dict(path):
    surface_dict = {}
    
    for _, _, files in walk(path):
        for image in files:  
            key = image.split('.')[0]
            full_path = join(path, image)
            surf = pygame.image.load(full_path).convert_alpha()
            surface_dict[key] = surf
            
    return surface_dict
        
    
def import_music(*path):
    sound = pygame.mixer.Sound(join(*path))
    return sound