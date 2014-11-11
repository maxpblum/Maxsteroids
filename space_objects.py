from __future__ import division
from math import sin, cos, atan, pi, copysign
import random
import pygame
import lines

ROUTE_THREE_OVER_TWO = (3 ** 0.5) / 2

#L_GRAY = ( 180, 180, 180)
WHITE  = ( 255, 255, 255)
L_GRAY = WHITE
YELLOW = ( 255, 255,   0)
BLUE   = (   0,   0, 255)
BLACK  = (   0,   0,   0)

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

def obj_rect_colliding(o1, o2):
    o1rects = o1.rect_list()
    o2rects = o2.rect_list()

    for o1r in o1rects:
        for o2r in o2rects:
            if rect_collision( o1r, o2r ):
                return True

    return False

def circ_colliding(o1, o2):
    if max(abs(o1.x - o2.x), abs(o1.y - o2.y)) > o1.radius + o2.radius:
        return False
    else:
        return True

def ray_test(point, segs):
    test_ray = lines.Ray([point[0] - 1, point[1]], point)
    isects = 0
    #isect_points = []
    for s in segs:
        i_p = s.Ray_isect(test_ray)
        if i_p:
            isects += 1
            #isect_points.append(i_p)

    if isects % 2 == 1:
        #isect_points.insert(0, point)
        return True

def colliding(o1, o2):

    if o1.exploding or o2.exploding:
        return False

    # If both are lasers, this is super easy
    if o1.particle and o2.particle:
        return o1.x == o2.x and o1.y == o2.y

    # See if they're even near each other
    if circ_colliding(o1, o2):

        pair = (o1, o2)

        # ----- SEE IF ONE IS A LASER --------

        for o, other in ((o1, o2), (o2, o1)):

            if o.particle:

                return ray_test( [ o.x, o.y ], other.line_segs() )

        # Ugh, test every point in each against the line segments in the other

        for o in (0, 1):

            for p in pair[o].points:

                if ray_test( p, pair[o - 1].line_segs() ):
                    return True

class Highlighter:
    def __init__(self, ray, points):
        self.ray = ray
        self.points = int_pointlist( points )

    def draw(self, surface, color=YELLOW):
        pygame.draw.line(surface, color, self.points[0], self.points[-1], 1)
        for p in self.points:
            pygame.draw.circle(surface, BLUE, p, 2)


class MaxShape(object):
    def __init__(self, loc, angle, surface, scale=1):
        self.x = loc[0]
        self.y = loc[1]
        self.angle = angle
        self.scale = scale
        self.surface = surface
        self.v = [0, 0]
        self.radius = self.RADIUS
        self.exploding = False

    def draw(self, surface, color):
        pass
        #pygame.draw.circle(surface, L_GRAY, int_point([self.x, self.y]), int(self.radius), 1)

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
        raise NotImplementedError
        pass

    def __rect__(self):
        raise NotImplementedError
        pass

   


class MaxPoly(MaxShape):
    def __init__(self, loc, angle, surface, scale=1):
        MaxShape.__init__(self, loc, angle, surface, scale)
        self.points = []
        self.particle = False

    def _move_points(self, x, y):
        self.points = [[p[0] + x, p[1] + y] for p in self.points]

    def move(self, x, y):
        super(MaxPoly, self).move(x, y)
        self._move_points(x, y)
        

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

    def __circ__(self):
        raise NotImplementedError
        pass

    def convex_points(self):
        return self.points[:]

    def normals(self):
        conp = self.convex_points()
        for i in range( len( conp ) ):
            yield vector( conp[i][1] - conp[i - 1][1],
                          conp[i - 1][0] - conp[i][0] )

    def line_segs(self):
        return [lines.Line_Seg( self.points[ i ],
                                self.points[ i - 1 ], ) 
                 for i in range(len(self.points)) ]

        # for a generator version:
        # for i in range(len(self.points)):
        #     yield lines.Line_Seg( self.points[ i ], 
        #                           self.points[ i - 1 ] )

    def bounce(o1, o2, m1=1, m2=1):

        oldvx1 = o1.v[0]
        oldvx2 = o2.v[0]
        oldvy1 = o1.v[1]
        oldvy2 = o2.v[1]

        newvx1 = (oldvx1 * (m1 - m2) +
                         oldvx2 * 2 * m2) / (m1 + m2)
        newvx2 = (oldvx2 * (m2 - m1) + 
                         oldvx1 * 2 * m1) / (m2 + m1)
        newvy1 = (oldvy1 * (m1 - m2) + 
                         oldvy2 * 2 * m2) / (m1 + m2)
        newvy2 = (oldvy2 * (m2 - m1) + 
                         oldvy1 * 2 * m1) / (m2 + m1)

        o1.v = [newvx1, newvy1]
        o2.v = [newvx2, newvy2]


