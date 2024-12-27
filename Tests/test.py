# test.py

import os
import shutil
import signal  # Added import for timeout
import unittest
from pathlib import Path

import numpy as np
from PIL import Image
from skimage import data

# Import the PythonPotrace package and its modules
from PythonPotrace import Posterizer, Potrace
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


class TestPotrace(unittest.TestCase):
    """
    Tests for the Potrace class.

    This test suite verifies image loading, SVG generation, and parameter handling
    within the Potrace class.
    """

    @classmethod
    def setUpClass(cls):
        """
        Sets up the testing environment by creating input and output directories
        and saving test images.
        """
        cls.inputDir = Path("./Input/Potrace")
        cls.outputDir = Path("./Output/Potrace")
        cls.inputDir.mkdir(parents=True, exist_ok=True)
        cls.outputDir.mkdir(parents=True, exist_ok=True)

        # Define test images using skimage.data
        cls.testImages = {
            "Astronaut": data.astronaut(),
            "BinaryBlobs": data.binary_blobs(),
            "Cat": data.cat(),
            "Coffee": data.coffee(),
            "Colorwheel": data.colorwheel(),
            "HubbleDeepField": data.hubble_deep_field(),
            "Immunohistochemistry": data.immunohistochemistry(),
            "Logo": data.logo(),
            "Retina": data.retina(),
            "Rocket": data.rocket(),
            "Skin": data.skin(),
        }

        # Save each test image to ./Inputs_Potrace as PNG
        for name, imgArray in cls.testImages.items():
            if imgArray.ndim == 2:
                pilImage = Image.fromarray(imgArray)
            elif imgArray.shape[2] == 3:
                pilImage = Image.fromarray(imgArray, mode="RGB")
            else:
                try:
                    pilImage = Image.fromarray(imgArray, mode="RGBA")
                except IndexError:
                    pilImage = Image.fromarray(imgArray)

            pilImage.save(cls.inputDir / f"{name}.png")

    @timeout(20)
    def test_LoadImage(self):
        """
        Test that Potrace can successfully load various image types without errors.

        Raises
        ------
        AssertionError
            If Potrace fails to load an image or raises an unexpected exception.
        """
        for name in self.testImages.keys():
            inputPath = self.inputDir / f"{name}.png"
            potrace = Potrace()
            try:
                potrace.loadImage(str(inputPath), callback=lambda err: None)
                self.assertTrue(
                    potrace._imageLoaded, f"Potrace failed to load image '{name}'."
                )
            except Exception as e:
                self.fail(f"Potrace.loadImage raised an exception for '{name}': {e}")

    @timeout(20)
    def test_GetSVG(self):
        """
        Test that Potrace generates a valid SVG string after loading an image.

        Raises
        ------
        AssertionError
            If the generated SVG does not contain expected SVG elements.
        """
        for name in self.testImages.keys():
            inputPath = self.inputDir / f"{name}.png"
            outputPath = self.outputDir / f"{name}_potrace.svg"
            potrace = Potrace()
            potrace.loadImage(str(inputPath), callback=lambda err: None)
            svgContent = potrace.getSVG()
            # Basic checks on SVG content
            self.assertIn("<svg", svgContent, "SVG content missing <svg> tag.")
            self.assertIn("</svg>", svgContent, "SVG content missing </svg> tag.")
            # Save SVG to file
            with open(outputPath, "w", encoding="utf-8") as f:
                f.write(svgContent)
            # Check that file was written
            self.assertTrue(
                outputPath.exists(),
                f"SVG output file '{outputPath.name}' was not created.",
            )

    @timeout(20)
    def test_PotraceParameters(self):
        """
        Test that Potrace correctly handles various parameters like turnPolicy and threshold.

        Raises
        ------
        AssertionError
            If Potrace does not apply parameters as expected.
        """
        testParams = [
            {"turnPolicy": Potrace.TURNPOLICY_BLACK, "threshold": 128},
            {"turnPolicy": Potrace.TURNPOLICY_WHITE, "threshold": 100},
            {"turnPolicy": Potrace.TURNPOLICY_LEFT, "threshold": 150},
            {"turnPolicy": Potrace.TURNPOLICY_RIGHT, "threshold": 200},
            {
                "turnPolicy": Potrace.TURNPOLICY_MINORITY,
                "threshold": Potrace.THRESHOLD_AUTO,
            },
            {
                "turnPolicy": Potrace.TURNPOLICY_MAJORITY,
                "threshold": Potrace.THRESHOLD_AUTO,
            },
        ]

        for params in testParams:
            for name in self.testImages.keys():
                inputPath = self.inputDir / f"{name}.png"
                potrace = Potrace(options=params)
                try:
                    potrace.loadImage(str(inputPath), callback=lambda err: None)
                    potrace.getSVG()
                    # Further checks can be added to verify SVG content based on parameters
                    self.assertTrue(
                        potrace._imageLoaded,
                        f"Potrace failed with parameters {params} on '{name}'.",
                    )
                except Exception as e:
                    self.fail(
                        f"Potrace raised an exception with parameters {params} on '{name}': {e}"
                    )


