import math, colors, pygame as py, constants

class bob():
    def __init__(self, ep_x, ep_y):
        self.width = constants.BOB_WIDTH
        self.height = constants.BOB_HEIGHT
        self.color = colors.GREEN
        # the bob center will be endpoint_center
        self.x, self.y = ep_x, ep_y
        self.v_x, self.v_y = 0.0, 0.0
        self.is_free = False
        self.throw_angle = 0.0
        self.surface = py.Surface((self.width, self.height))
        # self.rect = self.surface.get_rect(topleft = self.update_rect_pos(ep_x, ep_y))

    # def update_and_get_bob_pos(self,ep_x, ep_y):
    #     return (ep_x, ep_y)

    # def get_rect(self):
    #     return py.Rect(self.x, self.y, self.width, self. height)

    def draw(self, screen):
        # bob_surface = self.create_and_get_new_surface()
        self.surface.fill(colors.GREEN)
        screen.blit(self.surface, (self.x - self.width/2, self.y - self.height/2))

    def set_parabolic_motion_initials(self, v_x, v_y):
        self.v_x, self.v_y = v_x, v_y

    def move(self):
        # self.rect.x += self.v_x
        # self.rect.y -= self.v_y
        self.x += self.v_x
        self.y -= self.v_y
        self.v_y -= 0.8

    # def create_and_get_new_surface(self):
    #     # py.draw.rect(screen, self.color, self.rect)
    #     bob_surface = py.Surface((self.width, self.height))  
    #     # fill the surface with green color
    #     bob_surface.fill(self.color)
    #     return bob_surface

    def is_collision(self, screen_width, screen_height, arc):
        # check collision with the 
        if self.x < self.width/2.0 or self.x > screen_width - self.width/2.0 or self.y < self.height/2.0 or self.y > screen_height - self.height/2.0:
            return True
        
        # check collision with the obstacle
        #bob_surface = self.create_and_get_new_surface()
        bob_mask = py.mask.from_surface(self.surface)
        arc_mask = arc.get_mask()
        offset = (arc.center[0] - arc.radius - self.x + self.width/2, arc.center[1] - arc.radius - self.y + self.height/2)
        point = bob_mask.overlap(arc_mask, offset)
        return True if point else False

    def is_goal_reached(self, c, r):
        dist = round(math.dist([self.x, self.y], c))
        if dist <= r - math.sqrt(2)*self.height/2.0:
            return True
        else: 
            return False