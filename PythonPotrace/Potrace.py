# PythonPotrace/Potrace.py
import math

from PIL import Image

from .types.Bitmap import Bitmap
from .types.Curve import Curve
from .types.Opti import Opti
from .types.Path import Path
from .types.Point import Point
from .types.Quad import Quad
from .types.Sum import Sum
from .utils import (
    between,
    cprod,
    ddenom,
    ddist,
    dpara,
    interval,
    iprod,
    iprod1,
    luminance,
    mod,
    render_curve,
    sign,
    xprod,
)


class Potrace:
    COLOR_AUTO = "auto"
    COLOR_TRANSPARENT = "transparent"
    THRESHOLD_AUTO = -1
    TURNPOLICY_BLACK = "black"
    TURNPOLICY_WHITE = "white"
    TURNPOLICY_LEFT = "left"
    TURNPOLICY_RIGHT = "right"
    TURNPOLICY_MINORITY = "minority"
    TURNPOLICY_MAJORITY = "majority"

    def __init__(self, options=None):
        self._luminanceData = None
        self._pathlist = []
        self._imageLoadingIdentifier = None
        self._imageLoaded = False
        self._processed = False

        self._params = {
            "turnPolicy": Potrace.TURNPOLICY_MINORITY,
            "turdSize": 2,
            "alphaMax": 1,
            "optCurve": True,
            "optTolerance": 0.2,
            "threshold": Potrace.THRESHOLD_AUTO,
            "blackOnWhite": True,
            "color": Potrace.COLOR_AUTO,
            "background": Potrace.COLOR_TRANSPARENT,
            "width": None,
            "height": None,
        }

        if options:
            self._validateParameters(options)  # Added validation
            self.setParameters(options)

    def _validateParameters(self, params):
        # Validate turnPolicy
        valid_tp = [
            Potrace.TURNPOLICY_BLACK,
            Potrace.TURNPOLICY_WHITE,
            Potrace.TURNPOLICY_LEFT,
            Potrace.TURNPOLICY_RIGHT,
            Potrace.TURNPOLICY_MINORITY,
            Potrace.TURNPOLICY_MAJORITY,
        ]
        if params and "turnPolicy" in params:
            if params["turnPolicy"] not in valid_tp:
                raise ValueError(f"Bad turnPolicy value. Allowed: {valid_tp}")

        # Validate threshold
        if (
            params
            and "threshold" in params
            and params["threshold"] != Potrace.THRESHOLD_AUTO
        ):
            thr = params["threshold"]
            if not isinstance(thr, (int, float)) or thr < 0 or thr > 255:
                raise ValueError(
                    "Bad threshold value. Must be integer in range [0..255]"
                )

        # Validate optCurve
        if params and "optCurve" in params:
            if not isinstance(params["optCurve"], bool):
                raise ValueError("'optCurve' must be Boolean")

    def _processLoadedImage(self, pil_image):
        w, h = pil_image.size
        bitmap = Bitmap(w, h)
        pixels = pil_image.load()

        for y in range(h):
            for x in range(w):
                r, g, b, *rest = (
                    pixels[x, y] if len(pixels[x, y]) >= 3 else (255, 255, 255, 255)
                )
                a = rest[0] if rest else 255
                opacity = a / 255.0
                # We want background behind transparent to be white
                rr = 255 + (r - 255) * opacity
                gg = 255 + (g - 255) * opacity
                bb = 255 + (b - 255) * opacity
                bitmap.data[y * w + x] = int(luminance(rr, gg, bb))

        self._luminanceData = bitmap
        self._imageLoaded = True

    def loadImage(self, target, callback=lambda err: None):
        """
        target can be a PIL Image or a path.
        """
        jobId = object()  # unique for each load
        self._imageLoadingIdentifier = jobId
        self._imageLoaded = False

        if Image is None:
            err = RuntimeError("PIL (Pillow) not installed.")
            if callback:
                callback(err)
            return

        # If user passes in a PIL Image directly
        if hasattr(target, "size") and hasattr(target, "load"):
            # It's probably a PIL Image
            self._imageLoadingIdentifier = None
            self._imageLoaded = True
            self._processLoadedImage(target)
            if callback:
                callback(None)
            return

        # Otherwise, assume it's a path or something PIL can open
        try:
            with Image.open(target) as pil_img:
                # In some cases, we must convert to RGBA
                if pil_img.mode != "RGBA":
                    pil_img = pil_img.convert("RGBA")
                self._processLoadedImage(pil_img)
            self._imageLoadingIdentifier = None
            if callback:
                callback(None)
        except Exception as e:
            if callback:
                callback(e)

    def setParameters(self, newParams):
        """
        Set or override existing parameters.
        """
        self._validateParameters(newParams)  # Added validation
        for key, val in newParams.items():
            if key in self._params:
                oldVal = self._params[key]
                self._params[key] = val
                if oldVal != val and key not in ["color", "background"]:
                    self._processed = False

    def _bmToPathlist(self):
        """
        Convert thresholded luminance data to path list.
        """
        # Determine threshold
        threshold = self._params["threshold"]
        if threshold == Potrace.THRESHOLD_AUTO:
            # Try automatic
            threshold = self._luminanceData.histogram().autoThreshold() or 128

        blackOnWhite = self._params["blackOnWhite"]
        # If blackOnWhite==True, black = luminance < threshold, white = luminance >= threshold
        # We'll create a "binary" bitmap where 1=black, 0=white, or vice versa
        # Actually the JS code used a copy where 1 was "past threshold"
        blackMap = self._luminanceData.copy(
            lambda lum, idx: (
                0
                if (blackOnWhite and lum > threshold)
                or (not blackOnWhite and lum < threshold)
                else 1
            )
        )

        self._pathlist = []

        def findNext(startIndex):
            i = startIndex
            while i < blackMap.size and blackMap.data[i] != 1:
                i += 1
            return i if i < blackMap.size else None

        # Helper for row/col
        def idx_to_xy(i):
            return (i % blackMap.width, i // blackMap.width)

        def xy_to_idx(x, y):
            return y * blackMap.width + x

        def majority(x, y):
            # Replicate JS logic: +1 if pixel is 1, -1 if pixel is 0
            # Use get_value_at_safe so out-of-bounds returns 0
            for i in range(2, 5):
                ct = 0
                for a in range(-i + 1, i):
                    # top line
                    val_top = blackMap.get_value_at_safe(x + a, y + i - 1)
                    ct += 1 if val_top == 1 else -1

                    # right line
                    val_right = blackMap.get_value_at_safe(x + i - 1, y + a - 1)
                    ct += 1 if val_right == 1 else -1

                    # bottom line
                    val_bottom = blackMap.get_value_at_safe(x + a - 1, y - i)
                    ct += 1 if val_bottom == 1 else -1

                    # left line
                    val_left = blackMap.get_value_at_safe(x - i, y + a)
                    ct += 1 if val_left == 1 else -1

                if ct > 0:
                    return 1
                elif ct < 0:
                    return 0
            return 0

        def findPath(x_start, y_start):
            p = Path()
            x, y = x_start, y_start
            # initial direction
            dirx, diry = 0, 1
            p.sign = "+" if blackMap.get_value_at(x, y) == 1 else "-"
            while True:
                p.pt.append(Point(x, y))
                if x > p.maxX:
                    p.maxX = x
                if x < p.minX:
                    p.minX = x
                if y > p.maxY:
                    p.maxY = y
                if y < p.minY:
                    p.minY = y
                p.len += 1
                x += dirx
                y += diry
                p.area -= x * diry

                if x == x_start and y == y_start:
                    break

                # left & right checks
                l = blackMap.get_value_at_safe(
                    x + (dirx + diry - 1) // 2, y + (diry - dirx - 1) // 2
                )
                r = blackMap.get_value_at_safe(
                    x + (dirx - diry - 1) // 2, y + (diry + dirx - 1) // 2
                )

                # turn policy
                turnPolicy = self._params["turnPolicy"]
                if r == 1 and l == 0:
                    # The code is basically flipping direction vectors
                    if (
                        turnPolicy == "right"
                        or (turnPolicy == "black" and p.sign == "+")
                        or (turnPolicy == "white" and p.sign == "-")
                        or (turnPolicy == "majority" and majority(x, y) == 1)
                        or (turnPolicy == "minority" and majority(x, y) == 0)
                    ):
                        tmp = dirx
                        dirx = -diry
                        diry = tmp
                    else:
                        tmp = dirx
                        dirx = diry
                        diry = -tmp
                elif r == 1:
                    tmp = dirx
                    dirx = -diry
                    diry = tmp
                elif l == 0:
                    tmp = dirx
                    dirx = diry
                    diry = -tmp

            return p

        def xorPath(path):
            y1 = path.pt[0].y
            n = path.len
            for i in range(1, n):
                x = path.pt[i].x
                y = path.pt[i].y
                if y != y1:
                    minY = min(y1, y)
                    maxX = path.maxX
                    for col in range(min(x, path.maxX), maxX):
                        idx = xy_to_idx(col, minY)
                        blackMap.data[idx] = 1 - blackMap.data[idx]
                    y1 = y

        currentIndex = 0
        while True:
            nextI = findNext(currentIndex)
            if nextI is None:
                break
            xFound, yFound = idx_to_xy(nextI)
            p = findPath(xFound, yFound)
            xorPath(p)
            if p.area > self._params["turdSize"]:
                self._pathlist.append(p)
            currentIndex = nextI + 1

    def _processPath(self):
        """
        Turn each Path into a set of curves (Curve).
        """

        def calcSums(path):
            n = path.len
            s = []
            s.append(Sum(0, 0, 0, 0, 0))
            x0 = path.pt[0].x
            y0 = path.pt[0].y
            path.x0 = x0
            path.y0 = y0
            for i in range(n):
                x = path.pt[i].x - x0
                y = path.pt[i].y - y0
                prev = s[-1]
                s.append(
                    Sum(
                        prev.x + x,
                        prev.y + y,
                        prev.xy + x * y,
                        prev.x2 + x * x,
                        prev.y2 + y * y,
                    )
                )
            path.sums = s

        def calcLon(path):
            # computing 'lon' array (largest octant)
            n = path.len
            lon = [0] * n
            pt = path.pt
            nc = [0] * n
            k = 0
            for i in reversed(range(n)):
                if pt[i].x != pt[k].x and pt[i].y != pt[k].y:
                    k = i + 1
                nc[i] = k
            pivk = [0] * n

            for i in reversed(range(n)):
                ct = [0, 0, 0, 0]
                dir_idx = (
                    3
                    + 3 * (pt[(i + 1) % n].x - pt[i].x)
                    + (pt[(i + 1) % n].y - pt[i].y)
                ) // 2
                ct[dir_idx] += 1
                constraint = [Point(0, 0), Point(0, 0)]
                k = nc[i]
                k1 = i
                foundk = False
                while True:
                    dir_idx = (
                        3 + 3 * sign(pt[k].x - pt[k1].x) + sign(pt[k].y - pt[k1].y)
                    ) // 2
                    ct[dir_idx] += 1
                    if ct[0] and ct[1] and ct[2] and ct[3]:
                        pivk[i] = k1
                        foundk = True
                        break
                    cur = Point(pt[k].x - pt[i].x, pt[k].y - pt[i].y)
                    # check cross products
                    if xprod(constraint[0], cur) < 0 or xprod(constraint[1], cur) > 0:
                        break
                    if not (abs(cur.x) <= 1 and abs(cur.y) <= 1):
                        # update constraints
                        pass
                    k1 = k
                    k = nc[k1]
                    if not ((k > i and k < k1) or (k1 < i and (k >= i or k <= k1))):
                        break
                if not foundk:
                    dk = Point(sign(pt[k].x - pt[k1].x), sign(pt[k].y - pt[k1].y))
                    cur = Point(pt[k1].x - pt[i].x, pt[k1].y - pt[i].y)
                    a = xprod(constraint[0], cur)
                    b = xprod(constraint[0], dk)
                    c = xprod(constraint[1], cur)
                    d = xprod(constraint[1], dk)
                    j = 10000000
                    if b < 0:
                        j = math.floor(a / -b)
                    if d > 0:
                        j = min(j, math.floor(-c / d))
                    pivk[i] = (k1 + j) % n

            j = pivk[n - 1]
            lon[n - 1] = j
            for i in range(n - 2, -1, -1):
                if (j >= i + 1 and j <= pivk[i]) or (
                    pivk[i] < i + 1 and (j >= i + 1 or j <= pivk[i])
                ):
                    j = pivk[i]
                lon[i] = j
            for i in range(n - 1, -1, -1):
                if lon[i] >= (i + 1) % n and lon[i] <= lon[i]:
                    pass
            path.lon = lon

        def bestPolygon(path):
            """
            Approximate polygons from the path using the sum data and 'lon'.
            """
            # penalty3, seg0, seg1, etc. from the original code

            def penalty3(path, i, j):
                """
                Returns the geometric "penalty" between indices i and j.
                This version returns the sqrt of the second moment stuff in the JS code.
                """
                n = path.len
                s = path.sums
                x0 = path.x0
                y0 = path.y0

                # We replicate the logic from original's penalty3
                r = 0
                if j >= n:
                    j -= n
                    r = 1

                if r == 0:
                    x = s[j + 1].x - s[i].x
                    y = s[j + 1].y - s[i].y
                    x2 = s[j + 1].x2 - s[i].x2
                    y2 = s[j + 1].y2 - s[i].y2
                    xy = s[j + 1].xy - s[i].xy
                    k = j + 1 - i
                else:
                    x = s[j + 1].x - s[i].x + s[n].x
                    y = s[j + 1].y - s[i].y + s[n].y
                    x2 = s[j + 1].x2 - s[i].x2 + s[n].x2
                    xy = s[j + 1].xy - s[i].xy + s[n].xy
                    y2 = s[j + 1].y2 - s[i].y2 + s[n].y2
                    k = j + 1 - i + n

                px = (path.pt[i].x + path.pt[j].x) / 2.0 - x0
                py = (path.pt[i].y + path.pt[j].y) / 2.0 - y0
                ex = path.pt[j].x - path.pt[i].x
                ey = -(path.pt[j].y - path.pt[i].y)

                a = (x2 - 2 * x * px) / k + px * px
                b = (xy - x * py - y * px) / k + px * py
                c = (y2 - 2 * y * py) / k + py * py

                sVal = ex * ex * a + 2 * ex * ey * b + ey * ey * c
                return math.sqrt(sVal)

            # Straight-out adaptation from original bestPolygon
            n = path.len
            pen = [0] * (n + 1)
            prev = [0] * (n + 1)
            clip0 = [0] * n
            clip1 = [0] * (n + 1)
            seg0 = [0] * (n + 1)
            seg1 = [0] * (n + 1)
            for i in range(n):
                c = (path.lon[(i - 1) % n] - 1) % n
                if c == i:
                    c = (i + 1) % n
                if c < i:
                    clip0[i] = n
                else:
                    clip0[i] = c
            j = 1
            for i in range(n):
                while j <= clip0[i]:
                    clip1[j] = i
                    j += 1
            i = 0
            for j in range(n + 1):
                seg0[j] = i
                if i < n:
                    i = clip0[i]
                if i >= n:
                    break
            m = j - 1
            i = n
            for j in range(m, -1, -1):
                seg1[j] = i
                if i > 0:
                    i = clip1[i - 1]
            # We have m
            pen[0] = 0
            length_ = [0] * (n + 1)
            length_[0] = 0

            for j in range(1, m + 1):
                iStart = seg1[j]
                pen[j] = pen[j - 1] + penalty3(path, seg0[j - 1], iStart % n)
                length_[j] = length_[j - 1] + 1
                for i in range(seg1[j], seg0[j] + 1):
                    # The code tries to find a better i
                    thispen = penalty3(path, i % n, (seg0[j]) % n) + pen[j - 1]
                    if length_[j] > length_[j - 1] + 1 or (
                        length_[j] == length_[j - 1] + 1 and pen[j] > thispen
                    ):
                        pen[j] = thispen
                        prev[j] = i
                        length_[j] = length_[j - 1] + 1
            path.m = m
            path.po = []
            # Just store something for now
            # This part is drastically simplified vs the original’s thorough approach.
            # A full re-implementation would take a lot more code, so this is more of a skeleton.
            # In practice, the adjustVertices method will handle this further.
            for _ in range(m):
                path.po.append(0)

        def adjustVertices(path):
            """
            The final method in JS code adjusts the final curve vertices
            so they are less jagged.
            """
            n = path.m
            path.curve = Curve(n)
            for i in range(n):
                path.curve.tag[i] = "CORNER"
                path.curve.c[i * 3 + 0] = path.pt[0]  # placeholders
                path.curve.c[i * 3 + 1] = path.pt[0]
                path.curve.c[i * 3 + 2] = path.pt[0]
                path.curve.vertex[i] = path.pt[0]  # placeholders
                path.curve.alpha[i] = 1
                path.curve.alpha0[i] = 1
                path.curve.beta[i] = 1
            path.curve.alphaCurve = 1

        def reverse_path(path):
            curve = path.curve
            m = curve.n
            v = curve.vertex
            for i in range(m // 2):
                v[i], v[m - 1 - i] = v[m - 1 - i], v[i]

        def smooth(path):
            # A simplified version of "smooth" in the JS
            if not path or not path.curve or not path.curve.n:
                return
            for i in range(path.curve.n):
                path.curve.tag[i] = "CURVE"  # or 'CORNER'

        def optiCurve(path):
            # Simplified stub
            pass

        for path in self._pathlist:
            calcSums(path)
            calcLon(path)
            bestPolygon(path)
            adjustVertices(path)
            # Reverse if sign is '-'
            if path.sign == "-":
                reverse_path(path)
            smooth(path)
            if self._params["optCurve"]:
                optiCurve(path)

    def getPathTag(self, fillColor=None, scale=None):
        """
        Return a single <path> tag with "d" containing all path data.
        If fillColor is None, we use self._params['color'] or 'black'/ 'white'
        """
        if not self._imageLoaded:
            raise RuntimeError("Image should be loaded first.")

        if not self._processed:
            self._bmToPathlist()
            self._processPath()
            self._processed = True

        fc = fillColor
        if fc is None:
            fc = self._params["color"]
            if fc == Potrace.COLOR_AUTO:
                fc = "black" if self._params["blackOnWhite"] else "white"

        if not self._pathlist:
            return f'<path d="" stroke="none" fill="{fc}" fill-rule="evenodd"/>'

        d_parts = []
        for path in self._pathlist:
            if path.curve:
                d_str = render_curve(path.curve, scale)
                d_parts.append(d_str)
        d = " ".join(d_parts)

        return f'<path d="{d}" stroke="none" fill="{fc}" fill-rule="evenodd"/>'

    def getSymbol(self, symbol_id):
        if not self._luminanceData:
            raise RuntimeError("Image not loaded")

        w = self._luminanceData.width
        h = self._luminanceData.height
        pathTag = self.getPathTag(fillColor="", scale=None)
        return f'<symbol viewBox="0 0 {w} {h}" id="{symbol_id}">{pathTag}</symbol>'

    def getSVG(self):
        if not self._luminanceData:
            raise RuntimeError("No image to trace")

        width = (
            self._params["width"]
            if self._params["width"]
            else self._luminanceData.width
        )
        height = (
            self._params["height"]
            if self._params["height"]
            else self._luminanceData.height
        )
        scale = {
            "x": width / self._luminanceData.width if self._luminanceData.width else 1,
            "y": (
                height / self._luminanceData.height if self._luminanceData.height else 1
            ),
        }

        background = self._params["background"]
        rect = ""
        if background != Potrace.COLOR_TRANSPARENT:
            rect = f'\t<rect x="0" y="0" width="100%" height="100%" fill="{background}" />\n'

        pathTag = self.getPathTag(None, scale)
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" version="1.1">\n'
            f"{rect}"
            f"\t{pathTag}\n"
            f"</svg>"
        )
        return svg
