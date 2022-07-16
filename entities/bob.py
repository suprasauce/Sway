import colors
import pygame as py

class bob:
    def __init__(self, ep_x, ep_y):
        self.width = 24
        self.height = 24
        self.color = colors.GREEN
        self.x, self.y = self.get_bob_pos(ep_x, ep_y)

    def get_bob_pos(self,ep_x, ep_y):
        return [ep_x - self.width/2, ep_y]

    def draw(self, screen, ep_x, ep_y):
        self.x, self.y = self.get_bob_pos(ep_x, ep_y)
        py.draw.rect(screen, self.color, py.Rect(self.x, self.y, self.width, self.height))