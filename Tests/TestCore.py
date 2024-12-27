# TestCore.py

import shutil
import signal
import unittest

import numpy as np
from PIL import Image
from skimage import data

from PythonPotrace.types.Bitmap import Bitmap
from PythonPotrace.types.Histogram import Histogram


# Added timeout decorator
def timeout(seconds):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(
                f"Test '{func.__name__}' timed out after {seconds} seconds."
            )

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)

        return wrapper

    return decorator


class TestBitmap(unittest.TestCase):
    """
    Tests for the Bitmap class.

    This test suite verifies the correct initialization, pixel manipulation,
    copying functionality, and boundary conditions of the Bitmap class.
    """

    @timeout(10)
    def test_Initialization(self):
        """
        Test that a Bitmap initializes with correct width, height, and size.

        Raises
        ------
        AssertionError
            If the Bitmap's width, height, or size does not match expected values.
        """
        width, height = 10, 20
        bmp = Bitmap(width, height)
        self.assertEqual(bmp.width, width, "Bitmap width mismatch.")
        self.assertEqual(bmp.height, height, "Bitmap height mismatch.")
        self.assertEqual(bmp.size, width * height, "Bitmap size mismatch.")
        self.assertEqual(len(bmp.data), width * height, "Bitmap data length mismatch.")

    @timeout(10)
    def test_SetAndGetValue(self):
        """
        Test setting and retrieving pixel values in the Bitmap.

        Raises
        ------
        AssertionError
            If retrieved pixel values do not match the set values.
        """
        width, height = 5, 5
        bmp = Bitmap(width, height)
        # Set pixel values to their index
        for y in range(height):
            for x in range(width):
                idx = y * width + x
                bmp.data[idx] = idx * 10  # Arbitrary value assignment

        # Retrieve and verify pixel values
        for y in range(height):
            for x in range(width):
                idx = y * width + x
                expected_value = idx * 10
                actual_value = bmp.get_value_at(x, y)
                self.assertEqual(
                    actual_value,
                    expected_value,
                    f"Pixel value mismatch at ({x}, {y}). Expected {expected_value}, got {actual_value}.",
                )

    @timeout(10)
    def test_Copy(self):
        """
        Test that copying a Bitmap preserves all pixel data correctly.

        Raises
        ------
        AssertionError
            If the copied Bitmap's pixel data does not match the original.
        """
        width, height = 4, 4
        bmp_original = Bitmap(width, height)
        # Initialize original Bitmap with specific values
        for i in range(bmp_original.size):
            bmp_original.data[i] = i + 1  # Values from 1 to 16

        bmp_copy = bmp_original.copy()
        self.assertEqual(
            bmp_copy.width, bmp_original.width, "Copied Bitmap width mismatch."
        )
        self.assertEqual(
            bmp_copy.height, bmp_original.height, "Copied Bitmap height mismatch."
        )
        self.assertEqual(
            bmp_copy.size, bmp_original.size, "Copied Bitmap size mismatch."
        )
        self.assertEqual(
            list(bmp_copy.data), list(bmp_original.data), "Copied Bitmap data mismatch."
        )

    @timeout(10)
    def test_BoundaryConditions(self):
        """
        Test accessing pixels outside the Bitmap boundaries.

        Raises
        ------
        AssertionError
            If accessing out-of-bounds pixels does not return -1.
        """
        width, height = 3, 3
        bmp = Bitmap(width, height)
        # Accessing out-of-bounds should return -1
        self.assertEqual(
            bmp.get_value_at(-1, 0), -1, "Out-of-bounds access did not return -1."
        )
        self.assertEqual(
            bmp.get_value_at(0, -1), -1, "Out-of-bounds access did not return -1."
        )
        self.assertEqual(
            bmp.get_value_at(width, 0), -1, "Out-of-bounds access did not return -1."
        )
        self.assertEqual(
            bmp.get_value_at(0, height), -1, "Out-of-bounds access did not return -1."
        )

    @timeout(10)
    def test_BoundaryConditions(self):
        """
        Test accessing pixels outside the Bitmap boundaries.

        Raises
        ------
        AssertionError
            If accessing out-of-bounds pixels does not return -1.
        """
        width, height = 3, 3
        bmp = Bitmap(width, height)
        # Accessing out-of-bounds should return -1
        self.assertEqual(
            bmp.get_value_at(-1, 0), -1, "Out-of-bounds access did not return -1."
        )
        self.assertEqual(
            bmp.get_value_at(0, -1), -1, "Out-of-bounds access did not return -1."
        )
        self.assertEqual(
            bmp.get_value_at(width, 0), -1, "Out-of-bounds access did not return -1."
        )
        self.assertEqual(
            bmp.get_value_at(0, height), -1, "Out-of-bounds access did not return -1."
        )


