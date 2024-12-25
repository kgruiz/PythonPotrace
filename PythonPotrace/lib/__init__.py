# lib/__init__.py

from .Potrace import Potrace
from .Posterizer import Posterizer
from .utils import (
    get_attr_regexp,
    set_html_attribute,
    fixed,
    mod,
    xprod,
    cyclic,
    sign,
    quadform,
    interval,
    dorth_infty,
    ddenom,
    dpara,
    cprod,
    iprod,
    iprod1,
    ddist,
    luminance,
    between,
    clamp,
    is_number,
    render_curve,
    bezier,
    tangent
)
from .index import trace, posterize
from .types import Bitmap, Curve, Histogram, Opti, Path, Point, Quad, Sum

__all__ = [
    "Potrace",
    "Posterizer",
    "get_attr_regexp",
    "set_html_attribute",
    "fixed",
    "mod",
    "xprod",
    "cyclic",
    "sign",
    "quadform",
    "interval",
    "dorth_infty",
    "ddenom",
    "dpara",
    "cprod",
    "iprod",
    "iprod1",
    "ddist",
    "luminance",
    "between",
    "clamp",
    "is_number",
    "render_curve",
    "bezier",
    "tangent",
    "trace",
    "posterize",
    "Bitmap",
    "Curve",
    "Histogram",
    "Opti",
    "Path",
    "Point",
    "Quad",
    "Sum"
]
