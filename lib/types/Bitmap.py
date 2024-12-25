# Bitmap.py

from Point import Point
from utils import between
from Histogram import Histogram

class Bitmap:
    """
    Represents a bitmap with pixel values ranging from 0 to 255.

    Parameters
    ----------
    w : int
        Width of the bitmap.
    h : int
        Height of the bitmap.

    Attributes
    ----------
    width : int
        Width of the bitmap.
    height : int
        Height of the bitmap.
    size : int
        Total number of pixels.
    array_buffer : bytearray
        Byte array representing pixel data.
    data : bytearray
        Access to pixel data.
    """
    def __init__(self, w, h):
        self._histogram = None

        self.width = w
        self.height = h
        self.size = w * h
        self.array_buffer = bytearray(self.size)  # Equivalent to ArrayBuffer in JS
        self.data = self.array_buffer  # Accessing data as a bytearray

    def get_value_at(self, x, y=None):
        """
        Retrieve the pixel value at a specified position.

        Parameters
        ----------
        x : int or Point
            X-coordinate or a Point instance.
        y : int, optional
            Y-coordinate if x is an integer.

        Returns
        -------
        int
            Pixel value at the specified location.

        Raises
        ------
        IndexError
            If the index is out of bounds.
        """
        if isinstance(x, int) and y is None:
            index = x
        else:
            index = self.point_to_index(x, y)

        if 0 <= index < self.size:
            return self.data[index]
        else:
            raise IndexError("Index out of bounds.")

    def index_to_point(self, index):
        """
        Convert a linear index to a (x, y) coordinate.

        Parameters
        ----------
        index : int
            Linear index.

        Returns
        -------
        Point
            Corresponding Point instance.
        """
        if between(index, 0, self.size):
            y = index // self.width
            x = index - y * self.width
            return Point(x, y)
        else:
            return Point(-1, -1)

    def point_to_index(self, point_or_x, y=None):
        """
        Convert a Point or (x, y) coordinates to a linear index.

        Parameters
        ----------
        point_or_x : Point or int
            Point instance or x-coordinate.
        y : int, optional
            Y-coordinate if point_or_x is an integer.

        Returns
        -------
        int
            Linear index corresponding to the (x, y) coordinate.
        """
        if isinstance(point_or_x, Point):
            _x = point_or_x.x
            _y = point_or_x.y
        else:
            _x = point_or_x
            _y = y

        if not (between(_x, 0, self.width - 1) and between(_y, 0, self.height - 1)):
            return -1

        return self.width * _y + _x

    def copy(self, iterator=None):
        """
        Create a copy of the current bitmap.

        Parameters
        ----------
        iterator : callable, optional
            Function to process each pixel value.

        Returns
        -------
        Bitmap
            A new Bitmap instance.
        """
        bm = Bitmap(self.width, self.height)
        iterator_present = callable(iterator)

        for i in range(self.size):
            if iterator_present:
                bm.data[i] = iterator(self.data[i], i)
            else:
                bm.data[i] = self.data[i]

        return bm

    def histogram(self):
        """
        Generate and retrieve the histogram of the bitmap.

        Returns
        -------
        Histogram
            Histogram of the bitmap.
        """
        if self._histogram is not None:
            return self._histogram

        self._histogram = Histogram(self)
        return self._histogram
