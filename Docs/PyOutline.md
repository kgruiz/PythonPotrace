# PythonPotrace Library Documentation

This document provides comprehensive information about the PythonPotrace library, detailing each class, function, and their respective purposes.

## `PythonPotrace/lib/Potrace.py`

### Class: `Potrace`

**Description:**
Implements the Potrace algorithm for vectorizing raster images.

**Parameters:**

* `options` : `dict`, *optional*
    A dictionary of tracing options.

    * `turnPolicy` : `str`, default: `'minority'`
        Determines how ambiguities in path decomposition are resolved. Allowed values: `'black'`, `'white'`, `'left'`, `'right'`, `'minority'`, `'majority'`.
    * `turdSize` : `int`, default: `2`
        Suppresses speckles smaller than or equal to this size.
    * `alphaMax` : `float`, default: `1.0`
        Corner threshold parameter.
    * `optCurve` : `bool`, default: `True`
        Enables curve optimization.
    * `optTolerance` : `float`, default: `0.2`
        Curve optimization tolerance.
    * `threshold` : `int`, default: `-1`
        Threshold below which color is considered black (`0..255`). Use `-1` for auto thresholding.
    * `blackOnWhite` : `bool`, default: `True`
        Specifies whether to trace black on white or white on black.
    * `color` : `str`, default: `'auto'`
        Foreground color. Ignored when exporting as `<symbol>`. Use `'auto'` to default to black or white based on `blackOnWhite`.
    * `background` : `str`, default: `'transparent'`
        Background color. Ignored when exporting as `<symbol>`.
    * `width` : `int`, *optional*
        Optional width for SVG output. Defaults to image width.
    * `height` : `int`, *optional*
        Optional height for SVG output. Defaults to image height.

**Attributes:**

* `_luminanceData` : `Bitmap`
    Luminance data of the loaded image.
* `_pathlist` : `list`
    List of paths generated from the image.
* `_imageLoaded` : `bool`
    Indicates whether an image has been loaded.
* `_processed` : `bool`
    Indicates whether image processing is complete.
* `_params` : `dict`
    Dictionary containing tracing parameters.

**Class Attributes:**

* `COLOR_AUTO` : `'auto'`
* `COLOR_TRANSPARENT` : `'transparent'`
* `THRESHOLD_AUTO` : `-1`
* `TURNPOLICY_BLACK` : `'black'`
* `TURNPOLICY_WHITE` : `'white'`
* `TURNPOLICY_LEFT` : `'left'`
* `TURNPOLICY_RIGHT` : `'right'`
* `TURNPOLICY_MINORITY` : `'minority'`
* `TURNPOLICY_MAJORITY` : `'majority'`
* `SUPPORTED_TURNPOLICY_VALUES` : `list` = `['black', 'white', 'left', 'right', 'minority', 'majority']`

**Methods:**

* `__init__(self, options=None)`
    * **Description:** Initializes a new instance of the `Potrace` class.
    * **Parameters:**
        * `options` : `dict`, *optional* - Tracing options.

* `_bmToPathlist(self)`
    * **Description:** Creates a new `Path` for each group of black pixels in the `Bitmap`.

* `_processPath(self)`
    * **Description:** Processes the path list by creating and optimizing `Curve` objects.

* `_validateParameters(self, params)`
    * **Description:** Validates the provided tracing parameters.
    * **Parameters:**
        * `params` : `dict` - Parameters to validate.
    * **Raises:**
        * `ValueError` - If any parameter is invalid.

* `_processLoadedImage(self, image)`
    * **Description:** Processes the loaded `PIL.Image` and stores its luminance data in `self._luminanceData`.
    * **Parameters:**
        * `image` : `PIL.Image.Image` - Image to process.

* `loadImage(self, target, callback)`
    * **Description:** Loads an image for processing.
    * **Parameters:**
        * `target` : `str` or `PIL.Image.Image` - Image file path, file-like object, or PIL Image.
        * `callback` : `callable` - Function called after loading, with signature `(error)`.
    * **Raises:**
        * `Exception` - If image loading fails.

