from __future__ import division
from space_objects import Ship, Laser, Asteroid, Ufo, colliding, circ_colliding
from math import pi
from random import randint, uniform
import pygame


BLACK = (   0,   0,   0)
MAX_DEAD_TIME = 2.5
AVG_TIME_TO_UFO = 8


def new_ship(screen):
    SW = screen.get_width()
    SH = screen.get_height()
    return Ship((SW // 2, SH // 2), pi / 2, screen)


def make_asteroids(num, screen):

    SW = screen.get_width()
    SH = screen.get_height()

    asts = []

    for i in range(num):

        asts.append(Asteroid((randint(0, SW), randint(0, SH)), 
                      0, screen))

        asts[-1].v = [ randint(0, 15), randint(0, 15) ]


    return asts


def make_ufos(num, screen):

    SW = screen.get_width()
    SH = screen.get_height()

    ufos = []

    for i in range(num):

        ufos.append(Ufo((randint(0, SW), randint(0, SH)), 
                      0, screen))


    return ufos


def get_user_input(arrowsdown):
    fire_away = False
    hyperspace = False
    done = False

    for e in pygame.event.get():

        if   e.type == pygame.KEYDOWN or e.type == pygame.KEYUP:

            newval = True if e.type == pygame.KEYDOWN else False

            if   e.key == pygame.K_LEFT:
                arrowsdown[0] = newval
            elif e.key == pygame.K_RIGHT:
                arrowsdown[1] = newval
            elif e.key == pygame.K_UP:
                arrowsdown[2] = newval
            elif e.key == pygame.K_SPACE:
                fire_away = newval
            elif e.key == pygame.K_RETURN:
                hyperspace = newval

        elif e.type == pygame.QUIT:
            done = True

    return (fire_away, hyperspace, done)


def detect_collisions(my_ship, non_ship_objs):
    lasers, asteroids, ufos = non_ship_objs
    expl_ship = False
    expl_ast_list = []
    expl_laser_list = []
    expl_ufo_list = []

    # Check if lasers are destroying any asteroids or ufos

    for i in range(len(lasers)):

        if colliding(lasers[i], my_ship):

            expl_laser_list.append(i)
            expl_ship = True

        for j in range(len(asteroids)):

            if colliding(lasers[i], asteroids[j]):

                expl_laser_list.append(i)
                expl_ast_list.append(j)

        for j in range(len(ufos)):

            if colliding(lasers[i], ufos[j]):

                expl_laser_list.append(i)
                expl_ufo_list.append(j)

    # Check if our ship is hitting any non-laser objects
    for o in asteroids + ufos:

        if colliding( my_ship, o ):

            expl_ship = True

    # Check if any ufos are hitting asteroids or each other

    for i in range(len(ufos)):

        for j in range(len(asteroids)):

            if colliding( ufos[i], asteroids[j] ):

                expl_ufo_list.append(i)

        for j in range( i + 1, len(ufos) ):

            if colliding( ufos[i], ufos[j] ):

                expl_ufo_list.extend( (i, j) )

    exp_indices = (expl_laser_list, expl_ast_list, expl_ufo_list)

    if expl_ship:
        my_ship.explode()

    for things, things_to_splode in zip(non_ship_objs, exp_indices):
        blow_things_up( things, things_to_splode )


def blow_things_up(obj_list, indices):

    for i in set(indices):

        new_things = obj_list[i].explode()
        if new_things:
            obj_list.extend(new_things)
  

def next_ufo_time():

    return uniform(AVG_TIME_TO_UFO * 0.8, 
                   AVG_TIME_TO_UFO * 1.2)

def replace_my_ship(my_ship, non_ship_objs, screen):

    lasers, asteroids, ufos = non_ship_objs

    try_ship = new_ship(screen)

    collision = False

    for o in lasers + asteroids + ufos:

        if circ_colliding( try_ship, o ):
            collision = True
            return None

    if not collision:

        return try_ship


def update_ship(my_ship, arrowsdown, dt):

    my_ship.inertia(dt)

    if arrowsdown[2]:
        my_ship.accel(dt)

    if arrowsdown[0:2] == [True, False]:
        my_ship.rotate_left(dt)
    elif arrowsdown[0:2] == [False, True]:
        my_ship.rotate_right(dt)


def update_objs(non_ship_objs, dt):

    lasers = non_ship_objs[0]

    for l in non_ship_objs:

        i = 0
        while i < len(l):
            rval = l[i].inertia(dt)
            if rval == 666:
                l.pop(i)
            else:
                if isinstance(rval, Laser):
                    lasers.append(rval)
                i += 1


def game_loop(my_ship, non_ship_objs, screen, arrowsdown, 
              clock, dt, time_to_ufo):

    lasers, asteroids, ufos = non_ship_objs

    # ----------- GET USER INPUT ------------------------------------

    fire_away, hyperspace, done = get_user_input(arrowsdown)

    if done:
        return -1, None

    # ---------- FIRE! AND BLOW THINGS UP -------------------------

    if fire_away:
        laser = my_ship.fire()
        if laser:
            lasers.append(laser)
        fire_away = False

    if hyperspace:
        my_ship.hyperspace()
        hyperspace = False

    # ---------- DETECT COLLISIONS ----------------------------------       

    detect_collisions(my_ship, non_ship_objs)

    # ---------- TIME FOR A UFO? ----------------------------

    if time_to_ufo <= 0:

        ufos.append(Ufo((randint(0, screen.get_width()),
                         randint(0, screen.get_height())),
                        0, screen, asteroids, my_ship))

        time_to_ufo = next_ufo_time()

    # ------ UPDATE POSITIONS -------------------------------------

    update_ship(my_ship, arrowsdown, dt)

    time_to_ufo -= dt

    if my_ship.explode_time >= MAX_DEAD_TIME:

        replacement = replace_my_ship(my_ship, non_ship_objs, screen)

        if replacement:
            my_ship = replacement
            for u in ufos:
                u.good_guy = my_ship

    update_objs(non_ship_objs, dt)
    

    # ------------ DRAW --------------------------------------------

    screen.fill(BLACK)

    [o.draw(screen) for o in [my_ship] + lasers + asteroids + ufos]

    pygame.display.flip()

    # Get time in SECONDS
    return (clock.tick(60) / 1000, my_ship, time_to_ufo)


def one_play(players, SW, SH, screen):

    clock = pygame.time.Clock()

    dt = 0
    done = False

    arrowsdown = [False, False, False]

    my_ship = new_ship(screen)
    asteroids = make_asteroids(4, screen)
    #ufos = make_ufos(4, screen)
    ufos = []
    lasers = []
    non_ship_objs = (lasers, asteroids, ufos)
    time_to_ufo = next_ufo_time()

    while not done:

        dt, my_ship, time_to_ufo = game_loop(my_ship, non_ship_objs, screen, arrowsdown, 
                                clock, dt, time_to_ufo)
        if dt == -1:
            break

    pygame.quit()


def game_init(players=1, SW=1000, SH=700, fullscreen=False):

    pygame.init()

    mode = pygame.display.list_modes()[0]

    screen = None

    if fullscreen:
        screen = pygame.display.set_mode(mode, pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((SW, SH))

    one_play(players, SW, SH, screen)

if __name__ == '__main__':
    game_init()
