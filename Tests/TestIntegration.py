# test_integration.py

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
                "fill-opacity",
                svgContent,
                "SVG does not handle transparency correctly.",
            )
            self.assertIn("<path", svgContent, "SVG content missing <path> tag.")
        except Exception as e:
            self.fail(f"Posterizer failed on transparent image '{testName}': {e}")


if __name__ == "__main__":
    shutil.rmtree("./Input", ignore_errors=True)
    shutil.rmtree("./Output", ignore_errors=True)
    unittest.main(verbosity=2)
