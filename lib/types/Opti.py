# Opti.py

from Point import Point

class Opti:
    def __init__(self):
        """
        Initialize an Opti instance with default values.
        """
        self.pen = 0
        self.c = [Point(), Point()]
        self.t = 0
        self.s = 0
        self.alpha = 0
