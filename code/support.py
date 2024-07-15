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