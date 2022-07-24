import math
from random import randint
import constants


class end_point:
    def __init__(self, x, y, pivot):
        self.x, self.y = x, y
        self.pivot = pivot
        self.length = self.get_length()
        self.time = 0.0
        self.theta1 = math.radians(randint(-120,0))
        self.theta2 = math.radians(0.0)
        # self.theta1 = 0.0
        # self.theta2 = 0.0
        self.delta_time = constants.DELTA_TIME
        self.is_free = False # free from nnet hold

    def get_length(self):
        return math.dist([self.x, self.y],self.pivot)

    def move(self):
        self.time += self.delta_time
        d_theta2 = -((constants.B/constants.MASS)*self.theta2 + (constants.GRAVITY/self.length)*math.sin(self.theta1))
        self.theta2 += d_theta2*self.delta_time
        d_theta1 = self.theta2
        self.theta1 += d_theta1*self.delta_time
        self.x, self.y = self.get_new_pos()

    def get_new_pos(self):
        return [self.pivot[0] + self.length*math.sin(self.theta1), self.pivot[1] + self.length*math.cos(self.theta1)]

    def get_length(self):
        return round(math.dist([self.x, self.y], self.pivot))


    def get_angle(self):
        temp, sign = 0.0, 1
        if self.y < self.pivot[1]:
            temp = 180 if self.is_free else math.pi
            sign = -1
        if self.x < self.pivot[0]:
            temp *= -1.0
        return temp + sign*math.asin((self.x - self.pivot[0])/self.length)

    def reset_attributes(self, new_x = 0, new_y = 0):
        self.x, self.y = self.get_new_pos()
        # self.x, self.y = new_x, new_y
        # self.length = self.get_length()
        # self.time = 0.0
        # self.theta1 = self.get_angle()
        # self.theta2 = np.radians(0.0)

    
