from __future__ import division
from space_objects import Ship, Laser, Asteroid, colliding, circ_colliding
from math import pi
from random import randint
import pygame

SW = 600
SH = 600

BLACK = (   0,   0,   0)

MAX_DEAD_TIME = 2.5

clock = pygame.time.Clock()

pygame.init()
screen = pygame.display.set_mode((SW, SH))

dt = 0
done = False

arrowsdown = [False, False]
accel = False

my_ship = Ship((SW // 2, SH // 2), pi / 2, screen)
objs = [my_ship]
highlighters = []

for i in range(randint(4, 8)):
    new_ast = None
    while True:
        new_ast = Asteroid((randint(0, SW), randint(0, SH)), 0, screen)
        collision = False
        for o in objs:
            if circ_colliding(o, new_ast):
                collision = True
                break
        if not collision:
            break

    new_ast.v = [randint(-10, 10), randint(-10, 10)]
    objs.append(new_ast)

was_firing = False
fire_away = False
explode_ship = False

while not done:

    for e in pygame.event.get():

        if   e.type == pygame.KEYDOWN or e.type == pygame.KEYUP:

            newval = True if e.type == pygame.KEYDOWN else False

            if   e.key == pygame.K_LEFT:
                arrowsdown[0] = newval
            elif e.key == pygame.K_RIGHT:
                arrowsdown[1] = newval
            elif e.key == pygame.K_UP:
                accel = newval
            elif e.key == pygame.K_SPACE:
                fire_away = newval
            elif e.key == pygame.K_RETURN:
                explode_ship = newval

        elif e.type == pygame.QUIT:
            done = True
            break

    # ---------- ACT ON USER INPUT ----------------------------------

    if fire_away:
        exp = my_ship.fire()
        if exp:
            objs.append(exp)
        fire_away = False

    if explode_ship:
        for i in range(len(objs)):
            exp = objs[i].explode()
            if exp:
                objs.extend(exp)
        explode_ship = False



    # --------- DETECT COLLISIONS -----------------------------------

    explode_indices = []

    for i in range(len(objs)):

        for j in range(i + 1, len(objs)):

            includes_laser = True in [ isinstance( o, Laser ) for o in (objs[i], objs[j]) ]

            if includes_laser or not (objs[i].exploding or objs[j].exploding):

                c = colliding(objs[i], objs[j])

                if c:
                    pair = (objs[i], objs[j])

                    # If one thing is a laser, explode both things
                    if includes_laser:
                        explode_indices.extend( (i, j) )
                        break

                    # Elif one thing is a ship, explode only the ship
                    includes_ship = False
                    for x in (i, j):

                        if isinstance( objs[x], Ship):
                            explode_indices.append( x )
                        break
                    if includes_ship:
                        break

                    # Elif one thing is a UFO, explode only the UFO
                    # Elif both things are asteroids, Asteroid.bounce
                    if isinstance(objs[i], Asteroid) and isinstance(objs[j], Asteroid):

                        Asteroid.bounce(objs[i], objs[j])
                        break
                    # Else bounce, but this should never happen so we'll leave it out.

    for i in set(explode_indices):
        # objs[i].v = [0, 0]
        exp = objs[i].explode()
        if exp:
            objs.extend(exp)

    # ------ UPDATE POSITIONS -------------------------------------

    if my_ship.explode_time >= MAX_DEAD_TIME:

        new_ship = Ship( (SW // 2, SH // 2), pi / 2, screen )

        collision = False

        for o in objs:

            if circ_colliding( new_ship, o ):
                collision = True
                break

        if not collision:

            my_ship = new_ship
            objs.insert(0, my_ship)

    i = 0
    while i < len(objs):
        ship_updated = False
        rval = objs[i].inertia(dt)
        if objs[i] is my_ship:
            ship_updated = True
        if rval == 666:
            objs.pop(i)
        else:
            i += 1

    if not ship_updated:
        my_ship.inertia(dt)

    if accel:
        my_ship.accel(dt)

    if arrowsdown == [True, False]:
        my_ship.rotate_left(dt)
    elif arrowsdown == [False, True]:
        my_ship.rotate_right(dt)

    # ------------ DRAW --------------------------------------------

    screen.fill(BLACK)

    [o.draw(screen) for o in objs]
    [h.draw(screen) for h in highlighters]

    pygame.display.flip()

    # Get time in SECONDS
    dt = clock.tick(60) / 1000

pygame.quit()