* `setParameters(self, newParams)`
    * **Description:** Updates tracing parameters.
    * **Parameters:**
        * `newParams` : `dict` - New parameters to update.
    * **Raises:**
        * `ValueError` - If provided parameters are invalid.

* `getPathTag(self, fillColor=None, scale=None)`
    * **Description:** Generates the `<path>` tag for the traced image.
    * **Parameters:**
        * `fillColor` : `str`, *optional* - Override color. Use `None` to respect the `color` setting in `options`.
        * `scale` : `dict`, *optional* - Scaling factors for `x` and `y`.
    * **Returns:** `str` - `<path>` SVG element.
    * **Raises:**
        * `RuntimeError` - If the image has not been loaded first.

* `getSymbol(self, id_)`
    * **Description:** Generates an SVG `<symbol>` tag for the traced image.
    * **Parameters:**
        * `id_` : `str` - Symbol ID for the SVG.
    * **Returns:** `str` - `<symbol>` SVG element.

* `getSVG(self)`
    * **Description:** Generates the complete SVG representation.
    * **Returns:** `str` - SVG document.
    * **Raises:**
        * `RuntimeError` - If no image has been loaded for SVG generation.

## `PythonPotrace/lib/index.py`

### Function: `trace`

**Description:**
Traces an input image to SVG format using Potrace.

**Parameters:**

* `file` : `str` or `PIL.Image.Image`
    Image source (file path or PIL Image object).
* `options` : `dict`, *optional*
    Tracing options for Potrace.
* `cb` : `callable`, *optional*
    Callback function with signature `(error, svg_content, potrace_instance)`.

### Function: `posterize`

**Description:**
Applies posterization to an image using the `Posterizer`.

**Parameters:**

* `file` : `str` or `PIL.Image.Image`
    Image source (file path or PIL Image object).
* `options` : `dict`, *optional*
    Posterization options.
* `cb` : `callable`, *optional*
    Callback function with signature `(error, posterized_image, posterizer_instance)`.

## `PythonPotrace/lib/utils.py`

### Functions:

* `get_attr_regexp(attr_name)`
    * **Description:** Compiles or retrieves a regular expression for the specified HTML attribute name.
    * **Parameters:**
        * `attr_name` : `str` - Name of the HTML attribute.
    * **Returns:** `re.Pattern` - Compiled regex object.

* `set_html_attribute(html, attr_name, value)`
    * **Description:** Sets or updates an HTML attribute within the provided string.
    * **Parameters:**
        * `html` : `str` - HTML string.
        * `attr_name` : `str` - Attribute name.
        * `value` : `str` - Attribute value.
    * **Returns:** `str` - Updated HTML string.

* `fixed(number)`
    * **Description:** Formats a number to three decimal places, removing trailing `.000`.
    * **Parameters:**
        * `number` : `float` - The number to format.
    * **Returns:** `str` - Formatted number as a string.

* `mod(a, n)`
    * **Description:** Calculates the modulo of `a` with `n`, handling negative values correctly.
    * **Parameters:**
        * `a` : `int` - The dividend.
        * `n` : `int` - The divisor.
    * **Returns:** `int` - The modulo result.

* `xprod(p1, p2)`
    * **Description:** Calculates the cross product of two `Point` objects.
    * **Parameters:**
        * `p1` : `Point`
        * `p2` : `Point`
    * **Returns:** `float` - Cross product.

* `cyclic(a, b, c)`
    * **Description:** Checks if `b` is cyclically between `a` and `c`.
    * **Parameters:**
        * `a` : `int`
        * `b` : `int`
        * `c` : `int`
    * **Returns:** `bool` - `True` if `b` is within the cyclic interval.

