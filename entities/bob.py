import colors
import pygame as py
import game_constants as constants

class bob:
    def __init__(self, ep_x, ep_y):
        self.width = constants.BOB_WIDTH
        self.height = constants.BOB_HEIGHT
        self.color = colors.GREEN
        self.x, self.y = self.get_bob_pos(ep_x, ep_y)
        self.v_x, self.v_y = 0.0, 0.0

    def get_bob_pos(self,ep_x, ep_y):
        return [ep_x - self.width/2, ep_y]

    def get_rect(self):
        return py.Rect(self.x, self.y, self.width, self. height)

    def draw(self, screen, is_bob_free, ep_x = 0.0, ep_y = 0.0):
        if not is_bob_free:
            self.x, self.y = self.get_bob_pos(ep_x, ep_y)
        py.draw.rect(screen, self.color, self.get_rect())

    def set_parabolic_motion_initials(self, v_x, v_y):
        self.v_x, self.v_y = v_x, v_y

    def move(self):
        self.x += self.v_x
        self.y -= self.v_y
        self.v_y -= 0.8

    def is_collision(self):
        pass

    def is_goal_reached(self):
        pass