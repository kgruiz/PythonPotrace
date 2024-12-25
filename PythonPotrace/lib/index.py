# index.py
#
# This Python code mirrors the interface and callbacks of the original index.js.
# Pillow is used for image handling instead of Jimp.

from .Potrace import Potrace
from .Posterizer import Posterizer

def trace(file, options=None, cb=None):
    """
    Trace an input image and convert it to SVG format.

    Parameters
    ----------
    file : str or PIL.Image.Image
        Source image. Can be a file path or a PIL Image instance.
    options : dict, optional
        Dictionary of tracing options. Defaults to an empty dictionary.
    cb : callable, optional
        Callback function with signature (error, svg_content, potrace_instance).

    Returns
    -------
    None

    Notes
    -----
    If only `file` and `cb` are provided, `options` defaults to an empty dictionary.
    """
    # Imitate the JavaScript argument handling: if called with (file, cb),
    # then shift cb to the second argument and set options = {}
    if cb is None and callable(options):
        cb = options
        options = {}

    if options is None:
        options = {}

    potrace = Potrace(options)

    def after_load(err):
        if err is not None:
            return cb(err, None, None)
        try:
            svg = potrace.getSVG()
            cb(None, svg, potrace)
        except Exception as e:
            cb(e, None, None)

    potrace.loadImage(file, after_load)

def posterize(file, options=None, cb=None):
    """
    Apply posterization to the input image.

    Parameters
    ----------
    file : str or PIL.Image.Image
        Source image. Can be a file path or a PIL Image instance.
    options : dict, optional
        Dictionary of posterization options. Defaults to an empty dictionary.
    cb : callable, optional
        Callback function with signature (error, posterized_image, posterizer_instance).

    Returns
    -------
    None

    Notes
    -----
    If only `file` and `cb` are provided, `options` defaults to an empty dictionary.
    """
    # Same argument shifting logic
    if cb is None and callable(options):
        cb = options
        options = {}

    if options is None:
        options = {}

    posterizer = Posterizer(options)

    def after_load(err):
        if err is not None:
            return cb(err, None, None)
        try:
            svg = posterizer.getSVG()
            cb(None, svg, posterizer)
        except Exception as e:
            cb(e, None, None)

    posterizer.loadImage(file, after_load)