* `sign(i)`
    * **Description:** Determines the sign of a number.
    * **Parameters:**
        * `i` : `int`
    * **Returns:** `int` - `1`, `-1`, or `0` based on the sign of `i`.

* `quadform(Q, w)`
    * **Description:** Computes the quadratic form `w^T Q w`.
    * **Parameters:**
        * `Q` : `Quad`
        * `w` : `Point`
    * **Returns:** `float` - Result of the quadratic form.

* `interval(lambda_, a, b)`
    * **Description:** Performs linear interpolation between two `Point` objects.
    * **Parameters:**
        * `lambda_` : `float` - Interpolation factor.
        * `a` : `Point` - Start point.
        * `b` : `Point` - End point.
    * **Returns:** `Point` - Interpolated point.

* `dorth_infty(p0, p2)`
    * **Description:** Determines the direction orthogonal to the vector from `p0` to `p2`.
    * **Parameters:**
        * `p0` : `Point`
        * `p2` : `Point`
    * **Returns:** `Point` - Orthogonal direction.

* `ddenom(p0, p2)`
    * **Description:** Computes the denominator used in certain calculations.
    * **Parameters:**
        * `p0` : `Point`
        * `p2` : `Point`
    * **Returns:** `float` - Denominator value.

* `dpara(p0, p1, p2)`
    * **Description:** Calculates the determinant to check for parallelism between vectors defined by points.
    * **Parameters:**
        * `p0` : `Point`
        * `p1` : `Point`
        * `p2` : `Point`
    * **Returns:** `float` - Determinant.

* `cprod(p0, p1, p2, p3)`
    * **Description:** Calculates the cross product of two vectors defined by pairs of `Point` objects.
    * **Parameters:**
        * `p0` : `Point`
        * `p1` : `Point`
        * `p2` : `Point`
        * `p3` : `Point`
    * **Returns:** `float` - Cross product.

* `iprod(p0, p1, p2)`
    * **Description:** Calculates the inner product of vectors defined by points.
    * **Parameters:**
        * `p0` : `Point`
        * `p1` : `Point`
        * `p2` : `Point`
    * **Returns:** `float` - Inner product.

* `iprod1(p0, p1, p2, p3)`
    * **Description:** Calculates the inner product of two vectors defined by `Point` objects.
    * **Parameters:**
        * `p0` : `Point`
        * `p1` : `Point`
        * `p2` : `Point`
        * `p3` : `Point`
    * **Returns:** `float` - Inner product.

* `ddist(p, q)`
    * **Description:** Computes the Euclidean distance between two points.
    * **Parameters:**
        * `p` : `Point`
        * `q` : `Point`
    * **Returns:** `float` - Euclidean distance.

* `luminance(r, g, b)`
    * **Description:** Calculates the luminance from RGB values.
    * **Parameters:**
        * `r` : `int` - Red component.
        * `g` : `int` - Green component.
        * `b` : `int` - Blue component.
    * **Returns:** `int` - Luminance value.

* `between(val, min_val, max_val)`
    * **Description:** Checks if a value is within a specified range, inclusive.
    * **Parameters:**
        * `val`
        * `min_val`
        * `max_val`
    * **Returns:** `bool` - `True` if the value is within the range.

* `clamp(val, min_val, max_val)`
    * **Description:** Clamps a value within a specified range.
    * **Parameters:**
        * `val`
        * `min_val`
        * `max_val`
    * **Returns:** The clamped value.

* `is_number(val)`
    * **Description:** Determines if a value is a number (`int` or `float`).
    * **Parameters:**
        * `val`
    * **Returns:** `bool`

* `render_curve(curve, scale=None)`
    * **Description:** Generates SVG path instructions for a `Curve` object.
    * **Parameters:**
        * `curve` : `Curve`
        * `scale` : `dict`, *optional* - Scaling factors for `x` and `y`.
    * **Returns:** `str` - SVG path string.

