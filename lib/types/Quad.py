# Quad.py


class Quad:
    def __init__(self):
        """
        Initialize a Quad instance with default values.
        """
        self.data = [0] * 9  # Initializes a list with nine zeros

    def at(self, x, y):
        """
        Access the element at the specified position.

        Parameters
        ----------
        x : int
            Row index (0-based).
        y : int
            Column index (0-based).

        Returns
        -------
        int
            The value at the specified position.

        Raises
        ------
        IndexError
            If x or y is out of bounds.
        """
        index = x * 3 + y
        if 0 <= index < len(self.data):
            return self.data[index]
        else:
            raise IndexError("Quad index out of range")
