import pygame as py, constants, colors, neat, os, pickle, math, random
from entities.bob import bob as b
from entities.end_point import end_point as ep
from entities.box import box as bx
from copy import deepcopy

py.init()

fps = constants.FPS
screen = py.display.set_mode()
screen_width, screen_height = py.display.get_surface().get_size()
clock = py.time.Clock()

global_nnets= []

def get_normalised_inputs(inputs):
    xmin = min(inputs) 
    xmax=max(inputs)
    for i, x in enumerate(inputs):
        inputs[i] = (x-xmin) / (xmax-xmin)

    return inputs

def get_inputs(bob, box, pivot, frames):
    # total 12 inputs
    inputs = []
    inputs.append(bob.y)
    inputs.append(screen_height - bob.y)
    inputs.append(bob.x)
    inputs.append(screen_width - bob.x)
    inputs.append(box.center[1] - bob.y)
    inputs.append(box.center[0] - bob.x)
    inputs.append(pivot[1] - bob.y)
    inputs.append(pivot[0] - bob.x)
    inputs.append(box.vertical_vel*box.vel_dir)
    inputs.append(box.center[1])
    inputs.append(screen_height - box.center[1])
    inputs.append(frames)
    inputs = get_normalised_inputs(inputs)
    return inputs

def lets_play(num_bobs):
    nnets = []
    temp = deepcopy(global_nnets)
    random.shuffle(temp)
    for i in range(num_bobs):
        nnets.append(temp[i])
    
    del temp

    bobs = []
    end_points = []
    
    loop = True
    frames = 1200
    pivot = (screen_width/4, screen_height/3)
    ep_x, ep_y = screen_width/4, screen_height/3 + 1.0
    box = bx(5*screen_width/6, 0, screen_height)

    player_bob = b(ep_x, ep_y, colors.DARK_PURPLE)
    player_end_point = ep(ep_x, ep_y, pivot)
    player_mouse_down = False

    for i in range(num_bobs):
        bobs.append(b(ep_x, ep_y, colors.LIGHT_PURPLE))
        end_points.append(ep(ep_x, ep_y, pivot))

    while(loop):

        clock.tick(fps)
        screen.fill(colors.WHITE)
        for event in py.event.get():
            if event.type == py.QUIT:
                loop = False
            elif event.type == py.MOUSEBUTTONDOWN:
                player_mouse_down = True
                player_end_point.is_free = False
            elif event.type == py.MOUSEBUTTONUP:
                if player_mouse_down:
                    player_end_point.is_free = True
                player_mouse_down = False
            elif event.type == py.KEYDOWN:
                if event.key == py.K_SPACE:
                    player_bob.is_free = True
                    curr_velocity = player_end_point.theta2*player_end_point.length
                    curr_angle = player_end_point.theta1
                    v_x = curr_velocity*math.cos(curr_angle)
                    v_y = curr_velocity*math.sin(curr_angle)
                    player_bob.set_parabolic_motion_initials(1.2*v_x/constants.MASS, 1.2*v_y/constants.MASS)


        # drawing the box updates its location too
        box.draw(screen)

        # This loop handles movements of agent bobs
        for bob in bobs[:]:
        
            if bob.is_free: 
                bob.move()
                bob.goal_reached = bob.is_goal_reached(box)
                
                # remove if collision with the walls
                if bob.is_collision(screen_width, screen_height, box) or bob.goal_reached:
                    nnets.pop(bobs.index(bob))
                    end_points.pop(bobs.index(bob))
                    bobs.pop(bobs.index(bob))
                    continue
                    
            elif end_points[bobs.index(bob)].is_free:
        
                # first move end_point and update bob pos
                end_points[bobs.index(bob)].move()
                bob.x, bob.y = end_points[bobs.index(bob)].x, end_points[bobs.index(bob)].y

                # remove if collision with the walls    
                if bob.is_collision(screen_width, screen_height, box):
                    nnets.pop(bobs.index(bob))
                    end_points.pop(bobs.index(bob))
                    bobs.pop(bobs.index(bob))
                    continue
        
                # second check if we should free bob or not based on o/p of nnet
                if end_points[bobs.index(bob)].theta1 >= bob.throw_angle:
                    bob.is_free = True
                    curr_velocity = end_points[bobs.index(bob)].theta2*end_points[bobs.index(bob)].length
                    curr_angle = end_points[bobs.index(bob)].theta1
                    v_x = curr_velocity*math.cos(curr_angle)
                    v_y = curr_velocity*math.sin(curr_angle)
                    bob.set_parabolic_motion_initials(1.2*v_x/constants.MASS, 1.2*v_y/constants.MASS)

            else:
                # get inputs for the current agent
                inputs = get_inputs(bob, box, pivot, frames)
                # get outputs of the current agent
                outputs = nnets[bobs.index(bob)].activate(inputs)
                # length of string
                end_points[bobs.index(bob)].length += 1.0 if outputs[0] >= 0.5 else 0.0
                # end_point initial_angle
                end_points[bobs.index(bob)].theta1 += -1.0 if outputs[1] >= 0.5 else 0.0
                
                # remove if angle not in range
                if end_points[bobs.index(bob)].theta1 <= -180.0:
                    nnets.pop(bobs.index(bob))
                    end_points.pop(bobs.index(bob))
                    bobs.pop(bobs.index(bob))
                    continue

                # end_point throw_angle
                bob.throw_angle += 1.0 if outputs[2] >= 0.5 else 0.0

                # remove if angle not in range
                if bob.throw_angle >= 180.0:
                    nnets.pop(bobs.index(bob))
                    end_points.pop(bobs.index(bob))
                    bobs.pop(bobs.index(bob))
                    continue
                
                # update the pos of end_points[i]
                end_points[bobs.index(bob)].reset_attributes()

                # upate bob pos
                bob.x, bob.y = end_points[bobs.index(bob)].x, end_points[bobs.index(bob)].y
                    
                # remove if collision with wall
                if bob.is_collision(screen_width, screen_height, box):
                    nnets.pop(bobs.index(bob))
                    end_points.pop(bobs.index(bob))
                    bobs.pop(bobs.index(bob))
                    continue
                
                # if we should free the end_point
                end_points[bobs.index(bob)].is_free = True if outputs[3] >= 0.5 else False
                
                if end_points[bobs.index(bob)].is_free is True:
                    
                    # remove if throw_angle greater than initial release angle
                    if bob.throw_angle > abs(end_points[bobs.index(bob)].theta1):
                        nnets.pop(bobs.index(bob))
                        end_points.pop(bobs.index(bob))
                        bobs.pop(bobs.index(bob))
                        continue
                    
                    # convert degrees to radians
                    bob.throw_angle = math.radians(bob.throw_angle)
                    end_points[bobs.index(bob)].theta1 = math.radians(end_points[bobs.index(bob)].theta1)
                    end_points[bobs.index(bob)].theta2 = math.radians(0.0)
                    
        
        # This for loop manages all the drawing stuff
        for bob in bobs:
            if not bob.goal_reached:
                if not bob.is_free:
                    # draw string
                    py.draw.line(screen, colors.BLACK, pivot, [end_points[bobs.index(bob)].x, end_points[bobs.index(bob)].y],4)
                bob.draw(screen)
        

        
        # This handles players_bob
        if player_bob.is_free:
            player_bob.move()
        else:
            if player_end_point.is_free:
                player_end_point.move()
                player_bob.x, player_bob.y = player_end_point.x, player_end_point.y
            elif player_mouse_down:
                player_end_point.player_reset_attributes(py.mouse.get_pos())
                player_bob.x, player_bob.y = player_end_point.x, player_end_point.y

        # check players collision with walls
        if player_bob.is_collision(screen_width, screen_height, box):
            loop = False
        # check if player hit box
        if player_bob.is_goal_reached(box):
            player_bob.goal_reached = True
            loop = False

        # after checking all collisions drawing of player happens
        if not player_bob.is_free:
            py.draw.line(screen, colors.BLACK, pivot, [player_end_point.x, player_end_point.y],4)
        
        player_bob.draw(screen)
        
        frames -= 1
        py.display.update()