* `bezier(t, p0, p1, p2, p3)`
    * **Description:** Calculates a point on a cubic Bezier curve.
    * **Parameters:**
        * `t` : `float` - Parameter between `0` and `1`.
        * `p0` : `Point` - First control point.
        * `p1` : `Point` - Second control point.
        * `p2` : `Point` - Third control point.
        * `p3` : `Point` - Fourth control point.
    * **Returns:** `Point` - Point on the Bezier curve.

* `tangent(p0, p1, p2, p3, q0, q1)`
    * **Description:** Calculates the tangent parameter for intersection with another curve.
    * **Parameters:**
        * `p0` : `Point` - First control point of the first curve.
        * `p1` : `Point` - Second control point of the first curve.
        * `p2` : `Point` - Third control point of the first curve.
        * `p3` : `Point` - Fourth control point of the first curve.
        * `q0` : `Point` - First control point of the second curve.
        * `q1` : `Point` - Second control point of the second curve.
    * **Returns:** `float` - Tangent parameter or `-1.0` if no valid tangent exists.

## `PythonPotrace/lib/Posterizer.py`

### Class: `Posterizer`

**Description:**
Combines multiple Potrace samples with varying threshold settings to generate a posterized SVG output.

**Parameters:**

* `options` : `dict`, *optional*
    A dictionary of Posterizer options. Defaults to `None`.

**Attributes:**

* `_potrace` : `Potrace`
    An instance of the `Potrace` class.
* `_calculatedThreshold` : `float` or `None`
    The calculated threshold value.
* `_params` : `dict`
    A dictionary of parameters for posterizing.

**Class Attributes:**

* `STEPS_AUTO` : `-1`
* `FILL_SPREAD` : `'spread'`
* `FILL_DOMINANT` : `'dominant'`
* `FILL_MEDIAN` : `'median'`
* `FILL_MEAN` : `'mean'`
* `RANGES_AUTO` : `'auto'`
* `RANGES_EQUAL` : `'equal'`

**Methods:**

* `__init__(self, options=None)`
    * **Description:** Initializes a new instance of the `Posterizer` class with optional parameters.
    * **Parameters:**
        * `options` : `dict`, *optional* - A dictionary of Posterizer options. Defaults to `None`.

* `_addExtraColorStop(self, ranges)`
    * **Description:** Adds an additional color stop to the color ranges if the last range exceeds 25 units.
    * **Parameters:**
        * `ranges` : `list` - A list of color range dictionaries.
    * **Returns:** `list` - The updated list of color ranges with an additional color stop if applicable.

* `_calcColorIntensity(self, colorStops)`
    * **Description:** Calculates the color intensity for each color stop based on the selected fill strategy.
    * **Parameters:**
        * `colorStops` : `list` - A list of threshold values.
    * **Returns:** `list of dict` - A list containing dictionaries with `'value'` and `'colorIntensity'` keys.

* `_getImageHistogram(self)`
    * **Description:** Retrieves the histogram of the loaded image's luminance data.
    * **Returns:** `Histogram` - The histogram instance of the image's luminance data.

* `_getRanges(self)`
    * **Description:** Determines the color ranges based on threshold and distribution parameters.
    * **Returns:** `list of dict` - A list of color ranges with their respective intensities.

* `_getRangesAuto(self)`
    * **Description:** Automatically calculates color ranges using the histogram's thresholding.
    * **Returns:** `list of dict` - A list of automatically calculated color ranges with intensities.

* `_getRangesEquallyDistributed(self)`
    * **Description:** Calculates equally distributed color ranges across the color spectrum.
    * **Returns:** `list of dict` - A list of equally distributed color ranges with intensities.

* `_paramSteps(self, count=False)`
    * **Description:** Retrieves the number of steps or the steps list based on the current parameters.
    * **Parameters:**
        * `count` : `bool`, *optional* - If `True`, returns the count of steps. Defaults to `False`.
    * **Returns:** `int` or `list` - The number of steps or the list of step thresholds.

