import math, os, neat, colors, pygame as py, constants
from random import randint
from secrets import randbelow
from entities.end_point import end_point as ep
from entities.bob import bob as b
from entities.arc import arc as ar

py.init()

fps = constants.FPS
screen = py.display.set_mode()
screen_width, screen_height = py.display.get_surface().get_size()
clock = py.time.Clock()

def test():


    loop = True
    arc = ar([screen_width, screen_height])
    bob = py.Surface((24,24))
    bob.fill(colors.GREEN)

    while(loop):

        clock.tick(fps)
        screen.fill(colors.WHITE)
        for event in py.event.get():
            if event.type == py.QUIT:
                loop = False
            
        center = [0,0]
        if py.mouse.get_pos():
            center = py.mouse.get_pos()

        new_rect = bob.get_rect(center = center)

        screen.blit(bob, new_rect.topleft)
        
        arc.rotate()
        arc.surface.fill(colors.WHITE)
        arc.draw(screen)

        arc_mask = arc.get_mask()
        bob_mask = py.mask.from_surface(bob)

        offset = (arc.center[0] - arc.radius - new_rect.x, arc.center[1] - arc.radius - new_rect.y)
        point = bob_mask.overlap(arc_mask, offset)

        if point is not None:
            bob.fill(colors.RED)
        else:
            bob.fill(colors.GREEN)

        py.display.update()

    

if __name__ == '__main__':

    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    test()
    # local_dir = os.path.dirname(__file__)
    # config_path = os.path.join(local_dir, 'config-feedforward.txt')
    # run(config_path)
