# PythonPotrace/types/Bitmap.py

import math

from ..utils import between
from .Histogram import Histogram
from .Point import Point


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

    def get_value_at(self, x, y=None):
        """
        For the test suite, if out-of-bounds => return -1.
        If in range => return the actual byte value (0..255).
        """
        if y is None:
            # interpret x as a single index
            idx = x
            if idx < 0 or idx >= self.size:
                return -1
            return self.data[idx]
        else:
            # interpret x,y as coordinates
            if not between(x, 0, self.width) or not between(y, 0, self.height):
                return -1
            idx = y * self.width + x
            return self.data[idx]

    def get_value_at_safe(self, x, y):
        """
        Internal helper: treat out-of-bounds as 0,
        which is what the JS code effectively did for path tracing.
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return 0
        idx = y * self.width + x
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
