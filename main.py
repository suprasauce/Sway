import pygame as py
import numpy as np
import colors
from end_point import end_point as ep
from bob import bob as b

py.init()

fps = 30
screen = py.display.set_mode()
screen_width, screen_height = py.display.get_surface().get_size()
clock = py.time.Clock()

def main():
    run = True
    pivot = (screen_width/4, screen_height/2)
    ep_x, ep_y = screen_width/4, 3*screen_height/4
    end_point = ep(ep_x, ep_y, pivot)
    bob =b(ep_x, ep_y)
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
        py.display.update()


main()