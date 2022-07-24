import math, os, neat, colors, pygame as py, constants
from entities.end_point import end_point as ep
from entities.bob import bob as b
from entities.arc import arc as ar

py.init()

fps = constants.FPS
screen = py.display.set_mode()
screen_width, screen_height = py.display.get_surface().get_size()
clock = py.time.Clock()

def get_inputs(bob, arc, pivot):
    # total 12 inputs
    # [u_w, b_w, l_w, r_w, dy_start_bob, dx_start_bob, dy_stop_bob, dx_stop_bob, dy_obsatcle_bob, dx_obstacle_bob, dy_pivot_bob, dx_pivot_bob]    
    inputs = []
    inputs.append(bob.y - bob.height/2)
    inputs.append(screen_height - bob.y - bob.height/2)
    inputs.append(bob.x - bob.width/2)
    inputs.append(screen_width - bob.x - bob.width/2)
    inputs.append(arc.start_angle_pos[1] - bob.y)
    inputs.append(arc.start_angle_pos[0] - bob.x)
    inputs.append(arc.stop_angle_pos[1] - bob.y)
    inputs.append(arc.stop_angle_pos[0] - bob.x)
    inputs.append(arc.center[1] - bob.y)
    inputs.append(arc.center[0] - bob.x)
    inputs.append(pivot[1] - bob.y)
    inputs.append(pivot[0] - bob.x)
    return inputs

def eval_genomes(genomes, config):

    # at 60 fps running one simulation for 60 seconds
    frames = 3600
    loop = True
    # is_pen_free = True
    # is_bob_free = False
    pivot = (screen_width/4, screen_height/3)
    ep_x, ep_y = screen_width/4, 2*screen_height/3
    arc = ar([screen_width, screen_height])

    bobs = []
    end_points = [] # end_points for the bobs
    nnets = [] # stores the nnet for the corresponding bob
    ge = []   # stores the genome for the corresponding bob

    for genome_id, genome in genomes:
        genome.fitness = -1.0
        bobs.append(b(ep_x, ep_y))
        end_points.append(ep(ep_x, ep_y, pivot))
        ge.append(genome)
        nnets.append(neat.nn.FeedForwardNetwork.create(genome, config))

    while(loop and frames > 0):

        clock.tick(fps)
        screen.fill(colors.WHITE)
        for event in py.event.get():
            if event.type == py.QUIT:
                loop = False
            # elif event.type == py.MOUSEBUTTONDOWN:
            #     is_pen_free = False
            # elif event.type == py.MOUSEBUTTONUP:
            #     is_pen_free = True
            # elif event.type == py.KEYDOWN:
            #     if event.key == py.K_SPACE and not is_bob_free:
            #         is_bob_free = True
                    # curr_velocity = end_point.theta2*end_point.length
                    # curr_angle = end_point.theta1
                    # v_x = curr_velocity*math.cos(curr_angle)
                    # v_y = curr_velocity*math.sin(curr_angle)
                    # bob.set_parabolic_motion_initials(v_x/2, v_y/2)


        ''' 
        This loop handles all the movements of entities, check collisions, gives input 
        to the nnet and moves entities according to the output of nnet
        '''
        for bob in bobs:
            if bob.is_free:

                # assign fitness
                ge[bobs.index(bob)].fitness = 1.0/abs(bob.center, arc.center)
                
                # first move
                bob.move()

                # penalize if bob out of screen and if so then erase
                if bob.is_collision():
                    ge[bobs.index(bob)].fitness -= 1.0
                    nnets.pop(bobs.index(bob))
                    end_points.pop(bobs.index(bob))
                    ge.pop(bobs.index(bob))
                    bobs.pop(bobs.index(bob))
                    continue

                if bob.is_goal_reached(arc.center, arc.radius):
                    # assign fitness
                    ge[bobs.index(bob)].fitness = 1.0/abs(bob.center, arc.center) + 1.0

                    # erase 
                    nnets.pop(bobs.index(bob))
                    end_points.pop(bobs.index(bob))
                    ge.pop(bobs.index(bob))
                    bobs.pop(bobs.index(bob))
                    continue
                    
            elif end_points[bobs.index(bob)].is_free:
                
                # assign fitness as the bob was alive till the previous frame
                ge[bobs.index(bob)].fitness = 1.0/abs(bob.center, arc.center)                

                # first move end_point and update bob pos
                end_points[bobs.index(bob)].move()
                bob.x, bob.y = bob.get_bob_pos(end_points[bobs.index(bob)].x, end_points[bobs.index(bob)].y)


                # penalize if bob out of screen and if so then erase
                if bob.is_collision():
                    ge[bobs.index(bob)].fitness -= 1.0
                    nnets.pop(bobs.index(bob))
                    end_points.pop(bobs.index(bob))
                    ge.pop(bobs.index(bob))
                    bobs.pop(bobs.index(bob))
                    continue
                
                # second check if we should free bob or not based on o/p of nnet
                if end_points[bobs.index(bob)].theta1 >= bob.throw_angle:
                    bob.is_free = True
                    curr_velocity = end_points[bobs.index(bob)].theta2*end_points[bobs.index(bob)].length
                    curr_angle = end_points[bobs.index(bob)].theta1
                    v_x = curr_velocity*math.cos(curr_angle)
                    v_y = curr_velocity*math.sin(curr_angle)
                    bob.set_parabolic_motion_initials(v_x/2, v_y/2)

                

            else:
                # if we are here this means pendulum is not freed by nnet yet

                # first get new inputs
                inputs = get_inputs(bob, arc, pivot)

                # second get nnet outputs

                # outputs = [len_of_string, initial_angle, throw_angle, is_end_point_free], we have total 4 output nodes
                outputs = nnets[bobs.index(bob)].activate(inputs)
                
                # third use the output to update

                # length of string
                end_points[bobs.index(bob)].length += 1.0 if outputs[0] >= 0.5 else 0.0
                
                # end_point initial_angle
                end_points[bobs.index(bob)].theta1 += -0.5 if outputs[1] >= 0.5 else 0.0
                
                # penalize, if theta1 < -180 update fitness and erase
                if end_points[bobs.index(bob)].theta1 < -180.0:
                    nnets.pop(bobs.index(bob))
                    end_points.pop(bobs.index(bob))
                    ge.pop(bobs.index(bob))
                    bobs.pop(bobs.index(bob))
                    continue

                # end_point throw_angle
                bob.throw_angle += 0.5 if outputs[2] >= 0.5 else 0.0

                # should i penalise throw_angle?
                if bob.throw_angle > 180.0:
                    nnets.pop(bobs.index(bob))
                    end_points.pop(bobs.index(bob))
                    ge.pop(bobs.index(bob))
                    bobs.pop(bobs.index(bob))
                    continue
                
                # update the pos of end_points[i]
                end_points[bobs.index(bob)].reset_attributes()

                # upate bob pos
                bob.x, bob.y = bob.get_bob_pos(end_points[bobs.index(bob)].x, end_points[bobs.index(bob)].y)
                
                # penalize if bob out of screen and if so then erase
                if bob.is_collision():
                    nnets.pop(bobs.index(bob))
                    end_points.pop(bobs.index(bob))
                    ge.pop(bobs.index(bob))
                    bobs.pop(bobs.index(bob))
                    continue
                
                # if we should free the end_point
                end_points[bobs.index(bob)].is_free = True if outputs[3] >= 0.5 else 0.0
                
                if end_points[bobs.index(bob)].is_free is True:
                    
                    # should i penalise throw_angle?
                    if bob.throw_angle > abs(end_points[bobs.index(bob)].theta1):
                        nnets.pop(bobs.index(bob))
                        end_points.pop(bobs.index(bob))
                        ge.pop(bobs.index(bob))
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
            bob.draw(screen)
            if not bob.is_free:
                # draw string
                py.draw.line(screen, colors.GREEN, pivot, [end_points[bobs.index(bob)].x, end_points[bobs.index(bob)].y],1)
                 
                
        # if is_bob_free:
        #     bob.move()
        #     bob.draw(screen, is_bob_free=is_bob_free)
        # else:
        #     if is_pen_free:
        #         end_point.move()
        #     else:
        #         new_x, new_y = py.mouse.get_pos()
        #         end_point.reset_attributes(new_x, new_y)
        #     bob.draw(screen,  is_bob_free, end_point.x, end_point.y)
        #     py.draw.line(screen, colors.GREEN, pivot, [end_point.x, end_point.y],1)

        # updating and drawing the obstacle
        arc.rotate()
        arc.draw(screen)

        frames -= 1
        
        py.display.update()


