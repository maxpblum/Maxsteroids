from __future__ import division
from ship import Ship, Laser, Asteroid, colliding
from math import pi
from random import randint
import pygame

SW = 600
SH = 600

BLACK = (   0,   0,   0)

clock = pygame.time.Clock()

pygame.init()
screen = pygame.display.set_mode((SW, SH))

dt = 0
done = False

arrowsdown = [False, False]
accel = False

my_ship = Ship((SW // 2, SH // 2), pi / 2, screen)
#my_laser = Laser((SW + 800, (SH // 2) - 200), -pi)
objs = [my_ship]

for i in range(randint(4, 8)):
    new_ast = Asteroid((randint(0, SW), randint(0, SH)), 0, screen)
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

    # colliding_indices = []
    # for i in range(len(objs)):
    #     for j in range(i + 1, len(objs)):
    #         if colliding( objs[i], objs[j] ):
    #             if type(objs[i]).__name__ == type(objs[j]).__name__ \
    #                 == 'Asteroid':
    #                 Asteroid.bounce(objs[i], objs[j])
    #             else:
    #                 for ind in (i, j):
    #                     if ind not in colliding_indices:
    #                         colliding_indices.append(ind)

    # for ind in colliding_indices:
    #     exp = objs[ind].explode()
    #     if exp:
    #         objs.extend(exp)

                # objs[i].v = [0, 0]
                # objs[j].v = [0, 0]

    i = 0
    while i < len(objs):
        if objs[i].inertia(dt) == 666:
            objs.pop(i)
        else:
            i += 1

    if accel:
        my_ship.accel(dt)

    if arrowsdown == [True, False]:
        my_ship.rotate_left(dt)
    elif arrowsdown == [False, True]:
        my_ship.rotate_right(dt)

    screen.fill(BLACK)

    [o.draw(screen) for o in objs]

    pygame.display.flip()

    # Get time in SECONDS
    dt = clock.tick(60) / 1000

pygame.quit()
