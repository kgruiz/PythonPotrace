import unittest
import os
import tempfile
from PIL import Image, ImageDraw
import io
import sys
from pathlib import Path
from PythonPotrace import index, Potrace, Posterizer
from PythonPotrace.types.Bitmap import Bitmap
from PythonPotrace.types.Point import Point
from PythonPotrace.types.Histogram import Histogram
from skimage import data
import matplotlib.pyplot as plt


# Helper function to create a simple test image
def CreateTestImage(width, height, color=(255, 255, 255)):
    """Creates a simple test image with a given width, height, and color.

    Parameters
    ----------
    width : int
        Width of the image.
    height : int
        Height of the image.
    color : tuple of int, optional
        RGB color tuple, defaults to white (255, 255, 255).

    Returns
    -------
    PIL.Image.Image
        A new PIL Image object.
    """
    img = Image.new('RGB', (width, height), color)
    return img

def CreateComplexTestImage(width, height):
    """Creates a more complex test image with lines, rectangles, circles, and arcs.

    Parameters
    ----------
    width : int
        Width of the image.
    height : int
        Height of the image.

    Returns
    -------
    PIL.Image.Image
        A new PIL Image object.
    """
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    # Draw a diagonal line
    draw.line((0, 0, width-1, height-1), fill='black', width=5)

    # Draw a rectangle
    draw.rectangle((width // 4, height // 4, 3 * width // 4, 3 * height // 4), outline='black', width=3)

    # Draw a circle
    draw.ellipse((width // 3, height // 3, 2 * width // 3, 2 * height // 3), outline='black', width=2)

    # Draw an arc
    draw.arc((width // 6, height // 6, 5 * width // 6, 5 * height // 6), 30, 270, fill='red')

    return img

def CreateGradientImage(width, height):
    """Creates a gradient test image.

    Parameters
    ----------
    width : int
        Width of the image.
    height : int
        Height of the image.

    Returns
    -------
    PIL.Image.Image
        A new grayscale PIL Image object with a horizontal gradient.
    """
    img = Image.new('L', (width, height))
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            pixels[x, y] = int(x / width * 255) # Horizontal gradient
    return img

def CreateAlphaTestImage(width, height):
    """Creates a test image with transparency.

    Parameters
    ----------
    width : int
        Width of the image.
    height : int
        Height of the image.

    Returns
    -------
    PIL.Image.Image
        A new RGBA PIL Image object.
    """
    img = Image.new('RGBA', (width, height), (255, 0, 0, 0)) # transparent red
    draw = ImageDraw.Draw(img)
    draw.ellipse((10, 10, width-10, height-10), fill=(0, 255, 0, 128)) # semi-transparent green
    return img


def AssertImagesEqual(testcase, img1, img2):
    """Asserts that two PIL images are pixel-by-pixel equal.

    Parameters
    ----------
    testcase : unittest.TestCase
        The test case instance.
    img1 : PIL.Image.Image
        The first PIL Image object.
    img2 : PIL.Image.Image
        The second PIL Image object.

    Raises
    ------
    AssertionError
        If the images are not equal.
    """
    testcase.assertEqual(img1.size, img2.size, "Image sizes are different")
    pixels1 = img1.load()
    pixels2 = img2.load()

    for x in range(img1.width):
      for y in range(img1.height):
        testcase.assertEqual(pixels1[x,y], pixels2[x,y], f"Pixel mismatch at ({x}, {y})")

def SaveInputs():
    """Saves test images to the Input directory within Tests using skimage data."""
    images = {
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

    Path("./Tests/Input").resolve().mkdir(exist_ok=True)

    for title, image in images.items():
        try:
            plt.imsave(f"./Tests/Input/{title}.png", image)
        except Exception as e:
            print(f"Error saving {title}: {e}")


class TestPotrace(unittest.TestCase):

    def setUp(self):
        """Setup method called before each test."""
        SaveInputs()

    def test_basic_tracing(self):
        """Tests basic tracing functionality with a simple white square."""
        print("Running test_basic_tracing")
        # Input image: a simple white square on a black background
        inputImg = CreateTestImage(100, 100, color='black')
        draw = ImageDraw.Draw(inputImg)
        draw.rectangle((20, 20, 80, 80), fill='white')

        # Output image: the expected SVG string
        expectedSvg =  '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100" version="1.1">\n\t<path d="M 20.000 20.000 L 80.000 20.000 80.000 80.000 20.000 80.000 20.000 20.000" stroke="none" fill="black" fill-rule="evenodd"/>\n</svg>'


        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpFile:
            inputImg.save(tmpFile.name)

            def CheckSvg(error, svg, potrace):
                """Callback to check SVG output for test_basic_tracing."""
                self.assertIsNone(error, f"Error during tracing: {error}")
                self.assertEqual(svg, expectedSvg, f"SVG output mismatch. Actual:\n{svg}\nExpected:\n{expectedSvg}")

            index.trace(tmpFile.name, cb=CheckSvg)

        os.remove(tmpFile.name)

    def test_complex_tracing(self):
        """Tests tracing functionality with a complex shape."""
        print("Running test_complex_tracing")
        # Input image: a more complex shape
        inputImg = CreateComplexTestImage(200, 200)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpFile:
            inputImg.save(tmpFile.name)

            def CheckSvg(error, svg, potrace):
                """Callback to check SVG output for test_complex_tracing."""
                self.assertIsNone(error, f"Error during tracing: {error}")
                self.assertIn("<svg", svg, "SVG output should contain the <svg tag")
                self.assertIn("<path", svg, "SVG output should contain <path tag")

            index.trace(tmpFile.name, cb=CheckSvg)
        os.remove(tmpFile.name)


    def test_tracing_with_options(self):
        """Tests tracing functionality with options (turnPolicy, optCurve, width, height)."""
        print("Running test_tracing_with_options")
        # Input image: a simple image
        inputImg = CreateTestImage(100, 100, color="white")
        draw = ImageDraw.Draw(inputImg)
        draw.ellipse((20, 20, 80, 80), fill="black")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpFile:
            inputImg.save(tmpFile.name)

            def CheckSvg(error, svg, potrace):
                """Callback to check SVG output for test_tracing_with_options."""
                self.assertIsNone(error, f"Error during tracing: {error}")
                self.assertIn('fill-rule="evenodd"', svg)
                self.assertIn('width="200"', svg)
                self.assertIn('height="200"', svg)
                self.assertNotIn('viewBox="0 0 100 100"', svg)


            index.trace(
              tmpFile.name,
              options={"turnPolicy": "right", "optCurve": False, "width": 200, "height": 200},
              cb=CheckSvg,
            )

        os.remove(tmpFile.name)

    def test_image_as_input(self):
        """Tests tracing with a PIL image object as input."""
        print("Running test_image_as_input")
        # Input image: same simple white square
        inputImg = CreateTestImage(100, 100, color='white')
        draw = ImageDraw.Draw(inputImg)
        draw.rectangle((20, 20, 80, 80), fill='black')

        # Output image: The SVG output string, same as above but uses direct image input
        expectedSvg =  '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100" version="1.1">\n\t<path d="M 20.000 20.000 L 80.000 20.000 80.000 80.000 20.000 80.000 20.000 20.000" stroke="none" fill="black" fill-rule="evenodd"/>\n</svg>'

        def CheckSvg(error, svg, potrace):
            """Callback to check SVG output for test_image_as_input."""
            self.assertIsNone(error, f"Error during tracing: {error}")
            self.assertEqual(svg, expectedSvg, f"SVG output mismatch. Actual:\n{svg}\nExpected:\n{expectedSvg}")

        index.trace(inputImg, cb=CheckSvg)


    def test_error_handling_image_load(self):
        """Tests error handling when loading a non-existent image file."""
        print("Running test_error_handling_image_load")
        def CheckError(error, svg, potrace):
            """Callback to check error during image load."""
            self.assertIsNotNone(error, "Error expected but not raised")
            self.assertIsNone(svg)
            self.assertIsNone(potrace)

        index.trace("non_existent_file.png", cb=CheckError)


    def test_posterizer_basic(self):
        """Tests basic posterizer functionality with a gradient image."""
        print("Running test_posterizer_basic")
        inputImg = CreateGradientImage(256, 100)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpFile:
            inputImg.save(tmpFile.name)

            def CheckSvg(error, svg, posterizer):
                """Callback to check SVG output for test_posterizer_basic."""
                self.assertIsNone(error, f"Error during posterization: {error}")
                self.assertIn("<svg", svg)
                self.assertIn("<path", svg)


            index.posterize(tmpFile.name, cb=CheckSvg)

        os.remove(tmpFile.name)


    def test_posterizer_with_options(self):
        """Tests posterizer functionality with various options."""
        print("Running test_posterizer_with_options")
        inputImg = CreateTestImage(100, 100, color="white")
        draw = ImageDraw.Draw(inputImg)
        draw.ellipse((20, 20, 80, 80), fill='black')

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpFile:
            inputImg.save(tmpFile.name)

            def CheckSvg(error, svg, posterizer):
                """Callback to check SVG output for test_posterizer_with_options."""
                self.assertIsNone(error, f"Error during posterization: {error}")
                self.assertIn('<svg xmlns="http://www.w3.org/2000/svg"', svg)
                self.assertIn('fill-opacity="', svg)
                self.assertIn('width="200"', svg)
                self.assertIn('height="200"', svg)
                self.assertNotIn('viewBox="0 0 100 100"', svg)


            index.posterize(
              tmpFile.name,
              options={
                  "steps": 3,
                  "blackOnWhite": False,
                  "width": 200,
                  "height": 200,
                  "fillStrategy": Posterizer.FILL_MEAN,
                  "background": "red",
              },
              cb=CheckSvg,
            )

        os.remove(tmpFile.name)

    def test_alpha_tracing(self):
        """Tests tracing functionality with an image containing alpha channel."""
        print("Running test_alpha_tracing")
        # Create an image with some alpha
        inputImg = CreateAlphaTestImage(100, 100)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpFile:
            inputImg.save(tmpFile.name)
            def CheckSvg(error, svg, potrace):
                """Callback to check SVG output for test_alpha_tracing."""
                self.assertIsNone(error, f"Error during tracing: {error}")
                self.assertIn("<svg", svg, "SVG output should contain the <svg tag")
                self.assertIn("<path", svg, "SVG output should contain <path tag")

            index.trace(tmpFile.name, cb=CheckSvg)

        os.remove(tmpFile.name)

    def test_path_tag_generation(self):
        """Tests getPathTag method to get only the path tag."""
        print("Running test_path_tag_generation")
        # Create a basic image to vectorize
        inputImg = CreateTestImage(100, 100, color='white')
        draw = ImageDraw.Draw(inputImg)
        draw.rectangle((20, 20, 80, 80), fill='black')

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpFile:
            inputImg.save(tmpFile.name)

            def CheckPathTag(error, svg, potrace):
                """Callback to check Path Tag output for test_path_tag_generation."""
                self.assertIsNone(error, f"Error during tracing: {error}")
                pathTag = potrace.getPathTag()
                self.assertIn('<path d="', pathTag)
                self.assertIn('fill="black"', pathTag)

            index.trace(tmpFile.name, cb=CheckPathTag)

        os.remove(tmpFile.name)

    def test_symbol_generation(self):
        """Tests getSymbol method to get a symbol tag."""
        print("Running test_symbol_generation")
        # Create a basic image to vectorize
        inputImg = CreateTestImage(100, 100, color='white')
        draw = ImageDraw.Draw(inputImg)
        draw.rectangle((20, 20, 80, 80), fill='black')

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpFile:
            inputImg.save(tmpFile.name)

            def CheckSymbol(error, svg, potrace):
                """Callback to check Symbol output for test_symbol_generation."""
                self.assertIsNone(error, f"Error during tracing: {error}")
                symbol = potrace.getSymbol("testSymbol")
                self.assertIn('<symbol viewBox="0 0 100 100" id="testSymbol">', symbol)
                self.assertIn('<path d="', symbol)

            index.trace(tmpFile.name, cb=CheckSymbol)

        os.remove(tmpFile.name)

    def test_posterizer_symbol_generation(self):
        """Tests getSymbol method of posterizer to get a symbol tag."""
        print("Running test_posterizer_symbol_generation")
        # Create a basic image to vectorize
        inputImg = CreateGradientImage(256, 100)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpFile:
            inputImg.save(tmpFile.name)

            def CheckSymbol(error, svg, posterizer):
                """Callback to check Symbol output for test_posterizer_symbol_generation."""
                self.assertIsNone(error, f"Error during tracing: {error}")
                symbol = posterizer.getSymbol("testPosterizerSymbol")
                self.assertIn('<symbol viewBox="0 0 256 100" id="testPosterizerSymbol">', symbol)
                self.assertIn('<path d="', symbol)

            index.posterize(tmpFile.name, cb=CheckSymbol)

        os.remove(tmpFile.name)

    def test_bitmap_methods(self):
        """Tests the methods of the Bitmap class."""
        print("Running test_bitmap_methods")
        # Create a simple bitmap
        bitmap = Bitmap(5, 5)
        for i in range(bitmap.size):
            bitmap.data[i] = i % 256

        # Test get value
        self.assertEqual(bitmap.get_value_at(2,2), 12, "incorrect pixel value")
        self.assertEqual(bitmap.get_value_at(12), 12, "incorrect pixel value")

        # Test index to point
        point = bitmap.index_to_point(12)
        self.assertEqual(point.x, 2, "Incorrect x conversion")
        self.assertEqual(point.y, 2, "Incorrect y conversion")

        # Test point to index
        index = bitmap.point_to_index(Point(3, 2))
        self.assertEqual(index, 13, "incorrect index conversion")

        index = bitmap.point_to_index(3, 2)
        self.assertEqual(index, 13, "incorrect index conversion")

        # Test copy
        copyBitmap = bitmap.copy()
        self.assertEqual(bitmap.data[0], copyBitmap.data[0], "copy pixel value mismatch")

        # Test copy with iterator
        copyBitmapIt = bitmap.copy(lambda val, idx: val + 1)
        self.assertEqual(bitmap.data[0] + 1, copyBitmapIt.data[0], "copy with iterator mismatch")

    def test_histogram_methods(self):
        """Tests the methods of the Histogram class."""
        print("Running test_histogram_methods")

        #create bitmap for the test
        testBitmap = Bitmap(5,5)
        for i in range(testBitmap.size):
          testBitmap.data[i] = (i * 15) % 256

        # Create a histogram
        histogram = Histogram(testBitmap)

        # Test basic properties
        self.assertEqual(histogram.pixels, 25, "Incorrect number of pixels")
        self.assertIsInstance(histogram.data, list, "Data must be an array")

        # Test stats
        stats = histogram.getStats()
        self.assertAlmostEqual(stats['levels']['mean'], 112.5, delta=0.001)
        self.assertAlmostEqual(stats['levels']['stdDev'], 73.63, delta=0.001)
        self.assertEqual(stats['pixels'], 25, "Incorrect number of pixels in stats")

        # Test segment stats
        statsSeg = histogram.getStats(50, 150)
        self.assertGreaterEqual(statsSeg['pixels'], 0)

        # Test dominant color
        dominant = histogram.getDominantColor(0, 255)
        self.assertGreaterEqual(dominant, 0)
        self.assertLessEqual(dominant, 255)

        # Test multi-level thresholding
        thresholds = histogram.multilevelThresholding(2)
        self.assertTrue(len(thresholds) >= 0)

        # Test auto-threshold
        autoThreshold = histogram.autoThreshold()
        self.assertGreaterEqual(autoThreshold, 0)
        self.assertLessEqual(autoThreshold, 255)

    def test_various_images(self):
        """Tests potrace on a variety of images from skimage."""
        print("Running test_various_images")

        inputDir = Path("./Tests/Input")

        for file in inputDir.glob("*.png"):
            with self.subTest(imageFile=file.name):
                def checkVarious(error, svg, potrace):
                    """Callback to check SVG output for each image in test_various_images."""
                    self.assertIsNone(error, f"Error during tracing for {file.name}: {error}")
                    self.assertIn("<svg", svg, f"SVG output should contain the <svg tag for {file.name}")
                    self.assertIn("<path", svg, f"SVG output should contain <path tag for {file.name}")

                index.trace(str(file), cb=checkVarious)


def RunTests():
    """Runs all the tests."""
    unittest.main(verbosity=2, exit=False)

if __name__ == '__main__':
    RunTests()