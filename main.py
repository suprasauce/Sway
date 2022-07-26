import math, os, neat, colors, pygame as py, constants, pickle
from random import randint
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
    inputs.append(bob.y)
    inputs.append(screen_height - bob.y)
    inputs.append(bob.x)
    inputs.append(screen_width - bob.x)
    inputs.append(arc.start_angle_pos[1] - bob.y)
    inputs.append(arc.start_angle_pos[0] - bob.x)
    inputs.append(arc.stop_angle_pos[1] - bob.y)
    inputs.append(arc.stop_angle_pos[0] - bob.x)
    inputs.append(arc.center[1] - bob.y)
    inputs.append(arc.center[0] - bob.x)
    inputs.append(pivot[1] - bob.y)
    inputs.append(pivot[0] - bob.x)
    # adding two extra values, so now total 14 inputs
    inputs.append(arc.mid_angle_pos[1] - bob.y)
    inputs.append(arc.mid_angle_pos[0] - bob.x)
    return inputs

def eval_genomes(genomes, config):

    # at 60 fps running one simulation for 30 seconds
    frames = 1800
    loop = True
    # is_pen_free = True
    # is_bob_free = False
    pivot = (screen_width/4, screen_height/3)
    ep_x, ep_y = screen_width/4, screen_height/3 + 1.0
    arc = ar([screen_width, screen_height])

    bobs = []
    end_points = [] # end_points for the bobs
    nnets = [] # stores the nnet for the corresponding bob
    ge = []   # stores the genome for the corresponding bob

    

    for genome_id, genome in genomes:
        genome.fitness = -math.inf
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

        # drawing the obstacle
        arc.draw(screen)
        py.draw.line(screen,colors.RED,arc.center,arc.start_angle_pos)
        py.draw.line(screen,colors.RED,arc.center,arc.mid_angle_pos)
        py.draw.line(screen,colors.RED,arc.center,arc.stop_angle_pos)

        ''' 
        This loop handles all the movements of entities, check collisions, gives input 
        to the nnet and moves entities according to the output of nnet
        '''
        for bob in bobs[:]:
            if bob.is_free:
                bob.goal_reached = bob.is_goal_reached(arc.center, arc.radius)
                bob_a = math.dist([bob.x, bob.y], arc.center)**2
                bob_b = math.dist([bob.x, bob.y], arc.bobby)**2
                curr_fitness = 1.0 / bob_a + 1.0 / bob_b + bob.goal_reached*1.0*(1.0 / bob_a + math.sqrt(bob_b)) 

                ge[bobs.index(bob)].fitness = max(curr_fitness, ge[bobs.index(bob)].fitness)

                # # assign fitness
                # if bob.is_goal_reached(arc.center, arc.radius):
                #     # assign fitness
                #     ge[bobs.index(bob)].fitness = max(1.0/distance ,ge[bobs.index(bob)].fitness) + 50.0

                #     # erase 
                #     # nnets.pop(bobs.index(bob))
                #     # end_points.pop(bobs.index(bob))
                #     # ge.pop(bobs.index(bob))
                #     # bobs.pop(bobs.index(bob))
                #     # continue
                # else:
                #     ge[bobs.index(bob)].fitness = max(1.0/distance,ge[bobs.index(bob)].fitness)
                
                # first move
                bob.move()

                # penalize if bob out of screen and if so then erase
                if bob.is_collision(screen_width, screen_height, arc):
                    if not bob.goal_reached:
                        ge[bobs.index(bob)].fitness = -(1.0/ge[bobs.index(bob)].fitness)
                    nnets.pop(bobs.index(bob))
                    end_points.pop(bobs.index(bob))
                    ge.pop(bobs.index(bob))
                    bobs.pop(bobs.index(bob))
                    continue

                
                    
            elif end_points[bobs.index(bob)].is_free:
                
                # assign fitness as the bob was alive till the previous frame
                bob.goal_reached = bob.is_goal_reached(arc.center, arc.radius)
                bob_a = math.dist([bob.x, bob.y], arc.center)**2
                bob_b = math.dist([bob.x, bob.y], arc.bobby)**2
                curr_fitness = 1.0 / bob_a + 1.0 / bob_b + bob.goal_reached*1.0*(1.0 / bob_a + math.sqrt(bob_b)) 


                ge[bobs.index(bob)].fitness = max(curr_fitness, ge[bobs.index(bob)].fitness)           

                # first move end_point and update bob pos
                end_points[bobs.index(bob)].move()
                bob.x, bob.y = end_points[bobs.index(bob)].x, end_points[bobs.index(bob)].y


                # penalize if bob out of screen and if so then erase
                if bob.is_collision(screen_width, screen_height, arc):
                    ge[bobs.index(bob)].fitness = -(1.0/ge[bobs.index(bob)].fitness)
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
                    bob.set_parabolic_motion_initials(1.2*v_x/constants.MASS, 1.2*v_y/constants.MASS)

                

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
                end_points[bobs.index(bob)].theta1 += -1.0 if outputs[1] >= 0.5 else 0.0
                
                # penalize, if theta1 < -180 update fitness and erase
                if end_points[bobs.index(bob)].theta1 <= -180.0:
                    #ge[bobs.index(bob)].fitness *= 2.0
                    nnets.pop(bobs.index(bob))
                    end_points.pop(bobs.index(bob))
                    ge.pop(bobs.index(bob))
                    bobs.pop(bobs.index(bob))
                    continue

                # end_point throw_angle
                bob.throw_angle += 1.0 if outputs[2] >= 0.5 else 0.0

                # should i penalise throw_angle?
                if bob.throw_angle >= 180.0:
                    #ge[bobs.index(bob)].fitness *= 2.0
                    nnets.pop(bobs.index(bob))
                    end_points.pop(bobs.index(bob))
                    ge.pop(bobs.index(bob))
                    bobs.pop(bobs.index(bob))
                    continue
                
                # update the pos of end_points[i]
                end_points[bobs.index(bob)].reset_attributes()

                # upate bob pos
                bob.x, bob.y = end_points[bobs.index(bob)].x, end_points[bobs.index(bob)].y
                
                # penalize if bob out of screen and if so then erase
                if bob.is_collision(screen_width, screen_height, arc):
                    #ge[bobs.index(bob)].fitness *= 2.0
                    nnets.pop(bobs.index(bob))
                    end_points.pop(bobs.index(bob))
                    ge.pop(bobs.index(bob))
                    bobs.pop(bobs.index(bob))
                    continue
                
                # if we should free the end_point
                end_points[bobs.index(bob)].is_free = True if outputs[3] >= 0.5 else False
                
                if end_points[bobs.index(bob)].is_free is True:
                    
                    # should i penalise throw_angle?
                    if bob.throw_angle > abs(end_points[bobs.index(bob)].theta1):
                        #ge[bobs.index(bob)].fitness *= 2.0
                        nnets.pop(bobs.index(bob))
                        end_points.pop(bobs.index(bob))
                        ge.pop(bobs.index(bob))
                        bobs.pop(bobs.index(bob))
                        continue

                    # assign fitness as the bob was alive till the previous frame
                    bob.goal_reached = bob.is_goal_reached(arc.center, arc.radius)
                    bob_a = math.dist([bob.x, bob.y], arc.center)**2
                    bob_b = math.dist([bob.x, bob.y], arc.bobby)**2
                    curr_fitness = 1.0 / bob_a + 1.0 / bob_b + bob.goal_reached*1.0*(1.0 / bob_a + math.sqrt(bob_b)) 
 
                    ge[bobs.index(bob)].fitness = curr_fitness
                    
                    # convert degrees to radians
                    bob.throw_angle = math.radians(bob.throw_angle)
                    end_points[bobs.index(bob)].theta1 = math.radians(end_points[bobs.index(bob)].theta1)
                    end_points[bobs.index(bob)].theta2 = math.radians(0.0)

                # print(end_points[bobs.index(bob)].theta1)
                # print(len(bobs), end=" ")
                # print(len(ge))
                

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

        # update angles of the arc
        arc.rotate()
        arc.update_start_stop_pos()

        frames -= 1

        if len(bobs) == 0:
            loop = False

        # if not loop or frames == 0:
        #     for bob in bobs:
        #         if not end_points[bobs.index(bob)].is_free:
        #             ge[bobs.index(bob)].fitness = -math.inf
        
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
    winner = p.run(eval_genomes, 500)

    with open('model_2','wb') as files:
        pickle.dump(winner, files)

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))
        