* `_paramThreshold(self)`
    * **Description:** Determines the threshold value, calculating it if set to auto.
    * **Returns:** `float` - The determined threshold value.

* `_pathTags(self, noFillColor=False)`
    * **Description:** Generates SVG `<path>` tags based on the calculated color ranges.
    * **Parameters:**
        * `noFillColor` : `bool`, *optional* - If `True`, does not apply fill colors to the paths. Defaults to `False`.
    * **Returns:** `list of str` - A list of SVG `<path>` tags as strings.

* `loadImage(self, target, callback)`
    * **Description:** Loads an image and initializes Potrace with it.
    * **Parameters:**
        * `target` : `str` or `PIL.Image.Image` - The image path or a PIL Image to load.
        * `callback` : `callable` - A callback function to execute after loading the image, with signature `(posterizer_instance, error)`.

* `setParameters(self, params)`
    * **Description:** Updates the posterizer parameters.
    * **Parameters:**
        * `params` : `dict` - A dictionary of parameters to update.
    * **Raises:**
        * `ValueError` - If the `'steps'` parameter is invalid.

* `getSymbol(self, id_)`
    * **Description:** Generates an SVG `<symbol>` tag containing the traced paths.
    * **Parameters:**
        * `id_` : `str` - The ID to assign to the SVG `<symbol>`.
    * **Returns:** `str` - An SVG `<symbol>` element as a string.

* `getSVG(self)`
    * **Description:** Generates the complete SVG representation of the posterized image.
    * **Returns:** `str` - A string containing the full SVG content.

## `PythonPotrace/lib/types/Quad.py`

### Class: `Quad`

**Description:**
Represents a 3x3 matrix.

**Methods:**

* `__init__(self)`
    * **Description:** Initializes a new `Quad` instance with a 3x3 matrix filled with zeros.

* `at(self, x, y)`
    * **Description:** Accesses an element at the specified `(x, y)` position.
    * **Parameters:**
        * `x` : `int` - Row index (0-based).
        * `y` : `int` - Column index (0-based).
    * **Returns:** `int` - Value at the given position.
    * **Raises:**
        * `IndexError` - If `x` or `y` are out of bounds.

## `PythonPotrace/lib/types/Histogram.py`

### Functions:

* `index(x, y)`
    * **Description:** Calculates the index in a 2D representation.
    * **Parameters:**
        * `x` : `int`
        * `y` : `int`
    * **Returns:** `int`

* `normalizeMinMax(levelMin, levelMax)`
    * **Description:** Normalizes and clamps the minimum and maximum levels.
    * **Parameters:**
        * `levelMin` : `int` or `float` - Minimum level value.
        * `levelMax` : `int` or `float` - Maximum level value.
    * **Returns:** `list of int` - Normalized `[levelMin, levelMax]`.
    * **Raises:**
        * `ValueError` - If `levelMin` is greater than `levelMax`.

### Class: `Histogram`

**Description:**
Represents a histogram for aggregating color data.

**Attributes:**

* `data` : `list of int`
    Histogram data.
* `pixels` : `int`
    Total number of pixels.
* `_sortedIndexes` : `list of int or None`
    Cached sorted color indices.
* `_cachedStats` : `dict`
    Cached statistics.
* `_lookupTableH` : `list of float or None`
    Lookup table for thresholding.

**Class Attributes:**

* `MODE_LUMINANCE` : `'luminance'`
* `MODE_R` : `'r'`
* `MODE_G` : `'g'`
* `MODE_B` : `'b'`

**Methods:**

* `__init__(self, imageSource, mode=None)`
    * **Description:** Initializes a new `Histogram` instance.
    * **Parameters:**
        * `imageSource` : `int`, `Bitmap`, or `PIL.Image.Image` - Image data source.
        * `mode` : `str`, *optional* - The mode for the histogram (`'r'`, `'g'`, `'b'`, `'luminance'`).

