# PythonPotrace

A Python port of [node-potrace][node-potrace] by @tooolbox, which is a NodeJS-compatible fork of [Potrace in JavaScript][potrace-by-kilobtye] by @kilobtye with some additions. `node-potrace` is itself a fork of an earlier version by @iwsfg. `Potrace` is in turn a port of [the original Potrace][potrace] — a tool for tracing bitmaps.

This project aims to provide the same functionality and API as the original JavaScript version, using Python and Pillow for image processing. This port addresses installation issues and provides an up-to-date implementation, as many existing `PyPotrace` ports are outdated.

## Example and demo

| **Original image**        | **Potrace output**           | **Posterized output**                   |
|---------------------------|------------------------------|-----------------------------------------|
| ![](test/sources/yao.jpg) | ![](https://cdn.rawgit.com/tooolbox/node-potrace/9ee822d/test/example-output.svg) | ![](https://cdn.rawgit.com/tooolbox/node-potrace/9ee822d/test/example-output-posterized.svg) |

(Example image inherited from [online demo of the browser version][potrace-js-demo])

## Usage

Install

```sh
pip install PythonPotrace
```

Basic usage

```python
import potrace
import os

def MyCallback(err, svg, potraceInstance):
  if err:
    raise err
  with open('./output.svg', 'w') as f:
    f.write(svg)


potrace.trace('./path/to/image.png', cb=MyCallback)

# or

with open('./path/to/image.png', 'rb') as f:
    potrace.trace(f, cb=MyCallback)

```

You can also provide a configuration dictionary as a second argument.

```python
import potrace
import os


def MyCallback(err, svg, potraceInstance):
  if err:
    raise err
  with open('./output.svg', 'w') as f:
    f.write(svg)

params = {
  'background': '#49ffd2',
  'color': 'blue',
  'threshold': 120
}

potrace.trace('./path/to/image.png', params, cb=MyCallback)
```

If you want to run the Potrace algorithm multiple times on the same image with different threshold settings and merge results together in a single file, the `posterize` method does exactly that.

```python
import potrace
import os

def MyCallback(err, svg, posterizerInstance):
  if err:
    raise err
  with open('./output.svg', 'w') as f:
    f.write(svg)

potrace.posterize('./path/to/image.png', {'threshold': 180, 'steps': 4 }, cb=MyCallback)

# or if you know exactly where you want to break it on different levels

potrace.posterize('./path/to/image.png', {'steps': [40, 85, 135, 180]}, cb=MyCallback)
```

### Advanced usage and configuration

Both `trace` and `posterize` methods return instances of `Potrace` and `Posterizer` classes respectively to a callback function as the third argument.

You can also instantiate these classes directly:

```python
import potrace

# Tracing

trace = potrace.Potrace()

# You can also pass a configuration dictionary to the constructor
trace.setParameters({
  'threshold': 128,
  'color': '#880000'
})


def AfterLoad(err):
  if err:
    raise err
  svg = trace.getSVG() # returns SVG document contents
  pathTag = trace.getPathTag() # will return just <path> tag
  symbolTag = trace.getSymbol('traced-image') # will return <symbol> tag with given ID

trace.loadImage('path/to/image.png', AfterLoad)

# Posterization
posterizer = potrace.Posterizer()

def AfterPosterizeLoad(err):
  if err:
    raise err
  posterizer.setParameters({
    'color': '#ccc',
    'background': '#222',
    'steps': 3,
    'threshold': 200,
    'fillStrategy': potrace.Posterizer.FILL_MEAN
  })
  svg = posterizer.getSVG()
  symbolTag = posterizer.getSymbol('posterized-image')

posterizer.loadImage('path/to/image.png', AfterPosterizeLoad)

```

Callback function provided to `loadImage` methods will be executed after the image has been processed.

The first argument accepted by `loadImage` method can be a local file path or a file-like object (anything that Pillow can open). Supported formats are: PNG, JPEG or BMP. It can also be a Pillow Image instance.

### Parameters

The `Potrace` class expects the following parameters:

- **turnPolicy** - how to resolve ambiguities in path decomposition. Possible values are exported as constants: `Potrace.TURNPOLICY_BLACK`, `Potrace.TURNPOLICY_WHITE`, `Potrace.TURNPOLICY_LEFT`, `Potrace.TURNPOLICY_RIGHT`, `Potrace.TURNPOLICY_MINORITY`, `Potrace.TURNPOLICY_MAJORITY`. Refer to [this document][potrace-algorithm] for more information (page 4)
  (default: `Potrace.TURNPOLICY_MINORITY`)
- **turdSize** - suppress speckles of up to this size
  (default: 2)
- **alphaMax** - corner threshold parameter
  (default: 1)
- **optCurve** - curve optimization
  (default: `True`)
- **optTolerance** - curve optimization tolerance
  (default: 0.2)
- **threshold** - threshold below which color is considered black.
  Should be a number in range 0..255 or `Potrace.THRESHOLD_AUTO` in which case threshold will be selected automatically using [Algorithm For Multilevel Thresholding][multilevel-thresholding]
  (default: `Potrace.THRESHOLD_AUTO`)
- **blackOnWhite** - specifies colors by which side from threshold should be turned into vector shape
  (default: `True`)
- **color** - Fill color. Will be ignored when exporting as `<symbol>`. (default: `Potrace.COLOR_AUTO`, which means black or white, depending on `blackOnWhite` property)
- **background** - Background color. Will be ignored when exporting as `<symbol>`. By default is not present (`Potrace.COLOR_TRANSPARENT`)
-  **width** - Optional width for SVG output. Defaults to image width.
-  **height** - Optional height for SVG output. Defaults to image height.


---------------

The `Posterizer` class has the same methods as `Potrace`, with the exception of `.getPathTag()`.
The configuration dictionary is extended with the following properties:

- **fillStrategy** - determines how the fill color for each layer should be selected. Possible values are exported as constants:
    - `Posterizer.FILL_DOMINANT` - most frequent color in range (used by default),
    - `Posterizer.FILL_MEAN` - arithmetic mean (average),
    - `Posterizer.FILL_MEDIAN` - median color,
    - `Posterizer.FILL_SPREAD` - ignores color information of the image and just spreads colors equally in the range 0..<threshold> (or <threshold>..255 if `blackOnWhite` is set to `False`),
- **rangeDistribution** - how color stops for each layer should be selected. Ignored if `steps` is an array. Possible values are:
    - `Posterizer.RANGES_AUTO` - Performs automatic thresholding (using [Algorithm For Multilevel Thresholding][multilevel-thresholding]). Preferable method for already posterized sources but takes a long time to calculate 5 or more thresholds (exponential time complexity).
      *(used by default)*
    - `Posterizer.RANGES_EQUAL` - Ignores color information of the image and breaks the available color space into equal chunks
- **steps** - Specifies the desired number of layers in the resulting image. If a number is provided, thresholds for each layer will be automatically calculated according to the `rangeDistribution` parameter. If an array is provided, it is expected to be an array with precomputed thresholds for each layer (in the range 0..255)
  (default: `Posterizer.STEPS_AUTO`, which will result in `3` or `4`, depending on the `threshold` value)
- **threshold** - Breaks the image into foreground and background (and only the foreground is broken into the desired number of layers). Basically, when provided, it becomes a threshold for the last (least opaque) layer, and then `steps - 1` intermediate thresholds are calculated. If **steps** is an array of thresholds and every value from the array is lower (or larger if the **blackOnWhite** parameter is set to `False`) than the threshold, the threshold will be added to the array; otherwise, it's ignored.
  (default: `Potrace.THRESHOLD_AUTO`)
- *All other parameters that the `Potrace` class accepts*

**Notes:**

- When the number of `steps` is greater than 10, an extra layer could be added to ensure the presence of the darkest/brightest colors if needed to ensure the presence of probably-important-at-this-point details like shadows or line art.
- With a big number of layers, the produced image will be looking brighter overall than the original due to math error at the rendering phase because of how layers are composited.
- With the default configuration (`steps`, `threshold`, and `rangeDistribution` settings all set to `auto`), this results in 4 thresholds/color stops being calculated with the Multilevel Thresholding algorithm mentioned above. The calculation of 4 thresholds takes 3-5 seconds on an average laptop. You may want to explicitly limit the number of `steps` to 3 to moderately improve the processing speed.

## Thanks to

- Peter Selinger for the [original Potrace tool and algorithm][potrace]
- @kilobtye for the original [JavaScript port][potrace-by-kilobtye]
- @tooolbox for [node-potrace][node-potrace]
- @iwsfg for the original [node-potrace][node-potrace]
- @ertrzyiks for contributions to [node-potrace][node-potrace]

## Author

This Python port was created by [kgruiz](https://github.com/kgruiz).

## License

The GNU General Public License version 2 (GPLv2). Please see [License File](LICENSE) for more information.

[potrace]: http://potrace.sourceforge.net/
[potrace-algorithm]: http://potrace.sourceforge.net/potrace.pdf
[multilevel-thresholding]: http://www.iis.sinica.edu.tw/page/jise/2001/200109_01.pdf
[potrace-by-kilobtye]: https://github.com/kilobtye/potrace
[potrace-js-demo]: http://kilobtye.github.io/potrace/
[jimp]: https://github.com/oliver-moran/jimp
[node-potrace]: https://github.com/tooolbox/node-potrace