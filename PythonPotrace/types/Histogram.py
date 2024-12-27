# PythonPotrace/types/Histogram.py

import math

from ..utils import between, clamp, luminance

COLOR_DEPTH = 256
COLOR_RANGE_END = COLOR_DEPTH - 1


def index_xy(x, y):
    """
    JS used a 2D array for color data (256x256).
    index_xy merges them: index = 256*x + y
    """
    if not (0 <= x < COLOR_DEPTH and 0 <= y < COLOR_DEPTH):
        return -1
    return COLOR_DEPTH * x + y


def normalizeMinMax(levelMin, levelMax):
    if isinstance(levelMin, (int, float)):
        levelMin = clamp(round(levelMin), 0, COLOR_RANGE_END)
    else:
        levelMin = 0

    if isinstance(levelMax, (int, float)):
        levelMax = clamp(round(levelMax), 0, COLOR_RANGE_END)
    else:
        levelMax = COLOR_RANGE_END

    if levelMin > levelMax:
        raise ValueError("Invalid range")
    return (levelMin, levelMax)


class Histogram:
    MODE_LUMINANCE = "luminance"
    MODE_R = "r"
    MODE_G = "g"
    MODE_B = "b"

    def __init__(self, imageSource, mode=None):
        """
        imageSource can be an integer (size), a Bitmap, or something else we adapt.
        """
        self.data = None
        self.pixels = 0
        self._sortedIndexes = None
        self._cachedStats = {}
        self._lookupTableH = None

        if isinstance(imageSource, int):
            self._createArray(imageSource)
        else:
            # If it's a Bitmap, collect values
            self._collectValuesBitmap(imageSource)

    def _createArray(self, imageSize):
        if imageSize <= (1 << 8):
            ArrayType = list
        elif imageSize <= (1 << 16):
            ArrayType = list
        else:
            ArrayType = list
        self.data = [0] * COLOR_DEPTH
        self.pixels = imageSize

    def _collectValuesBitmap(self, bmp):
        self._createArray(bmp.size)
        for i in range(bmp.size):
            colorVal = bmp.data[i]
            self.data[colorVal] += 1

    def _getSortedIndexes(self, refresh=False):
        if (not refresh) and self._sortedIndexes:
            return self._sortedIndexes
        idxs = list(range(COLOR_DEPTH))
        d = self.data
        idxs.sort(key=lambda x: d[x])  # ascending
        self._sortedIndexes = idxs
        return idxs

    def multilevelThresholding(self, amount, levelMin=None, levelMax=None):
        """
        Returns 'amount' thresholds in [levelMin..levelMax].
        """
        levelMin, levelMax = normalizeMinMax(levelMin, levelMax)
        amount = min(levelMax - levelMin - 2, int(amount))
        if amount < 1:
            return []

        if not self._lookupTableH:
            self._thresholdingBuildLookupTable()

        colorStops = None
        maxSig = 0

        def iterateRecursive(startingPoint, prevVariance, indexes, previousDepth):
            nonlocal colorStops, maxSig
            # In JS: startingPoint = (startingPoint || 0) + 1
            start = (startingPoint if startingPoint is not None else 0) + 1
            variance_local = prevVariance
            indexes_local = indexes[:]
            depth = previousDepth + 1

            for i in range(start, levelMax - amount + previousDepth):
                var_here = variance_local + self._lookupTableH[index_xy(start, i)]
                indexes_local[depth - 1] = i
                if depth + 1 < amount + 1:
                    iterateRecursive(i, var_here, indexes_local, depth)
                else:
                    if (i + 1) <= levelMax:
                        var_here += (
                            self._lookupTableH[index_xy(i + 1, levelMax)]
                            if index_xy(i + 1, levelMax) != -1
                            else 0
                        )
                    else:
                        var_here += 0
                    if var_here > maxSig:
                        maxSig = var_here
                        colorStops = indexes_local[:]

        iterateRecursive(levelMin, 0, [0] * amount, 0)
        return colorStops if colorStops else []

    def autoThreshold(self, levelMin=None, levelMax=None):
        thresholds = self.multilevelThresholding(1, levelMin, levelMax)
        return thresholds[0] if thresholds else None

    def getDominantColor(self, levelMin=None, levelMax=None, tolerance=1):
        levelMin, levelMax = normalizeMinMax(levelMin, levelMax)
        colors = self.data
        dominantIndex = -1
        dominantValue = -1

        if levelMin == levelMax:
            return levelMin if colors[levelMin] else -1

        for i in range(levelMin, levelMax + 1):
            tmpSum = 0
            for j in range(int(tolerance / -2), tolerance):
                idx = i + j
                if between(idx, 0, COLOR_RANGE_END):
                    tmpSum += colors[idx]
            if tmpSum > dominantValue:
                dominantIndex = i
                dominantValue = tmpSum
            elif tmpSum == dominantValue:
                # if tie, pick whichever has more direct hits
                if dominantIndex < 0 or colors[i] > colors[dominantIndex]:
                    dominantIndex = i

        return dominantIndex if dominantValue > 0 else -1

    def getStats(self, levelMin=None, levelMax=None, refresh=False):
        """
        Returns dict with 'levels': { 'mean','median','stdDev','unique'},
        'pixelsPerLevel': { 'mean','median','peak'}, 'pixels'
        """
        levelMin, levelMax = normalizeMinMax(levelMin, levelMax)
        cacheKey = f"{levelMin}-{levelMax}"
        if (not refresh) and (cacheKey in self._cachedStats):
            return self._cachedStats[cacheKey]

        d = self.data
        sortedIdx = self._getSortedIndexes()

        pixelsTotal = 0
        sumOfVals = 0
        uniqueCount = 0
        mostPixels = 0
        for i in range(levelMin, levelMax + 1):
            c = d[i]
            pixelsTotal += c
            sumOfVals += c * i
            if c > 0:
                uniqueCount += 1
            if c > mostPixels:
                mostPixels = c

        meanValue = sumOfVals / pixelsTotal if pixelsTotal else float("nan")
        pxPerLevelMean = (
            pixelsTotal / (levelMax - levelMin)
            if (levelMax > levelMin)
            else float("nan")
        )
        pxPerLevelMedian = pixelsTotal / uniqueCount if uniqueCount else float("nan")
        # median
        halfPx = pixelsTotal / 2
        running = 0
        medianVal = None
        for i in range(levelMin, levelMax + 1):
            running += d[i]
            if medianVal is None and running >= halfPx:
                medianVal = i
                break

        # std dev
        sumOfDev = 0
        seenPixels = 0
        for idx in sortedIdx:
            if idx < levelMin or idx > levelMax:
                continue
            countPx = d[idx]
            sumOfDev += (idx - meanValue) * (idx - meanValue) * countPx
            seenPixels += countPx

        stdDev = math.sqrt(sumOfDev / seenPixels) if seenPixels else float("nan")

        result = {
            "levels": {
                "mean": meanValue,
                "median": medianVal if medianVal is not None else float("nan"),
                "stdDev": stdDev,
                "unique": uniqueCount,
            },
            "pixelsPerLevel": {
                "mean": pxPerLevelMean,
                "median": pxPerLevelMedian,
                "peak": mostPixels,
            },
            "pixels": pixelsTotal,
        }
        self._cachedStats[cacheKey] = result
        return result

    def _thresholdingBuildLookupTable(self):
        # Builds H matrix from P and S, as in the JS code
        n = COLOR_DEPTH
        P = [0.0] * (n * n)
        S = [0.0] * (n * n)
        H = [0.0] * (n * n)
        pixTotal = self.pixels

        # diag
        for i in range(1, n):
            idx = index_xy(i, i)
            tmp = self.data[i] / pixTotal
            P[idx] = tmp
            S[idx] = i * tmp

        # first row?
        for i in range(1, n - 1):
            tmp = self.data[i + 1] / pixTotal
            idx = index_xy(1, i)
            P[idx + 1] = P[idx] + tmp
            S[idx + 1] = S[idx] + (i + 1) * tmp

        # reusing row 1 to fill others
        for i in range(2, n):
            for j in range(i + 1, n):
                P[index_xy(i, j)] = P[index_xy(1, j)] - P[index_xy(1, i - 1)]
                S[index_xy(i, j)] = S[index_xy(1, j)] - S[index_xy(1, i - 1)]

        # now compute H[i][j]
        for i in range(1, n):
            for j in range(i + 1, n):
                idx = index_xy(i, j)
                if abs(P[idx]) > 1e-12:
                    H[idx] = (S[idx] * S[idx]) / P[idx]
                else:
                    H[idx] = 0
        self._lookupTableH = H