def run_menu():
    num_agents = 1
    menu_loop = True
    font = py.font.Font('fav_font.ttf', 32)
    start = font.render("START", True, colors.RED)
    exit = font.render("EXIT", True, colors.RED)
    plus = font.render("+", True, colors.RED)
    minus = font.render("-", True, colors.RED)
    agents = font.render(str(num_agents) + " AGENTS", True, colors.DARK_PURPLE)
    start_rect = start.get_rect()
    exit_rect = exit.get_rect()
    plus_rect = plus.get_rect()
    minus_rect = minus.get_rect()
    agents_rect = agents.get_rect()
    start_rect.center = [screen_width/2, screen_height/2]
    exit_rect.center = [screen_width/2, screen_height/2 + 200]
    plus_rect.center = [screen_width/2 - 200, screen_height/2 + 100]
    minus_rect.center = [screen_width/2 + 200, screen_height/2 + 100]
    agents_rect.center = [screen_width/2, screen_height/2 + 100]
    start_high = False
    exit_high = False
    plus_high = False
    minus_high = False

    while menu_loop:
        clock.tick(fps)
        screen.fill(colors.WHITE)
        for event in py.event.get():
            if event.type == py.QUIT:
                menu_loop = False
            elif event.type == py.MOUSEBUTTONDOWN:
                if exit_high:
                    menu_loop = False
                elif start_high: 
                    lets_play(num_agents)
                elif plus_high:
                    num_agents = min(num_agents+1,6)
                elif minus_high:
                    num_agents = max(num_agents - 1, 1)

        # render the fonts
        start = font.render("START", True, colors.LIGHT_PURPLE if start_high else colors.DARK_PURPLE)
        exit = font.render("EXIT", True, colors.LIGHT_PURPLE if exit_high else colors.DARK_PURPLE)
        plus = font.render("+", True, colors.LIGHT_RED if plus_high or num_agents ==  6 else colors.RED)
        minus = font.render("-", True, colors.LIGHT_RED if minus_high or num_agents ==1 else colors.RED)
        agents = font.render(str(num_agents) + " AGENTS", True, colors.DARK_PURPLE)


        screen.blit(start, start_rect.topleft)
        screen.blit(exit, exit_rect.topleft)
        screen.blit(plus, plus_rect.topleft)
        screen.blit(minus, minus_rect.topleft)
        screen.blit(agents, agents_rect.topleft)

        if start_rect.collidepoint(py.mouse.get_pos()):
            start_high = True
        elif exit_rect.collidepoint(py.mouse.get_pos()): 
            exit_high = True
        elif plus_rect.collidepoint(py.mouse.get_pos()):
            plus_high = True
        elif minus_rect.collidepoint(py.mouse.get_pos()):
            minus_high = True
        else:
            start_high = False
            exit_high = False
            plus_high = False
            minus_high = False

        py.display.update()

def main():
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config_feedforward.txt')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    
    # adding my best 6 models to play against the human counterpart
    for i in range(6):
        with open("models/genomes/" + str(i+1),'rb') as f:
            genome = pickle.load(f)
            global_nnets.append(neat.nn.FeedForwardNetwork.create(genome, config))

    run_menu()

if __name__ == '__main__':
    main()

    