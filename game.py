import pygame as py, constants, colors, neat, os, pickle, math
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

def lets_play(num_bobs, mainnets):
    nnets = deepcopy(mainnets)
    bobs = []
    end_points = []
    
    loop = True
    frames = 1200
    pivot = (screen_width/4, screen_height/3)
    ep_x, ep_y = screen_width/4, screen_height/3 + 1.0
    box = bx(5*screen_width/6, 0, screen_height)

    for i in range(num_bobs):
        bobs.append(b(ep_x, ep_y))
        end_points.append(ep(ep_x, ep_y, pivot))

    while(loop):

        clock.tick(fps)
        screen.fill(colors.WHITE)
        for event in py.event.get():
            if event.type == py.QUIT:
                loop = False
            elif event.type == py.MOUSEBUTTONDOWN:
                pass
            elif event.type == py.MOUSEBUTTONUP:
                pass
            elif event.type == py.KEYDOWN:
                if event.key == py.K_SPACE:
                    pass

        # drawing the box updates its location too
        box.draw(screen)

        ''' 
        This loop handles movements of agent bobs
        '''
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
                    
        
        '''
        This for loop manages all the drawing stuff
        '''
        for bob in bobs:
            if not bob.goal_reached:
                bob.draw(screen)
                if not bob.is_free:
                    # draw string
                    py.draw.line(screen, colors.GREEN, pivot, [end_points[bobs.index(bob)].x, end_points[bobs.index(bob)].y],1)

        frames -= 1
        py.display.update()


def run_menu():
    lets_play(6, global_nnets)
    pass


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

    