def test(config_file):
 # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    loop = True
    pivot = (screen_width/4, screen_height/3)
    ep_x, ep_y = screen_width/4, screen_height/3 + 1.0

    bobs = []
    end_points = [] # end_points for the bobs

    arc = ar([screen_width, screen_height])
    
    for i in range(1):
        bobs.append(b(ep_x, ep_y))
        end_points.append(ep(ep_x, ep_y, pivot))
        #end_points[i].is_free = True
        #end_points[i].theta1 = math.radians(randint(-170.0, -60.0))
    

    with open('model', 'rb') as f:
        genome = pickle.load(f)
    model = neat.nn.FeedForwardNetwork.create(genome,config)  

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
                        bob.set_parabolic_motion_initials(1.2*v_x/constants.MASS, 1.2*v_y/constants.MASS)
        
        
        # for i, bob in enumerate(bobs):
        #     if not bob.is_free:
        #         end_points[i].move()
        #         bob.x, bob.y = end_points[i].x, end_points[i].y
        #     else:
        #         bob.move()

        arc.rotate()
        arc.update_start_stop_pos()
        arc.draw(screen)
        py.draw.line(screen,colors.RED,arc.center,arc.start_angle_pos)
        py.draw.line(screen,colors.RED,arc.center,arc.mid_angle_pos)
        py.draw.line(screen,colors.RED,arc.center,arc.stop_angle_pos)


        inputs = get_inputs(bobs[0],arc,pivot)

        outputs = model.activate(inputs)

        outputs = [0.0,0.0,0.0,0.0]
        if bobs[0].is_free:
            bobs[0].move()

        elif end_points[0].is_free:




                # first move end_point and update bob pos
                end_points[0].move()
                bobs[0].x, bobs[0].y = end_points[0].x, end_points[0].y


                
                # second check if we should free bob or not based on o/p of nnet
                if end_points[0].theta1 >= bobs[0].throw_angle:
                    bobs[0].is_free = True
                    curr_velocity = end_points[0].theta2*end_points[0].length
                    curr_angle = end_points[0].theta1
                    v_x = curr_velocity*math.cos(curr_angle)
                    v_y = curr_velocity*math.sin(curr_angle)
                    bobs[0].set_parabolic_motion_initials(1.2*v_x/constants.MASS, 1.2*v_y/constants.MASS)
        else:
            # length of string
            end_points[0].length += 1.0 if outputs[0] >= 0.5 else 0.0
                
                # end_point initial_angle
            end_points[0].theta1 += -1.0 if outputs[1] >= 0.5 else 0.0
                
                # end_point throw_angle
            bobs[0].throw_angle += 1.0 if outputs[2] >= 0.5 else 0.0

