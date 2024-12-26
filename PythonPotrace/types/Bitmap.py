# Bitmap.py

import math
from .Point import Point
from .Histogram import Histogram
from ..utils import between

class Bitmap:
    """
    Represents a bitmap where each pixel is a luminance value 0..255.
    """

    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.size = w * h
        self.data = bytearray(self.size)
        self._histogram = None

    def getValueAt(self, x, y=None):
        """
        If x is int and y not given, treat x as index.
        If x is int and y is given, treat x,y as coords.
        """
        if y is None:
            idx = x
        else:
            if not between(x, 0, self.width) or not between(y, 0, self.height):
                return 0
            idx = y * self.width + x
        if idx < 0 or idx >= self.size:
            return 0
        return self.data[idx]

    def indexToPoint(self, index):
        if not between(index, 0, self.size):
            return Point(-1, -1)
        row = index // self.width
        col = index % self.width
        return Point(col, row)

    def pointToIndex(self, x, y=None):
        if isinstance(x, Point):
            pt = x
            x_ = pt.x
            y_ = pt.y
        else:
            x_ = x
            y_ = y

        if not between(x_, 0, self.width) or not between(y_, 0, self.height):
            return -1
        return y_ * self.width + x_

    def copy(self, iterator=None):
        bm = Bitmap(self.width, self.height)
        if iterator:
            for i in range(self.size):
                bm.data[i] = iterator(self.data[i], i)
        else:
            bm.data[:] = self.data
        return bm

    def histogram(self):
        if self._histogram:
            return self._histogram
        self._histogram = Histogram(self)
        return self._histogram