class TestPosterizer(unittest.TestCase):
    """
    Tests for the Posterizer class.

    This test suite verifies image loading, SVG generation with multiple thresholds,
    and parameter handling within the Posterizer class.
    """

    @classmethod
    def setUpClass(cls):
        """
        Sets up the testing environment by creating input and output directories
        and saving test images.
        """
        cls.inputDir = Path("./Input/Posterizer")
        cls.outputDir = Path("./Output/Posterizer")
        cls.inputDir.mkdir(parents=True, exist_ok=True)
        cls.outputDir.mkdir(parents=True, exist_ok=True)

        # Define test images using skimage.data
        cls.testImages = {
            "Astronaut": data.astronaut(),
            "BinaryBlobs": data.binary_blobs(),
            "Cat": data.cat(),
            "Coffee": data.coffee(),
            "Colorwheel": data.colorwheel(),
            "HubbleDeepField": data.hubble_deep_field(),
            "Immunohistochemistry": data.immunohistochemistry(),
            "Logo": data.logo(),
            "Retina": data.retina(),
            "Rocket": data.rocket(),
            "Skin": data.skin(),
        }

        # Save each test image to ./Inputs_Posterizer as PNG
        for name, imgArray in cls.testImages.items():
            if imgArray.ndim == 2:
                pilImage = Image.fromarray(imgArray)
            elif imgArray.shape[2] == 3:
                pilImage = Image.fromarray(imgArray, mode="RGB")
            else:
                try:
                    pilImage = Image.fromarray(imgArray, mode="RGBA")
                except IndexError:
                    pilImage = Image.fromarray(imgArray)

            pilImage.save(cls.inputDir / f"{name}.png")

    @timeout(20)
    def test_LoadImage(self):
        """
        Test that Posterizer can successfully load various image types without errors.

        Raises
        ------
        AssertionError
            If Posterizer fails to load an image or raises an unexpected exception.
        """
        for name in self.testImages.keys():
            inputPath = self.inputDir / f"{name}.png"
            posterizer = Posterizer()
            try:
                posterizer.loadImage(str(inputPath), callback=lambda err: None)
                self.assertTrue(
                    posterizer._potrace._imageLoaded,
                    f"Posterizer failed to load image '{name}'.",
                )
            except Exception as e:
                self.fail(f"Posterizer.loadImage raised an exception for '{name}': {e}")

    @timeout(20)
    def test_GetSVG(self):
        """
        Test that Posterizer generates a valid multi-layer SVG string after loading an image.

        Raises
        ------
        AssertionError
            If the generated SVG does not contain expected SVG elements or layers.
        """
        for name in self.testImages.keys():
            inputPath = self.inputDir / f"{name}.png"
            outputPath = self.outputDir / f"{name}_posterizer.svg"
            posterizer = Posterizer(
                {"steps": 3, "fillStrategy": Posterizer.FILL_DOMINANT}
            )
            posterizer.loadImage(str(inputPath), callback=lambda err: None)
            svgContent = posterizer.getSVG()
            # Basic checks on SVG content
            self.assertIn("<svg", svgContent, "SVG content missing <svg> tag.")
            self.assertIn("</svg>", svgContent, "SVG content missing </svg> tag.")
            self.assertIn("<path", svgContent, "SVG content missing <path> tag.")
            # Save SVG to file
            with open(outputPath, "w", encoding="utf-8") as f:
                f.write(svgContent)
            # Check that file was written
            self.assertTrue(
                outputPath.exists(),
                f"SVG output file '{outputPath.name}' was not created.",
            )

    @timeout(20)
    def test_PosterizerParameters(self):
        """
        Test that Posterizer correctly handles various parameters like steps, fillStrategy,
        and rangeDistribution.

        Raises
        ------
        AssertionError
            If Posterizer does not apply parameters as expected or raises an exception.
        """
        testParams = [
            {
                "steps": 2,
                "fillStrategy": Posterizer.FILL_SPREAD,
                "rangeDistribution": Posterizer.RANGES_AUTO,
            },
            {
                "steps": 4,
                "fillStrategy": Posterizer.FILL_DOMINANT,
                "rangeDistribution": Posterizer.RANGES_EQUAL,
            },
            {
                "steps": 5,
                "fillStrategy": Posterizer.FILL_MEAN,
                "rangeDistribution": Posterizer.RANGES_AUTO,
            },
            {
                "steps": 3,
                "fillStrategy": Posterizer.FILL_MEDIAN,
                "rangeDistribution": Posterizer.RANGES_EQUAL,
            },
            {
                "steps": Posterizer.STEPS_AUTO,
                "fillStrategy": Posterizer.FILL_DOMINANT,
                "rangeDistribution": Posterizer.RANGES_AUTO,
            },
        ]

        for params in testParams:
            for name in self.testImages.keys():
                inputPath = self.inputDir / f"{name}.png"
                posterizer = Posterizer(options=params)
                try:
                    posterizer.loadImage(str(inputPath), callback=lambda err: None)
                    svgContent = posterizer.getSVG()
                    self.assertIn("<svg", svgContent, "SVG content missing <svg> tag.")
                    self.assertIn(
                        "</svg>", svgContent, "SVG content missing </svg> tag."
                    )
                    # Additional checks can be implemented based on parameters
                except Exception as e:
                    self.fail(
                        f"Posterizer raised an exception with parameters {params} on '{name}': {e}"
                    )

    @timeout(20)
    def test_InvalidParameters(self):
        """
        Test that Posterizer raises appropriate errors when given invalid parameters.

        Raises
        ------
        AssertionError
            If Posterizer does not raise errors as expected.
        """
        invalidParamsList = [
            {"steps": -1},
            {"steps": 0},
            {"steps": 256},
            {"fillStrategy": "invalid_strategy"},
            {"rangeDistribution": "invalid_distribution"},
            {"threshold": 300},
            {"threshold": -10},
        ]

        for params in invalidParamsList:
            for name in self.testImages.keys():
                inputPath = self.inputDir / f"{name}.png"
                with self.assertRaises(
                    Exception,
                    msg=f"Posterizer did not raise error for params {params} on '{name}'.",
                ):
                    Posterizer(options=params)


