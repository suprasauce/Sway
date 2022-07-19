import math
import pygame as py
import numpy as np
import colors
import game_constants as constants
from entities.end_point import end_point as ep
from entities.bob import bob as b
from arc import arc as ar

py.init()

fps = constants.FPS
screen = py.display.set_mode()
screen_width, screen_height = py.display.get_surface().get_size()
clock = py.time.Clock()

def main():
    
    run = True
    is_pen_free = True
    is_bob_free = False
    pivot = (screen_width/4, screen_height/3)
    ep_x, ep_y = screen_width/4, 2*screen_height/3
    end_point = ep(ep_x, ep_y, pivot)
    bob =b(ep_x, ep_y)
    arc = ar([screen_width, screen_height])

    while(run):

        clock.tick(fps)
        screen.fill(colors.WHITE)
        for event in py.event.get():
            if event.type == py.QUIT:
                run = False
            elif event.type == py.MOUSEBUTTONDOWN:
                is_pen_free = False
            elif event.type == py.MOUSEBUTTONUP:
                is_pen_free = True
            elif event.type == py.KEYDOWN:
                if event.key == py.K_SPACE and not is_bob_free:
                    is_bob_free = True
                    curr_velocity = end_point.theta2*end_point.length
                    curr_angle = end_point.theta1
                    v_x = curr_velocity*math.cos(curr_angle)
                    v_y = curr_velocity*math.sin(curr_angle)
                    bob.set_parabolic_motion_initials(v_x/2, v_y/2)

        if not is_bob_free:
            if is_pen_free:
                end_point.move()
            else:
                new_x, new_y = py.mouse.get_pos()
                end_point.reset_attributes(new_x, new_y)

        if is_bob_free:
            bob.move()
            bob.draw(screen, is_bob_free=is_bob_free)
        else:
            bob.draw(screen,  is_bob_free, end_point.x, end_point.y)
            py.draw.line(screen, colors.GREEN, pivot, [end_point.x, end_point.y],1)

        arc.rotate()
        arc.draw(screen)
        py.display.update()


main()