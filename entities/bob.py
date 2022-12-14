import math, colors, pygame as py, constants
import sys

class bob():
    def __init__(self, ep_x, ep_y, color):
        self.width = constants.BOB_WIDTH
        self.height = constants.BOB_HEIGHT
        self.color = color
        # the bob center will be endpoint_center
        self.x, self.y = ep_x, ep_y
        self.v_x, self.v_y = 0.0, 0.0
        self.is_free = False
        self.goal_reached = False
        self.throw_angle = 0.0
        self.surface = py.Surface((self.width, self.height))
        # self.rect = self.surface.get_rect(topleft = self.update_rect_pos(ep_x, ep_y))

    def reset(self, ep_x, ep_y):
        self.x, self.y = ep_x, ep_y
        self.is_free = False
        self.goal_reached = False
        self.throw_angle = 0.0
        self.v_x, self.v_y = 0.0, 0.0

    def draw(self, screen):
        # bob_surface = self.create_and_get_new_surface()
        self.surface.fill(self.color)
        screen.blit(self.surface, (self.x - self.width/2, self.y - self.height/2))

    def set_parabolic_motion_initials(self, v_x, v_y):
        self.v_x, self.v_y = v_x, v_y

    def move(self):
        self.x += self.v_x
        self.y -= self.v_y
        self.v_y -= 0.8

    def is_collision(self, screen_width, screen_height, box):
        # check collision with the 
        if self.x < self.width/2.0 or self.x > screen_width - self.width/2.0 or self.y < self.height/2.0 or self.y > screen_height - self.height/2.0:
            return True

    def is_goal_reached(self, box):
        bob_mask = py.mask.from_surface(self.surface)
        box_mask = box.get_mask()
        offset = (box.surface_pos[0] - self.x + self.width/2, box.surface_pos[1] - self.y + self.height/2)
        point = bob_mask.overlap(box_mask, offset)
        return True if point else False