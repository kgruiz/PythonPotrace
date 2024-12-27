# PythonPotrace/Potrace.py

import math
from dataclasses import dataclass
from typing import Callable, Optional, Union

from PIL import Image

# Importing custom types and utility functions
from .types.Bitmap import Bitmap
from .types.Curve import Curve
from .types.Opti import Opti
from .types.Path import Path
from .types.Point import Point
from .types.Quad import Quad
from .types.Sum import Sum
from .utils import (
    between,
    bezier,
    cprod,
    cyclic,
    ddenom,
    ddist,
    dpara,
    interval,
    iprod,
    iprod1,
    luminance,
    mod,
    quadform,
    render_curve,
    sign,
    tangent,
    xprod,
)


@dataclass
class PotraceOptions:
    turnPolicy: str = "minority"
    turdSize: float = 2
    alphaMax: float = 1
    optCurve: bool = True
    optTolerance: float = 0.2
    threshold: int = -1  # Potrace.THRESHOLD_AUTO
    blackOnWhite: bool = True
    color: str = "auto"
    background: str = "transparent"
    width: Optional[int] = None
    height: Optional[int] = None


class Potrace:
    """
    Potrace class for tracing bitmap images to vector paths.
    """

    # Constants
    COLOR_AUTO = "auto"
    COLOR_TRANSPARENT = "transparent"
    THRESHOLD_AUTO = -1
    TURNPOLICY_BLACK = "black"
    TURNPOLICY_WHITE = "white"
    TURNPOLICY_LEFT = "left"
    TURNPOLICY_RIGHT = "right"
    TURNPOLICY_MINORITY = "minority"
    TURNPOLICY_MAJORITY = "majority"

    SUPPORTED_TURNPOLICY_VALUES = [
        TURNPOLICY_BLACK,
        TURNPOLICY_WHITE,
        TURNPOLICY_LEFT,
        TURNPOLICY_RIGHT,
        TURNPOLICY_MINORITY,
        TURNPOLICY_MAJORITY,
    ]

    def __init__(self, options: Optional[dict] = None):
        self._luminanceData: Optional[Bitmap] = None
        self._pathlist: list[Path] = []
        self._imageLoadingIdentifier = None
        self._imageLoaded: bool = False
        self._processed: bool = False

        self._params = {
            "turnPolicy": self.TURNPOLICY_MINORITY,
            "turdSize": 2,
            "alphaMax": 1,
            "optCurve": True,
            "optTolerance": 0.2,
            "threshold": self.THRESHOLD_AUTO,
            "blackOnWhite": True,
            "color": self.COLOR_AUTO,
            "background": self.COLOR_TRANSPARENT,
            "width": None,
            "height": None,
        }

        if options:
            self.setParameters(options)

    def _validateParameters(self, params: dict):
        # Validate turnPolicy
        valid_tp = self.SUPPORTED_TURNPOLICY_VALUES
        if params and "turnPolicy" in params:
            if params["turnPolicy"] not in valid_tp:
                raise ValueError(f"Bad turnPolicy value. Allowed: {valid_tp}")

        # Validate threshold
        if (
            params
            and "threshold" in params
            and params["threshold"] != self.THRESHOLD_AUTO
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

    def _processLoadedImage(self, pil_image: Image.Image):
        w, h = pil_image.size
        bitmap = Bitmap(w, h)
        pixels = pil_image.load()

        for y in range(h):
            for x in range(w):
                rgba = pixels[x, y]
                if len(rgba) == 4:
                    r, g, b, a = rgba
                elif len(rgba) == 3:
                    r, g, b = rgba
                    a = 255
                else:
                    r = g = b = 255
                    a = 255
                opacity = a / 255.0
                # We want background behind transparent to be white
                rr = 255 + (r - 255) * opacity
                gg = 255 + (g - 255) * opacity
                bb = 255 + (b - 255) * opacity
                bitmap.data[y * w + x] = int(luminance(rr, gg, bb))

        self._luminanceData = bitmap
        self._imageLoaded = True

    def loadImage(
        self,
        target: Union[str, bytes, Image.Image],
        callback: Optional[Callable[[Optional[Exception]], None]] = None,
    ):
        """
        Loads an image from a file path, bytes, or a PIL Image object.

        :param target: Image source. Could be a file path, bytes, or a PIL Image object.
        :param callback: Optional callback function that takes an Exception if an error occurs.
        """
        jobId = object()  # Unique identifier for the loading job
        self._imageLoadingIdentifier = jobId
        self._imageLoaded = False

        if not Image:
            err = RuntimeError("PIL (Pillow) not installed.")
            if callback:
                callback(err)
            return

        # If user passes in a PIL Image directly
        if isinstance(target, Image.Image):
            self._imageLoadingIdentifier = None
            self._imageLoaded = True
            self._processLoadedImage(target)
            if callback:
                callback(None)
            return

        # Otherwise, assume it's a path or something PIL can open
        try:
            with Image.open(target) as pil_img:
                # Convert to RGBA to ensure consistency
                if pil_img.mode != "RGBA":
                    pil_img = pil_img.convert("RGBA")
                self._processLoadedImage(pil_img)
            self._imageLoadingIdentifier = None
            if callback:
                callback(None)
        except Exception as e:
            if callback:
                callback(e)

    def setParameters(self, newParams: dict):
        """
        Set or override existing parameters.

        :param newParams: Dictionary containing new parameters.
        """
        self._validateParameters(newParams)
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
        if threshold == self.THRESHOLD_AUTO:
            # Try automatic thresholding
            threshold = self._luminanceData.histogram().autoThreshold() or 128

        blackOnWhite = self._params["blackOnWhite"]
        # Create a binary bitmap: 1=black, 0=white (or vice versa)
        blackMap = self._luminanceData.copy(
            lambda lum, idx: (
                0
                if (blackOnWhite and lum > threshold)
                or (not blackOnWhite and lum < threshold)
                else 1
            )
        )

        self._pathlist = []

        def find_next(start_index: int) -> Optional[int]:
            i = start_index
            while i < blackMap.size and blackMap.data[i] != 1:
                i += 1
            return i if i < blackMap.size else None

        # Helper functions to convert between index and coordinates
        def idx_to_xy(i: int) -> tuple:
            return (i % blackMap.width, i // blackMap.width)

        def xy_to_idx(x: int, y: int) -> int:
            return y * blackMap.width + x

        def majority(x: int, y: int) -> int:
            for i in range(2, 5):
                ct = 0
                for a in range(-i + 1, i):
                    # Top line
                    val_top = blackMap.get_value_at_safe(x + a, y + i - 1)
                    ct += 1 if val_top else -1

                    # Right line
                    val_right = blackMap.get_value_at_safe(x + i - 1, y + a - 1)
                    ct += 1 if val_right else -1

                    # Bottom line
                    val_bottom = blackMap.get_value_at_safe(x + a - 1, y - i)
                    ct += 1 if val_bottom else -1

                    # Left line
                    val_left = blackMap.get_value_at_safe(x - i, y + a)
                    ct += 1 if val_left else -1

                if ct > 0:
                    return 1
                elif ct < 0:
                    return 0
            return 0

        def find_path(x_start: int, y_start: int) -> Path:
            path = Path()
            x, y = x_start, y_start
            dirx, diry = 0, 1  # Initial direction (right)

            path.sign = "+" if blackMap.get_value_at(x, y) == 1 else "-"

            while True:
                path.pt.append(Point(x, y))
                path.maxX = max(x, path.maxX)
                path.minX = min(x, path.minX)
                path.maxY = max(y, path.maxY)
                path.minY = min(y, path.minY)
                path.len += 1

                x += dirx
                y += diry
                path.area -= x * diry

                if x == x_start and y == y_start:
                    break

                # Check left and right pixels
                l = blackMap.get_value_at(
                    int(x + (dirx + diry - 1) / 2), int(y + (diry - dirx - 1) / 2)
                )
                r = blackMap.get_value_at(
                    int(x + (dirx - diry - 1) / 2), int(y + (diry + dirx - 1) / 2)
                )

                # Apply turn policy
                turnPolicy = self._params["turnPolicy"]
                if r and not l:
                    if (
                        turnPolicy == self.TURNPOLICY_RIGHT
                        or (turnPolicy == self.TURNPOLICY_BLACK and path.sign == "+")
                        or (turnPolicy == self.TURNPOLICY_WHITE and path.sign == "-")
                        or (
                            turnPolicy == self.TURNPOLICY_MAJORITY
                            and majority(x, y) == 1
                        )
                        or (
                            turnPolicy == self.TURNPOLICY_MINORITY
                            and majority(x, y) == 0
                        )
                    ):
                        dirx, diry = -diry, dirx
                    else:
                        dirx, diry = diry, -dirx
                elif r:
                    dirx, diry = -diry, dirx
                elif not l:
                    dirx, diry = diry, -dirx

            return path

        def xor_path(path: Path):
            y1 = path.pt[0].y
            for i in range(1, path.len):
                x = path.pt[i].x
                y = path.pt[i].y
                if y != y1:
                    min_y = min(y1, y)
                    max_x = path.maxX
                    for j in range(x, max_x):
                        idx = xy_to_idx(j, min_y)
                        blackMap.data[idx] = 1 - blackMap.data[idx]
                    y1 = y

        current_index = 0
        while True:
            next_i = find_next(current_index)
            if next_i is None:
                break
            x_found, y_found = idx_to_xy(next_i)
            p = find_path(x_found, y_found)
            xor_path(p)
            if p.area > self._params["turdSize"]:
                self._pathlist.append(p)
            current_index = next_i + 1

    def _processPath(self):
        """
        Processes path list created by _bmToPathlist method, creating and optimizing Curves.
        """

        for path in self._pathlist:
            self._calcSums(path)
            self._calcLon(path)
            self._bestPolygon(path)
            self._adjustVertices(path)

            if path.sign == "-":
                self._reverse(path)

            self._smooth(path)

            if self._params["optCurve"]:
                self._optiCurve(path)

    def _calcSums(self, path: Path):
        path.x0 = path.pt[0].x
        path.y0 = path.pt[0].y

        path.sums = [Sum(0, 0, 0, 0, 0)]
        for i in range(path.len):
            x = path.pt[i].x - path.x0
            y = path.pt[i].y - path.y0
            prev_sum = path.sums[-1]
            new_sum = Sum(
                prev_sum.x + x,
                prev_sum.y + y,
                prev_sum.xy + x * y,
                prev_sum.x2 + x * x,
                prev_sum.y2 + y * y,
            )
            path.sums.append(new_sum)

    def _calcLon(self, path: Path):
        n = path.len
        pt = path.pt
        pivk = [0] * n
        nc = [0] * n

        path.lon = [0] * n

        constraint = [Point(0, 0), Point(0, 0)]
        cur = Point(0, 0)
        off = Point(0, 0)
        dk = Point(0, 0)
        foundk = False

        k = 0
        for i in range(n - 1, -1, -1):
            if pt[i].x != pt[k].x and pt[i].y != pt[k].y:
                k = i + 1
            nc[i] = k

        for i in range(n - 1, -1, -1):
            ct = [0, 0, 0, 0]
            next_pt = pt[mod(i + 1, n)]
            dir_val = (3 + 3 * (next_pt.x - pt[i].x) + (next_pt.y - pt[i].y)) // 2
            ct[dir_val] += 1

            constraint[0].x = 0
            constraint[0].y = 0
            constraint[1].x = 0
            constraint[1].y = 0

            k = nc[i]
            k1 = i
            foundk = False
            while True:
                dir_val = (
                    3 + 3 * sign(pt[k].x - pt[k1].x) + sign(pt[k].y - pt[k1].y)
                ) // 2
                ct[dir_val] += 1

                if all(ct_val > 0 for ct_val in ct):
                    pivk[i] = k1
                    foundk = True
                    break
                cur = Point(pt[k].x - pt[i].x, pt[k].y - pt[i].y)
                if xprod(constraint[0], cur) < 0 or xprod(constraint[1], cur) > 0:
                    break
                if abs(cur.x) > 1 or abs(cur.y) > 1:
                    off = Point(
                        cur.x
                        + (1 if (cur.y >= 0 and (cur.y > 0 or cur.x < 0)) else -1),
                        cur.y
                        + (1 if (cur.x <= 0 and (cur.x < 0 or cur.y < 0)) else -1),
                    )
                    if xprod(constraint[0], off) >= 0:
                        constraint[0].x = off.x
                        constraint[0].y = off.y

                    off = Point(
                        cur.x
                        + (1 if (cur.y <= 0 and (cur.y < 0 or cur.x < 0)) else -1),
                        cur.y
                        + (1 if (cur.x >= 0 and (cur.x > 0 or cur.y < 0)) else -1),
                    )
                    if xprod(constraint[1], off) <= 0:
                        constraint[1].x = off.x
                        constraint[1].y = off.y

                k1 = k
                k = nc[k1]
                if not cyclic(k, i, k1):
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
        path.lon[n - 1] = j
        for i in range(n - 2, -1, -1):
            if cyclic(i + 1, pivk[i], j):
                j = pivk[i]
            path.lon[i] = j

        # Ensuring cyclic closure
        for i in range(n - 1, -1, -1):
            if cyclic(mod(i + 1, n), j, path.lon[i]):
                path.lon[i] = j

    def _bestPolygon(self, path: Path):
        """
        Finds the best polygon approximation for the given path.
        """
        n = path.len
        m = path.curve.n

        pen = [0] * (m + 1)
        prev = [0] * (m + 1)
        clip0 = [0] * m
        clip1 = [0] * (m + 1)
        seg0 = [0] * (m + 1)
        seg1 = [0] * (m + 1)
        opt = [Opti() for _ in range(m + 1)]

        # Initialize clip0
        for i in range(m):
            c_val = mod(path.lon[mod(i - 1, m)] - 1, m)
            if c_val == i:
                c_val = mod(i + 1, m)
            clip0[i] = m if c_val < i else c_val

        # Initialize clip1
        j = 1
        for i in range(m):
            while j <= clip0[i]:
                clip1[j] = i
                j += 1

        # Initialize seg0
        i = 0
        for j in range(m + 1):
            seg0[j] = i
            if i < m:
                i = clip0[i]
            if i >= m:
                break

        # Initialize seg1
        i = m
        for j in range(m, 0, -1):
            seg1[j] = i
            i = clip1[i]
        seg1[0] = 0

        # Initialize pen and prev
        pen[0] = 0
        length_ = [0] * (n + 1)
        length_[0] = 0

        for j in range(1, m + 1):
            iStart = seg1[j]
            pen[j] = pen[j - 1] + self._penalty3(path, seg0[j - 1], iStart % n)
            length_[j] = length_[j - 1] + 1
            for i in range(seg1[j], seg0[j] + 1):
                # The code tries to find a better i
                thispen = self._penalty3(path, i % n, (seg0[j]) % n) + pen[j - 1]
                if length_[j] > length_[j - 1] + 1 or (
                    length_[j] == length_[j - 1] + 1 and pen[j] > thispen
                ):
                    pen[j] = thispen
                    prev[j] = i
                    length_[j] = length_[j - 1] + 1
        path.m = m
        path.po = []
        j = m
        for i in range(path.m):
            path.po.append(0)

    def _penalty3(self, path, i, j):
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

    def _adjustVertices(self, path: Path):
        """
        Adjusts the vertices of the path to create smooth curves.
        """

        def pointslope(path: Path, i: int, j: int, ctr: Point, dir: Point):
            n = path.len
            sums = path.sums
            x = sums[j + 1].x - sums[i].x
            y = sums[j + 1].y - sums[i].y
            x2 = sums[j + 1].x2 - sums[i].x2
            xy = sums[j + 1].xy - sums[i].xy
            y2 = sums[j + 1].y2 - sums[i].y2
            k = j + 1 - i

            ctr.x = x / k
            ctr.y = y / k

            a = (x2 - 2 * x * ctr.x) / k + ctr.x * ctr.x
            b = (xy - x * ctr.y - y * ctr.x) / k + ctr.x * ctr.y
            c = (y2 - 2 * y * ctr.y) / k + ctr.y * ctr.y

            lambda2 = (a + c + math.sqrt((a - c) ** 2 + 4 * b * b)) / 2

            a -= lambda2
            c -= lambda2

            if abs(a) >= abs(c):
                l = math.sqrt(a * a + b * b)
                if l != 0:
                    dir.x = -b / l
                    dir.y = a / l
            else:
                l = math.sqrt(c * c + b * b)
                if l != 0:
                    dir.x = -c / l
                    dir.y = b / l
            if l == 0:
                dir.x = dir.y = 0

        m = path.m
        po = path.po
        n = path.len
        pt = path.pt
        x0 = path.x0
        y0 = path.y0

        ctr = [Point(0, 0) for _ in range(m)]
        dir = [Point(0, 0) for _ in range(m)]
        q = [Quad() for _ in range(m)]
        v = [Point(0, 0), Point(0, 0), Point(0, 0)]
        curve = Curve(m)

        for i in range(m):
            j = po[mod(i + 1, m)]
            j = mod(j - po[i], n) + po[i]
            pointslope(path, po[i], j, ctr[i], dir[i])

        for i in range(m):
            q[i] = Quad()
            d = dir[i].x * dir[i].x + dir[i].y * dir[i].y
            if d == 0.0:
                for l in range(3):
                    for k in range(3):
                        q[i].data[l * 3 + k] = 0
            else:
                v[0].x = dir[i].y
                v[0].y = -dir[i].x
                v[1].x = -v[0].y
                v[1].y = v[0].x
                v[2].x = -v[1].x * ctr[i].y - v[0].x * ctr[i].x
                v[2].y = -v[1].y * ctr[i].y - v[0].y * ctr[i].x
                for l in range(3):
                    for k in range(3):
                        q[i].data[l * 3 + k] = v[l].x * v[k].x / d

        for i in range(m):
            Q = Quad()
            w = Point()

            s = Point()
            s.x = pt[po[i]].x - x0
            s.y = pt[po[i]].y - y0

            j = mod(i - 1, m)

            for l in range(3):
                for k in range(3):
                    Q.data[l * 3 + k] = q[j].data[l * 3 + k] + q[i].data[l * 3 + k]

            # Solve Q * w = [-Q[0][2], -Q[1][2]]
            det = Q.at(0, 0) * Q.at(1, 1) - Q.at(0, 1) * Q.at(1, 0)
            if det != 0.0:
                w.x = (-Q.at(0, 2) * Q.at(1, 1) + Q.at(1, 2) * Q.at(0, 1)) / det
                w.y = (Q.at(0, 2) * Q.at(1, 0) - Q.at(1, 2) * Q.at(0, 0)) / det
            else:
                # Handle singular matrix by adjusting Q
                if Q.at(0, 0) > Q.at(1, 1):
                    v_dir = Point(-Q.at(0, 1), Q.at(0, 0))
                elif Q.at(1, 1) != 0.0:
                    v_dir = Point(-Q.at(1, 1), Q.at(1, 0))
                else:
                    v_dir = Point(1, 0)
                d = v_dir.x * v_dir.x + v_dir.y * v_dir.y
                v_dir.z = -v_dir.y * s.y - v_dir.x * s.x
                for l in range(3):
                    for k in range(3):
                        Q.data[l * 3 + k] += v_dir.x * v_dir.x / d

                # Recompute determinant
                det = Q.at(0, 0) * Q.at(1, 1) - Q.at(0, 1) * Q.at(1, 0)
                if det != 0.0:
                    w.x = (-Q.at(0, 2) * Q.at(1, 1) + Q.at(1, 2) * Q.at(0, 1)) / det
                    w.y = (Q.at(0, 2) * Q.at(1, 0) - Q.at(1, 2) * Q.at(0, 0)) / det
                else:
                    w.x = w.y = 0.0  # Fallback

            dx = abs(w.x - s.x)
            dy = abs(w.y - s.y)
            if dx <= 0.5 and dy <= 0.5:
                curve.vertex[i] = Point(w.x + x0, w.y + y0)
                continue

            min_val = quadform(Q, s)
            xmin = s.x
            ymin = s.y

            if Q.at(0, 0) != 0.0:
                for z in range(2):
                    w.y = s.y - 0.5 + z
                    if Q.at(0, 0) != 0.0:
                        w.x = -(Q.at(0, 1) * w.y + Q.at(0, 2)) / Q.at(0, 0)
                        dx = abs(w.x - s.x)
                        cand = quadform(Q, w)
                        if dx <= 0.5 and cand < min_val:
                            min_val = cand
                            xmin = w.x
                            ymin = w.y

            if Q.at(1, 1) != 0.0:
                for z in range(2):
                    w.x = s.x - 0.5 + z
                    if Q.at(1, 1) != 0.0:
                        w.y = -(Q.at(1, 0) * w.x + Q.at(1, 2)) / Q.at(1, 1)
                        dy = abs(w.y - s.y)
                        cand = quadform(Q, w)
                        if dy <= 0.5 and cand < min_val:
                            min_val = cand
                            xmin = w.x
                            ymin = w.y

            for l in range(2):
                for k in range(2):
                    w.x = s.x - 0.5 + l
                    w.y = s.y - 0.5 + k
                    cand = quadform(Q, w)
                    if cand < min_val:
                        min_val = cand
                        xmin = w.x
                        ymin = w.y

            curve.vertex[i] = Point(xmin + x0, ymin + y0)

    def _reverse(self, path: Path):
        """
        Reverses the order of vertices in the curve.
        """
        curve = path.curve
        m = curve.n
        v = curve.vertex.copy()
        for i in range(m // 2):
            v[i], v[m - 1 - i] = v[m - 1 - i], v[i]
        curve.vertex = v

    def _smooth(self, path: Path):
        """
        Smooths the curve by adjusting control points based on alphaMax.
        """
        m = path.curve.n
        curve = path.curve

        for i in range(m):
            j = mod(i + 1, m)
            k = mod(i + 2, m)
            p4 = interval(0.5, curve.vertex[k], curve.vertex[j])

            denom = ddenom(curve.vertex[i], curve.vertex[k])
            if denom != 0.0:
                dd = dpara(curve.vertex[i], curve.vertex[j], curve.vertex[k]) / denom
                dd = abs(dd)
                alpha = (2 - math.sqrt(4 - dd / 0.3)) if dd > 1 else 0
                alpha /= 0.75
            else:
                alpha = 4 / 3.0

            curve.alpha0[j] = alpha

            if alpha >= self._params["alphaMax"]:
                curve.tag[j] = "CORNER"
                curve.c[3 * j + 1] = curve.vertex[j]
                curve.c[3 * j + 2] = p4
            else:
                alpha = max(0.55, min(alpha, 1))
                p2 = interval(0.5 + 0.5 * alpha, curve.vertex[i], curve.vertex[j])
                p3 = interval(0.5 + 0.5 * alpha, curve.vertex[k], curve.vertex[j])
                curve.tag[j] = "CURVE"
                curve.c[3 * j + 0] = p2
                curve.c[3 * j + 1] = p3
                curve.c[3 * j + 2] = p4

            curve.alpha[j] = alpha
            curve.beta[j] = 0.5

        curve.alphaCurve = 1

    def _optiCurve(self, path: Path):
        """
        Optimizes the curve for better approximation.
        """
        # Simplified stub
        pass

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
            if fc == self.COLOR_AUTO:
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
        if background != self.COLOR_TRANSPARENT:
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
