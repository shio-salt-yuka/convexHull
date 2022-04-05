from which_pyqt import PYQT_VER
import numpy as np

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
# elif PYQT_VER == 'PYQT4':
# 	from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
    from PyQt6.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25


#
# This is the class you have to complete.
#
def slope(p1, p2):
    return (p1.y() - p2.y()) / (p1.x() - p2.x())


class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull

    def upper_left(self, left_hull, lut, rut):
        index = left_hull.index(lut)
        s0 = slope(lut, rut)  # Slope of lut, rut
        temp = left_hull[(index - 1)]
        # temp = left_hull[(index - 1) % len(left_hull)]  # candidate lut point
        s1 = slope(temp, rut)
        i = 1
        while s1 < s0:
        # while s1 > s0:
            lut = left_hull[(index - i)]
            i = i + 1
            s0 = s1
            k = (left_hull.index(lut) - 1)   # index of next lut candidate
            s1 = slope(left_hull[k], rut)  # slope of self[index - i] and rut
        return lut

    def upper_right(self, right_hull, lut, rut):
        index = right_hull.index(rut)
        s0 = slope(rut, lut)  # slope of lut and rut
        temp = right_hull[(index + 1) % len(right_hull)]
        s1 = slope(temp, lut)  # slope of lut and self[index + 1]
        j = 1
        while s1 > s0:
        # while s1 < s0:
            rut = right_hull[(index + j) % len(right_hull)]
            j = j + 1
            s0 = s1
            k = (right_hull.index(rut) + 1) % len(right_hull)  # index of next rut candidate
            s1 = slope(right_hull[k], lut)  # slope of self[index + j](new rut) and lut

        return rut

    def lower_left(self, left_hull, llt, rlt):
        index = left_hull.index(llt)
        s0 = slope(llt, rlt)
        temp = left_hull[(index + 1) % len(left_hull)]
        s1 = slope(temp, rlt)
        i = 1
        while s1 > s0:
        # while s1 < s0:
            llt = left_hull[(index + i) % len(left_hull)]
            i = i + 1
            s0 = s1
            k = (left_hull.index(llt) + 1) % len(left_hull)  # index of next llt candidate
            s1 = slope(left_hull[k], rlt)  # slope of self[index - i] and rlt
        return llt

    def lower_right(self, right_hull, llt, rlt):
        index = right_hull.index(rlt)
        s0 = slope(rlt, llt)
        # temp = right_hull[(index - 1) % len(right_hull)]
        temp = right_hull[index-1]
        s1 = slope(temp, llt)
        i = 1
        while s1 < s0:
        # while s1 > s0:
            # rlt = right_hull[(index - i) % len(right_hull)]
            rlt = right_hull[index-i]
            i = i + 1
            s0 = s1
            k = (right_hull.index(rlt) - 1)  # index of next rlt candidate
            s1 = slope(right_hull[k], llt)  # slope of self[index - i] and rlt
        return rlt

    def merge(self, left_hull, right_hull):
        # upper tangent
        lut = left_hull[np.argmax([p.x() for p in left_hull])]  # right most point of the left hull
        temp_lut = left_hull[np.argmax([p.x() for p in left_hull])]
        rut = right_hull[np.argmin([p.x() for p in right_hull])]  # left most point of the right hull
        temp_rut = right_hull[np.argmin([p.x() for p in right_hull])]
        lut = self.upper_left(left_hull, lut, rut)
        rut = self.upper_right(right_hull, lut, rut)

        while temp_lut != lut and temp_rut != rut:
            temp_lut = lut
            temp_rut = rut
            lut = self.upper_left(left_hull, lut, rut)
            rut = self.upper_right(right_hull, lut, rut)

        # lower
        llt = left_hull[np.argmax([p.x() for p in left_hull])]  # right most point of the left hull
        temp_llt = left_hull[np.argmax([p.x() for p in left_hull])]
        rlt = right_hull[np.argmin([p.x() for p in right_hull])]  # left most point of the right hull
        temp_rlt = right_hull[np.argmin([p.x() for p in right_hull])]
        llt = self.lower_left(left_hull, llt, rlt)
        rlt = self.lower_right(right_hull, llt, rlt)

        while temp_llt != llt and temp_rlt != rlt:
            temp_llt = llt
            temp_rlt = rlt
            llt = self.lower_left(left_hull, llt, rlt)
            rlt = self.lower_right(right_hull, llt, rlt)

        # clockwise
        final_hull = [lut, rut]
        rut_i = right_hull.index(rut)
        llt_i = left_hull.index(llt)

        index = (rut_i + 1) % len(right_hull)
        while right_hull[index] != rlt:
            final_hull.append(right_hull[index])
            index = (index + 1) % len(right_hull)

        final_hull.append(rlt)
        final_hull.append(llt)

        index = (llt_i + 1) % len(left_hull)
        while left_hull[index] != lut:
            final_hull.append(left_hull[index])
            index = (index + 1) % len(left_hull)

        result = []
        for i in final_hull:
            if i not in result:
                result.append(i)

        return result

    def convex_hull_solver(self, points):
        if len(points) == 1:
            return points

        median_index = len(points) // 2
        left = points[0:median_index]
        right = points[median_index:len(points)]
        # recursive call, until base case
        left_hull = self.convex_hull_solver(left)
        right_hull = self.convex_hull_solver(right)

        return self.merge(left_hull, right_hull)

    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        t1 = time.time()
        # TODO: SORT THE POINTS BY INCREASING X-VALUE
        # points.sort(key=lambda p: p.x())

        t2 = time.time()

        t3 = time.time()
        # this is a dummy polygon of the first 3 unsorted points
        # polygon = [QLineF(points[i], points[(i + 1) % 3]) for i in range(3)]
        # TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
        points.sort(key=lambda p: p.x())
        convex_hull = self.convex_hull_solver(points)
        polygon = [QLineF(convex_hull[i], convex_hull[(i + 1) % len(convex_hull)]) for i in range(len(convex_hull))]

        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4 - t3))
