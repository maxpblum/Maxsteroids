from __future__ import division
from math import sin, cos, atan, pi, copysign
import random
import pygame

L_GRAY = ( 180, 180, 180)
WHITE  = ( 255, 255, 255)

def point_between(a, p, b):
    if (a[0] <= p[0] <= b[0] or a[0] >= p[0] >= b[0]) and \
       (a[1] <= p[1] <= b[1] or a[1] >= p[1] >= b[1]):
        return True
    else:
        return False

def rotate(point, theta, focus=[0,0]):
    x_pr = point[0] - focus[0]
    y_pr = point[1] - focus[1]

    new_x = x_pr * cos(theta) + y_pr * sin(theta) + focus[0]
    new_y = y_pr * cos(theta) - x_pr * sin(theta) + focus[1]

    return [new_x, new_y]

def multi_rotate(points, theta, focus):
    return map(lambda p: rotate(p, theta, focus), points)

def int_point(point):
    return [int(point[0]), int(point[1])]

def int_pointlist(pointlist):
    return map(int_point, pointlist)

def rect_collision(rect1, rect2):
    x_col = False
    y_col = False

    if (rect1[0] <= rect2[0] < (rect1[0] + rect1[2])) or \
       (rect2[0] <= rect1[0] < (rect2[0] + rect2[2])):
        x_col = True

    if (rect1[1] <= rect2[1] < (rect1[1] + rect1[3])) or \
       (rect2[1] <= rect1[1] < (rect2[1] + rect2[3])):
        y_col = True

    return (x_col and y_col)

def colliding(o1, o2):
    o1rects = o1.rect_list()
    o2rects = o2.rect_list()

    for o1r in o1rects:
        for o2r in o2rects:
            if rect_collision( o1r, o2r ):
                return True

    return False


class MaxShape(object):
    def __init__(self, loc, angle, surface, scale=1):
        self.x = loc[0]
        self.y = loc[1]
        self.angle = angle
        self.scale = scale
        self.surface = surface
        self.v = [0, 0]

    def draw(self, surface, color):
        pass

    def move(self, x, y):
        self.x += x
        self.y += y

        # Check for wrap
        if self.x > self.surface.get_width():
            self.move( -self.surface.get_width(), 0 )
        elif self.y > self.surface.get_height():
            self.move( 0, -self.surface.get_height() )
        elif self.x < 0:
            self.move( self.surface.get_width(), 0)
        elif self.y < 0:
            self.move( 0, self.surface.get_height() )

    def inertia(self, dt):
        self.move(self.v[0] * dt, self.v[1] * dt)

    def explode(self):
        pass

    def __rect__(self):
        pass

    def rect_list(self):
        return [self.__rect__()]

    def draw(self):
        pass
        # for r in self.rect_list():
        #     r_points = [ [r[0], r[1]], [r[0] + r[2], r[1]],
        #                  [r[0] + r[2], r[1] + r[3]], [r[0], r[1] + r[3]]  ]
        #     pygame.draw.polygon(self.surface, L_GRAY, r_points, 1)


class MaxPoly(MaxShape):
    def __init__(self, loc, angle, surface, scale=1):
        MaxShape.__init__(self, loc, angle, surface, scale)
        self.points = []
        self.exploding = False

    def __move_points__(self, x, y):
        self.points = [[p[0] + x, p[1] + y] for p in self.points]

    def move(self, x, y):
        self.__move_points__(x, y)
        MaxShape.move(self, x, y)

    def explode(self):
        self.exploding = True

    def __rect__(self):
        min_x = self.points[0][0] + 1
        min_y = self.points[0][1] + 1
        max_x = 0
        max_y = 0

        for p in self.points:
            if p[0] < min_x:
                min_x = p[0]
            if p[1] < min_y:
                min_y = p[1]
            if p[0] > max_x:
                max_x = p[0]
            if p[1] > max_y:
                max_y = p[1]

        return [min_x, min_y, max_x - min_x, max_y - min_y]

    def rect_list(self):
        rsize = 5
        rects = []
        for i in range(len(self.points)):
            cur_p = self.points[i]
            next_p = self.points[(i + 1) % len(self.points)]
            if next_p[0] == cur_p[0]:
                rects.append([cur_p[0] - rsize / 2, cur_p[1],
                             rsize, next_p[1] - cur_p[1]])
            else:
                slope = (next_p[1] - cur_p[1]) / (next_p[0] - cur_p[0])
                new_p = cur_p
                x_decreasing = (next_p[0] < cur_p[0])
                while (new_p[0] > next_p[0] if x_decreasing else new_p[0] < next_p[0]):
                    if x_decreasing:
                        rect_p = [new_p[0] - rsize]
                        rect_p.append(new_p[1] - rsize * slope)
                        rects.append([rect_p[0], rect_p[1], rsize, rsize * slope])
                        new_p = rect_p
                    else:
                        rects.append([new_p[0], new_p[1], rsize, rsize * slope])
                        new_p = [new_p[0] + rsize, new_p[1] + rsize * slope]
                if x_decreasing:
                    y_correction = next_p[1] - rects[-1][1]
                    rects[-1][1] += y_correction
                    rects[-1][3] -= y_correction
                else:
                    rects[-1][3] = next_p[1] - rects[-1][1]
        return rects

