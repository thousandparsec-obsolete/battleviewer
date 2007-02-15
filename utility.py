import pygame, Numeric, random

def blur_surface (rgb_surface):
    # Basic averaging blur
    array_rgb = pygame.surfarray.array3d(rgb_surface)
    array_soften = Numeric.array(array_rgb).astype(Numeric.Int)
    array_soften[1:,:] += array_rgb[:-1,:]*8
    array_soften[:-1,:] += array_rgb[1:,:]*8
    array_soften[:,1:]  += array_rgb[:,:-1]*8
    array_soften[:,:-1] += array_rgb[:,1:]*8
    array_soften /= 33
    pygame.surfarray.blit_array(rgb_surface, array_soften)
    
    # this alters the original surface but we will return the reference to be friendly
    return rgb_surface

def static_starfield (rgb_surface, star_count=200):
    # Basic starfield
    for n in range(star_count):
        r = random.randrange(10,200)
        color = (r,r,r)
        #if n % 100 == 0:
        #    blur_surface(rgb_surface)
        rgb_surface.set_at((random.randrange(0, rgb_surface.get_width()), random.randrange(0, rgb_surface.get_height())), color)
    #blur_surface(rgb_surface)
    
    # this alters the original surface but we will return the reference to be friendly
    return rgb_surface