* `_createArray(self, imageSize)`
    * **Description:** Initializes a list of integers to store the histogram.
    * **Parameters:**
        * `imageSize` : `int` - Number of pixels in the source image.

* `_collectValuesPillow(self, source, mode)`
    * **Description:** Aggregates color data from a Pillow image object.
    * **Parameters:**
        * `source` : `PIL.Image.Image` - Pillow image.
        * `mode` : `str` - The mode for the histogram (`'r'`, `'g'`, `'b'`, `'luminance'`).

* `_collectValuesBitmap(self, source)`
    * **Description:** Aggregates color data from a `Bitmap` object.
    * **Parameters:**
        * `source` : `Bitmap` - Instance of `Bitmap`.

* `_getSortedIndexes(self, refresh=False)`
    * **Description:** Returns sorted color indexes based on usage frequency.
    * **Parameters:**
        * `refresh` : `bool`, *optional* - Force refresh of the sort.
    * **Returns:** `list of int` - Sorted indexes (`0-255`).

* `_thresholdingBuildLookupTable(self)`
    * **Description:** Builds a lookup table for multi-level thresholding.
    * **Returns:** `list of float` - Lookup table.

* `multilevelThresholding(self, amount, levelMin=None, levelMax=None)`
    * **Description:** Computes multi-level thresholds based on the histogram data.
    * **Parameters:**
        * `amount` : `int` - Number of thresholds to compute.
        * `levelMin` : `int` or `float`, *optional* - Start of the histogram segment.
        * `levelMax` : `int` or `float`, *optional* - End of the histogram segment.
    * **Returns:** `list of int` - Calculated threshold values.

* `autoThreshold(self, levelMin=None, levelMax=None)`
    * **Description:** Automatically computes a threshold value for the histogram data.
    * **Parameters:**
        * `levelMin` : `int` or `float`, *optional* - Start of the histogram segment.
        * `levelMax` : `int` or `float`, *optional* - End of the histogram segment.
    * **Returns:** `int` or `None` - Calculated threshold value, or `None` if not found.

* `getDominantColor(self, levelMin=None, levelMax=None, tolerance=1)`
    * **Description:** Retrieves the most dominant color within a specified range of levels.
    * **Parameters:**
        * `levelMin` : `int` or `float`, *optional* - Minimum level.
        * `levelMax` : `int` or `float`, *optional* - Maximum level.
        * `tolerance` : `int`, *optional* - Number of adjacent bins to consider.
    * **Returns:** `int` - Dominant color index.

* `getStats(self, levelMin=None, levelMax=None, refresh=False)`
    * **Description:** Retrieves statistics for specified histogram levels.
    * **Parameters:**
        * `levelMin` : `int` or `float`, *optional* - Minimum level.
        * `levelMax` : `int` or `float`, *optional* - Maximum level.
        * `refresh` : `bool`, *optional* - Refresh cached results.
    * **Returns:** `dict` - Dictionary containing level statistics.

## `PythonPotrace/lib/types/Opti.py`

### Class: `Opti`

**Description:**
Represents optimization data for curves.

**Methods:**

* `__init__(self)`
    * **Description:** Initializes a new `Opti` instance with default values.

## `PythonPotrace/lib/types/Curve.py`

### Class: `Curve`

**Description:**
Represents a curve composed of multiple elements.

**Parameters:**

* `n` : `int`
    Number of elements.

**Attributes:**

* `tag` : `list`
    A list of tags (e.g., `CORNER`, `CURVE`).
* `c` : `list`
    List of control points.
* `alphaCurve` : `bool`
    Flag indicating if the curve is an alpha curve.
* `vertex` : `list`
    List of vertices.
* `alpha` : `list`
    List of alpha values.
* `alpha0` : `list`
    List of alpha0 values.
* `beta` : `list`
    List of beta values.

**Methods:**

* `__init__(self, n)`
    * **Description:** Initializes a new `Curve` instance.
    * **Parameters:**
        * `n` : `int` - Number of elements in the curve.

