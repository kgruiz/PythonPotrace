# Point.py


class Point:
    def __init__(self, x=0, y=0):
        """
        Initialize a Point instance.

        Parameters
        ----------
        x : float, optional
            X-coordinate, defaults to 0.
        y : float, optional
            Y-coordinate, defaults to 0.
        """
        self.x = x
        self.y = y

    def copy(self):
        """
        Create a copy of the current Point instance.

        Returns
        -------
        Point
            A new Point instance with the same coordinates.
        """
        return Point(self.x, self.y)