# update the pos of end_points[i]
            end_points[0].reset_attributes()

                # upate bob pos
            bobs[0].x, bobs[0].y = end_points[0].x, end_points[0].y

        # if we should free the end_point
            end_points[0].is_free = True if outputs[3] >= 0.5 else False


            if end_points[0].is_free:
                # convert degrees to radians
                print(bobs[0].throw_angle)
                print(end_points[0].theta1)
                bobs[0].throw_angle = math.radians(bobs[0].throw_angle)
                end_points[0].theta1 = math.radians(end_points[0].theta1)
                end_points[0].theta2 = math.radians(0.0)


        
        '''
        check for collisions of bob with arc, or walls
        '''
        for bob in bobs:
            if bob.is_goal_reached(arc.center, arc.radius):
                loop = False
            if bob.is_collision(screen_width, screen_height, arc):
                loop = False
        
        '''
        This for loop manages all the drawing stuff
        '''
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
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config_feedforward.txt')
    # test(config_path)
    run(config_path)
    # pp = [10,20,30,40,50]
    # yo = [11,21,31,41,51]
    # for i in pp[:]:
    #     if i is 30 or i is 50:
    #         yo.pop(pp.index(i))
    #         pp.pop(pp.index(i))
    #         continue
    #     print(len(pp), end=" ")
    #     print(i)
        
    # print(pp)
    # print(yo)
        




