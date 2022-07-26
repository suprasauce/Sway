import math
from random import randint
import colors
import pygame as py
from random import randint
import constants 

class arc:
    def __init__(self, screen_size):
        self.center = [5.0*screen_size[0]/6.0, screen_size[1]/2.0]
        self.radius = randint(3.0*constants.BOB_WIDTH, screen_size[0]/6.0)
        #self.radius = 200.0
        self.color = colors.GREEN
        self.start_angle, self.stop_angle = self.get_initial_angles()
        #self.start_angle, self.stop_angle = math.radians(120.0), math.radians(60.0)
        self.mid_angle_pos = []
        self.start_angle_pos, self.stop_angle_pos = self.update_start_stop_pos() 
        self.angular_velocity = randint(10,20)/500
        self.surface = py.Surface((2*self.radius, 2*self.radius))
        self.surface.set_colorkey(colors.WHITE)
        # self.surface.fill(colors.WHITE)
        self.rect = self.surface.get_rect()
        arc.bobby = [self.center[0], self.center[1] - self.radius]

    # def get_rect(self):
    #     return self.surface.get_rect()

    def get_initial_angles(self):
        theta = 2*math.degrees(math.atan(constants.BOB_RADIUS/self.radius))
        new_stop_angle = math.radians(randint(0,360))
        new_start_angle = math.radians((math.degrees(new_stop_angle) + theta + randint(10,45))%360)
        return [new_start_angle, new_stop_angle]

    def rotate(self):
        self.start_angle = (self.angular_velocity + self.start_angle)%(math.pi*2)
        self.stop_angle = (self.angular_velocity + self.stop_angle)%(math.pi*2)

    def update_start_stop_pos(self):
        pos = []
        # for start_angle_pos
        if self.start_angle <= math.pi/2.0:
            x = self.center[0] + self.radius*math.cos(self.start_angle)
            y = self.center[1] - self.radius*math.sin(self.start_angle)
            pos.append([x, y])
        elif self.start_angle <= math.pi:
            y = self.center[1] - self.radius*math.sin(self.start_angle)
            x = self.center[0] + self.radius*math.cos(self.start_angle)
            pos.append([x, y])
        elif self.start_angle  <= math.pi + math.pi/2.0:
            x = self.center[0] + self.radius*math.cos(self.start_angle)
            y = self.center[1] - self.radius*math.sin(self.start_angle)
            pos.append([x, y])
        else:
            y = self.center[1] - self.radius*math.sin(self.start_angle)
            x = self.center[0] + self.radius*math.cos(self.start_angle)
            pos.append([x, y])
        
        # for stop_angle_pos
        if self.start_angle <= math.pi/2.0:
            x = self.center[0] + self.radius*math.cos(self.stop_angle)
            y = self.center[1] - self.radius*math.sin(self.stop_angle)
            pos.append([x, y])
        elif self.start_angle <= math.pi:
            y = self.center[1] - self.radius*math.sin(self.stop_angle)
            x = self.center[0] + self.radius*math.cos(self.stop_angle)
            pos.append([x, y])
        elif self.start_angle  <= math.pi + math.pi/2.0:
            x = self.center[0] + self.radius*math.cos(self.stop_angle)
            y = self.center[1] - self.radius*math.sin(self.stop_angle)
            pos.append([x, y])
        else:
            y = self.center[1] - self.radius*math.sin(self.stop_angle)
            x = self.center[0] + self.radius*math.cos(self.stop_angle)
            pos.append([x, y])

        mid_angle = math.acos(((pos[0][0] - self.center[0])*(pos[1][0] - self.center[0]) + (pos[0][1] - self.center[1])*(pos[1][1]-self.center[1]))/(self.radius)**2)
        # print(math.degrees(self.start_angle),end=" ")
        # print(math.degrees(self.stop_angle),end=" ")
        # print(math.degrees(mid_angle), end=" ")
        mid_angle /= 2.0
        mid_angle  = self.start_angle - mid_angle
        #print(math.degrees(mid_angle))
        if mid_angle < 0.0:
             mid_angle += 2.0*math.pi
        
        # for mid_angle_pos
        if mid_angle <= math.pi/2.0:
            x = self.center[0] + self.radius*math.cos(mid_angle)
            y = self.center[1] - self.radius*math.sin(mid_angle)
            self.mid_angle_pos = [x, y]
        elif mid_angle <= math.pi:
            y = self.center[1] - self.radius*math.sin(mid_angle)
            x = self.center[0] + self.radius*math.cos(mid_angle)
            self.mid_angle_pos = [x, y]
        elif mid_angle  <= math.pi + math.pi/2.0:
            x = self.center[0] + self.radius*math.cos(mid_angle)
            y = self.center[1] - self.radius*math.sin(mid_angle)
            self.mid_angle_pos = [x, y]
        else:
            y = self.center[1] - self.radius*math.sin(mid_angle)
            x = self.center[0] + self.radius*math.cos(mid_angle)
            self.mid_angle_pos = [x, y]

        self.start_angle_pos = pos[0]
        self.stop_angle_pos = pos[1]

        return pos

    def get_mask(self):
        return py.mask.from_surface(self.surface)

    # def create_and_get_new_surface(self):
    #     arc_surface = py.Surface((2*self.radius, 2*self.radius))
    #     arc_surface.fill(colors.WHITE)
    #     # set color_key of the surface to white such that all the white colored
    #     # pixels in that surface become transparent, this is useful when checking
    #     # if masks overlap or not, as non transparent pixel will be set to 1.
    #     arc_surface.set_colorkey(colors.WHITE)
    #     # rect necessary in order to draw an arc
    #     arc_rect = arc_surface.get_rect()
    #     py.draw.arc(arc_surface, self.color, arc_rect, self.start_angle, self.stop_angle,6)
    #     return arc_surface

    def draw(self, screen):
        #arc_surface = self.create_and_get_new_surface()
        self.surface.fill(colors.WHITE)
        py.draw.arc(self.surface, self.color, self.rect, self.start_angle, self.stop_angle,6)
        screen.blit(self.surface, (self.center[0]-self.radius,self.center[1] - self.radius))