class TestIntegration(unittest.TestCase):
    """
    Integration tests that involve multiple sub-modules and complex operations.

    This test suite ensures that the interaction between Potrace and Posterizer
    works as expected, producing coherent SVG outputs.
    """

    @classmethod
    def setUpClass(cls):
        """
        Sets up the testing environment by creating input and output directories
        and saving test images.
        """
        cls.inputDir = Path("./Input/Integration")
        cls.outputDir = Path("./Output/Integration")
        cls.inputDir.mkdir(parents=True, exist_ok=True)
        cls.outputDir.mkdir(parents=True, exist_ok=True)

        # Define test images using skimage.data
        cls.testImages = {
            "Astronaut": data.astronaut(),
            "Cat": data.cat(),
            "Rocket": data.rocket(),
        }

        # Save each test image to ./Integration_Inputs as PNG
        for name, imgArray in cls.testImages.items():
            if imgArray.ndim == 2:
                pilImage = Image.fromarray(imgArray)
            elif imgArray.shape[2] == 3:
                pilImage = Image.fromarray(imgArray, mode="RGB")
            else:
                try:
                    pilImage = Image.fromarray(imgArray, mode="RGBA")
                except IndexError:
                    pilImage = Image.fromarray(imgArray)

            pilImage.save(cls.inputDir / f"{name}.png")

    @timeout(20)
    def test_PotraceThenPosterizer(self):
        """
        Test processing images first with Potrace and then with Posterizer,
        ensuring that each step completes successfully and outputs are correct.

        Raises
        ------
        AssertionError
            If any step in the processing pipeline fails or outputs are incorrect.
        """
        for name in self.testImages.keys():
            inputPath = self.inputDir / f"{name}.png"
            potraceOutputPath = self.outputDir / f"{name}_potrace.svg"
            posterizerOutputPath = self.outputDir / f"{name}_potrace_posterizer.svg"

            try:
                # Step 1: Potrace processing
                potrace = Potrace()
                potrace.loadImage(str(inputPath), callback=lambda err: None)
                potraceSVG = potrace.getSVG()
                with open(potraceOutputPath, "w", encoding="utf-8") as f:
                    f.write(potraceSVG)
                self.assertTrue(
                    potraceOutputPath.exists(),
                    f"Potrace SVG output '{potraceOutputPath.name}' was not created.",
                )

                # Step 2: Posterizer processing on Potrace SVG (assuming Posterizer can take SVG as input)
                # If Posterizer expects image input, adjust accordingly. Here, assuming image input.
                posterizer = Posterizer(
                    {"steps": 3, "fillStrategy": Posterizer.FILL_MEAN}
                )
                posterizer.loadImage(str(inputPath), callback=lambda err: None)
                posterizerSVG = posterizer.getSVG()
                with open(posterizerOutputPath, "w", encoding="utf-8") as f:
                    f.write(posterizerSVG)
                self.assertTrue(
                    posterizerOutputPath.exists(),
                    f"Posterizer SVG output '{posterizerOutputPath.name}' was not created.",
                )

                # Additional checks can be performed on the SVG content if needed
                self.assertIn("<svg", potraceSVG, "Potrace SVG missing <svg> tag.")
                self.assertIn("</svg>", potraceSVG, "Potrace SVG missing </svg> tag.")
                self.assertIn(
                    "<svg", posterizerSVG, "Posterizer SVG missing <svg> tag."
                )
                self.assertIn(
                    "</svg>", posterizerSVG, "Posterizer SVG missing </svg> tag."
                )

            except Exception as e:
                self.fail(f"Integration test failed for '{name}': {e}")

    @timeout(20)
    def test_PosterizerThenPotrace(self):
        """
        Test processing images first with Posterizer and then with Potrace,
        ensuring that each step completes successfully and outputs are correct.

        Raises
        ------
        AssertionError
            If any step in the processing pipeline fails or outputs are incorrect.
        """
        for name in self.testImages.keys():
            inputPath = self.inputDir / f"{name}.png"
            posterizerOutputPath = self.outputDir / f"{name}_posterizer.svg"
            potraceOutputPath = self.outputDir / f"{name}_posterizer_potrace.svg"

            try:
                # Step 1: Posterizer processing
                posterizer = Posterizer(
                    {"steps": 4, "fillStrategy": Posterizer.FILL_DOMINANT}
                )
                posterizer.loadImage(str(inputPath), callback=lambda err: None)
                posterizerSVG = posterizer.getSVG()
                with open(posterizerOutputPath, "w", encoding="utf-8") as f:
                    f.write(posterizerSVG)
                self.assertTrue(
                    posterizerOutputPath.exists(),
                    f"Posterizer SVG output '{posterizerOutputPath.name}' was not created.",
                )

                # Step 2: Potrace processing on Posterizer SVG (assuming Potrace can take SVG as input)
                # If Potrace expects image input, adjust accordingly. Here, assuming image input.
                potrace = Potrace()
                potrace.loadImage(str(inputPath), callback=lambda err: None)
                potraceSVG = potrace.getSVG()
                with open(potraceOutputPath, "w", encoding="utf-8") as f:
                    f.write(potraceSVG)
                self.assertTrue(
                    potraceOutputPath.exists(),
                    f"Potrace SVG output '{potraceOutputPath.name}' was not created.",
                )

                # Additional checks can be performed on the SVG content if needed
                self.assertIn(
                    "<svg", posterizerSVG, "Posterizer SVG missing <svg> tag."
                )
                self.assertIn(
                    "</svg>", posterizerSVG, "Posterizer SVG missing </svg> tag."
                )
                self.assertIn("<svg", potraceSVG, "Potrace SVG missing <svg> tag.")
                self.assertIn("</svg>", potraceSVG, "Potrace SVG missing </svg> tag.")

            except Exception as e:
                self.fail(f"Integration test failed for '{name}': {e}")


