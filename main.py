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
                new_x, new_y = py.mouse.get_pos()
                end_point.reset_attributes(new_x, new_y)
        end_point.move()
        bob.draw(screen, end_point.x, end_point.y)
        py.draw.line(screen, colors.GREEN, pivot, [end_point.x, end_point.y],1)
        arc.rotate()
        arc.draw(screen)
        py.display.update()


main()