## `PythonPotrace/lib/types/Point.py`

### Class: `Point`

**Description:**
Represents a 2D point in space.

**Parameters:**

* `x` : `float`, *optional*
    X-coordinate, defaults to `0`.
* `y` : `float`, *optional*
    Y-coordinate, defaults to `0`.

**Attributes:**

* `x` : `float`
    X-coordinate.
* `y` : `float`
    Y-coordinate.

**Methods:**

* `__init__(self, x=0, y=0)`
    * **Description:** Initializes a new `Point` instance.
    * **Parameters:**
        * `x` : `float`, *optional* - X-coordinate.
        * `y` : `float`, *optional* - Y-coordinate.

* `copy(self)`
    * **Description:** Creates a copy of the current `Point` instance.
    * **Returns:** `Point` - A new `Point` object with the same coordinates.

## `PythonPotrace/lib/types/Sum.py`

### Class: `Sum`

**Description:**
Represents cumulative sums for curve calculations.

**Parameters:**

* `x` : `float`
    Sum of x values.
* `y` : `float`
    Sum of y values.
* `xy` : `float`
    Sum of x*y products.
* `x2` : `float`
    Sum of x squared.
* `y2` : `float`
    Sum of y squared.

**Methods:**

* `__init__(self, x, y, xy, x2, y2)`
    * **Description:** Initializes a new `Sum` instance with the provided parameters.
    * **Parameters:**
        * `x` : `float`
        * `y` : `float`
        * `xy` : `float`
        * `x2` : `float`
        * `y2` : `float`

## `PythonPotrace/lib/types/Bitmap.py`

### Class: `Bitmap`

**Description:**
Represents bitmap image data.

**Parameters:**

* `w` : `int`
    Width of the bitmap.
* `h` : `int`
    Height of the bitmap.

**Attributes:**

* `width` : `int`
    Width of the bitmap.
* `height` : `int`
    Height of the bitmap.
* `size` : `int`
    Total number of pixels.
* `array_buffer` : `bytearray`
    Internal storage for bitmap pixel data.
* `data` : `bytearray`
    Access to pixel data.

**Methods:**

* `__init__(self, w, h)`
    * **Description:** Initializes a new `Bitmap` instance.
    * **Parameters:**
        * `w` : `int` - Width of the bitmap.
        * `h` : `int` - Height of the bitmap.

* `get_value_at(self, x, y=None)`
    * **Description:** Retrieves the pixel value at a specific position.
    * **Parameters:**
        * `x` : `int` or `Point` - X-coordinate or a `Point` instance.
        * `y` : `int`, *optional* - Y-coordinate (required if `x` is an integer).
    * **Returns:** `int` - Pixel value.
    * **Raises:**
        * `IndexError` - If the index is out of bounds.

* `index_to_point(self, index)`
    * **Description:** Converts a linear index to a `Point`.
    * **Parameters:**
        * `index` : `int` - Linear index.
    * **Returns:** `Point` - Corresponding `Point` instance.

* `point_to_index(self, point_or_x, y=None)`
    * **Description:** Converts a `Point` or `(x, y)` coordinates to a linear index.
    * **Parameters:**
        * `point_or_x` : `Point` or `int` - `Point` instance or x-coordinate.
        * `y` : `int`, *optional* - Y-coordinate (required if `point_or_x` is an integer).
    * **Returns:** `int` - Linear index or `-1` if out of bounds.

* `copy(self, iterator=None)`
    * **Description:** Creates a copy of the `Bitmap`, optionally applying a function to each pixel.
    * **Parameters:**
        * `iterator` : `callable`, *optional* - Function to apply to each pixel.
    * **Returns:** `Bitmap` - A new `Bitmap` object.

* `histogram(self)`
    * **Description:** Generates and retrieves the `Histogram` of the bitmap.
    * **Returns:** `Histogram` - Histogram instance.