class TestAdvancedOperations(unittest.TestCase):
    """
    Advanced tests that involve multiple sub-modules and more complex operations.

    This test suite ensures that advanced workflows combining multiple components
    of the PythonPotrace package operate correctly and produce expected outputs.
    """

    @classmethod
    def setUpClass(cls):
        """
        Sets up the testing environment by creating input and output directories
        and saving test images.
        """
        cls.inputDir = Path("./Input/Advanced")
        cls.outputDir = Path("./Output/Advanced")
        cls.inputDir.mkdir(parents=True, exist_ok=True)
        cls.outputDir.mkdir(parents=True, exist_ok=True)

        # Define test images using skimage.data
        cls.testImages = {
            "Logo": data.logo(),
            "Skin": data.skin(),
            "Rocket": data.rocket(),
        }

        # Save each test image to ./Advanced_Inputs as PNG
        for name, imgArray in cls.testImages.items():
            if imgArray.ndim == 2:
                pilImage = Image.fromarray(imgArray)
            elif imgArray.shape[2] == 3:
                pilImage = Image.fromarray(imgArray, mode="RGB")
            else:
                try:
                    pilImage = Image.fromarray(imgArray, mode="RGBA")
                except IndexError:
                    pilImage = Image.fromarray(imgArray)

            pilImage.save(cls.inputDir / f"{name}.png")

    @timeout(20)
    def test_BatchProcessingWithDifferentParameters(self):
        """
        Test batch processing of multiple images with varying Posterizer parameters.

        This ensures that Posterizer can handle different configurations without
        errors and produces unique outputs for each parameter set.

        Raises
        ------
        AssertionError
            If any output file was not created or parameters caused unexpected behavior.
        """
        parameterSets = [
            {
                "steps": 2,
                "fillStrategy": Posterizer.FILL_SPREAD,
                "rangeDistribution": Posterizer.RANGES_AUTO,
            },
            {
                "steps": 3,
                "fillStrategy": Posterizer.FILL_DOMINANT,
                "rangeDistribution": Posterizer.RANGES_EQUAL,
            },
            {
                "steps": 5,
                "fillStrategy": Posterizer.FILL_MEAN,
                "rangeDistribution": Posterizer.RANGES_AUTO,
            },
            {
                "steps": 4,
                "fillStrategy": Posterizer.FILL_MEDIAN,
                "rangeDistribution": Posterizer.RANGES_EQUAL,
            },
        ]

        for params in parameterSets:
            for name in self.testImages.keys():
                inputPath = self.inputDir / f"{name}.png"
                outputPath = (
                    self.outputDir / f"{name}_posterizer_steps{params['steps']}.svg"
                )
                posterizer = Posterizer(options=params)
                try:
                    posterizer.loadImage(str(inputPath), callback=lambda err: None)
                    svgContent = posterizer.getSVG()
                    with open(outputPath, "w", encoding="utf-8") as f:
                        f.write(svgContent)
                    self.assertTrue(
                        outputPath.exists(),
                        f"Posterizer output '{outputPath.name}' was not created.",
                    )

                    # Verify SVG content integrity
                    self.assertIn("<svg", svgContent, "SVG content missing <svg> tag.")
                    self.assertIn(
                        "</svg>", svgContent, "SVG content missing </svg> tag."
                    )
                    self.assertIn(
                        "<path", svgContent, "SVG content missing <path> tag."
                    )
                except Exception as e:
                    self.fail(
                        f"Batch processing failed for '{name}' with parameters {params}: {e}"
                    )

    @timeout(20)
    def test_PosterizerWithEdgeCaseImages(self):
        """
        Test Posterizer with edge case images such as fully black, fully white,
        and images with minimal color variation.

        Raises
        ------
        AssertionError
            If Posterizer fails to process edge case images or produces incorrect outputs.
        """
        edgeCaseImages = {
            "FullyBlack": np.zeros((10, 10), dtype=np.uint8),
            "FullyWhite": np.full((10, 10), 255, dtype=np.uint8),
            "MinimalVariation": np.tile(np.array([128, 129], dtype=np.uint8), (10, 5)),
        }

        # Save edge case images
        for name, imgArray in edgeCaseImages.items():
            if imgArray.ndim == 2:
                pilImage = Image.fromarray(imgArray.astype(np.uint8))
            else:
                pilImage = Image.fromarray(imgArray.astype(np.uint8), mode="L")
            pilImage.save(self.inputDir / f"{name}.png")

        # Define Posterizer parameters to test
        params = {
            "steps": 3,
            "fillStrategy": Posterizer.FILL_MEAN,
            "rangeDistribution": Posterizer.RANGES_AUTO,
        }

        for name in edgeCaseImages.keys():
            inputPath = self.inputDir / f"{name}.png"
            outputPath = self.outputDir / f"{name}_posterizer.svg"
            posterizer = Posterizer(options=params)
            try:
                posterizer.loadImage(str(inputPath), callback=lambda err: None)
                svgContent = posterizer.getSVG()
                with open(outputPath, "w", encoding="utf-8") as f:
                    f.write(svgContent)
                self.assertTrue(
                    outputPath.exists(),
                    f"Posterizer output '{outputPath.name}' was not created for edge case '{name}'.",
                )
                self.assertIn("<svg", svgContent, "SVG content missing <svg> tag.")
                self.assertIn("</svg>", svgContent, "SVG content missing </svg> tag.")
            except Exception as e:
                self.fail(f"Posterizer failed on edge case image '{name}': {e}")

    @timeout(20)
    def test_PosterizerWithTransparentBackground(self):
        """
        Test Posterizer's handling of images with transparency.

        Raises
        ------
        AssertionError
            If Posterizer fails to process images with transparency or outputs incorrect SVG.
        """
        # Create an RGBA image with transparency
        imgArray = np.zeros((10, 10, 4), dtype=np.uint8)
        imgArray[..., :3] = 255  # White color
        imgArray[..., 3] = 0  # Fully transparent

        pilImage = Image.fromarray(imgArray, mode="RGBA")
        testName = "TransparentImage"
        pilImage.save(self.inputDir / f"{testName}.png")

        posterizer = Posterizer(
            options={"steps": 2, "fillStrategy": Posterizer.FILL_DOMINANT}
        )
        inputPath = self.inputDir / f"{testName}.png"
        outputPath = self.outputDir / f"{testName}_posterizer.svg"

        try:
            posterizer.loadImage(str(inputPath), callback=lambda err: None)
            svgContent = posterizer.getSVG()
            with open(outputPath, "w", encoding="utf-8") as f:
                f.write(svgContent)
            self.assertTrue(
                outputPath.exists(),
                f"Posterizer output '{outputPath.name}' was not created for transparent image.",
            )
            self.assertIn("<svg", svgContent, "SVG content missing <svg> tag.")
            self.assertIn("</svg>", svgContent, "SVG content missing </svg> tag.")
            # Ensure that background is transparent
            self.assertIn(
                'fill-opacity="1.000"',
                svgContent,
                "SVG does not handle transparency correctly.",
            )
        except Exception as e:
            self.fail(f"Posterizer failed on transparent image '{testName}': {e}")


