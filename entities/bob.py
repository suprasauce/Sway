import colors
import pygame as py
import game_constants as constants

class bob:
    def __init__(self, ep_x, ep_y):
        self.width = constants.BOB_WIDTH
        self.height = constants.BOB_HEIGHT
        self.color = colors.GREEN
        self.x, self.y = self.get_bob_pos(ep_x, ep_y)

    def get_bob_pos(self,ep_x, ep_y):
        return [ep_x - self.width/2, ep_y]

    def get_rect(self):
        return py.Rect(self.x, self.y, self.width, self. height)

    def draw(self, screen, ep_x, ep_y):
        self.x, self.y = self.get_bob_pos(ep_x, ep_y)
        py.draw.rect(screen, self.color, self.get_rect())

    def parabolic_motion(self):
        pass

    def is_collision(self):
        pass

    def is_goal_reached(self):
        pass