class Laser(MaxShape):
    DEFAULT_SPEED = 500
    RADIUS = 1

    def __init__(self, loc, angle, surface, v = DEFAULT_SPEED, scale=1):
        MaxShape.__init__(self, loc, angle, surface, scale)
        self.speed = v
        self.v = rotate((self.speed, 0), self.angle)
        self.LIFESPAN = min(self.surface.get_width(),
                            self.surface.get_height()) * 0.9
        self.kill_after = self.LIFESPAN / self.speed
        self.life = 0

    def inertia(self, dt):
        MaxShape.inertia(self, dt)
        self.life += dt
        if self.life > self.kill_after:
            return 666

    def draw(self, surface, color=WHITE):
        pygame.draw.circle(surface, WHITE, int_point((self.x, self.y)), self.RADIUS)

    def __rect__(self):
        return [self.x, self.y, 2 * self.RADIUS, 2 * self.RADIUS]

    def explode(self):
        self.kill_after = -1


class Ship(MaxPoly):

    # segment to be used as 1/3 of short side,
    # 1/4 of long side
    SEG = 8
    __RSPEED__ = 3
    ACCEL = 50
    EXPLODE_LENGTH = 1
    EXPLODE_DOTS = 8
    EXPLODE_RADIUS = 0.75 * SEG
    EXPLODE_ROTATION = 2

    def __init__(self, loc, angle, surface, scale=1):

        MaxPoly.__init__(self, loc, angle, surface, scale)

        self.angle += pi
        self.SEG *= self.scale
        self.__init_points__()

    def __init_points__(self):
        ''' Top, bottom left, bottom right'''
        self.points = ([0, -2 * self.SEG], [-self.SEG, self.SEG],
                           [self.SEG, self.SEG])
        self.__move_points__(self.x, self.y)
        self.points = multi_rotate(self.points, self.angle, (self.x, self.y))

    def draw(self, surface, color=L_GRAY):
        if not self.exploding:
            pygame.draw.polygon(surface, color, int_pointlist(self.points), 1)
        else:
            for d in int_pointlist( self.dots ):
                pygame.draw.circle(surface, color, d, 0)
        MaxShape.draw(self)

    def accel(self, dt):
        v_change = rotate((0, -self.ACCEL * dt), self.angle)
        self.v = [v_change[0] + self.v[0], v_change[1] + self.v[1]]

    def rotate_left(self, dt):
        angle_change = (dt * self.__RSPEED__)
        self.angle += angle_change
        self.points = multi_rotate(self.points, angle_change, (self.x, self.y))

    def rotate_right(self, dt):
        angle_change = (dt * self.__RSPEED__)
        self.angle -= angle_change
        self.points = multi_rotate(self.points, -angle_change, (self.x, self.y))

    def fire(self):
        if self.exploding:
            return None
        point = rotate((0, -((2 * self.SEG) + 5 )), self.angle)
        return Laser((self.x + point[0], self.y + point[1]), self.angle + (pi / 2), self.surface)

    def inertia(self, dt):
        if not self.exploding:
            MaxPoly.inertia(self, dt)
        else:
            self.explode_time += dt
            if self.explode_time > self.EXPLODE_LENGTH:
                return 666
            angle_change = self.EXPLODE_ROTATION * dt
            self.dots = multi_rotate( self.dots, angle_change, [self.x, self.y] )

    def explode(self):
        MaxPoly.explode(self)
        self.v = [0, 0]
        self.dots = []
        self.explode_time = 0
        for i in range(self.EXPLODE_DOTS):
            angle = (i / self.EXPLODE_DOTS) * (2 * pi)
            self.dots.append( rotate( (self.x + self.EXPLODE_RADIUS, self.y),
                                       angle, [self.x, self.y]) )


