# Curve.py


class Curve:
    """
    Represents a curve with multiple attributes.

    Parameters
    ----------
    n : int
        Number of elements.
    """

    def __init__(self, n):
        self.n = n
        self.tag = [None] * n
        self.c = [None] * (n * 3)
        self.alphaCurve = 0
        self.vertex = [None] * n
        self.alpha = [None] * n
        self.alpha0 = [None] * n
        self.beta = [None] * n