class TestHistogram(unittest.TestCase):
    """
    Tests for the Histogram class.

    This test suite verifies the correct construction of histograms from Bitmap data,
    calculation of statistics, and thresholding functionality.
    """

    @timeout(10)
    def test_HistogramConstruction(self):
        """
        Test that Histogram correctly counts pixel values from a Bitmap.

        Raises
        ------
        AssertionError
            If the histogram does not accurately reflect the Bitmap's pixel data.
        """
        bmp = Bitmap(4, 1)
        bmp.data = bytearray([10, 20, 20, 30])  # Pixel values: 10, 20, 20, 30
        histogram = Histogram(bmp)

        expected_counts = {10: 1, 20: 2, 30: 1}
        for value in [10, 20, 30]:
            self.assertEqual(
                histogram.data[value],
                expected_counts[value],
                f"Histogram count mismatch for value {value}.",
            )

        # Ensure other values are zero
        for value in range(0, 256):
            if value not in expected_counts:
                self.assertEqual(
                    histogram.data[value],
                    0,
                    f"Histogram should have zero count for value {value}.",
                )

    @timeout(10)
    def test_GetStats(self):
        """
        Test that Histogram.getStats returns correct statistical values.

        Raises
        ------
        AssertionError
            If the calculated statistics do not match expected values.
        """
        bmp = Bitmap(5, 1)
        bmp.data = bytearray([0, 0, 255, 128, 128])  # Pixel values: 0, 0, 255, 128, 128
        histogram = Histogram(bmp)

        stats = histogram.getStats()
        self.assertEqual(stats["pixels"], 5, "Total pixel count mismatch.")
        self.assertEqual(stats["levels"]["unique"], 3, "Unique levels count mismatch.")
        self.assertAlmostEqual(
            stats["levels"]["mean"],
            (0 + 0 + 255 + 128 + 128) / 5,
            places=2,
            msg="Mean value mismatch.",
        )
        self.assertEqual(stats["levels"]["median"], 128, "Median value mismatch.")
        self.assertAlmostEqual(
            stats["levels"]["stdDev"],
            np.std([0, 0, 255, 128, 128], ddof=0),
            places=2,
            msg="Standard deviation mismatch.",
        )

    @timeout(20)
    def test_MultilevelThresholding(self):
        """
        Test that Histogram.multilevelThresholding correctly identifies thresholds.

        Raises
        ------
        AssertionError
            If the identified thresholds do not match expected values.
        """
        bmp = Bitmap(6, 1)
        bmp.data = bytearray(
            [10, 10, 50, 50, 200, 200]
        )  # Pixel values: 10,10,50,50,200,200
        histogram = Histogram(bmp)

        thresholds = histogram.multilevelThresholding(2)
        self.assertEqual(len(thresholds), 2, "Number of thresholds mismatch.")
        self.assertTrue(
            10 < thresholds[0] < 50, "First threshold out of expected range."
        )
        self.assertTrue(
            50 < thresholds[1] < 200, "Second threshold out of expected range."
        )

    @timeout(10)
    def test_GetDominantColor(self):
        """
        Test that Histogram.getDominantColor correctly identifies the most frequent color.

        Raises
        ------
        AssertionError
            If the dominant color does not match the expected value.
        """
        bmp = Bitmap(6, 1)
        bmp.data = bytearray(
            [10, 20, 20, 30, 30, 30]
        )  # Pixel values: 10,20,20,30,30,30
        histogram = Histogram(bmp)

        dominant = histogram.getDominantColor()
        self.assertEqual(dominant, 30, "Dominant color mismatch.")


if __name__ == "__main__":
    shutil.rmtree("./Input", ignore_errors=True)
    shutil.rmtree("./Output", ignore_errors=True)
    unittest.main(verbosity=2)