class Asteroid(MaxPoly):
    SIDES = 6
    AVG_SIDE = 50
    AVG_CHILD_V = 10
    MAX_GENERATIONS = 5
    MIN_SIDES = 4

    def __init__(self, loc, angle, surface, generation=0, scale=1):
        MaxPoly.__init__(self, loc, angle, surface, scale)
        self.generation = generation
        self.SIDES = max( self.MIN_SIDES, self.SIDES - self.generation )
        self.AVG_SIDE = Asteroid.AVG_SIDE * ((2/3) ** generation)
        self.turtle_rotate = (2 * pi) / self.SIDES
        self.turtledraw_points()
        self.fix_center()

    def bounce(ast1, ast2):
        m1 = 1 / (ast1.generation + 1)
        m2 = 1 / (ast2.generation + 1)

        oldvx1 = ast1.v[0]
        oldvx2 = ast2.v[0]
        oldvy1 = ast1.v[1]
        oldvy2 = ast2.v[1]

        newvx1 = (oldvx1 * (m1 - m2) + \
                         oldvx2 * 2 * m2) / (m1 + m2)
        newvx2 = (oldvx2 * (m2 - m1) + \
                         oldvx1 * 2 * m1) / (m2 + m1)
        newvy1 = (oldvy1 * (m1 - m2) + \
                         oldvy2 * 2 * m2) / (m1 + m2)
        newvy2 = (oldvy2 * (m2 - m1) + \
                         oldvy1 * 2 * m1) / (m2 + m1)

        ast1.v = [newvx1, newvy1]
        ast2.v = [newvx2, newvy2]

    def inertia(self, dt):
        if self.exploding:
            return 666
        else:
            MaxPoly.inertia(self, dt)

    def turtledraw_points(self):
        turtle = (self.x + (self.AVG_SIDE // 2), self.y + (self.AVG_SIDE // 2))
        turtle_angle = 0
        for i in range(self.SIDES):
            self.points.append(turtle)
            turtle_angle += self.turtle_rotate * (random.random() * 0.6 + 0.7) 
            turtle = rotate((self.AVG_SIDE + turtle[0], turtle[1]), turtle_angle, turtle)

        self.points.append( self.__add_crater__( self.points[-2],
                                                 self.points[-1],
                                                 self.points[0] ) )

    def draw(self, surface, color=L_GRAY):
        pygame.draw.polygon(surface, WHITE, int_pointlist(self.points), 1)
        # pygame.draw.circle(surface, WHITE, int_point((self.x, self.y)), 2)
        MaxShape.draw(self)

    def __add_crater__(self, p1, p2, p3):

        dy1 = p2[1] - p1[1]
        dx1 = p2[0] - p1[0]

        dy2 = p3[1] - p2[1]
        dx2 = p3[0] - p2[0]

        # Get the angles of the line segments
        theta1 = atan( dy1 / dx1 )
        theta2 = atan( dy2 / dx2 )

        # Test if dx < 0; add pi to theta if so (since the range of
        # atan is -pi/2 --> pi/2)
        if dx1 < 0:
            theta1 += pi
        if dx2 < 0:
            theta2 += pi

        # Find the angle p1p2p3
        d_theta = theta2 - theta1
        new_d_theta = random.uniform(d_theta / 4, d_theta / 3)
        new_theta = theta2 + new_d_theta

        # Find a point on the new crater line
        old_dist = min( dy1 ** 2 + dx1 ** 2,
                        dy2 ** 2 + dx2 ** 2 ) ** 0.5
        max_new_dist = (old_dist / 2) + (2 ** 0.5) * (2 * new_d_theta / pi)
        min_new_dist = old_dist / 2
        new_dist = random.uniform( min_new_dist, max_new_dist )

        new_point = rotate( (new_dist, 0), new_theta )
        new_point = [ new_point[0] + p2[0], new_point[1] + p2[1] ]

        return new_point

    def fix_center(self):
        r = self.__rect__()
        self.x = r[0] + r[2] / 2
        self.y = r[1] + r[3] / 2

    def explode(self):
        MaxPoly.explode(self)

        if self.generation < self.MAX_GENERATIONS:

            child_v_1 = [ random.uniform(-1.5 * self.AVG_CHILD_V, 1.5 * self.AVG_CHILD_V),
                          random.uniform(-1.5 * self.AVG_CHILD_V, 1.5 * self.AVG_CHILD_V) ]
            child_v_2 = [ random.uniform(-1.5 * self.AVG_CHILD_V, 1.5 * self.AVG_CHILD_V),
                          random.uniform(-1.5 * self.AVG_CHILD_V, 1.5 * self.AVG_CHILD_V) ]

            child_v_2 = [ copysign( child_v_2[0], -child_v_1[0] ),
                          copysign( child_v_2[1], -child_v_1[1] ) ]

            new_ast_1 = Asteroid( (self.x, self.y), 0,
                                    self.surface, generation = self.generation + 1 )

            new_ast_1.move( child_v_1[0] * 1.5, child_v_1[1] * 1.5)

            new_ast_2 = Asteroid( (self.x, self.y), 0,
                                    self.surface, generation = self.generation + 1 )

            new_ast_2.move( child_v_2[0] * 1.5, child_v_2[1] * 1.5)

            new_ast_1.v = child_v_1
            new_ast_2.v = child_v_2

            return [new_ast_1, new_ast_2]

        else:
            return None

    def get_child_v(self):
        return [random.randint(-self.AVG_CHILD_V, self.AVG_CHILD_V),
                random.randint(-self.AVG_CHILD_V, self.AVG_CHILD_V)]

# class Half_Asteroid(Asteroid):
#     SIDES = Asteroid.SIDES - 1
#     AVG_SIDE = Asteroid.AVG_SIDE / 2

# class Quarter_Asteroid(Half_Asteroid):
#     SIDES = Asteroid.SIDES - 1
#     AVG_SIDE = Asteroid.AVG_SIDE / 2

# class Eighth_Asteroid(Quarter_Asteroid):
#     AVG_SIDE = Quarter_Asteroid.AVG_SIDE / 2

# class Sixteenth_Asteroid(Eighth_Asteroid):
#     AVG_SIDE = Eighth_Asteroid.AVG_SIDE / 2