class Laser(MaxShape):
    DEFAULT_SPEED = 500
    RADIUS = 1

    def __init__(self, loc, angle, surface, s = DEFAULT_SPEED, scale=1):
        MaxShape.__init__(self, loc, angle, surface, scale)
        self.speed = s
        self.v = rotate((self.speed, 0), self.angle)
        self.LIFESPAN = min(self.surface.get_width(),
                            self.surface.get_height()) * 0.9
        self.kill_after = self.LIFESPAN / self.speed
        self.life = 0
        self.particle = True

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
    RADIUS = 2 * SEG
    HYPERSPACE_LENGTH = 0.5

    def __init__(self, loc, angle, surface, scale=1):

        MaxPoly.__init__(self, loc, angle, surface, scale)

        self.angle += pi
        self.SEG *= self.scale
        self.__init_points__()

        self.explode_time = 0
        self.hyperspace_time = 0
        self.warping = False
        self.hyperspace_dx = surface.get_width() * 2
        self.hyperspace_dy = surface.get_height() * 2

        self.invis = False

    def __init_points__(self):
        ''' Top, bottom left, bottom right'''
        self.points = ([0, -2 * self.SEG], [-self.SEG, self.SEG],
                           [self.SEG, self.SEG])
        self._move_points(self.x, self.y)
        self.points = multi_rotate(self.points, self.angle, (self.x, self.y))

    def draw(self, surface, color=L_GRAY):
        if not self.invis:
            if not self.exploding:
                pygame.draw.polygon(surface, color, int_pointlist(self.points), 1)
            else:
                for d in int_pointlist( self.dots ):
                    pygame.draw.circle(surface, color, d, 0)
            MaxShape.draw(self, surface, color)

    def accel(self, dt):
        if not self.warping:
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
        if not (self.exploding or self.warping):
            MaxPoly.inertia(self, dt)
        elif self.warping and not self.exploding:
            if self.hyperspace_time > self.HYPERSPACE_LENGTH:
                new_x, new_y = (random.randrange(n) 
                          for n in (self.surface.get_width(), 
                                    self.surface.get_height()))
                self.move(new_x - self.x, new_y - self.y)
                self.rotate_right(random.random() * pi / self.__RSPEED__)
                self.warping = False
            else:
                self.hyperspace_time += dt
        else:
            assert self.exploding
            self.explode_time += dt
            if self.explode_time > self.EXPLODE_LENGTH:
                self.invis = True
                return 666
            angle_change = self.EXPLODE_ROTATION * dt
            self.dots = multi_rotate( self.dots, angle_change, [self.x, self.y] )

    def explode(self):
        MaxPoly.explode(self)
        self.v = [0, 0]
        self.dots = []
        for i in range(self.EXPLODE_DOTS):
            angle = (i / self.EXPLODE_DOTS) * (2 * pi)
            self.dots.append( rotate( (self.x + self.EXPLODE_RADIUS, self.y),
                                       angle, [self.x, self.y]) )

    def hyperspace(self):

        self.v = [0, 0]
        self.x += self.hyperspace_dx
        self.y += self.hyperspace_dy
        self._move_points(self.hyperspace_dx,
                          self.hyperspace_dy)
        self.warping = True
        self.hyperspace_time = 0

