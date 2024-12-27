# PythonPotrace/Posterizer.py

import math

from .Potrace import Potrace
from .types.Histogram import Histogram
from .utils import between, clamp, luminance
from .utils import set_html_attribute as setHtmlAttr


class Posterizer:
    """
    Takes multiple samples using Potrace with different threshold
    settings and combines output into a single file.
    """

    STEPS_AUTO = -1
    FILL_SPREAD = "spread"
    FILL_DOMINANT = "dominant"
    FILL_MEDIAN = "median"
    FILL_MEAN = "mean"
    RANGES_AUTO = "auto"
    RANGES_EQUAL = "equal"

    def __init__(self, options=None):
        self._potrace = Potrace()
        self._calculatedThreshold = None
        self._params = {
            "threshold": Potrace.THRESHOLD_AUTO,
            "blackOnWhite": True,
            "steps": Posterizer.STEPS_AUTO,
            "background": Potrace.COLOR_TRANSPARENT,
            "fillStrategy": Posterizer.FILL_DOMINANT,
            "rangeDistribution": Posterizer.RANGES_AUTO,
        }

        if options:
            self._validateParameters(options)  # Added validation
            self.setParameters(options)

    def _validateParameters(self, params):
        if params and "steps" in params:
            steps = params["steps"]
            if isinstance(steps, list):
                for s in steps:
                    if not isinstance(s, int) or s < 0 or s > 255:
                        raise ValueError(
                            "Elements of 'steps' must be integers in [0..255]"
                        )
            elif isinstance(steps, int) and (
                steps < 1 and steps != Posterizer.STEPS_AUTO
            ):
                raise ValueError("'steps' must be in [1..255], or -1 for STEPS_AUTO.")
        if (
            params
            and "threshold" in params
            and params["threshold"] != Potrace.THRESHOLD_AUTO
        ):
            if (
                not isinstance(params["threshold"], (int, float))
                or params["threshold"] < 0
                or params["threshold"] > 255
            ):
                raise ValueError(
                    "'threshold' must be in [0..255], or -1 for THRESHOLD_AUTO."
                )

        if (
            params
            and "fillStrategy" in params
            and params["fillStrategy"]
            not in [
                Posterizer.FILL_SPREAD,
                Posterizer.FILL_DOMINANT,
                Posterizer.FILL_MEAN,
                Posterizer.FILL_MEDIAN,
            ]
        ):
            raise ValueError(
                f"'fillStrategy' must be one of the following {Posterizer.FILL_SPREAD}, {Posterizer.FILL_DOMINANT}, {Posterizer.FILL_MEAN}, {Posterizer.FILL_MEDIAN}"
            )

        if (
            params
            and "rangeDistribution" in params
            and params["rangeDistribution"]
            not in [Posterizer.RANGES_AUTO, Posterizer.RANGES_EQUAL]
        ):
            raise ValueError(
                f"'rangeDistribution' must be one of the following {Posterizer.RANGES_AUTO}, {Posterizer.RANGES_EQUAL}"
            )

    def _getImageHistogram(self):
        return self._potrace._luminanceData.histogram()

    def _paramSteps(self, count=False):
        steps = self._params["steps"]

        if isinstance(steps, list):
            return len(steps) if count else steps

        if (
            steps == Posterizer.STEPS_AUTO
            and self._params["threshold"] == Potrace.THRESHOLD_AUTO
        ):
            return 4

        blackOnWhite = self._params["blackOnWhite"]
        colorsCount = (
            self._paramThreshold() if blackOnWhite else 255 - self._paramThreshold()
        )

        if steps == Posterizer.STEPS_AUTO:
            return 4 if colorsCount > 200 else 3

        # Return numeric value, making sure it doesn't exceed the color count
        return min(colorsCount, max(2, steps))

    def _paramThreshold(self):
        if self._calculatedThreshold is not None:
            return self._calculatedThreshold

        # If threshold is not auto, just return it
        if self._params["threshold"] != Potrace.THRESHOLD_AUTO:
            self._calculatedThreshold = self._params["threshold"]
            return self._calculatedThreshold

        # If threshold is auto, we do a 2-level thresholding to find a suitable threshold
        twoThresholds = self._getImageHistogram().multilevelThresholding(2)
        if self._params["blackOnWhite"]:
            self._calculatedThreshold = (
                twoThresholds[1] if len(twoThresholds) > 1 else 128
            )
        else:
            self._calculatedThreshold = twoThresholds[0] if len(twoThresholds) else 128

        return self._calculatedThreshold

    def _calcColorIntensity(self, colorStops):
        """
        For each threshold in colorStops, pick a representative color intensity
        based on fillStrategy.
        """
        blackOnWhite = self._params["blackOnWhite"]
        colorSelectionStrat = self._params["fillStrategy"]
        histogram = (
            None
            if colorSelectionStrat == self.FILL_SPREAD
            else self._getImageHistogram()
        )
        fullRange = abs(self._paramThreshold() - (0 if blackOnWhite else 255))

        results = []
        for i, threshold in enumerate(colorStops):
            # The next threshold for reference in bounding the color
            if i + 1 == len(colorStops):
                nextValue = -1 if blackOnWhite else 256
            else:
                nextValue = colorStops[i + 1]

            rangeStart = round(nextValue + 1) if blackOnWhite else round(threshold)
            rangeEnd = round(threshold) if blackOnWhite else round(nextValue - 1)
            factor = i / (len(colorStops) - 1) if len(colorStops) > 1 else 0
            intervalSize = rangeEnd - rangeStart

            if colorSelectionStrat == self.FILL_SPREAD:
                # Spread color across range
                # We want 0 or 255 at the most saturated end, scaled by factor
                color = (rangeStart if blackOnWhite else rangeEnd) + (
                    1 if blackOnWhite else -1
                ) * intervalSize * max(0.5, fullRange / 255) * factor
                color = round(color)
                pixelCount = 1  # not used for this strategy
            else:
                stats = histogram.getStats(rangeStart, rangeEnd)
                pixelCount = stats["pixels"]
                if pixelCount == 0:
                    results.append({"value": threshold, "colorIntensity": 0})
                    continue

                if colorSelectionStrat == self.FILL_DOMINANT:
                    dom = histogram.getDominantColor(
                        rangeStart, rangeEnd, clamp(intervalSize, 1, 5)
                    )
                    color = dom if dom >= 0 else -1
                elif colorSelectionStrat == self.FILL_MEAN:
                    color = stats["levels"]["mean"]
                elif colorSelectionStrat == self.FILL_MEDIAN:
                    color = stats["levels"]["median"]
                else:
                    color = -1

            if color == -1:
                results.append({"value": threshold, "colorIntensity": 0})
                continue

            # We don’t want colors to be too close to each other, so we add spacing
            if i != 0 and intervalSize > 0:
                if blackOnWhite:
                    # Don’t let color go beyond interval end minus 10%
                    color = clamp(
                        color, rangeStart, rangeEnd - round(intervalSize * 0.1)
                    )
                else:
                    color = clamp(
                        color, rangeStart + round(intervalSize * 0.1), rangeEnd
                    )

            # Convert to [0..1] intensity
            colorIntensity = (255 - color if blackOnWhite else color) / 255
            results.append({"value": threshold, "colorIntensity": colorIntensity})

        return results

    def _getRangesAuto(self):
        """
        Automatically calculates threshold stops with the histogram's multilevelThresholding.
        """
        histogram = self._getImageHistogram()
        steps = self._paramSteps(True)
        colorStops = []

        # If threshold is auto, we can do a plain multilevelThresholding
        if self._params["threshold"] == Potrace.THRESHOLD_AUTO:
            colorStops = histogram.multilevelThresholding(steps)
        else:
            threshold = self._paramThreshold()
            if self._params["blackOnWhite"]:
                # Then we do one fewer threshold below our main threshold
                colorStops = histogram.multilevelThresholding(steps - 1, 0, threshold)
                colorStops.append(threshold)
            else:
                # One fewer threshold above our main threshold
                colorStops = histogram.multilevelThresholding(steps - 1, threshold, 255)
                colorStops.insert(0, threshold)

        if self._params["blackOnWhite"]:
            colorStops.reverse()

        return self._calcColorIntensity(colorStops)

    def _getRangesEquallyDistributed(self):
        """
        If user wants color steps at equal intervals from threshold to black or white.
        """
        blackOnWhite = self._params["blackOnWhite"]
        threshold = self._paramThreshold()
        colorsToThreshold = threshold if blackOnWhite else 255 - threshold
        steps = self._paramSteps()

        stepSize = colorsToThreshold / steps if steps > 0 else colorsToThreshold
        colorStops = []
        i = steps - 1
        while i >= 0:
            factor = i / (steps - 1) if steps > 1 else 0
            thr = min(colorsToThreshold, (i + 1) * stepSize)
            thr = thr if blackOnWhite else (255 - thr)
            colorStops.append(thr)
            i -= 1

        return self._calcColorIntensity(colorStops)

    def _getRanges(self):
        """
        Prepares array of color stops (thresholds) for the final layered tracing.
        """
        steps = self._params["steps"]

        # If steps is a user-provided array
        if isinstance(steps, list):
            blackOnWhite = self._params["blackOnWhite"]
            threshold = self._paramThreshold()

            # Deduplicate & keep in 0..255
            arrayStops = sorted(
                set([s for s in steps if 0 <= s <= 255]), reverse=blackOnWhite
            )

            if blackOnWhite and (not arrayStops or arrayStops[0] < threshold):
                arrayStops.insert(0, threshold)
            elif not blackOnWhite and arrayStops and arrayStops[-1] < threshold:
                arrayStops.append(threshold)

            if not arrayStops:
                arrayStops = [threshold]

            return self._calcColorIntensity(arrayStops)

        # If steps is not array, we rely on auto or equally distributed
        if self._params["rangeDistribution"] == self.RANGES_AUTO:
            return self._getRangesAuto()
        else:
            return self._getRangesEquallyDistributed()

    def _addExtraColorStop(self, ranges):
        """
        Fine tuning: if last range is bigger than 25, we add a new color stop
        for shadows. This is to improve presence of darkest pixels when blackOnWhite=True
        or brightest when blackOnWhite=False.
        """
        blackOnWhite = self._params["blackOnWhite"]
        if not ranges:
            return ranges

        lastColorStop = ranges[-1]
        lastValue = lastColorStop["value"]
        lastRangeFrom = 0 if blackOnWhite else lastValue
        lastRangeTo = lastValue if blackOnWhite else 255

        if (
            abs(lastRangeTo - lastRangeFrom) > 25
            and lastColorStop["colorIntensity"] != 1
        ):
            histogram = self._getImageHistogram()
            stats = histogram.getStats(lastRangeFrom, lastRangeTo)
            mean = stats["levels"]["mean"]
            std = stats["levels"]["stdDev"]

            # Attempt a new color stop that’s near (mean +/- std)
            candidate = 25
            if (mean + std) <= 25:
                candidate = mean + std
            elif (mean - std) <= 25:
                candidate = mean - std

            candidate = int(candidate)
            if blackOnWhite:
                # stats for 0..candidate
                newStats = histogram.getStats(0, candidate)
                color = newStats["levels"]["mean"]
                newIntensity = (255 - color) / 255 if not math.isnan(color) else 0
                ranges.append(
                    {
                        "value": abs((0 if blackOnWhite else 255) - candidate),
                        "colorIntensity": newIntensity,
                    }
                )
            else:
                # stats for candidate..255
                newStats = histogram.getStats(candidate, 255)
                color = newStats["levels"]["mean"]
                newIntensity = (color / 255) if not math.isnan(color) else 0
                ranges.append({"value": candidate, "colorIntensity": newIntensity})

        return ranges

    def _pathTags(self, noFillColor=False):
        """
        Traces image multiple times for each threshold in our color stops and returns an array of <path> tags.
        """
        ranges = self._getRanges()
        blackOnWhite = self._params["blackOnWhite"]

        if len(ranges) >= 10:
            ranges = self._addExtraColorStop(ranges)

        self._potrace.setParameters({"blackOnWhite": blackOnWhite})
        actualPrevLayersOpacity = 0

        result = []
        for colorStop in ranges:
            thisLayerOpacity = colorStop["colorIntensity"]

            if thisLayerOpacity == 0:
                result.append("")
                continue

            # Some hack to approximate layering with partial alpha
            if not actualPrevLayersOpacity or thisLayerOpacity == 1:
                calculatedOpacity = thisLayerOpacity
            else:
                calculatedOpacity = (actualPrevLayersOpacity - thisLayerOpacity) / (
                    actualPrevLayersOpacity - 1.0
                )
                calculatedOpacity = round(clamp(calculatedOpacity, 0, 1), 3)

            calculatedOpacity = clamp(calculatedOpacity, 0, 1)

            actualPrevLayersOpacity = (
                actualPrevLayersOpacity
                + (1 - actualPrevLayersOpacity) * calculatedOpacity
            )

            # Now do the trace for that threshold
            self._potrace.setParameters({"threshold": colorStop["value"]})
            element = self._potrace.getPathTag("" if noFillColor else None)

            # Insert fill-opacity, even if zero, otherwise the layer wont be transparent!
            element = setHtmlAttr(element, "fill-opacity", f"{calculatedOpacity:.3f}")

            canBeIgnored = (calculatedOpacity == 0) or (' d=""' in element)

            result.append("" if canBeIgnored else element)

        return result

    def loadImage(self, target, callback=lambda err: None):
        """
        Loads image. `target` can be a path, PIL Image, or something the underlying Potrace loadImage can handle.
        """

        def after_load(err):
            self._calculatedThreshold = None
            callback(err)

        self._potrace.loadImage(target, after_load)

    def setParameters(self, params):
        """
        Overrides or adds new parameters.
        """
        if not params:
            return

        self._validateParameters(params)
        self._potrace.setParameters(params)

        for key in self._params:
            if key in params:
                oldVal = self._params[key]
                self._params[key] = params[key]
                if oldVal != self._params[key] and key not in ["background", "color"]:
                    self._calculatedThreshold = None
        # Reset threshold if relevant param changed

    def getSymbol(self, id_value):
        """
        Returns image as <symbol> tag. Always has viewBox specified
        """
        width = self._potrace._luminanceData.width
        height = self._potrace._luminanceData.height
        paths = self._pathTags(noFillColor=True)
        joined = "".join(paths)
        return (
            f'<symbol viewBox="0 0 {width} {height}" id="{id_value}">{joined}</symbol>'
        )

    def getSVG(self):
        width = self._potrace._luminanceData.width
        height = self._potrace._luminanceData.height

        tags = self._pathTags(noFillColor=False)
        background = self._params["background"]
        rectTag = ""
        if background != Potrace.COLOR_TRANSPARENT:
            rectTag = f'<rect x="0" y="0" width="100%" height="100%" fill="{background}" />\n\t'

        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" version="1.1">\n\t'
            f"{rectTag}" + "\n\t".join(tags) + "\n</svg>"
        )

        # Remove extra blank lines introduced by \n\t
        return svg.replace(r"\n\t\n", "\n").replace(r"\n\t\t", "\n\t")
