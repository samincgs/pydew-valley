from settings import *

def import_folder(path):
    surface_list = []
    
    for _, _, img_files in walk(path):
        for img in img_files:
            full_path = join(path, img)
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
    
    return surface_list