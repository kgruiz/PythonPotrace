# utils.py

import re
import math
from types.Point import Point

attr_regexps = {}

def get_attr_regexp(attr_name):
    """
    Get or compile a regular expression for the given HTML attribute name.

    :param attr_name: The name of the HTML attribute.
    :return: Compiled regular expression object.
    """
    if attr_name in attr_regexps:
        return attr_regexps[attr_name]

    # The JavaScript regex: ' ' + attrName + '="((?:\\\\(?=")"|[^"])+)"'
    # Translated to Python regex
    pattern = r' ' + re.escape(attr_name) + r'="((?:\\(?=")|[^"])+)"'
    attr_regexps[attr_name] = re.compile(pattern, re.IGNORECASE)
    return attr_regexps[attr_name]

def set_html_attribute(html, attr_name, value):
    """
    Set or update an HTML attribute in the given HTML string.

    :param html: The HTML string.
    :param attr_name: The name of the attribute to set.
    :param value: The value to set for the attribute.
    :return: Updated HTML string.
    """
    attr = f' {attr_name}="{value}"'

    if f' {attr_name}="' not in html:
        # Add the attribute to the opening tag
        # Equivalent to JS: html.replace(/<[a-z]+/i, function(beginning) { return beginning + attr; });
        def replacer(match):
            return match.group(0) + attr
        html = re.sub(r'<[a-z]+', replacer, html, flags=re.IGNORECASE)
    else:
        # Replace the existing attribute value
        html = get_attr_regexp(attr_name).sub(attr, html)

    return html

def fixed(number):
    """
    Format a number to three decimal places, removing trailing '.000' if present.

    :param number: The number to format.
    :return: Formatted string.
    """
    formatted = f"{number:.3f}"
    return formatted[:-4] if formatted.endswith('.000') else formatted

def mod(a, n):
    """
    Compute a modulo n, handling negative values appropriately.

    :param a: The dividend.
    :param n: The divisor.
    :return: Result of a modulo n.
    """
    if a >= n:
        return a % n
    elif a >= 0:
        return a
    else:
        return n - 1 - ((-1 - a) % n)

def xprod(p1, p2):
    """
    Compute the cross product of two points treated as vectors.

    :param p1: First Point.
    :param p2: Second Point.
    :return: Cross product value.
    """
    return p1.x * p2.y - p1.y * p2.x

def cyclic(a, b, c):
    """
    Determine if b is in the cyclic interval [a, c).

    :param a: Start of interval.
    :param b: Value to check.
    :param c: End of interval.
    :return: True if b is within the interval, False otherwise.
    """
    if a <= c:
        return a <= b < c
    else:
        return a <= b or b < c

def sign(i):
    """
    Determine the sign of a number.

    :param i: The number.
    :return: 1 if positive, -1 if negative, 0 if zero.
    """
    return 1 if i > 0 else (-1 if i < 0 else 0)

def quadform(Q, w):
    """
    Compute the quadratic form w^T Q w.

    :param Q: Quad instance.
    :param w: Point instance treated as a vector with homogeneous coordinate.
    :return: Quadratic form value.
    """
    v = [w.x, w.y, 1]
    sum_val = 0.0

    for i in range(3):
        for j in range(3):
            sum_val += v[i] * Q.at(i, j) * v[j]
    return sum_val

def interval(lambda_, a, b):
    """
    Compute the linear interpolation between points a and b.

    :param lambda_: The interpolation parameter (0 <= lambda_ <= 1).
    :param a: Start Point.
    :param b: End Point.
    :return: Interpolated Point.
    """
    res = Point()
    res.x = a.x + lambda_ * (b.x - a.x)
    res.y = a.y + lambda_ * (b.y - a.y)
    return res

def dorth_infty(p0, p2):
    """
    Compute the direction orthogonal to the vector from p0 to p2.

    :param p0: Starting Point.
    :param p2: Ending Point.
    :return: Orthogonal Point.
    """
    r = Point()
    r.y = sign(p2.x - p0.x)
    r.x = -sign(p2.y - p0.y)
    return r

def ddenom(p0, p2):
    """
    Compute the denominator for certain calculations.

    :param p0: Starting Point.
    :param p2: Ending Point.
    :return: Denominator value.
    """
    r = dorth_infty(p0, p2)
    return r.y * (p2.x - p0.x) - r.x * (p2.y - p0.y)

def dpara(p0, p1, p2):
    """
    Compute the determinant to check for parallelism.

    :param p0: Origin Point.
    :param p1: Second Point.
    :param p2: Third Point.
    :return: Determinant value.
    """
    x1 = p1.x - p0.x
    y1 = p1.y - p0.y
    x2 = p2.x - p0.x
    y2 = p2.y - p0.y
    return x1 * y2 - x2 * y1

def cprod(p0, p1, p2, p3):
    """
    Compute the cross product for two vectors defined by points.

    :param p0: First Point of the first vector.
    :param p1: Second Point of the first vector.
    :param p2: First Point of the second vector.
    :param p3: Second Point of the second vector.
    :return: Cross product value.
    """
    x1 = p1.x - p0.x
    y1 = p1.y - p0.y
    x2 = p3.x - p2.x
    y2 = p3.y - p2.y
    return x1 * y2 - x2 * y1

