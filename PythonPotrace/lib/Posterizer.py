# Posterizer.py

import math
from PythonPotrace.lib.Potrace import Potrace
from PythonPotrace.lib.utils import (
    between,
    clamp,
    is_number,
    set_html_attribute
)

class Posterizer:
    """
    Combines multiple Potrace samples with different threshold settings into a single result.

    Parameters
    ----------
    options : dict, optional
        A dictionary of Posterizer options. Defaults to None.

    Attributes
    ----------
    _potrace : Potrace
        An instance of the Potrace class.
    _calculatedThreshold : float or None
        The calculated threshold value.
    _params : dict
        A dictionary of parameters for posterizing.

    """

    STEPS_AUTO = -1
    FILL_SPREAD = 'spread'
    FILL_DOMINANT = 'dominant'
    FILL_MEDIAN = 'median'
    FILL_MEAN = 'mean'
    RANGES_AUTO = 'auto'
    RANGES_EQUAL = 'equal'

    def __init__(self, options=None):
        """
        Initialize the Posterizer with optional parameters.

        Parameters
        ----------
        options : dict, optional
            A dictionary of Posterizer options. Defaults to None.

        """
        self._potrace = Potrace()
        self._calculatedThreshold = None

        # Default parameters
        self._params = {
            'threshold': Potrace.THRESHOLD_AUTO,
            'blackOnWhite': True,
            'steps': Posterizer.STEPS_AUTO,
            'background': Potrace.COLOR_TRANSPARENT,
            'fillStrategy': Posterizer.FILL_DOMINANT,
            'rangeDistribution': Posterizer.RANGES_AUTO
        }

        if options:
            self.setParameters(options)

        # Inherit constants from Potrace class if needed, similar to JS approach
        # But in Python, we usually just reference them directly.

    def _addExtraColorStop(self, ranges):
        """
        Add an extra color stop if the last range exceeds 25 units.

        Parameters
        ----------
        ranges : list
            A list of color range dictionaries.

        Returns
        -------
        list
            The updated list of color ranges with an additional color stop if applicable.

        """
        blackOnWhite = self._params['blackOnWhite']
        lastColorStop = ranges[-1]
        lastRangeFrom = 0 if blackOnWhite else lastColorStop['value']
        lastRangeTo = lastColorStop['value'] if blackOnWhite else 255

        if (lastRangeTo - lastRangeFrom) > 25 and lastColorStop['colorIntensity'] != 1:
            histogram = self._getImageHistogram()
            levels = histogram.getStats(lastRangeFrom, lastRangeTo)['levels']

            # Suggest a new color stop around mean +/- stdDev,
            # or fallback to 25 if those values are not suitable
            potentialNewStop = None
            if (levels['mean'] + levels['stdDev']) <= 25:
                potentialNewStop = levels['mean'] + levels['stdDev']
            elif (levels['mean'] - levels['stdDev']) <= 25:
                potentialNewStop = levels['mean'] - levels['stdDev']
            else:
                potentialNewStop = 25

            # Ensure we have a valid integer
            newColorStop = int(round(potentialNewStop))

            if blackOnWhite:
                newStats = histogram.getStats(0, newColorStop)
            else:
                newStats = histogram.getStats(newColorStop, 255)

            color = newStats['levels']['mean']
            colorIntensity = 0 if math.isnan(color) else (
                (255 - color) / 255 if blackOnWhite else color / 255
            )

            ranges.append({
                'value': abs((0 if blackOnWhite else 255) - newColorStop),
                'colorIntensity': colorIntensity
            })

        return ranges

    def _calcColorIntensity(self, colorStops):
        """
        Calculate color intensity for each color stop.

        Parameters
        ----------
        colorStops : list
            A list of threshold values.

        Returns
        -------
        list of dict
            A list containing dictionaries with 'value' and 'colorIntensity' keys.

        """
        blackOnWhite = self._params['blackOnWhite']
        colorSelectionStrat = self._params['fillStrategy']
        histogram = None

        # If fill strategy is 'spread', we won't need histogram.
        if colorSelectionStrat != Posterizer.FILL_SPREAD:
            histogram = self._getImageHistogram()

        fullRange = abs(self._paramThreshold() - (0 if blackOnWhite else 255))
        output = []

        for index, threshold in enumerate(colorStops):
            # If last in array, nextValue is either -1 or 256
            if index + 1 == len(colorStops):
                nextValue = -1 if blackOnWhite else 256
            else:
                nextValue = colorStops[index + 1]

            # Define the range where we get stats from the histogram
            # For blackOnWhite, the range is reversed.
            rangeStart = round(nextValue + 1 if blackOnWhite else threshold)
            rangeEnd = round(threshold if blackOnWhite else nextValue - 1)
            factor = index / float(len(colorStops) - 1) if len(colorStops) > 1 else 0
            intervalSize = rangeEnd - rangeStart
            stats = {'pixels': 0, 'levels': {}}

            if histogram:
                stats = histogram.getStats(rangeStart, rangeEnd)

            if stats['pixels'] == 0:
                output.append({'value': threshold, 'colorIntensity': 0})
                continue

            color = -1
            if colorSelectionStrat == Posterizer.FILL_SPREAD:
                # We want it to be 0 (or 255) at the most saturated end, so:
                if blackOnWhite:
                    color = (rangeStart +
                             intervalSize * max(0.5, fullRange / 255.0) * factor)
                else:
                    color = (rangeEnd -
                             intervalSize * max(0.5, fullRange / 255.0) * factor)
            elif colorSelectionStrat == Posterizer.FILL_DOMINANT:
                color = histogram.getDominantColor(
                    rangeStart, rangeEnd, clamp(intervalSize, 1, 5)
                )
            elif colorSelectionStrat == Posterizer.FILL_MEAN:
                color = stats['levels']['mean']
            elif colorSelectionStrat == Posterizer.FILL_MEDIAN:
                color = stats['levels']['median']

            # Avoid colors that are too close to each other by adding spacing
            if index != 0 and color != -1:
                if blackOnWhite:
                    color = clamp(color, rangeStart, rangeEnd - round(intervalSize * 0.1))
                else:
                    color = clamp(color, rangeStart + round(intervalSize * 0.1), rangeEnd)

            if color == -1:
                intensity = 0
            else:
                intensity = (255 - color) / 255.0 if blackOnWhite else (color / 255.0)

            output.append({
                'value': threshold,
                'colorIntensity': intensity
            })

        return output

    def _getImageHistogram(self):
        """
        Retrieve the histogram of the loaded image.

        Returns
        -------
        Histogram
            The histogram of the image's luminance data.

        """
        return self._potrace._luminanceData.histogram()

    def _getRanges(self):
        """
        Determine the color ranges based on threshold and distribution parameters.

        Returns
        -------
        list of dict
            A list of color ranges with their respective intensities.

        """
        steps = self._paramSteps(count=False)

        if not isinstance(steps, list):
            if self._params['rangeDistribution'] == Posterizer.RANGES_AUTO:
                return self._getRangesAuto()
            else:
                return self._getRangesEquallyDistributed()

        # If steps is an array of thresholds, preprocess it
        colorStops = []
        threshold = self._paramThreshold()
        lookingForDarkPixels = self._params['blackOnWhite']

        for item in steps:
            if item not in colorStops and between(item, 0, 255):
                colorStops.append(item)

        if not colorStops:
            colorStops.append(threshold)

        colorStops.sort(key=lambda x: x, reverse=lookingForDarkPixels)

        # Ensure threshold is part of the colorStops if needed
        if lookingForDarkPixels and colorStops[0] < threshold:
            colorStops.insert(0, threshold)
        elif (not lookingForDarkPixels and
              colorStops[len(colorStops) - 1] < threshold):
            colorStops.append(threshold)

        return self._calcColorIntensity(colorStops)

    def _getRangesAuto(self):
        """
        Automatically calculate color ranges using the histogram's thresholding.

        Returns
        -------
        list of dict
            A list of automatically calculated color ranges with intensities.

        """
        histogram = self._getImageHistogram()
        steps = self._paramSteps(count=True)

        if self._params['threshold'] == Potrace.THRESHOLD_AUTO:
            colorStops = histogram.multilevelThresholding(steps)
        else:
            threshold = self._paramThreshold()
            # If blackOnWhite, compute thresholds below the main threshold
            # otherwise above it.
            if self._params['blackOnWhite']:
                colorStops = histogram.multilevelThresholding(
                    steps - 1, 0, threshold
                )
                colorStops.append(threshold)
            else:
                colorStops = histogram.multilevelThresholding(
                    steps - 1, threshold, 255
                )
                colorStops.insert(0, threshold)

        if self._params['blackOnWhite']:
            colorStops.reverse()

        return self._calcColorIntensity(colorStops)

    def _getRangesEquallyDistributed(self):
        """
        Calculate equally distributed color ranges.

        Returns
        -------
        list of dict
            A list of equally distributed color ranges with intensities.

        """
        blackOnWhite = self._params['blackOnWhite']
        threshold = self._paramThreshold()
        colorsToThreshold = threshold if blackOnWhite else 255 - threshold
        steps = self._paramSteps(count=False)

        stepSize = colorsToThreshold / float(steps)
        colorStops = []

        i = steps - 1
        while i >= 0:
            factor = i / float(steps - 1) if steps > 1 else 0
            th = min(colorsToThreshold, (i + 1) * stepSize)
            th = th if blackOnWhite else 255 - th
            i -= 1
            colorStops.append(th)

        return self._calcColorIntensity(colorStops)

    def _paramSteps(self, count=False):
        """
        Retrieve the number of steps or the steps list based on parameters.

        Parameters
        ----------
        count : bool, optional
            If True, return the count of steps. Otherwise, return the steps list. Defaults to False.

        Returns
        -------
        int or list
            The number of steps or the list of step thresholds.

        """
        steps = self._params['steps']

        if isinstance(steps, list):
            return len(steps) if count else steps

        if steps == Posterizer.STEPS_AUTO and self._params['threshold'] == Potrace.THRESHOLD_AUTO:
            return 4  # default to 4 if both steps and threshold are auto

        blackOnWhite = self._params['blackOnWhite']
        # How many possible color values from black/white up to threshold
        colorsCount = self._paramThreshold() if blackOnWhite else 255 - self._paramThreshold()

        if steps == Posterizer.STEPS_AUTO:
            # If there's a large color range, pick 4, otherwise 3
            return 4 if colorsCount > 200 else 3

        # If steps is numeric, clamp it between 2 and the available color range
        return min(colorsCount, max(2, steps))

    def _paramThreshold(self):
        """
        Determine the threshold value, calculating it if set to auto.

        Returns
        -------
        float
            The determined threshold value.

        """
        if self._calculatedThreshold is not None:
            return self._calculatedThreshold

        if self._params['threshold'] != Potrace.THRESHOLD_AUTO:
            self._calculatedThreshold = self._params['threshold']
            return self._calculatedThreshold

        # Automatic threshold
        twoThresholds = self._getImageHistogram().multilevelThresholding(2)
        if self._params['blackOnWhite']:
            self._calculatedThreshold = twoThresholds[1] if len(twoThresholds) > 1 else 128
        else:
            self._calculatedThreshold = twoThresholds[0] if len(twoThresholds) > 0 else 128

        return self._calculatedThreshold

    def _pathTags(self, noFillColor=False):
        """
        Generate SVG path tags based on color ranges.

        Parameters
        ----------
        noFillColor : bool, optional
            If True, do not apply fill colors to the paths. Defaults to False.

        Returns
        -------
        list of str
            A list of SVG path tags.

        """
        ranges = self._getRanges()
        blackOnWhite = self._params['blackOnWhite']

        if len(ranges) >= 10:
            ranges = self._addExtraColorStop(ranges)

        self._potrace.setParameters({'blackOnWhite': blackOnWhite})
        actualPrevLayersOpacity = 0
        path_tags = []

        for colorStop in ranges:
            thisLayerOpacity = colorStop['colorIntensity']

            if thisLayerOpacity == 0:
                path_tags.append('')
                continue

            # Compute the final opacity, layering on top of previous
            if not actualPrevLayersOpacity or thisLayerOpacity == 1:
                calculatedOpacity = thisLayerOpacity
            else:
                top = actualPrevLayersOpacity - thisLayerOpacity
                bot = actualPrevLayersOpacity - 1
                if abs(bot) < 1e-9:
                    calculatedOpacity = 0
                else:
                    calculatedOpacity = (top / bot)

                # Keep it tidy
                calculatedOpacity = float("{:.3f}".format(calculatedOpacity))
                calculatedOpacity = clamp(calculatedOpacity, 0, 1)

            actualPrevLayersOpacity = (
                actualPrevLayersOpacity + (1 - actualPrevLayersOpacity) * calculatedOpacity
            )

            self._potrace.setParameters({'threshold': colorStop['value']})
            if noFillColor:
                element = self._potrace.getPathTag(fillColor='')
            else:
                element = self._potrace.getPathTag()

            # Apply opacity
            element = set_html_attribute(element, 'fill-opacity',
                                         "{:.3f}".format(calculatedOpacity))

            # If there's no path data, skip it
            if calculatedOpacity == 0 or ' d=""' in element:
                path_tags.append('')
            else:
                path_tags.append(element)

        return path_tags

    def loadImage(self, target, callback):
        """
        Load an image and initialize Potrace with it.

        Parameters
        ----------
        target : str or PIL.Image.Image
            The image path or PIL Image to load.
        callback : function
            A callback function to execute after loading the image.

        """
        def internal_callback(err):
            self._calculatedThreshold = None
            callback(self, err)

        self._potrace.loadImage(target, internal_callback)

    def setParameters(self, params):
        """
        Update the posterizer parameters.

        Parameters
        ----------
        params : dict
            A dictionary of parameters to update.

        Raises
        ------
        ValueError
            If the 'steps' parameter is invalid.

        """
        if not params:
            return

        self._potrace.setParameters(params)

        if 'steps' in params:
            if (not isinstance(params['steps'], list) and
               (not is_number(params['steps']) or not between(params['steps'], 1, 255)) and
               params['steps'] != Posterizer.STEPS_AUTO):
                raise ValueError("Bad 'steps' value")

        for key in self._params:
            if key in params:
                self._params[key] = params[key]

        self._calculatedThreshold = None

    def getSymbol(self, id_):
        """
        Generate an SVG <symbol> tag with the traced paths.

        Parameters
        ----------
        id_ : str
            The ID to assign to the SVG symbol.

        Returns
        -------
        str
            An SVG <symbol> element as a string.

        """
        width = self._potrace._luminanceData.width
        height = self._potrace._luminanceData.height
        paths = self._pathTags(noFillColor=True)

        return (
            f'<symbol viewBox="0 0 {width} {height}" id="{id_}">' +
            ''.join(paths) +
            '</symbol>'
        )

    def getSVG(self):
        """
        Generate the complete SVG representation of the image.

        Returns
        -------
        str
            A string containing the full SVG content.

        """
        width = self._potrace._luminanceData.width
        height = self._potrace._luminanceData.height
        tags = self._pathTags(noFillColor=False)

        bg_part = ''
        if self._params['background'] != Potrace.COLOR_TRANSPARENT:
            bg_part = (
                f'<rect x="0" y="0" width="100%" height="100%" '
                f'fill="{self._params["background"]}" />\n\t'
            )

        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" '
            f'height="{height}" '
            f'viewBox="0 0 {width} {height}" '
            f'version="1.1">\n\t'
            + bg_part
            + '\n\t'.join(tags)
            + '\n</svg>'
        )

        # Remove extra blank lines
        return "\n".join([line for line in svg.splitlines() if line.strip()])
