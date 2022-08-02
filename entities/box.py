import pygame as py
import colors
from random import randint

class box:
    def __init__(self, s_pos_x, s_pos_y, screen_height):
        self.screen_height = screen_height
        self.surface_pos = [s_pos_x, s_pos_y]
        self.surface = py.Surface((200,100))
        self.rect = self.surface.get_rect()
        self.surface.set_colorkey(colors.WHITE)
        self.vertical_vel = randint(1,5)
        self.vel_dir = -1 if randint(0,1) == 1 else 1
        self.center = self.get_center()
        
    def get_center(self):
        return [self.surface_pos[0] + self.rect.width/2.0, self.surface_pos[1]]

    def get_mask(self):
        return py.mask.from_surface(self.surface)

    def move(self):
        self.surface_pos[1] += (self.vertical_vel*self.vel_dir)
        if self.surface_pos[1] < 0:
            self.vel_dir *= -1
            self.surface_pos[1] = 0
        elif self.surface_pos[1] > self.screen_height - 100:
            self.vel_dir *= -1
            self.surface_pos[1] = self.screen_height - 100
        self.center = self.get_center()

    def draw(self, screen):
        self.move()
        self.surface.fill(colors.GREEN)
        # py.draw.line(self.surface, colors.RED, self.rect.topleft, self.rect.bottomleft, 2)
        # py.draw.line(self.surface, colors.RED, [self.rect.topright[0] - 2, self.rect.topright[1]], [self.rect.bottomright[0] - 2, self.rect.bottomright[1]], 2)
        # py.draw.line(self.surface, colors.RED, [self.rect.bottomleft[0], self.rect.bottomleft[1]-2], [self.rect.bottomright[0], self.rect.bottomright[1]-2], 2)
        screen.blit(self.surface, self.surface_pos)