def iprod(p0, p1, p2):
    """
    Compute the inner product of two vectors defined by points.

    :param p0: Origin Point.
    :param p1: Endpoint of the first vector.
    :param p2: Endpoint of the second vector.
    :return: Inner product value.
    """
    x1 = p1.x - p0.x
    y1 = p1.y - p0.y
    x2 = p2.x - p0.x
    y2 = p2.y - p0.y
    return x1 * x2 + y1 * y2

def iprod1(p0, p1, p2, p3):
    """
    Compute the inner product of two vectors defined by points.

    :param p0: Origin Point of the first vector.
    :param p1: Endpoint of the first vector.
    :param p2: Origin Point of the second vector.
    :param p3: Endpoint of the second vector.
    :return: Inner product value.
    """
    x1 = p1.x - p0.x
    y1 = p1.y - p0.y
    x2 = p3.x - p2.x
    y2 = p3.y - p2.y
    return x1 * x2 + y1 * y2

def ddist(p, q):
    """
    Compute the Euclidean distance between two points.

    :param p: First Point.
    :param q: Second Point.
    :return: Distance value.
    """
    return math.sqrt((p.x - q.x) ** 2 + (p.y - q.y) ** 2)

def luminance(r, g, b):
    """
    Calculate the luminance from RGB values.

    :param r: Red component.
    :param g: Green component.
    :param b: Blue component.
    :return: Luminance value as an integer.
    """
    return round(0.2126 * r + 0.7153 * g + 0.0721 * b)

def between(val, min_val, max_val):
    """
    Check if a value is between min_val and max_val, inclusive.

    :param val: The value to check.
    :param min_val: The minimum bound.
    :param max_val: The maximum bound.
    :return: True if val is between min_val and max_val, else False.
    """
    return min_val <= val <= max_val

def clamp(val, min_val, max_val):
    """
    Clamp a value between min_val and max_val.

    :param val: The value to clamp.
    :param min_val: The minimum bound.
    :param max_val: The maximum bound.
    :return: Clamped value.
    """
    return max(min_val, min(val, max_val))

def is_number(val):
    """
    Check if a value is a number (int or float).

    :param val: The value to check.
    :return: True if val is a number, else False.
    """
    return isinstance(val, (int, float))

def render_curve(curve, scale=None):
    """
    Generates path instructions for a given curve.

    :param curve: Curve instance.
    :param scale: Optional scaling factor as a dictionary with 'x' and 'y'. Defaults to 1 for both axes.
    :return: SVG path string.
    """
    if scale is None:
        scale = {'x': 1, 'y': 1}

    starting_point = curve.c[(curve.n - 1) * 3 + 2]

    path = [
        f"M {fixed(starting_point.x * scale['x'])} {fixed(starting_point.y * scale['y'])}"
    ]

    for i, tag in enumerate(curve.tag):
        i3 = i * 3
        p0 = curve.c[i3]
        p1 = curve.c[i3 + 1]
        p2 = curve.c[i3 + 2]

        if tag == 'CURVE':
            path.append(
                f"C {fixed(p0.x * scale['x'])} {fixed(p0.y * scale['y'])}, "
                f"{fixed(p1.x * scale['x'])} {fixed(p1.y * scale['y'])}, "
                f"{fixed(p2.x * scale['x'])} {fixed(p2.y * scale['y'])}"
            )
        elif tag == 'CORNER':
            path.append(
                f"L {fixed(p1.x * scale['x'])} {fixed(p1.y * scale['y'])} "
                f"{fixed(p2.x * scale['x'])} {fixed(p2.y * scale['y'])}"
            )

    return ' '.join(path)

def bezier(t, p0, p1, p2, p3):
    """
    Calculate a point on a cubic Bezier curve at parameter t.

    :param t: Parameter between 0 and 1.
    :param p0: First control Point.
    :param p1: Second control Point.
    :param p2: Third control Point.
    :param p3: Fourth control Point.
    :return: Point on the Bezier curve.
    """
    s = 1 - t
    res = Point()

    res.x = (s ** 3) * p0.x + 3 * (s ** 2) * t * p1.x + 3 * (t ** 2) * s * p2.x + (t ** 3) * p3.x
    res.y = (s ** 3) * p0.y + 3 * (s ** 2) * t * p1.y + 3 * (t ** 2) * s * p2.y + (t ** 3) * p3.y

    return res

def tangent(p0, p1, p2, p3, q0, q1):
    """
    Calculate the tangent parameter for intersection with another curve.

    :param p0: First control Point of the first curve.
    :param p1: Second control Point of the first curve.
    :param p2: Third control Point of the first curve.
    :param p3: Fourth control Point of the first curve.
    :param q0: First control Point of the second curve.
    :param q1: Second control Point of the second curve.
    :return: Tangent parameter (float) or -1.0 if no valid tangent exists.
    """
    A = cprod(p0, p1, q0, q1)
    B = cprod(p1, p2, q0, q1)
    C = cprod(p2, p3, q0, q1)

    a = A - 2 * B + C
    b = -2 * A + 2 * B
    c = A

    d = b * b - 4 * a * c

    if a == 0 or d < 0:
        return -1.0

    s = math.sqrt(d)

    r1 = (-b + s) / (2 * a)
    r2 = (-b - s) / (2 * a)

    if 0 <= r1 <= 1:
        return r1
    elif 0 <= r2 <= 1:
        return r2
    else:
        return -1.0
