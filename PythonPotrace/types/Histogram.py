# Histogram.py
#
# This is a Python translation of histogram.js, maintaining the same interface and
# functionality. It uses Pillow (PIL) instead of Jimp to handle image data when necessary.
# The supporting classes and methods (Bitmap, utils, etc.) are assumed to exist in your
# environment, just like in the Node.js code.

from PIL import Image
from ..utils import clamp, luminance
from .Bitmap import Bitmap

COLOR_DEPTH = 256
COLOR_RANGE_END = COLOR_DEPTH - 1

def index(x, y):
    """
    Calculate the array index for a pair of coordinates.

    Parameters
    ----------
    x : int
        First index.
    y : int
        Second index.

    Returns
    -------
    int
        Calculated array index.
    """
    return COLOR_DEPTH * x + y

def normalizeMinMax(levelMin, levelMax):
    """
    Normalize and clamp minimum and maximum levels.

    Parameters
    ----------
    levelMin : int or float
        Minimum level value.
    levelMax : int or float
        Maximum level value.

    Returns
    -------
    list of int
        Normalized [levelMin, levelMax].

    Raises
    ------
    ValueError
        If levelMin is greater than levelMax.
    """
    levelMin = (
        clamp(int(round(levelMin)), 0, COLOR_RANGE_END)
        if isinstance(levelMin, (int, float))
        else 0
    )
    levelMax = (
        clamp(int(round(levelMax)), 0, COLOR_RANGE_END)
        if isinstance(levelMax, (int, float))
        else COLOR_RANGE_END
    )

    if levelMin > levelMax:
        raise ValueError(f'Invalid range "{levelMin}...{levelMax}"')

    return [levelMin, levelMax]

