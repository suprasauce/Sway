from distutils.command.config import config
import math, os, neat, colors, pygame as py, constants, pickle
import sys
from entities.box import box as bx
from random import randint
from entities.end_point import end_point as ep
from entities.bob import bob as b
from visualize import draw_net, plot_species, plot_stats

py.init()

fps = constants.FPS
screen = py.display.set_mode()
screen_width, screen_height = py.display.get_surface().get_size()
clock = py.time.Clock()
runs_per_net = 10

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

def eval_genomes(genomes, config):

    pivot = (screen_width/4, screen_height/3)
    ep_x, ep_y = screen_width/4, screen_height/3 + 1.0

    bobs = []
    end_points = [] # end_points for the bobs
    nnets = [] # stores the nnet for the corresponding bob
    ge = []   # stores the genome for the corresponding bob
    dis = [] # stores the min distance of bob from box

    

    for genome_id, genome in genomes:
        genome.fitness = 0.0
        bobs.append(b(ep_x, ep_y))
        end_points.append(ep(ep_x, ep_y, pivot))
        ge.append(genome)
        dis.append(1000000.0)
        nnets.append(neat.nn.FeedForwardNetwork.create(genome, config))

    for runs in range(runs_per_net):

         # at 60 fps running one simulation for 20 seconds
        frames = 1200
        loop = True

        box = bx(5*screen_width/6, 0, screen_height)

        # reset the surviving bobs
        for bob in bobs:
            bob.reset(ep_x, ep_y)
            end_points[bobs.index(bob)].reset(ep_x, ep_y)
            dis[bobs.index(bob)] = 1000000.0

        while(loop and frames > 0):

            clock.tick(fps)
            screen.fill(colors.WHITE)
            for event in py.event.get():
                if event.type == py.QUIT:
                    loop = False
                
            # drawing the box updates its location too
            box.draw(screen)

            ''' 
            This loop handles all the movements of entities, check collisions, gives input 
            to the nnet and moves entities according to the output of nnet
            '''
            for bob in bobs[:]:
                # if goal is reached then we should not compute bob for the current frame
                if bob.goal_reached:
                    continue

                if bob.is_free: 
                    bob.move()
                    bob.goal_reached = bob.is_goal_reached(box)

                    distance = math.dist([bob.x, bob.y], box.center)
                    dis[bobs.index(bob)] = min(dis[bobs.index(bob)], distance)
                    
                    if bob.is_collision(screen_width, screen_height, box):
                        ge[bobs.index(bob)].fitness += 1.0/dis[bobs.index(bob)]
                        nnets.pop(bobs.index(bob))
                        end_points.pop(bobs.index(bob))
                        ge.pop(bobs.index(bob))
                        dis.pop(bobs.index(bob))
                        bobs.pop(bobs.index(bob))
                        continue
                        
                elif end_points[bobs.index(bob)].is_free:
            
                    # first move end_point and update bob pos
                    end_points[bobs.index(bob)].move()
                    bob.x, bob.y = end_points[bobs.index(bob)].x, end_points[bobs.index(bob)].y

                    distance = math.dist([bob.x, bob.y], box.center)
                    dis[bobs.index(bob)] = min(dis[bobs.index(bob)], distance)

                    if bob.is_collision(screen_width, screen_height, box):
                        ge[bobs.index(bob)].fitness += 1.0/dis[bobs.index(bob)]
                        nnets.pop(bobs.index(bob))
                        end_points.pop(bobs.index(bob))
                        ge.pop(bobs.index(bob))
                        dis.pop(bobs.index(bob))
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
                    # if we are here this means pendulum is not freed by nnet yet

                    # first get new inputs
                    inputs = get_inputs(bob, box, pivot, frames)

                    # second get nnet outputs
                    # outputs = [len_of_string, initial_angle, throw_angle, is_end_point_free], we have total 4 output nodes
                    outputs = nnets[bobs.index(bob)].activate(inputs)
                    
                    # third use the output to update

                    # length of string
                    end_points[bobs.index(bob)].length += 1.0 if outputs[0] >= 0.5 else 0.0
                    
                    # end_point initial_angle
                    end_points[bobs.index(bob)].theta1 += -1.0 if outputs[1] >= 0.5 else 0.0
                    
                    # penalize, if theta1 < -180 update fitness and erase
                    if end_points[bobs.index(bob)].theta1 <= -180.0:
                        nnets.pop(bobs.index(bob))
                        end_points.pop(bobs.index(bob))
                        ge.pop(bobs.index(bob))
                        dis.pop(bobs.index(bob))
                        bobs.pop(bobs.index(bob))
                        continue

                    # end_point throw_angle
                    bob.throw_angle += 1.0 if outputs[2] >= 0.5 else 0.0

                    # should i penalise throw_angle?
                    if bob.throw_angle >= 180.0:
                        nnets.pop(bobs.index(bob))
                        end_points.pop(bobs.index(bob))
                        ge.pop(bobs.index(bob))
                        dis.pop(bobs.index(bob))
                        bobs.pop(bobs.index(bob))
                        continue
                    
                    # update the pos of end_points[i]
                    end_points[bobs.index(bob)].reset_attributes()

                    # upate bob pos
                    bob.x, bob.y = end_points[bobs.index(bob)].x, end_points[bobs.index(bob)].y
                        
                    # penalize if bob out of screen and if so then erase
                    if bob.is_collision(screen_width, screen_height, box):
                        nnets.pop(bobs.index(bob))
                        end_points.pop(bobs.index(bob))
                        ge.pop(bobs.index(bob))
                        dis.pop(bobs.index(bob))
                        bobs.pop(bobs.index(bob))
                        continue
                    
                    # if we should free the end_point
                    end_points[bobs.index(bob)].is_free = True if outputs[3] >= 0.5 else False
                    
                    if end_points[bobs.index(bob)].is_free is True:
                        
                        # should i penalise throw_angle?
                        if bob.throw_angle > abs(end_points[bobs.index(bob)].theta1):
                            nnets.pop(bobs.index(bob))
                            end_points.pop(bobs.index(bob))
                            ge.pop(bobs.index(bob))
                            dis.pop(bobs.index(bob))
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

            if len(bobs) == 0:
                loop = False           
            
            py.display.update()

        if len(bobs) == 0:
            break

        '''
        increment fitness by 1 as the bobs survived this run
        '''
        for bob in bobs[:]:
            if not bob.goal_reached:
                nnets.pop(bobs.index(bob))
                end_points.pop(bobs.index(bob))
                ge.pop(bobs.index(bob))
                dis.pop(bobs.index(bob))
                bobs.pop(bobs.index(bob)) 
            else:
                ge[bobs.index(bob)].fitness += 1.0/dis[bobs.index(bob)]
            

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
    
    # Run for up to inf  generations.
    winner = p.run(eval_genomes, 60)

    best_five_genomes = stats.best_genomes(5)

    plot_stats(stats)
    plot_species(stats)

    with open("best_genome",'wb') as f:
        pickle.dump(winner, f)

    for i in range(5):
        with open(str(i+1), 'wb') as f:
            pickle.dump(best_five_genomes[i], f)


    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':

    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config_feedforward.txt')
    run(config_path)
    
        




