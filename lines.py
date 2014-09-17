from __future__ import division

class Line:
    def __init__(self, p1, p2):
        if p1[0] == p2[0]:
            self.m = None
            self.x = p1[0]
        else:
            self.m = (p2[1] - p1[1]) / (p2[0] - p1[0])
            self.b = p1[1] - self.m * p1[0]

    def get_y(self, x):
        if self.m is not None:
            return self.m * x + self.b
        else:
            return 'inf'

    def get_x(self, y):
        if self.m:
            return (y - self.b) / self.m
        elif self.m == 0:
            return y == self.b
        else:
            return self.x

    def Line_isect(l1, l2):
        if l1.m == l2.m:
            if l1.m is not None and (l1.b == l2.b):
                # Both have a slope and the same y-intersect
                return 'inf'
            elif l1.m is None:
                if l1.x == l2.x:
                    # Both are vertical, same x
                    return 'inf'
                else:
                    # Both vertical, diff x
                    return None
            else:
                # Equal slope, diff y-intersect
                return None
        elif l1.m is None:
            return [l1.x, l2.get_y(l1.x)]
        elif l2.m is None:
            return [l2.x, l1.get_y(l2.x)]
        else:
            # Neither line vertical, and they definitely intersect
            isect_x = (l2.b - l1.b) / (l1.m - l2.m)
            isect_y = l1.get_y(isect_x)
            return [isect_x, isect_y]


class Ray(Line):
    def __init__(self, p1, p2):
        Line.__init__(self, p1, p2)
        if self.m is not None:
            self.x = p1[0]
            self.x_positive = (p2[0] - p1[0] > 0)
        else:
            self.x_positive = True

    def get_y(self, x):
        if (x - self.x >= 0) == self.x_positive:
            return Line.get_y(self, x)
        else:
            return None

    def get_x(self, y):
        x = Line.get_x(self, y)
        if (x - self.x >= 0) == self.x_positive:
            return x
        else:
            return None

    def Line_isect(r, l):
        p = Line.Line_isect(r, l)
        if p[1]:
            # This depends on my Line.Line_isect implementation,
            # which uses the get_y method of its first argument-line
            # (which is a ray here) to determine the y-coordinate of
            # intersection. So if it return None, the ray doesn't
            # exist there.
            return p
        else:
            return None

    def Ray_isect(r1, r2):
        p = Ray.Line_isect(r1, r2)
        if p and r2.get_y(p[0]):
            return p
        else: 
            return None

class Line_Seg(Line):
    def __init__(self, p1, p2):
        Line.__init__(self, p1, p2)
        self.min_x = min(p1[0], p2[0])
        self.max_x = max(p1[0], p2[0])
        self.min_y = min(p1[1], p2[1])
        self.max_y = max(p1[1], p2[1])

    def get_y(self, x):
        if self.min_x <= x <= self.max_x:
            return Line.get_y(self, x)
        else:
            return None

    def get_x(self, y):
        if self.min_y <= y <= self.max_y:
            return Line.get_x(self, y)
        else:
            return None

    def Ray_isect(seg, r):
        p = Ray.Line_isect(r, seg)
        if p and seg.min_x <= p[0] <= seg.max_x and \
           seg.min_y <= p[1] <= seg.max_y:
            return p
        else:
            return None
