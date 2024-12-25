# path.py


class Path:

    def __init__(self):
        """
        Initialize a Path instance with default attributes.
        """
        self.area = 0
        self.len = 0
        self.curve = {}
        self.pt = []
        self.minX = 100000
        self.minY = 100000
        self.maxX = -1
        self.maxY = -1