def run(config_file):
    
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 100 generations.
    winner = p.run(eval_genomes, 100)

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))
        
def test():

    loop = True
    pivot = (screen_width/4, screen_height/3)
    ep_x, ep_y = screen_width/4, 2*screen_height/3

    bobs = []
    end_points = [] # end_points for the bobs
    
    for i in range(1):
        bobs.append(b(ep_x, ep_y))
        end_points.append(ep(ep_x, ep_y, pivot))
        end_points[i].is_free = True

    while(loop):

        clock.tick(fps)
        screen.fill(colors.WHITE)
        for event in py.event.get():
            if event.type == py.QUIT:
                loop = False
            elif event.type == py.KEYDOWN:
                 if event.key == py.K_SPACE:
                    for i, bob in enumerate(bobs):
                        end_points[i].is_free = False
                        bob.is_free = True
                        curr_velocity = end_points[bobs.index(bob)].theta2*end_points[bobs.index(bob)].length
                        curr_angle = end_points[bobs.index(bob)].theta1
                        v_x = curr_velocity*math.cos(curr_angle)
                        v_y = curr_velocity*math.sin(curr_angle)
                        bob.set_parabolic_motion_initials(v_x/2, v_y/2)
        
        '''
        This for loop manages all the drawing stuff
        '''
        for i, bob in enumerate(bobs):
            if not bob.is_free:
                end_points[i].move()
                bob.x, bob.y = bob.get_bob_pos(end_points[i].x, end_points[i].y)
            else:
                bob.move()

        for bob in bobs:
            bob.draw(screen)
            if not bob.is_free:
                # draw string
                py.draw.line(screen, colors.GREEN, pivot, [end_points[bobs.index(bob)].x, end_points[bobs.index(bob)].y],1)

        py.display.update()

    

if __name__ == '__main__':

    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    test()
    # local_dir = os.path.dirname(__file__)
    # config_path = os.path.join(local_dir, 'config-feedforward.txt')
    # run(config_path)



