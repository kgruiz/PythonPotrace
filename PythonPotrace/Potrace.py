# Potrace.py
#
# This is a Python translation of the Potrace.js code, maintaining the same
# interface and functionality. It uses Pillow (PIL) instead of Jimp to
# handle image loading and pixel data. The supporting classes and methods
# (Bitmap, Curve, Path, Point, Quad, Sum, Opti, and utils) are assumed to
# exist in your environment, just like in the Node.js code.

from PIL import Image
from .types import Bitmap, Curve, Path, Point, Quad, Sum, Opti
from . import utils

class Potrace:
    """
    Python implementation of the Potrace algorithm for vectorizing raster images.

    Parameters
    ----------
    options : dict, optional
        Dictionary of tracing options. Available options include:

        turnPolicy : str, default 'minority'
            How to resolve ambiguities in path decomposition.
        turdSize : int, default 2
            Suppress speckles of up to this size.
        alphaMax : float, default 1.0
            Corner threshold parameter.
        optCurve : bool, default True
            Enable curve optimization.
        optTolerance : float, default 0.2
            Curve optimization tolerance.
        threshold : int, default -1
            Threshold below which color is considered black (0..255).
        blackOnWhite : bool, default True
            Specifies colors by which side from threshold should be traced.
        color : str, default 'auto'
            Foreground color. Ignored when exporting as <symbol>.
        background : str, default 'transparent'
            Background color. Ignored when exporting as <symbol>.
        width : int, optional
            Optional width for SVG output. Defaults to image width.
        height : int, optional
            Optional height for SVG output. Defaults to image height.

    Attributes
    ----------
    _luminanceData : Bitmap
        Luminance data of the loaded image.
    _pathlist : list
        List of paths generated from the image.
    _imageLoaded : bool
        Indicates if the image has been loaded.
    _processed : bool
        Indicates if the image has been processed.
    _params : dict
        Tracing parameters.
    """

    COLOR_AUTO = 'auto'
    COLOR_TRANSPARENT = 'transparent'
    THRESHOLD_AUTO = -1

    TURNPOLICY_BLACK = 'black'
    TURNPOLICY_WHITE = 'white'
    TURNPOLICY_LEFT = 'left'
    TURNPOLICY_RIGHT = 'right'
    TURNPOLICY_MINORITY = 'minority'
    TURNPOLICY_MAJORITY = 'majority'

    SUPPORTED_TURNPOLICY_VALUES = [
        TURNPOLICY_BLACK,
        TURNPOLICY_WHITE,
        TURNPOLICY_LEFT,
        TURNPOLICY_RIGHT,
        TURNPOLICY_MINORITY,
        TURNPOLICY_MAJORITY
    ]

    def __init__(self, options=None):
        self._luminanceData = None
        self._pathlist = []
        self._imageLoaded = False
        self._processed = False

        self._params = {
            'turnPolicy': Potrace.TURNPOLICY_MINORITY,
            'turdSize': 2,
            'alphaMax': 1,
            'optCurve': True,
            'optTolerance': 0.2,
            'threshold': Potrace.THRESHOLD_AUTO,
            'blackOnWhite': True,
            'color': Potrace.COLOR_AUTO,
            'background': Potrace.COLOR_TRANSPARENT,
            'width': None,
            'height': None
        }

        if options is not None:
            self.setParameters(options)

    def _bmToPathlist(self):
        """
        Create a new Path for every group of black pixels.
        """
        threshold = self._params['threshold']
        blackOnWhite = self._params['blackOnWhite']

        # If threshold is set to auto, try reading from histogram
        # or default to 128 if no auto threshold is found.
        if threshold == Potrace.THRESHOLD_AUTO:
            hist = self._luminanceData.histogram()
            auto_th = hist.autoThreshold() if hist else None
            threshold = auto_th if auto_th is not None else 128

        def map_to_black_or_white(lum):
            # If blackOnWhite: lum > threshold => 0 else 1
            # Otherwise:       lum < threshold => 1 else 0
            # Same logic as the JavaScript code.
            if blackOnWhite:
                return 0 if lum > threshold else 1
            else:
                return 1 if lum < threshold else 0

        # blackMap is a copy of luminanceData, but each pixel is set to
        # 1 or 0 depending on threshold
        blackMap = self._luminanceData.copy(map_to_black_or_white)

        currentPoint = Point(0, 0)
        self._pathlist = []

        def findNext(pt):
            i = blackMap.pointToIndex(pt)
            while i < blackMap.size and blackMap.data[i] != 1:
                i += 1
            if i < blackMap.size:
                return blackMap.indexToPoint(i)
            return None

        def majority(x, y):
            # same logic as JS
            for i in range(2, 5):
                ct = 0
                for a in range(-i + 1, i):
                    ct += 1 if blackMap.getValueAt(x + a, y + i - 1) else -1
                    ct += 1 if blackMap.getValueAt(x + i - 1, y + a - 1) else -1
                    ct += 1 if blackMap.getValueAt(x + a - 1, y - i) else -1
                    ct += 1 if blackMap.getValueAt(x - i, y + a) else -1
                if ct > 0:
                    return 1
                elif ct < 0:
                    return 0
            return 0

        def findPath(pt):
            path = Path()
            x, y = pt.x, pt.y
            dirx, diry = 0, 1

            # path.sign is '+' if pixel is 1, else '-'
            path.sign = '+' if blackMap.getValueAt(x, y) else '-'

            while True:
                path.pt.append(Point(x, y))
                # update min/max for path
                if x > path.maxX:
                    path.maxX = x
                if x < path.minX:
                    path.minX = x
                if y > path.maxY:
                    path.maxY = y
                if y < path.minY:
                    path.minY = y
                path.len += 1

                x += dirx
                y += diry
                path.area -= x * diry

                # If we've looped back to the start point
                if x == pt.x and y == pt.y:
                    break

                l = blackMap.getValueAt(
                    x + (dirx + diry - 1) / 2,
                    y + (diry - dirx - 1) / 2
                )
                r = blackMap.getValueAt(
                    x + (dirx - diry - 1) / 2,
                    y + (diry + dirx - 1) / 2
                )

                # Follows the same logic as the JavaScript code
                if r and not l:
                    if (self._params['turnPolicy'] == 'right'
                        or (self._params['turnPolicy'] == 'black'
                            and path.sign == '+')
                        or (self._params['turnPolicy'] == 'white'
                            and path.sign == '-')
                        or (self._params['turnPolicy'] == 'majority'
                            and majority(x, y))
                        or (self._params['turnPolicy'] == 'minority'
                            and not majority(x, y))):
                        tmp = dirx
                        dirx = -diry
                        diry = tmp
                    else:
                        tmp = dirx
                        dirx = diry
                        diry = -tmp
                elif r:
                    tmp = dirx
                    dirx = -diry
                    diry = tmp
                elif not l:
                    tmp = dirx
                    dirx = diry
                    diry = -tmp

            return path

        def xorPath(path):
            # same as JS logic
            y1 = path.pt[0].y
            length = path.len

            for i in range(1, length):
                x = path.pt[i].x
                y = path.pt[i].y
                if y != y1:
                    minY = y1 if y1 < y else y
                    maxX = path.maxX
                    for j in range(x, maxX):
                        idx = blackMap.pointToIndex(Point(j, minY))
                        blackMap.data[idx] = 0 if blackMap.data[idx] == 1 else 1
                    y1 = y

        while True:
            found = findNext(currentPoint)
            if not found:
                break
            path_obj = findPath(found)
            xorPath(path_obj)

            if path_obj.area > self._params['turdSize']:
                self._pathlist.append(path_obj)

            # Move currentPoint to the next index after found
            next_idx = blackMap.pointToIndex(found) + 1
            if next_idx >= blackMap.size:
                break
            currentPoint = blackMap.indexToPoint(next_idx)

    def _processPath(self):
        """
        Process the path list created by _bmToPathlist,
        creating and optimizing Curves.
        """
        # These helper functions mirror the original code structure
        def calcSums(path):
            path.x0 = path.pt[0].x
            path.y0 = path.pt[0].y
            path.sums = []
            s = path.sums
            s.append(Sum(0, 0, 0, 0, 0))

            for i in range(path.len):
                x = path.pt[i].x - path.x0
                y = path.pt[i].y - path.y0
                prev_sum = s[i]
                s.append(Sum(
                    prev_sum.x + x,
                    prev_sum.y + y,
                    prev_sum.xy + x * y,
                    prev_sum.x2 + x * x,
                    prev_sum.y2 + y * y
                ))

        def calcLon(path):
            """
            Mirror the calcLon logic from JS.
            """
            n = path.len
            pt = path.pt
            pivk = [0] * n
            nc = [0] * n
            ct = [0, 0, 0, 0]
            path.lon = [0] * n

            constraint = [Point(), Point()]
            cur = Point()
            off = Point()
            dk = Point()

            k = 0
            for i in range(n - 1, -1, -1):
                if (pt[i].x != pt[k].x) and (pt[i].y != pt[k].y):
                    k = i + 1
                nc[i] = k

            for i in range(n - 1, -1, -1):
                ct[0] = ct[1] = ct[2] = ct[3] = 0
                dir_ = (3 + 3 * (pt[utils.mod(i + 1, n)].x - pt[i].x)
                        + (pt[utils.mod(i + 1, n)].y - pt[i].y)) // 2
                ct[dir_] += 1

                constraint[0].x = 0
                constraint[0].y = 0
                constraint[1].x = 0
                constraint[1].y = 0

                k = nc[i]
                k1 = i
                foundk = 0
                while True:
                    dir_ = (3
                            + 3 * utils.sign(pt[k].x - pt[k1].x)
                            + utils.sign(pt[k].y - pt[k1].y)) // 2
                    ct[dir_] += 1

                    if ct[0] and ct[1] and ct[2] and ct[3]:
                        pivk[i] = k1
                        foundk = 1
                        break

                    cur.x = pt[k].x - pt[i].x
                    cur.y = pt[k].y - pt[i].y

                    if (utils.xprod(constraint[0], cur) < 0
                            or utils.xprod(constraint[1], cur) > 0):
                        break

                    if abs(cur.x) <= 1 and abs(cur.y) <= 1:
                        pass
                    else:
                        off.x = (cur.x
                                 + (1 if (cur.y >= 0 and (cur.y > 0 or cur.x < 0))
                                    else -1))
                        off.y = (cur.y
                                 + (1 if (cur.x <= 0 and (cur.x < 0 or cur.y < 0))
                                    else -1))
                        if utils.xprod(constraint[0], off) >= 0:
                            constraint[0].x = off.x
                            constraint[0].y = off.y

                        off.x = (cur.x
                                 + (1 if (cur.y <= 0 and (cur.y < 0 or cur.x < 0))
                                    else -1))
                        off.y = (cur.y
                                 + (1 if (cur.x >= 0 and (cur.x > 0 or cur.y < 0))
                                    else -1))
                        if utils.xprod(constraint[1], off) <= 0:
                            constraint[1].x = off.x
                            constraint[1].y = off.y

                    k1 = k
                    k = nc[k1]
                    if not utils.cyclic(k, i, k1):
                        break

                if foundk == 0:
                    dk.x = utils.sign(pt[k].x - pt[k1].x)
                    dk.y = utils.sign(pt[k].y - pt[k1].y)
                    cur.x = pt[k1].x - pt[i].x
                    cur.y = pt[k1].y - pt[i].y

                    a = utils.xprod(constraint[0], cur)
                    b = utils.xprod(constraint[0], dk)
                    c = utils.xprod(constraint[1], cur)
                    d = utils.xprod(constraint[1], dk)

                    j = 10000000

                    if b < 0:
                        j = int(a // -b)
                    if d > 0:
                        j = min(j, int(-c // d))

                    pivk[i] = utils.mod(k1 + j, n)

            j = pivk[n - 1]
            path.lon[n - 1] = j
            for i in range(n - 2, -1, -1):
                if utils.cyclic(i + 1, pivk[i], j):
                    j = pivk[i]
                path.lon[i] = j

            i = n - 1
            while utils.cyclic(utils.mod(i + 1, n), j, path.lon[i]):
                path.lon[i] = j
                i -= 1

        def bestPolygon(path):
            """
            Mirror bestPolygon logic from JS code
            """
            def penalty3(path, i, j):
                n = path.len
                pt = path.pt
                sums = path.sums
                r = 0
                if j >= n:
                    j -= n
                    r = 1

                if r == 0:
                    x = sums[j + 1].x - sums[i].x
                    y = sums[j + 1].y - sums[i].y
                    x2 = sums[j + 1].x2 - sums[i].x2
                    xy = sums[j + 1].xy - sums[i].xy
                    y2 = sums[j + 1].y2 - sums[i].y2
                    k = (j + 1) - i
                else:
                    x = sums[j + 1].x - sums[i].x + sums[n].x
                    y = sums[j + 1].y - sums[i].y + sums[n].y
                    x2 = sums[j + 1].x2 - sums[i].x2 + sums[n].x2
                    xy = sums[j + 1].xy - sums[i].xy + sums[n].xy
                    y2 = sums[j + 1].y2 - sums[i].y2 + sums[n].y2
                    k = (j + 1) - i + n

                px = (pt[i].x + pt[j].x) / 2.0 - pt[0].x
                py = (pt[i].y + pt[j].y) / 2.0 - pt[0].y
                ey = pt[j].x - pt[i].x
                ex = -(pt[j].y - pt[i].y)

                a = (x2 - 2 * x * px) / k + px * px
                b = (xy - x * py - y * px) / k + px * py
                c = (y2 - 2 * y * py) / k + py * py

                s = ex * ex * a + 2 * ex * ey * b + ey * ey * c
                return (s ** 0.5)

            n = path.len
            pen = [0] * (n + 1)
            prev = [0] * (n + 1)
            clip0 = [0] * n
            clip1 = [0] * (n + 1)
            seg0 = [0] * (n + 1)
            seg1 = [0] * (n + 1)

            # local aliases
            lon = path.lon
            pt = path.pt
            s = path.sums

            # The logic is the same as in the JS code
            for i in range(n):
                c = utils.mod(lon[utils.mod(i - 1, n)] - 1, n)
                if c == i:
                    c = utils.mod(i + 1, n)
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
            for j_ in range(n + 1):
                if i >= n:
                    break
                seg0[j_] = i
                i = clip0[i]
                if i >= n:
                    seg0[j_ + 1] = n
                    m = j_ + 1
                    break
            else:
                m = j_

            i = n
            for j_ in range(m, 0, -1):
                seg1[j_] = i
                i = clip1[i]
            seg1[0] = 0

            pen[0] = 0
            for j_ in range(1, m + 1):
                for i_ in range(seg1[j_], seg0[j_] + 1):
                    best = -1
                    for k_ in range(seg0[j_ - 1], clip1[i_] - 1, -1):
                        thispen = penalty3(path, k_, i_) + pen[k_]
                        if best < 0 or thispen < best:
                            prev[i_] = k_
                            best = thispen
                    pen[i_] = best

            path.m = m
            path.po = [0] * m
            i_ = n
            j_ = m - 1
            while i_ > 0:
                i_ = prev[i_]
                path.po[j_] = i_
                j_ -= 1

        def adjustVertices(path):
            """
            Mirror the adjustVertices logic
            """
            def pointslope(path, i, j, ctr, dir_):
                n = path.len
                s = path.sums
                r = 0

                while j >= n:
                    j -= n
                    r += 1
                while i >= n:
                    i -= n
                    r -= 1
                while j < 0:
                    j += n
                    r -= 1
                while i < 0:
                    i += n
                    r += 1

                x = s[j + 1].x - s[i].x + r * s[n].x
                y = s[j + 1].y - s[i].y + r * s[n].y
                x2 = s[j + 1].x2 - s[i].x2 + r * s[n].x2
                xy = s[j + 1].xy - s[i].xy + r * s[n].xy
                y2 = s[j + 1].y2 - s[i].y2 + r * s[n].y2
                k = (j + 1 - i) + r * n

                ctr.x = x / k
                ctr.y = y / k

                a = (x2 - (x * x / k)) / k
                b = (xy - (x * y / k)) / k
                c = (y2 - (y * y / k)) / k

                lambda2 = (a + c + ((a - c) ** 2 + 4 * b * b) ** 0.5) / 2.0

                a -= lambda2
                c -= lambda2

                l = 0.0
                if abs(a) >= abs(c):
                    l = (a * a + b * b) ** 0.5
                    if l != 0:
                        dir_.x = -b / l
                        dir_.y = a / l
                else:
                    l = (c * c + b * b) ** 0.5
                    if l != 0:
                        dir_.x = -c / l
                        dir_.y = b / l
                if l == 0:
                    dir_.x = 0
                    dir_.y = 0

            m = path.m
            po = path.po
            n = path.len
            pt = path.pt
            x0 = path.x0
            y0 = path.y0
            ctr = [Point() for _ in range(m)]
            dir_ = [Point() for _ in range(m)]
            q = [Quad() for _ in range(m)]
            v = [0, 0, 0]

            path.curve = Curve(m)
            curve = path.curve

            for i in range(m):
                j = po[utils.mod(i + 1, m)]
                j = utils.mod(j - po[i], n) + po[i]
                pointslope(path, po[i], j, ctr[i], dir_[i])

            for i in range(m):
                d = dir_[i].x * dir_[i].x + dir_[i].y * dir_[i].y
                if d == 0.0:
                    for row in range(3):
                        for col in range(3):
                            q[i].data[row * 3 + col] = 0
                else:
                    v[0] = dir_[i].y
                    v[1] = -dir_[i].x
                    v[2] = -(v[1] * ctr[i].y) - (v[0] * ctr[i].x)
                    for row in range(3):
                        for col in range(3):
                            q[i].data[row * 3 + col] = (v[row] * v[col]) / d

            # Solve Q
            w = Point()
            s_ = Point()
            for i in range(m):
                Q = Quad()
                s_.x = pt[po[i]].x - x0
                s_.y = pt[po[i]].y - y0
                j = utils.mod(i - 1, m)

                for row in range(3):
                    for col in range(3):
                        Q.data[row * 3 + col] = q[j].at(row, col) + q[i].at(row, col)

                while True:
                    det = Q.at(0, 0) * Q.at(1, 1) - Q.at(0, 1) * Q.at(1, 0)
                    if det != 0.0:
                        w.x = (-Q.at(0, 2) * Q.at(1, 1) + Q.at(1, 2) * Q.at(0, 1)) / det
                        w.y = (Q.at(0, 2) * Q.at(1, 0) - Q.at(1, 2) * Q.at(0, 0)) / det
                        break

                    # Adjust Q
                    if Q.at(0, 0) > Q.at(1, 1):
                        v[0] = -Q.at(0, 1)
                        v[1] = Q.at(0, 0)
                    elif Q.at(1, 1) != 0:
                        v[0] = -Q.at(1, 1)
                        v[1] = Q.at(1, 0)
                    else:
                        v[0] = 1
                        v[1] = 0
                    d_ = v[0] * v[0] + v[1] * v[1]
                    v[2] = -v[1] * s_.y - v[0] * s_.x
                    for row in range(3):
                        for col in range(3):
                            Q.data[row * 3 + col] += (v[row] * v[col]) / d_

                dx = abs(w.x - s_.x)
                dy = abs(w.y - s_.y)
                if dx <= 0.5 and dy <= 0.5:
                    curve.vertex[i] = Point(w.x + x0, w.y + y0)
                    continue

                # Otherwise, test for min
                minval = utils.quadform(Q, s_)
                xmin = s_.x
                ymin = s_.y

                # check Q(0,0) != 0
                if Q.at(0, 0) != 0.0:
                    for z in range(2):
                        w.y = s_.y - 0.5 + z
                        w.x = -(Q.at(0, 1) * w.y + Q.at(0, 2)) / Q.at(0, 0)
                        dx_ = abs(w.x - s_.x)
                        cand = utils.quadform(Q, w)
                        if dx_ <= 0.5 and cand < minval:
                            minval = cand
                            xmin = w.x
                            ymin = w.y

                if Q.at(1, 1) != 0.0:
                    for z in range(2):
                        w.x = s_.x - 0.5 + z
                        w.y = -(Q.at(1, 0) * w.x + Q.at(1, 2)) / Q.at(1, 1)
                        dy_ = abs(w.y - s_.y)
                        cand = utils.quadform(Q, w)
                        if dy_ <= 0.5 and cand < minval:
                            minval = cand
                            xmin = w.x
                            ymin = w.y

                # corners
                for l_ in range(2):
                    for k_ in range(2):
                        w.x = s_.x - 0.5 + l_
                        w.y = s_.y - 0.5 + k_
                        cand = utils.quadform(Q, w)
                        if cand < minval:
                            minval = cand
                            xmin = w.x
                            ymin = w.y

                curve.vertex[i] = Point(xmin + x0, ymin + y0)

        def reversePath(path):
            """
            Reverse the path if path.sign == '-'
            """
            curve = path.curve
            m = curve.n
            v_ = curve.vertex
            i, j = 0, m - 1
            while i < j:
                tmp = v_[i]
                v_[i] = v_[j]
                v_[j] = tmp
                i += 1
                j -= 1

        def smooth(path):
            """
            Mirror the smooth function in JS
            """
            curve = path.curve
            m = curve.n
            for i in range(m):
                j = utils.mod(i + 1, m)
                k = utils.mod(i + 2, m)
                p4 = utils.interval(0.5, curve.vertex[k], curve.vertex[j])

                denom = utils.ddenom(curve.vertex[i], curve.vertex[k])
                if denom != 0.0:
                    dd = utils.dpara(curve.vertex[i],
                                     curve.vertex[j],
                                     curve.vertex[k]) / denom
                    dd = abs(dd)
                    alpha = (1 - 1.0 / dd) if dd > 1 else 0
                    alpha = alpha / 0.75
                else:
                    alpha = 4 / 3.0

                curve.alpha0[j] = alpha

                if alpha >= self._params['alphaMax']:
                    curve.tag[j] = 'CORNER'
                    curve.c[3 * j + 1] = curve.vertex[j]
                    curve.c[3 * j + 2] = p4
                else:
                    if alpha < 0.55:
                        alpha = 0.55
                    elif alpha > 1:
                        alpha = 1
                    p2 = utils.interval(0.5 + 0.5 * alpha,
                                        curve.vertex[i],
                                        curve.vertex[j])
                    p3 = utils.interval(0.5 + 0.5 * alpha,
                                        curve.vertex[k],
                                        curve.vertex[j])
                    curve.tag[j] = 'CURVE'
                    curve.c[3 * j + 0] = p2
                    curve.c[3 * j + 1] = p3
                    curve.c[3 * j + 2] = p4
                curve.alpha[j] = alpha
                curve.beta[j] = 0.5

            curve.alphaCurve = 1

        def optiCurve(path):
            """
            Mirror the optiCurve logic
            """
            curve = path.curve
            m = curve.n
            vertex = curve.vertex
            pt_ = [0] * (m + 1)
            pen_ = [0] * (m + 1)
            length_ = [0] * (m + 1)
            opt_ = [None] * (m + 1)

            o = Opti()
            convc = [0] * m
            areac = [0] * (m + 1)
            # Fill convc
            for i in range(m):
                if curve.tag[i] == 'CURVE':
                    convc[i] = utils.sign(utils.dpara(
                        vertex[utils.mod(i - 1, m)],
                        vertex[i],
                        vertex[utils.mod(i + 1, m)]
                    ))
                else:
                    convc[i] = 0

            # compute area
            area = 0.0
            areac[0] = 0.0
            p0 = vertex[0]
            for i in range(m):
                i1 = utils.mod(i + 1, m)
                if curve.tag[i1] == 'CURVE':
                    alpha = curve.alpha[i1]
                    area += (0.3 * alpha * (4 - alpha)
                             * utils.dpara(curve.c[i * 3 + 2],
                                           vertex[i1],
                                           curve.c[i1 * 3 + 2]) / 2)
                    area += (utils.dpara(p0,
                                         curve.c[i * 3 + 2],
                                         curve.c[i1 * 3 + 2]) / 2)
                areac[i + 1] = area

            pt_[0] = -1
            pen_[0] = 0
            length_[0] = 0

            def opti_penalty(path, i_, j_, res, opttolerance, convc_, areac_):
                if i_ == j_:
                    return 1
                k_ = i_
                i1_ = utils.mod(i_ + 1, m)
                k1_ = utils.mod(k_ + 1, m)
                conv = convc_[k1_]
                if conv == 0:
                    return 1
                d_ = utils.ddist(vertex[i_], vertex[i1_])
                # same logic in the for loop
                while k_ != j_:
                    k1_ = utils.mod(k_ + 1, m)
                    k2_ = utils.mod(k_ + 2, m)
                    if convc_[k1_] != conv:
                        return 1
                    if utils.sign(utils.cprod(vertex[i_],
                                              vertex[i1_],
                                              vertex[k1_],
                                              vertex[k2_])) != conv:
                        return 1
                    if utils.iprod1(vertex[i_],
                                    vertex[i1_],
                                    vertex[k1_],
                                    vertex[k2_]) < (d_ * utils.ddist(vertex[k1_],
                                                                      vertex[k2_])
                                                    * -0.999847695156):
                        return 1
                    k_ = k1_
                    if k_ == j_:
                        break

                p0_ = curve.c[utils.mod(i_, m) * 3 + 2].copy()
                p1_ = vertex[utils.mod(i_ + 1, m)].copy()
                p2_ = vertex[utils.mod(j_, m)].copy()
                p3_ = curve.c[utils.mod(j_, m) * 3 + 2].copy()

                area_ = areac_[j_] - areac_[i_]
                area_ -= (utils.dpara(vertex[0],
                                      curve.c[i_ * 3 + 2],
                                      curve.c[j_ * 3 + 2]) / 2)
                if i_ >= j_:
                    area_ += areac_[m]

                A1 = utils.dpara(p0_, p1_, p2_)
                A2 = utils.dpara(p0_, p1_, p3_)
                A3 = utils.dpara(p0_, p2_, p3_)
                A4 = A1 + A3 - A2

                if A2 == A1:
                    return 1

                t_ = A3 / (A3 - A4)
                s_ = A2 / (A2 - A1)
                A_ = A2 * t_ / 2.0

                if A_ == 0.0:
                    return 1

                R_ = area_ / A_
                alpha_ = 2 - ((4 - R_ / 0.3) ** 0.5)
                res.c[0] = utils.interval(t_ * alpha_, p0_, p1_)
                res.c[1] = utils.interval(s_ * alpha_, p3_, p2_)
                res.alpha = alpha_
                res.t = t_
                res.s = s_

                p1_ = res.c[0].copy()
                p2_ = res.c[1].copy()

                res.pen = 0

                # check all points on the path
                k_ = utils.mod(i_ + 1, m)
                while True:
                    k1_ = utils.mod(k_ + 1, m)
                    if k_ == j_:
                        break
                    t_ = utils.tangent(p0_, p1_, p2_, p3_, vertex[k_], vertex[k1_])
                    if t_ < -0.5:
                        return 1
                    pt__ = utils.bezier(t_, p0_, p1_, p2_, p3_)
                    d__ = utils.ddist(vertex[k_], vertex[k1_])
                    if d__ == 0.0:
                        return 1
                    d1_ = utils.dpara(vertex[k_], vertex[k1_], pt__) / d__
                    if abs(d1_) > opttolerance:
                        return 1
                    if (utils.iprod(vertex[k_], vertex[k1_], pt__) < 0
                            or utils.iprod(vertex[k1_], vertex[k_], pt__) < 0):
                        return 1
                    res.pen += d1_ * d1_

                    k_ = k1_
                    if k_ == j_:
                        break

                # check all control points
                k_ = i_
                while True:
                    k1_ = utils.mod(k_ + 1, m)
                    if k_ == j_:
                        break
                    t_ = utils.tangent(p0_, p1_, p2_, p3_,
                                       curve.c[k_ * 3 + 2],
                                       curve.c[k1_ * 3 + 2])
                    if t_ < -0.5:
                        return 1
                    pt__ = utils.bezier(t_, p0_, p1_, p2_, p3_)
                    d__ = utils.ddist(curve.c[k_ * 3 + 2],
                                      curve.c[k1_ * 3 + 2])
                    if d__ == 0.0:
                        return 1
                    d1_ = utils.dpara(curve.c[k_ * 3 + 2],
                                      curve.c[k1_ * 3 + 2],
                                      pt__) / d__
                    d2_ = (utils.dpara(curve.c[k_ * 3 + 2],
                                       curve.c[k1_ * 3 + 2],
                                       vertex[k1_]) / d__)
                    d2_ *= 0.75 * curve.alpha[k1_]
                    if d2_ < 0:
                        d1_ = -d1_
                        d2_ = -d2_
                    if d1_ < d2_ - opttolerance:
                        return 1
                    if d1_ < d2_:
                        res.pen += (d1_ - d2_) * (d1_ - d2_)

                    k_ = k1_
                    if k_ == j_:
                        break

                return 0

            for j_ in range(1, m + 1):
                pt_[j_] = j_ - 1
                pen_[j_] = pen_[j_ - 1]
                length_[j_] = length_[j_ - 1] + 1

                i_ = j_ - 2
                while i_ >= 0:
                    r_ = opti_penalty(path, i_, utils.mod(j_, m), o,
                                      self._params['optTolerance'],
                                      convc, areac)
                    if r_ != 0:
                        break
                    if (length_[j_] > length_[i_] + 1
                       or (length_[j_] == length_[i_] + 1
                           and pen_[j_] > pen_[i_] + o.pen)):
                        pt_[j_] = i_
                        pen_[j_] = pen_[i_] + o.pen
                        length_[j_] = length_[i_] + 1
                        opt_[j_] = o
                        o = Opti()
                    i_ -= 1

            om = length_[m]
            ocurve = Curve(om)
            s_ar = [0] * om
            t_ar = [0] * om

            j_ = m
            for i_ in range(om - 1, -1, -1):
                if pt_[j_] == j_ - 1:
                    ocurve.tag[i_] = curve.tag[utils.mod(j_, m)]
                    ocurve.c[i_ * 3 + 0] = curve.c[utils.mod(j_, m) * 3 + 0]
                    ocurve.c[i_ * 3 + 1] = curve.c[utils.mod(j_, m) * 3 + 1]
                    ocurve.c[i_ * 3 + 2] = curve.c[utils.mod(j_, m) * 3 + 2]
                    ocurve.vertex[i_] = curve.vertex[utils.mod(j_, m)]
                    ocurve.alpha[i_] = curve.alpha[utils.mod(j_, m)]
                    ocurve.alpha0[i_] = curve.alpha0[utils.mod(j_, m)]
                    ocurve.beta[i_] = curve.beta[utils.mod(j_, m)]
                    s_ar[i_] = 1.0
                    t_ar[i_] = 1.0
                else:
                    ocurve.tag[i_] = 'CURVE'
                    ocurve.c[i_ * 3 + 0] = opt_[j_].c[0]
                    ocurve.c[i_ * 3 + 1] = opt_[j_].c[1]
                    ocurve.c[i_ * 3 + 2] = curve.c[utils.mod(j_, m) * 3 + 2]
                    ocurve.vertex[i_] = utils.interval(
                        opt_[j_].s,
                        curve.c[utils.mod(j_, m) * 3 + 2],
                        vertex[utils.mod(j_, m)]
                    )
                    ocurve.alpha[i_] = opt_[j_].alpha
                    ocurve.alpha0[i_] = opt_[j_].alpha
                    s_ar[i_] = opt_[j_].s
                    t_ar[i_] = opt_[j_].t
                j_ = pt_[j_]

            for i_ in range(om):
                i1_ = utils.mod(i_ + 1, om)
                ocurve.beta[i_] = s_ar[i_] / (s_ar[i_] + t_ar[i1_])
            ocurve.alphaCurve = 1
            path.curve = ocurve

        for path in self._pathlist:
            calcSums(path)
            calcLon(path)
            bestPolygon(path)
            adjustVertices(path)

            if path.sign == '-':
                reversePath(path)

            smooth(path)

            if self._params['optCurve']:
                optiCurve(path)

    def _validateParameters(self, params):
        if params is None:
            return

        if ('turnPolicy' in params
                and params['turnPolicy'] not in self.SUPPORTED_TURNPOLICY_VALUES):
            allowed = "', '".join(self.SUPPORTED_TURNPOLICY_VALUES)
            raise ValueError(f"Bad turnPolicy value. Allowed values are: '{allowed}'")

        if ('threshold' in params
                and params['threshold'] is not None
                and params['threshold'] != Potrace.THRESHOLD_AUTO):
            th = params['threshold']
            if not isinstance(th, (int, float)) or not (0 <= th <= 255):
                raise ValueError(
                    "Bad threshold value. Expected an integer in range 0..255"
                )

        if ('optCurve' in params
                and params['optCurve'] is not None
                and not isinstance(params['optCurve'], bool)):
            raise ValueError("'optCurve' must be a boolean")

    def _processLoadedImage(self, image):
        """
        Process the loaded Pillow image and store its luminance data in self._luminanceData.
        This mirrors the _processLoadedImage in the JS code, but uses Python/Pillow methods.
        """
        width, height = image.size
        bitmap = Bitmap(width, height)
        pixels = image.load()  # returns a pixel access object

        # We want background underneath non-opaque regions to be white
        for y in range(height):
            for x in range(width):
                # pixel might be RGBA
                r, g, b, a = (0, 0, 0, 255)
                px = pixels[x, y]
                if len(px) == 4:
                    r, g, b, a = px
                else:
                    # If there's no alpha, assume full opacity
                    r, g, b = px
                    a = 255

                opacity = a / 255.0
                r_ = 255 + (r - 255) * opacity
                g_ = 255 + (g - 255) * opacity
                b_ = 255 + (b - 255) * opacity

                idx = y * width + x
                bitmap.data[idx] = utils.luminance(r_, g_, b_)

        self._luminanceData = bitmap
        self._imageLoaded = True

    def loadImage(self, target, callback):
        """
        Load an image for processing.

        Parameters
        ----------
        target : str or PIL.Image.Image
            Source image. Can be a file path, file-like object, or a PIL Image instance.
        callback : callable
            Callback function with signature (error).

        Returns
        -------
        None

        Raises
        ------
        Exception
            If the image cannot be processed.
        """
        # We don't exactly replicate the "jobId" because Python isn't callback-based
        self._imageLoaded = False

        if isinstance(target, Image.Image):
            # We already have a Pillow image
            try:
                self._processLoadedImage(target)
                self._imageLoaded = True
                callback(None)
            except Exception as e:
                callback(e)
        else:
            # Attempt to open as path or file-like object
            try:
                with Image.open(target) as img:
                    # If needed, ensure RGBA
                    img = img.convert("RGBA")
                    self._processLoadedImage(img)
                    self._imageLoaded = True
                    callback(None)
            except Exception as e:
                callback(e)

    def setParameters(self, newParams):
        """
        Update tracing parameters.

        Parameters
        ----------
        newParams : dict
            Dictionary of new tracing parameters to update.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If any of the provided parameters are invalid.
        """
        self._validateParameters(newParams)

        for key in self._params:
            if key in newParams:
                old_val = self._params[key]
                self._params[key] = newParams[key]
                if (old_val != self._params[key]
                        and key not in ['color', 'background']):
                    self._processed = False

    def getPathTag(self, fillColor=None, scale=None):
        """
        Generates just the <path> tag without the rest of the SVG file.

        :param fillColor: optional color override.
        :param scale: dict with keys 'x' and 'y' to scale the paths, or None.
        :return: string of a <path> element.
        """
        if fillColor is None:
            fillColor = self._params['color']

        if fillColor == Potrace.COLOR_AUTO:
            fillColor = 'black' if self._params['blackOnWhite'] else 'white'

        if not self._imageLoaded:
            raise RuntimeError("Image should be loaded first")

        if not self._processed:
            self._bmToPathlist()
            self._processPath()
            self._processed = True

        path_data = []
        for path in self._pathlist:
            path_data.append(utils.renderCurve(path.curve, scale))

        tag = '<path d="{}" stroke="none" fill="{}" fill-rule="evenodd"/>'.format(
            " ".join(path_data),
            fillColor
        )
        return tag

    def getSymbol(self, id_):
        """
        Returns a <symbol> tag. Always has a viewBox specified and comes with no fill color,
        so it can be changed with a <use> tag.

        :param id_: Symbol ID for the SVG
        :return: string of a <symbol> element.
        """
        w = self._luminanceData.width
        h = self._luminanceData.height
        return (
            f'<symbol viewBox="0 0 {w} {h}" id="{id_}">'
            + self.getPathTag("")
            + '</symbol>'
        )

    def getSVG(self):
        """
        Generate an SVG representation of the processed image.

        Returns
        -------
        str
            SVG content as a string.

        Raises
        ------
        RuntimeError
            If no image data is available for SVG generation.
        """
        if self._luminanceData is None:
            raise RuntimeError("No image data to create SVG from.")

        w = self._params['width'] if self._params['width'] else self._luminanceData.width
        h = self._params['height'] if self._params['height'] else self._luminanceData.height

        scale = {
            'x': (self._params['width'] / self._luminanceData.width)
                  if self._params['width'] else 1,
            'y': (self._params['height'] / self._luminanceData.height)
                  if self._params['height'] else 1
        }

        background = self._params['background']
        svg = []
        svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                   f'width="{w}" height="{h}" '
                   f'viewBox="0 0 {w} {h}" version="1.1">')

        if background != Potrace.COLOR_TRANSPARENT:
            svg.append(f'\t<rect x="0" y="0" width="100%" height="100%" fill="{background}" />')

        svg.append("\t" + self.getPathTag(self._params['color'], scale))
        svg.append('</svg>')
        return "\n".join(svg)
