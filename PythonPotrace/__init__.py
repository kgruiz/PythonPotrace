# PythonPotrace/__init__.py

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
    "tangent"
]

from .index import trace, posterize
__all__.extend(["trace", "posterize"])

# Expose types module directly
from . import types as _types
__all__.append("types")

# This has all of the symbols in __all__ from types
from .types import *
__all__.extend(types.__all__)


def get_types():
    """Helper function to allow from PythonPotrace.types import * syntax"""
    return _types

types = get_types()