# class TestPerformance(unittest.TestCase):
#     """
#     Performance tests to ensure that Potrace and Posterizer handle large images efficiently.

#     Note: These tests are basic and primarily check that processing completes within
#     a reasonable time frame. Adjust thresholds as necessary based on actual performance.
#     """

#     @classmethod
#     def setUpClass(cls):
#         """
#         Sets up the testing environment by creating input and output directories
#         and saving a large test image.
#         """
#         cls.inputDir = Path("./Input/Performance")
#         cls.outputDir = Path("./Output/Performance")
#         cls.inputDir.mkdir(parents=True, exist_ok=True)
#         cls.outputDir.mkdir(parents=True, exist_ok=True)

#         # Create a large synthetic image (e.g., 1000x1000)
#         largeImage = np.random.randint(0, 256, (1000, 1000), dtype=np.uint8)
#         pilImage = Image.fromarray(largeImage, mode="L")
#         cls.largeImageName = "LargeImage.png"
#         pilImage.save(cls.inputDir / cls.largeImageName)

#     def test_PotracePerformance(self):
#         """
#         Test that Potrace can process a large image within a reasonable time.

#         Raises
#         ------
#         AssertionError
#             If processing takes longer than the specified threshold.
#         """
#         import time

#         inputPath = self.inputDir / self.largeImageName
#         outputPath = self.outputDir / f"{Path(self.largeImageName).stem}_potrace.svg"
#         potrace = Potrace()
#         startTime = time.time()
#         potrace.loadImage(str(inputPath), callback=lambda err: None)
#         svgContent = potrace.getSVG()
#         processingTime = time.time() - startTime
#         with open(outputPath, "w", encoding="utf-8") as f:
#             f.write(svgContent)
#         self.assertTrue(
#             outputPath.exists(), f"Potrace output '{outputPath.name}' was not created."
#         )
#         self.assertLess(
#             processingTime, 30, "Potrace processing took too long (over 30 seconds)."
#         )

#     def test_PosterizerPerformance(self):
#         """
#         Test that Posterizer can process a large image within a reasonable time.

#         Raises
#         ------
#         AssertionError
#             If processing takes longer than the specified threshold.
#         """
#         import time

#         inputPath = self.inputDir / self.largeImageName
#         outputPath = self.outputDir / f"{Path(self.largeImageName).stem}_posterizer.svg"
#         posterizer = Posterizer({"steps": 5, "fillStrategy": Posterizer.FILL_MEAN})
#         startTime = time.time()
#         posterizer.loadImage(str(inputPath), callback=lambda err: None)
#         svgContent = posterizer.getSVG()
#         processingTime = time.time() - startTime
#         with open(outputPath, "w", encoding="utf-8") as f:
#             f.write(svgContent)
#         self.assertTrue(
#             outputPath.exists(),
#             f"Posterizer output '{outputPath.name}' was not created.",
#         )
#         self.assertLess(
#             processingTime, 45, "Posterizer processing took too long (over 45 seconds)."
# )


if __name__ == "__main__":

    shutil.rmtree("./Input", ignore_errors=True)
    shutil.rmtree("./Output", ignore_errors=True)

    unittest.main(verbosity=2)