class Ufo(MaxPoly):
    SEG = 5
    WING_W = SEG
    WING_H = 8 * SEG
    CON_W = 2 * SEG
    CON_H = SEG
    CP_RAD = 2.4 * SEG
    CP_DY = ROUTE_THREE_OVER_TWO * CP_RAD
    WINDOW_RAD = 0.75 * CP_RAD
    WINDOW_DY = ROUTE_THREE_OVER_TWO * WINDOW_RAD
    WIDTH = (2 * WING_W) + (2 * CON_W) + (2 * CP_RAD)
    HEIGHT = WING_H
    RADIUS = (((WIDTH / 2) ** 2) + ((HEIGHT / 2) ** 2)) ** 0.5
    TIME_TO_CHANGE = 8
    AVG_FIRING_SPEED = 2
    SPEED = 100

    def __init__(self, loc, angle, surface, asteroids, good_guy, scale=1):
        super(Ufo, self).__init__(loc, angle, surface, scale)

        self.shapes = []
        self._set_points()
        self.asteroids = asteroids
        self.good_guy = good_guy
        self.set_v()
        self.time_since_dir_change = 0
        self.until_next_laser = self.time_to_next_laser()

    def random_v(self):
        return rotate((self.SPEED, 0), random.uniform(0, 2 * pi))

    def set_v(self):
        new_v = None
        while True:
            new_v = self.random_v()
            if not self.watch_out(new_v):
                self.v = new_v
                return None

    def watch_out(self, v):
        collision = False
        test_laser = Laser([self.x + v[0], self.y + v[1]], 0, self.surface)
        for a in self.asteroids:
            if colliding(test_laser, a):
                return True

    def _wing_points(self, cur_x):
        points = []

        points.append( [cur_x, self.y - self.WING_H / 2] )
        points.append( [cur_x, self.y + self.WING_H / 2] )

        cur_x += self.WING_W

        points.append( [cur_x, self.y + self.WING_H / 2] )
        points.append( [cur_x, self.y - self.WING_H / 2] )

        return points

    def _connector_points(self, cur_x):
        points = []

        points.append( [cur_x, self.y - self.CON_H / 2] )
        points.append( [cur_x, self.y + self.CON_H / 2] )

        cur_x += self.CON_W

        points.append( [cur_x, self.y + self.CON_H / 2] )
        points.append( [cur_x, self.y - self.CON_H / 2] )

        return points

    def _cockpit_points(self, cur_x):
        points = []

        points.append( [cur_x, self.y] )

        points.append( [cur_x, self.y + self.CON_H / 2] )

        cur_x += self.CP_RAD / 2
        points.append( [cur_x, self.y + self.CP_DY] )

        cur_x += self.CP_RAD
        points.append( [cur_x, self.y + self.CP_DY] )

        cur_x += self.CP_RAD / 2
        points.append( [cur_x, self.y] )
        # Now we're all the way on the right

        cur_x -= self.CP_RAD / 2
        points.append( [cur_x, self.y - self.CP_DY] )

        cur_x -= self.CP_RAD
        points.append( [cur_x, self.y - self.CP_DY] )

        cur_x -= self.CP_RAD / 2
        points.append( [cur_x, self.y - self.CON_H / 2] )

        return points

    def _window_points(self, cur_x):
        points = []

        points.append( [cur_x, self.y] )

        cur_x += self.WINDOW_RAD / 2
        points.append( [cur_x, self.y + self.WINDOW_DY] )

        cur_x += self.WINDOW_RAD
        points.append( [cur_x, self.y + self.WINDOW_DY] )

        cur_x += self.WINDOW_RAD / 2
        points.append( [cur_x, self.y] )
        # Now we're all the way on the right

        cur_x -= self.WINDOW_RAD / 2
        points.append( [cur_x, self.y - self.WINDOW_DY] )

        cur_x -= self.WINDOW_RAD
        points.append( [cur_x, self.y - self.WINDOW_DY] )

        return points

    def _set_points(self):

        self.shapes = []

        cur_x = self.x - (self.CP_RAD + self.CON_W + self.WING_W)

        self.shapes.append( self._wing_points(cur_x) )
        cur_x += self.WING_W

        self.shapes.append( self._connector_points(cur_x) )
        cur_x += self.CON_W

        self.shapes.append( self._cockpit_points(cur_x) )
        cur_x += (self.CP_RAD - self.WINDOW_RAD)

        # Now we update the window, which we don't use in collision detection
        self.window_points = self._window_points(cur_x)
        cur_x += self.WINDOW_RAD + self.CP_RAD

        self.shapes.append( self._connector_points(cur_x) )
        cur_x += self.CON_W

        self.shapes.append( self._wing_points(cur_x) )
        cur_x += self.WING_W

    def draw(self, surface, color=L_GRAY):
        
        for shape in self.shapes:
            pygame.draw.polygon(surface, color, int_pointlist(shape))

        pygame.draw.polygon(surface, BLACK, int_pointlist(self.window_points))

    def _move_points(self, x, y):
        for s in self.shapes:
            for p in s:
                p[0] += x
                p[1] += y

        for p in self.window_points:
            p[0] += x
            p[1] += y

    def outer_points(self):
        l_wing, l_con, cp, r_con, r_wing = self.shapes

        return [ l_wing[0], 
                 l_wing[1], 
                 l_wing[2], 
                 l_con[1],
                 l_con[2],
                 cp[2],
                 cp[3],
                 cp[4],
                 r_con[2],
                 r_wing[1],
                 r_wing[2],
                 r_wing[3],
                 r_wing[0],
                 r_con[3],
                 r_con[0],
                 cp[5],
                 cp[6],
                 l_con[3],
                 l_con[0],
                 l_wing[3] ]

    def line_segs(self):
        op = self.outer_points()

        return [lines.Line_Seg( op[ i ],
                                op[ i - 1 ], ) 
                 for i in range(len(op)) ]

        # segs = []
        # for shape in self.shapes:
        #     for i in range(len(shape)):
        #         segs.append( lines.Line_Seg( shape[i], shape[i - 1] ) )

        # return segs

    def inertia(self, dt):
        if self.exploding:
            return 666
        self.time_since_dir_change += dt
        self.until_next_laser -= dt
        if self.watch_out(self.v):
            self.set_v()
        if self.time_since_dir_change > self.TIME_TO_CHANGE:
            self.set_v()
            self.time_since_dir_change = 0
        super(Ufo, self).inertia(dt)
        if self.until_next_laser <= 0:
            self.until_next_laser = self.time_to_next_laser()
            return self.fire()


    def time_to_next_laser(self):
        return random.uniform(self.AVG_FIRING_SPEED * 0.6,
                              self.AVG_FIRING_SPEED * 1.4)

    def fire(self):
        distance = [self.good_guy.x - self.x,
                    self.good_guy.y - self.y]

        theta = atan(distance[1] / distance[0])

        if distance[0] < 0:
            theta += pi

        laser_spot = rotate([self.x + self.RADIUS, self.y], 
                            theta, [self.x, self.y])
        laser = Laser(laser_spot, theta, self.surface, Laser.DEFAULT_SPEED)
        laser.v = distance
        return laser

        


