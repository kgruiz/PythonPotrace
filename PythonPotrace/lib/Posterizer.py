# Posterizer.py
#
# This is a Python translation of Posterizer.js, maintaining the same interface and functionality.
# It uses Pillow (PIL) instead of Jimp to handle image loading and processing.

from .Potrace import Potrace
from . import utils

class Posterizer:
    """
    Combine multiple Potrace samples with different threshold settings into a single SVG file.

    Parameters
    ----------
    options : dict, optional
        Dictionary of Posterizer options.

    Attributes
    ----------
    STEPS_AUTO : int
        Automatic step selection.
    FILL_SPREAD : str
        Strategy to spread fill colors.
    FILL_DOMINANT : str
        Strategy to use dominant fill colors.
    FILL_MEDIAN : str
        Strategy to use median fill colors.
    FILL_MEAN : str
        Strategy to use mean fill colors.
    RANGES_AUTO : str
        Automatic range distribution.
    RANGES_EQUAL : str
        Equally distributed range.

    """

    # Inherit constants from Potrace class
    for key in Potrace.__dict__:
        if key.isupper():
            setattr(__class__, key, getattr(Potrace, key))

    STEPS_AUTO = -1
    FILL_SPREAD = 'spread'
    FILL_DOMINANT = 'dominant'
    FILL_MEDIAN = 'median'
    FILL_MEAN = 'mean'

    RANGES_AUTO = 'auto'
    RANGES_EQUAL = 'equal'

    def __init__(self, options=None):
        self._potrace = Potrace()

        self._calculatedThreshold = None

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

    def _addExtraColorStop(self, ranges):
        """
        Fine-tune color ranges by adding an extra color stop if necessary.

        If the last range exceeds 10% of the color space, add another color stop
        to enhance shadows and line art.

        Parameters
        ----------
        ranges : list
            List of existing color stops.

        Returns
        -------
        list
            Updated list of color stops.
        """
        blackOnWhite = self._params['blackOnWhite']
        lastColorStop = ranges[-1]
        lastRangeFrom = 0 if blackOnWhite else lastColorStop['value']
        lastRangeTo = lastColorStop['value'] if blackOnWhite else 255

        if (lastRangeTo - lastRangeFrom > 25) and (lastColorStop['colorIntensity'] != 1):
            histogram = self._getImageHistogram()
            stats = histogram.getStats(lastRangeFrom, lastRangeTo)['levels']

            if stats['mean'] + stats['stdDev'] <= 25:
                newColorStopValue = stats['mean'] + stats['stdDev']
            elif stats['mean'] - stats['stdDev'] <= 25:
                newColorStopValue = stats['mean'] - stats['stdDev']
            else:
                newColorStopValue = 25

            if blackOnWhite:
                newStats = histogram.getStats(0, newColorStopValue)
            else:
                newStats = histogram.getStats(newColorStopValue, 255)

            newColor = newStats['levels']['mean']

            ranges.append({
                'value': abs(0 if blackOnWhite else 255 - newColorStopValue),
                'colorIntensity': 0 if newColor is None else (
                    (255 - newColor) / 255 if blackOnWhite else (newColor / 255)
                )
            })

        return ranges

    def _calcColorIntensity(self, colorStops):
        """
        Calculate color intensity for each color stop.

        Parameters
        ----------
        colorStops : list
            List of color stop values.

        Returns
        -------
        list
            List of dictionaries with 'value' and 'colorIntensity'.
        """
        blackOnWhite = self._params['blackOnWhite']
        colorSelectionStrategy = self._params['fillStrategy']
        histogram = None
        if colorSelectionStrategy != Posterizer.FILL_SPREAD:
            histogram = self._getImageHistogram()

        fullRange = abs(self._paramThreshold() - (0 if blackOnWhite else 255))

        intensity_stops = []
        for index, stop in enumerate(colorStops):
            if index + 1 == len(colorStops):
                nextValue = -1 if blackOnWhite else 256
            else:
                nextValue = colorStops[index + 1]['value']

            rangeStart = round(nextValue + 1) if blackOnWhite else round(stop['value'])
            rangeEnd = round(stop['value']) if blackOnWhite else round(nextValue - 1)
            factor = index / (len(colorStops) - 1) if len(colorStops) > 1 else 0
            intervalSize = rangeEnd - rangeStart

            if histogram:
                stats = histogram.getStats(rangeStart, rangeEnd)
            else:
                stats = {'levels': {'mean': 0, 'median': 0, 'stdDev': 0, 'unique': 0}}

            color = -1

            if stats['pixels'] == 0:
                intensity_stops.append({'value': stop['value'], 'colorIntensity': 0})
                continue

            if colorSelectionStrategy == Posterizer.FILL_SPREAD:
                color = (rangeStart + (intervalSize * max(0.5, fullRange / 255) * factor)) \
                        if blackOnWhite else \
                        (rangeEnd - (intervalSize * max(0.5, fullRange / 255) * factor))
            elif colorSelectionStrategy == Posterizer.FILL_DOMINANT:
                tolerance = utils.clamp(intervalSize, 1, 5)
                color = histogram.getDominantColor(rangeStart, rangeEnd, tolerance)
            elif colorSelectionStrategy == Posterizer.FILL_MEAN:
                color = stats['levels']['mean']
            elif colorSelectionStrategy == Posterizer.FILL_MEDIAN:
                color = stats['levels']['median']

            if index != 0:
                if blackOnWhite:
                    color = utils.clamp(color, rangeStart, round(rangeEnd - intervalSize * 0.1))
                else:
                    color = utils.clamp(color, round(rangeStart + intervalSize * 0.1), rangeEnd)

            intensity = 0 if color == -1 else (
                (255 - color) / 255 if blackOnWhite else (color / 255)
            )
            intensity_stops.append({
                'value': stop['value'],
                'colorIntensity': intensity
            })

        return intensity_stops

    def _getImageHistogram(self):
        """
        Retrieve the histogram of the image.

        Returns
        -------
        Histogram
            Histogram instance of the image.
        """
        return self._potrace._luminanceData.histogram()

    def _getRanges(self):
        """
        Process parameters to return a normalized array of color stops.

        Returns
        -------
        list
            List of color stops with 'value' and 'colorIntensity'.
        """
        steps = self._paramSteps()

        if not isinstance(steps, list):
            if self._params['rangeDistribution'] == Posterizer.RANGES_AUTO:
                return self._getRangesAuto()
            else:
                return self._getRangesEquallyDistributed()

        # Steps is an array of thresholds; preprocess it
        colorStops = []
        threshold = self._paramThreshold()
        blackOnWhite = self._params['blackOnWhite']

        for item in steps:
            if item not in colorStops and utils.between(item, 0, 255):
                colorStops.append(item)

        if not colorStops:
            colorStops.append(threshold)

        colorStops.sort(reverse=blackOnWhite)

        if blackOnWhite and colorStops[0] < threshold:
            colorStops.insert(0, threshold)
        elif not blackOnWhite and colorStops[-1] < threshold:
            colorStops.append(threshold)

        return self._calcColorIntensity(colorStops)

    def _getRangesAuto(self):
        """
        Calculate color stops using an automatic thresholding algorithm.

        Returns
        -------
        list
            List of color stops with 'value' and 'colorIntensity'.
        """
        histogram = self._getImageHistogram()
        steps = self._paramSteps(count=True)
        steps = steps if isinstance(steps, int) else 4  # Default steps

        if self._params['threshold'] == Potrace.THRESHOLD_AUTO:
            colorStops = histogram.multilevelThresholding(steps)
        else:
            threshold = self._paramThreshold()
            if self._params['blackOnWhite']:
                colorStops = histogram.multilevelThresholding(steps - 1, 0, threshold)
                colorStops.append(threshold)
            else:
                colorStops = histogram.multilevelThresholding(steps - 1, threshold, 255)
                colorStops.insert(0, threshold)

        if self._params['blackOnWhite']:
            colorStops = list(reversed(colorStops))

        return self._calcColorIntensity(colorStops)

    def _getRangesEquallyDistributed(self):
        """
        Calculate color stops with equally distributed thresholds.

        Returns
        -------
        list
            List of color stops with 'value' and 'colorIntensity'.
        """
        blackOnWhite = self._params['blackOnWhite']
        colorsToThreshold = self._paramThreshold() if blackOnWhite else 255 - self._paramThreshold()
        steps = self._paramSteps(count=True)

        stepSize = colorsToThreshold / steps
        colorStops = []
        for i in range(steps - 1, -1, -1):
            factor = i / (steps - 1) if steps > 1 else 0
            threshold = min(colorsToThreshold, (i + 1) * stepSize)
            threshold = threshold if blackOnWhite else 255 - threshold
            colorStops.append(threshold)

        return self._calcColorIntensity(colorStops)

    def _paramSteps(self, count=False):
        """
        Retrieve the number of steps based on parameters.

        Parameters
        ----------
        count : bool, optional
            If True, return the number of steps; otherwise, return step value.

        Returns
        -------
        int
            Number of steps or step value.
        """
        steps = self._params['steps']

        if isinstance(steps, list):
            return steps if count else len(steps)

        if steps == Posterizer.STEPS_AUTO and self._params['threshold'] == Potrace.THRESHOLD_AUTO:
            return 4 if count else Posterizer.STEPS_AUTO

        blackOnWhite = self._params['blackOnWhite']
        colorsCount = self._paramThreshold() if blackOnWhite else 255 - self._paramThreshold()

        if steps == Posterizer.STEPS_AUTO:
            return 4 if colorsCount > 200 else 3
        else:
            return min(colorsCount, max(2, steps))

    def _paramThreshold(self):
        """
        Retrieve the valid threshold value.

        Returns
        -------
        int
            Valid threshold value.
        """
        if self._calculatedThreshold is not None:
            return self._calculatedThreshold

        if self._params['threshold'] != Potrace.THRESHOLD_AUTO:
            self._calculatedThreshold = self._params['threshold']
            return self._calculatedThreshold

        twoThresholds = self._getImageHistogram().multilevelThresholding(2)
        if self._params['blackOnWhite']:
            self._calculatedThreshold = twoThresholds[1] if len(twoThresholds) > 1 else 128
        else:
            self._calculatedThreshold = twoThresholds[0] if len(twoThresholds) > 0 else 128

        self._calculatedThreshold = self._calculatedThreshold or 128

        return self._calculatedThreshold

    def _pathTags(self, noFillColor=False):
        """
        Generate SVG path tags by running Potrace with different thresholds.

        Parameters
        ----------
        noFillColor : bool, optional
            If True, no fill color is applied.

        Returns
        -------
        list
            List of SVG path elements as strings.
        """
        ranges = self._getRanges()
        potrace = self._potrace
        blackOnWhite = self._params['blackOnWhite']

        if len(ranges) >= 10:
            ranges = self._addExtraColorStop(ranges)

        potrace.setParameters({'blackOnWhite': blackOnWhite})

        actualPrevLayersOpacity = 0

        path_elements = []
        for colorStop in ranges:
            thisLayerOpacity = colorStop['colorIntensity']

            if thisLayerOpacity == 0:
                path_elements.append('')
                continue

            if not actualPrevLayersOpacity or thisLayerOpacity == 1:
                calculatedOpacity = thisLayerOpacity
            else:
                calculatedOpacity = (actualPrevLayersOpacity - thisLayerOpacity) / (actualPrevLayersOpacity - 1)

            calculatedOpacity = utils.clamp(round(calculatedOpacity, 3), 0, 1)
            actualPrevLayersOpacity += (1 - actualPrevLayersOpacity) * calculatedOpacity

            potrace.setParameters({'threshold': colorStop['value']})

            element = potrace.getPathTag('' if noFillColor else None)
            element = utils.setHtmlAttr(element, 'fill-opacity', f"{calculatedOpacity:.3f}")

            canBeIgnored = (calculatedOpacity == 0) or ('d=""' in element)

            # Set fill color based on opacity
            # c = round(abs((0 if blackOnWhite else 255) - 255 * thisLayerOpacity))
            # element = utils.setHtmlAttr(element, 'fill', f'rgb({c}, {c}, {c})')
            # element = utils.setHtmlAttr(element, 'fill-opacity', '')

            path_elements.append('' if canBeIgnored else element)

        return path_elements

    def loadImage(self, target, callback):
        """
        Load the image for processing.

        Parameters
        ----------
        target : str or Image
            Image source, such as a file path or Pillow Image instance.
        callback : function
            Callback function with signature (error). `error` is None on success or an Exception on failure.
        """
        def after_load(err):
            self._calculatedThreshold = None
            callback(err)

        self._potrace.loadImage(target, after_load)

    def setParameters(self, params):
        """
        Set Posterizer parameters.

        Parameters
        ----------
        params : dict
            Dictionary of Posterizer options.
        """
        if not params:
            return

        self._potrace.setParameters(params)

        if 'steps' in params and not isinstance(params['steps'], list):
            steps = params['steps']
            if not (isinstance(steps, int) and utils.between(steps, 1, 255)):
                raise ValueError("Bad 'steps' value")

        for key in self._params:
            if key in params:
                self._params[key] = params[key]

        self._calculatedThreshold = None

    def getSymbol(self, id_):
        """
        Generate an SVG <symbol> tag for the image.

        Parameters
        ----------
        id_ : str
            Symbol ID for the SVG.

        Returns
        -------
        str
            String of a <symbol> element.
        """
        width = self._potrace._luminanceData.width
        height = self._potrace._luminanceData.height
        paths = self._pathTags(noFillColor=True)

        return f'<symbol viewBox="0 0 {width} {height}" id="{id_}">' + ''.join(paths) + '</symbol>'

    def getSVG(self):
        """
        Generate the complete SVG image.

        Returns
        -------
        str
            String of the complete SVG document.
        """
        width = self._potrace._luminanceData.width
        height = self._potrace._luminanceData.height

        tags = self._pathTags(noFillColor=False)

        svg_elements = []
        svg_elements.append('<svg xmlns="http://www.w3.org/2000/svg" '
                            f'width="{width}" height="{height}" '
                            f'viewBox="0 0 {width} {height}" version="1.1">')

        if self._params['background'] != Potrace.COLOR_TRANSPARENT:
            svg_elements.append(f'\t<rect x="0" y="0" width="100%" height="100%" fill="{self._params["background"]}" />')

        svg_elements.extend([f'\t{tag}' for tag in tags if tag])
        svg_elements.append('</svg>')

        # Join the SVG elements, removing any empty lines caused by ignored paths
        svg_content = '\n'.join(svg_elements).replace('\n\t\n', '\n')
        return svg_content
