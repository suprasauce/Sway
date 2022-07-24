import math
from random import randint
from numpy import pad
import colors
import pygame as py
from random import randint
import constants 

class arc:
    def __init__(self, screen_size):
        self.center = [5.0*screen_size[0]/6.0, screen_size[1]/2.0]
        self.radius = randint(2.0*constants.BOB_WIDTH, screen_size[0]/6.0)
        self.color = colors.GREEN
        self.start_angle, self.stop_angle = self.get_initial_angles()
        self.start_angle_pos, self.stop_angle_pos = self.update_start_stop_pos() 
        self.angular_velocity = randint(10,20)/500

    def get_rect(self):
        return py.Rect(self.center[0] - self.radius, self.center[1] - self.radius, 2*self.radius, 2*self.radius)

    def get_initial_angles(self):
        theta = 2*math.degrees(math.atan(constants.BOB_RADIUS/self.radius))
        new_stop_angle = math.radians(randint(0,360))
        new_start_angle = math.radians((math.degrees(new_stop_angle) + theta + randint(0,45))%360)
        return [new_start_angle, new_stop_angle]

    def rotate(self):
        self.start_angle = (self.angular_velocity + self.start_angle)%(math.pi*2)
        self.stop_angle = (self.angular_velocity + self.stop_angle)%(math.pi*2)

    def update_start_stop_pos(self):
        pass

    def draw(self, screen):
        py.draw.arc(screen, self.color, self.get_rect(), self.start_angle, self.stop_angle,6)