class Asteroid(MaxPoly):
    SIDES = 6
    AVG_SIDE = 50
    AVG_CHILD_V = 10
    MAX_GENERATIONS = 4
    MIN_SIDES = 4
    RADIUS = 70
    CHILD_SCALE = 2/3

    def __init__(self, loc, angle, surface, generation=0, scale=1):
        self.RADIUS = Asteroid.RADIUS * ((self.CHILD_SCALE) ** generation)
        MaxPoly.__init__(self, loc, angle, surface, scale)
        self.generation = generation
        self.SIDES = max( self.MIN_SIDES, self.SIDES - self.generation )
        self.AVG_SIDE = Asteroid.AVG_SIDE * ((self.CHILD_SCALE) ** generation)
        self.turtle_rotate = (2 * pi) / self.SIDES
        self.turtledraw_points()
        self.fix_center()

    def bounce(ast1, ast2):
        m1 = 1 / (ast1.generation + 1)
        m2 = 1 / (ast2.generation + 1)

        MaxPoly.bounce(ast1, ast2, m1, m2)

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

    def convex_points(self):
        return self.points[:-1]

    def draw(self, surface, color=L_GRAY):
        pygame.draw.polygon(surface, WHITE, int_pointlist(self.points), 1)
        MaxShape.draw(self, surface, color)

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

            # -------- NEW SPOTS -----------------

            child_rad = self.radius * self.CHILD_SCALE
            child_spot = rotate( [ child_rad, 0 ], random.uniform(0, pi) )

            # ---------- MAKE NEW ASTEROIDS ------------------

            new_ast_1 = Asteroid( (self.x + child_spot[0], self.y + child_spot[1]), 0,
                                    self.surface, generation = self.generation + 1 )


            new_ast_2 = Asteroid( (self.x - child_spot[0], self.y - child_spot[1]), 0,
                                    self.surface, generation = self.generation + 1 )

            # ------------- VELOCITIES ------------------------

            multiplier = random.uniform(1, 2)

            new_ast_1.v = [ child_spot[0] * multiplier,  child_spot[1] * multiplier]
            new_ast_2.v = [-child_spot[0] * multiplier, -child_spot[1] * multiplier]

            return [new_ast_1, new_ast_2]

        else:
            return None

    def get_child_v(self):
        return [random.randint(-self.AVG_CHILD_V, self.AVG_CHILD_V),
                random.randint(-self.AVG_CHILD_V, self.AVG_CHILD_V)]


class Circle_Asteroid(Asteroid):
    RADIUS = 50
    VERTICES = 6

    def __init__(self, loc, angle, surface, generation=0, scale=1):
        self.RADIUS *= scale
        MaxPoly.__init__(self, loc, angle, surface, scale)
        self.convices = self.generate_vertices()
        self.points = self.convices[:]
        self._move_points(self.x, self.y)

    def generate_vertices(self):

        v = self.VERTICES
        angles = []
        total_angle = 0

        while v > 0:
            new_p = random.random() * (2 * pi - total_angle) / v
            total_angle += new_p
            angles.append(total_angle)
            v -= 1

        return [ rotate( (0, self.RADIUS), a ) for a in proportions ]

    def convex_points(self):
        return self.convices[:]


