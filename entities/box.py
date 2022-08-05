import pygame as py
import colors
import random

class box:
    def __init__(self, s_pos_x, s_pos_y, screen_height):
        self.screen_height = screen_height
        self.surface_pos = [s_pos_x, s_pos_y]
        self.surface = py.Surface((50,50))
        self.rect = self.surface.get_rect()
        #self.surface.set_colorkey(colors.WHITE)
        self.vertical_vel = random.uniform(2,4)
        self.vel_dir = 1
        self.center = self.get_center()
        self.name_surface = py.Surface((50,12))
        
    def get_center(self):
        return [self.surface_pos[0] + 25, self.surface_pos[1] + 25]

    def get_mask(self):
        return py.mask.from_surface(self.surface)

    def move(self):
        self.surface_pos[1] += (self.vertical_vel*self.vel_dir)
        if self.surface_pos[1] < 0:
            self.vel_dir *= -1
            self.surface_pos[1] = 0
        elif self.surface_pos[1] > self.screen_height - 50:
            self.vel_dir *= -1
            self.surface_pos[1] = self.screen_height - 50
        self.center = self.get_center()

    def draw(self, screen):
        self.move()
        self.surface.fill(colors.RED)
        self.name_surface.fill(colors.WHITE)
        name_rect = self.name_surface.get_rect()
        py.draw.rect(self.name_surface, colors.RED, name_rect,0,2)
        # py.draw.line(self.surface, colors.RED, self.rect.topleft, self.rect.bottomleft, 2)
        # py.draw.line(self.surface, colors.RED, [self.rect.topright[0] - 2, self.rect.topright[1]], [self.rect.bottomright[0] - 2, self.rect.bottomright[1]], 2)
        # py.draw.line(self.surface, colors.RED, [self.rect.bottomleft[0], self.rect.bottomleft[1]-2], [self.rect.bottomright[0], self.rect.bottomright[1]-2], 2)
        font = py.font.Font("fav_font.ttf",8)
        name = font.render("Box", True, colors.WHITE)
        self.name_surface.blit(name, [name_rect.topleft[0] + 12.0, name_rect.topleft[1]])
        screen.blit(self.surface, self.surface_pos)
        screen.blit(self.name_surface, [self.surface_pos[0], self.surface_pos[1] - 20])