class Histogram:
    """
    Histogram for aggregating color data.

    Attributes
    ----------
    data : list of int
        Histogram data.
    pixels : int
        Total number of pixels.
    _sortedIndexes : list of int or None
        Cached sorted color indices.
    _cachedStats : dict
        Cached statistics.
    _lookupTableH : list of float or None
        Lookup table for thresholding.
    """

    MODE_LUMINANCE = 'luminance'
    MODE_R = 'r'
    MODE_G = 'g'
    MODE_B = 'b'

    def __init__(self, imageSource, mode=None):
        """
        Initialize the Histogram.

        Parameters
        ----------
        imageSource : int or Bitmap or Image.Image
            Source for histogram data.
        mode : str, optional
            Mode for histogram (e.g., 'r', 'g', 'b', 'luminance').
        """
        self.data = None
        self.pixels = 0
        self._sortedIndexes = None
        self._cachedStats = {}
        self._lookupTableH = None

        if isinstance(imageSource, int):
            # Create an empty histogram array sized for `imageSource` pixels
            self._createArray(imageSource)
        elif isinstance(imageSource, Bitmap):
            # Collect values from the Bitmap
            self._collectValuesBitmap(imageSource)
        elif isinstance(imageSource, Image.Image):
            # Collect values from a Pillow image
            self._collectValuesPillow(imageSource, mode)
        else:
            raise ValueError("Unsupported image source")

    def _createArray(self, imageSize):
        """
        Initializes data array for an image of given pixel size. We approximate the
        JavaScript approach:
          - If imageSize <= 2^8, use a smaller array type
          - If imageSize <= 2^16, medium
          - Otherwise, large
        In Python, we'll just store data in a list (or we could store in e.g. array.array).
        """
        # In Python, we don't strictly need different types for different ranges,
        # but we replicate the logic anyway.
        if imageSize <= 2 ** 8:
            # We'll just use a list of length 256 for counting.
            self.data = [0] * COLOR_DEPTH
        elif imageSize <= 2 ** 16:
            # We'll also just use a list, but let's note the original logic.
            self.data = [0] * COLOR_DEPTH
        else:
            self.data = [0] * COLOR_DEPTH

        self.pixels = imageSize
        return self.data

    def _collectValuesPillow(self, source, mode):
        """
        Aggregates color data from a Pillow Image instance.

        Parameters
        ----------
        source : Image.Image
            Pillow Image instance.
        mode : str
            Mode for histogram (e.g., 'r', 'g', 'b', 'luminance').
        """
        width, height = source.size
        pixelCount = width * height
        data = self._createArray(pixelCount)

        # We assume the source is in RGBA or has been converted accordingly
        pixels = source.load()

        for y in range(height):
            for x in range(width):
                px = pixels[x, y]
                # px could be (R, G, B) or (R, G, B, A)
                if len(px) == 4:
                    r, g, b, a = px
                else:
                    r, g, b = px
                    a = 255

                if mode == Histogram.MODE_R:
                    val = r
                elif mode == Histogram.MODE_G:
                    val = g
                elif mode == Histogram.MODE_B:
                    val = b
                else:
                    # Luminance
                    val = luminance(r, g, b)

                data[val] += 1

    def _collectValuesBitmap(self, source):
        """
        Aggregates color data from a Bitmap instance.

        Parameters
        ----------
        source : Bitmap
            Bitmap instance.
        """
        data = self._createArray(source.size)
        # Each entry in source.data is presumably an 8-bit color value
        for color in source.data:
            data[color] += 1

    def _getSortedIndexes(self, refresh=False):
        """
        Returns array of color indexes [0..255] in ascending order (from least used color
        to most used color).

        Parameters
        ----------
        refresh : bool, optional
            If True, always re-sort.

        Returns
        -------
        list of int
            Sorted color indices.
        """
        if not refresh and self._sortedIndexes is not None:
            return self._sortedIndexes

        # Sort indices [0..255] by the number of pixels that have each color
        indexes = list(range(COLOR_DEPTH))
        data = self.data

        # Ascending sort of color usage
        indexes.sort(key=lambda idx: data[idx])
        self._sortedIndexes = indexes
        return indexes

    def _thresholdingBuildLookupTable(self):
        """
        Builds lookup table H from intermediate lookup tables P and S. This is used for
        multi-level thresholding. The logic matches the JavaScript approach.

        Returns
        -------
        list of float
            Lookup table H.
        """
        # We'll store floats in Python
        P = [0.0] * (COLOR_DEPTH * COLOR_DEPTH)
        S = [0.0] * (COLOR_DEPTH * COLOR_DEPTH)
        H = [0.0] * (COLOR_DEPTH * COLOR_DEPTH)
        pixelsTotal = float(self.pixels)

        # diagonal
        for i in range(1, COLOR_DEPTH):
            idx = index(i, i)
            tmp = self.data[i] / pixelsTotal
            P[idx] = tmp
            S[idx] = i * tmp

        # first row (row 0 is all zeros, which is effectively done by default)
        for i in range(1, COLOR_DEPTH - 1):
            tmp = self.data[i + 1] / pixelsTotal
            idx = index(1, i)
            P[idx + 1] = P[idx] + tmp
            S[idx + 1] = S[idx] + (i + 1) * tmp

        # using row 1 to calculate others
        for i in range(2, COLOR_DEPTH):
            for j in range(i + 1, COLOR_DEPTH):
                P[index(i, j)] = P[index(1, j)] - P[index(1, i - 1)]
                S[index(i, j)] = S[index(1, j)] - S[index(1, i - 1)]

        # now calculate H[i][j]
        for i in range(1, COLOR_DEPTH):
            for j in range(i + 1, COLOR_DEPTH):
                idx = index(i, j)
                Pval = P[idx]
                H[idx] = (S[idx] * S[idx] / Pval) if Pval != 0 else 0

        self._lookupTableH = H
        return H

    def multilevelThresholding(self, amount, levelMin=None, levelMax=None):
        """
        Implements 'Algorithm For Multilevel Thresholding' to find `amount` thresholds.
        This might be limited to a range of levelMin..levelMax, but it still uses the
        entire histogram's variance to compute thresholds.

        Parameters
        ----------
        amount : int
            Number of thresholds to compute.
        levelMin : int or float, optional
            Histogram segment start.
        levelMax : int or float, optional
            Histogram segment end.

        Returns
        -------
        list of int
            List of threshold values.
        """
        [levelMin, levelMax] = normalizeMinMax(levelMin, levelMax)
        amount = min(levelMax - levelMin - 2, int(amount))

        if amount < 1:
            return []

        if self._lookupTableH is None:
            self._thresholdingBuildLookupTable()

        H = self._lookupTableH
        maxSig = 0.0
        colorStops = None

        if amount > 4:
            print("[Warning]: Threshold computation for more than 5 levels "
                  "may take a long time")

        def iterateRecursive(startingPoint=0, prevVariance=0.0, indexes=None, previousDepth=0):
            nonlocal maxSig, colorStops

            if indexes is None:
                indexes = [0] * amount

            sp = startingPoint + 1
            depth = previousDepth + 1

            for i in range(sp, levelMax - amount + previousDepth + 1):
                variance = prevVariance + H[index(sp, i)]
                indexes[depth - 1] = i

                if depth + 1 < amount + 1:
                    # go deeper
                    iterateRecursive(i, variance, indexes, depth)
                else:
                    # final
                    variance += H[index(i + 1, levelMax)]
                    if maxSig < variance:
                        maxSig = variance
                        colorStops = indexes[:]

        iterateRecursive(0)

        return colorStops if colorStops else []

    def autoThreshold(self, levelMin=None, levelMax=None):
        """
        Automatically finds threshold value using 'Algorithm For Multilevel Thresholding'
        with amount=1.

        Parameters
        ----------
        levelMin : int or float, optional
            Histogram segment start.
        levelMax : int or float, optional
            Histogram segment end.

        Returns
        -------
        int or None
            Single threshold value, or None if not found.
        """
        val = self.multilevelThresholding(1, levelMin, levelMax)
        return val[0] if len(val) else None

    def getDominantColor(self, levelMin=None, levelMax=None, tolerance=1):
        """
        Returns the dominant color in [levelMin..levelMax]. If not found, returns -1.

        Parameters
        ----------
        levelMin : int or float, optional
            Histogram segment start.
        levelMax : int or float, optional
            Histogram segment end.
        tolerance : int, optional
            How many adjacent color bins to consider.

        Returns
        -------
        int
            Dominant color index [0..255], or -1 if not found.
        """
        [levelMin, levelMax] = normalizeMinMax(levelMin, levelMax)

        colors = self.data
        dominantIndex = -1
        dominantValue = -1

        # If there's exactly one color to check
        if levelMin == levelMax:
            return levelMin if colors[levelMin] > 0 else -1

        for i in range(levelMin, levelMax + 1):
            tmp = 0
            # gather sum of a small range around i
            for j in range(int(-tolerance // 2), tolerance):
                idx = i + j
                if 0 <= idx <= COLOR_RANGE_END:
                    tmp += colors[idx]

            summIsBigger = tmp > dominantValue
            summEqualButMainColorIsBigger = (
                tmp == dominantValue and
                (dominantIndex < 0 or colors[i] > colors[dominantIndex])
            )

            if summIsBigger or summEqualButMainColorIsBigger:
                dominantIndex = i
                dominantValue = tmp

        return -1 if dominantValue <= 0 else dominantIndex

    def getStats(self, levelMin=None, levelMax=None, refresh=False):
        """
        Returns stats for the histogram or its segment [levelMin..levelMax].
        The returned dict includes:
            {
              'levels': {
                'mean': float,
                'median': float,
                'stdDev': float,
                'unique': int
              },
              'pixelsPerLevel': {
                'mean': float,
                'median': float,
                'peak': int
              },
              'pixels': int
            }

        Parameters
        ----------
        levelMin : int or float, optional
            Histogram segment start.
        levelMax : int or float, optional
            Histogram segment end.
        refresh : bool, optional
            If False and result is cached, returns cached result.

        Returns
        -------
        dict
            Dictionary with the stats.
        """
        [levelMin, levelMax] = normalizeMinMax(levelMin, levelMax)
        cacheKey = f"{levelMin}-{levelMax}"

        if not refresh and cacheKey in self._cachedStats:
            return self._cachedStats[cacheKey]

        data = self.data
        sortedIndexes = self._getSortedIndexes()  # ascending usage
        pixelsTotal = 0
        allPixelValuesCombined = 0
        uniqueValues = 0
        mostPixelsPerLevel = 0

        # Accumulate total pixels and weighted sum
        for i in range(levelMin, levelMax + 1):
            cnt = data[i]
            pixelsTotal += cnt
            allPixelValuesCombined += cnt * i
            if cnt > 0:
                uniqueValues += 1
            if cnt > mostPixelsPerLevel:
                mostPixelsPerLevel = cnt

        if pixelsTotal == 0:
            # no data in this range, create an "empty" stats
            stats = {
                'levels': {
                    'mean': float('nan'),
                    'median': float('nan'),
                    'stdDev': float('nan'),
                    'unique': 0
                },
                'pixelsPerLevel': {
                    'mean': float('nan'),
                    'median': float('nan'),
                    'peak': 0
                },
                'pixels': 0
            }
            self._cachedStats[cacheKey] = stats
            return stats

        meanValue = allPixelValuesCombined / float(pixelsTotal)
        pixelsPerLevelMean = pixelsTotal / float(levelMax - levelMin) if (levelMax - levelMin) > 0 else float('nan')
        pixelsPerLevelMedian = pixelsTotal / float(uniqueValues) if uniqueValues else float('nan')
        medianPixelIndex = pixelsTotal // 2

        tmpPixelsIterated = 0
        tmpSumOfDeviations = 0.0
        medianValue = None

        for idx in sortedIndexes:
            if idx < levelMin or idx > levelMax:
                continue
            count = data[idx]
            tmpPixelsIterated += count
            tmpSumOfDeviations += (idx - meanValue) ** 2 * count

            if medianValue is None and tmpPixelsIterated >= medianPixelIndex:
                medianValue = idx

        stdDevValue = (tmpSumOfDeviations / pixelsTotal) ** 0.5 if pixelsTotal else float('nan')

        stats = {
            'levels': {
                'mean': meanValue,
                'median': medianValue,
                'stdDev': stdDevValue,
                'unique': uniqueValues
            },
            'pixelsPerLevel': {
                'mean': pixelsPerLevelMean,
                'median': pixelsPerLevelMedian,
                'peak': mostPixelsPerLevel
            },
            'pixels': pixelsTotal
        }
        self._cachedStats[cacheKey] = stats
        return stats
