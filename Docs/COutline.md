# Potrace C Code Documentation


# Table of Contents


- [Core](#core)
  - [main.c](#mainc)
  - [main.h](#mainh)
  - [potracelib.c](#potracelibc)
  - [potracelib.h](#potracelibh)
  - [platform.h](#platformh)
  - [getopt.c](#getoptc)
  - [getopt1.c](#getopt1c)
  - [include/getopt/getopt.h](#includegetoptgetopth)
  - [getopt.h](#getopth)
- [Data Structures & Core Algorithms](#data-structures--core-algorithms)
  - [auxiliary.h](#auxiliaryh)
  - [bbox.h](#bboxh)
  - [bbox.c](#bboxc)
  - [bitmap.h](#bitmaph)
  - [bitmap_io.h](#bitmap_ioh)
  - [bitmap_io.c](#bitmap_ioc)
  - [curve.h](#curveh)
  - [curve.c](#curvec)
  - [decompose.h](#decomposeh)
  - [decompose.c](#decomposec)
  - [trace.h](#traceh)
  - [trace.c](#tracec)
  - [lists.h](#listsh)
  - [progress.h](#progressh)
  - [progress_bar.h](#progress_barh)
  - [progress_bar.c](#progress_barc)
  - [lzw.h](#lzwh)
  - [lzw.c](#lzwc)
  - [flate.h](#flateh)
  - [flate.c](#flatec)
  - [render.h](#renderh)
  - [render.c](#renderc)
  - [bitops.h](#bitopsh)
  - [trans.h](#transh)
  - [trans.c](#transc)
  - [greymap.h](#greymaph)
  - [greymap.c](#greymapc)
- [Backends (Output Formats)](#backends-output-formats)
  - [backend_eps.h](#backend_epsh)
  - [backend_eps.c](#backend_epsc)
  - [backend_pdf.h](#backend_pdfh)
  - [backend_pdf.c](#backend_pdfc)
  - [backend_pgm.h](#backend_pgmh)
  - [backend_pgm.c](#backend_pgmc)
  - [backend_svg.h](#backend_svgh)
  - [backend_svg.c](#backend_svgc)
  - [backend_xfig.h](#backend_xfigh)
  - [backend_xfig.c](#backend_xfigc)
  - [backend_dxf.h](#backend_dxfh)
  - [backend_dxf.c](#backend_dxfc)
  - [backend_geojson.h](#backend_geojsonh)
  - [backend_geojson.c](#backend_geojsonc)
- [Utilities & Demos](#utilities--demos)
  - [mkbitmap.c](#mkbitmapc)
  - [potracelib_demo.c](#potracelib_democ)


# Core


## File: main.c
```
This file contains the main function for the Potrace application, handling command-line parsing, dispatching tracing to the core library, generating output in various formats based on user selection, and managing program flow.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdio.h`: For standard input/output functions.
- `stdlib.h`: For standard memory allocation functions.
- `errno.h`: For error number definitions.
- `string.h`: For string functions.
- `strings.h`: For string functions.
- `getopt.h`: For command-line option parsing.
- `math.h`: For mathematical functions
- `main.h`: Header defining the interface of main structure.
- `potracelib.h`: Core Potrace library definitions.
- `backend_pdf.h`: Function declarations for the PDF backend.
- `backend_eps.h`: Function declarations for the EPS backend.
- `backend_pgm.h`: Function declarations for the PGM backend.
- `backend_svg.h`: Function declarations for the SVG backend.
- `backend_xfig.h`: Function declarations for the XFig backend.
- `backend_dxf.h`: Function declarations for the DXF backend.
- `backend_geojson.h`: Function declarations for the GeoJSON backend.
- `bitmap_io.h`: Function declarations for bitmap I/O.
- `bitmap.h`: Header defining bitmap types and helper functions.
- `platform.h`: Header for platform specific definitions and functions.
- `auxiliary.h`: Definition for commonly used helper macros and functions
- `progress_bar.h`: Function declarations for progress bar types and operations.
- `trans.h`: Header file that declares transformation data structures and related functions.

### Data Structures
#### `pageformat_s`
```c
struct pageformat_s {
  const char *name;
  int w, h;
};
```
Describes a page format with its dimensions.
- `name`: `const char *`, Name of the format
- `w`: `int`, Width in PostScript points
- `h`: `int`, Height in PostScript points

#### `turnpolicy_s`
```c
struct turnpolicy_s {
  const char *name;
  int n;
};
```
Describes the mapping of a turn policy name to a numerical representation of the strategy for handling ambiguous path turns.
- `name`: `const char *`, The name of the turn policy
- `n`: `int`, The numerical value representing the turn policy

#### `backend_s`
```c
struct backend_s {
  const char *name;       /* name of this backend */
  const char *ext;        /* file extension */
  int fixed;        /* fixed page size backend? */
  int pixel;        /* pixel-based backend? */
  int multi;        /* multi-page backend? */
  int (*init_f)(FILE *fout);                 /* initialization function */
  int (*page_f)(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
                                             /* per-bitmap function */
  int (*term_f)(FILE *fout);                 /* finalization function */
  int opticurve;    /* opticurve capable (true Bezier curves?) */
};
```
Describes the characteristics of various backends, providing information on the type of output and other properties.
- `name`: `const char *`, The name of the backend
- `ext`: `const char *`, The file extension of this backend.
- `fixed`: `int`, True if this backend has fixed page size
- `pixel`: `int`, True if this backend is pixel based (as opposed to vector).
- `multi`: `int`, True if this is a multi-page backend (ie. PDF or PS).
- `init_f`: `int (*)(FILE *fout)`, Initializes backend output.
- `page_f`: `int (*)(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo)`, Outputs the vector data in selected format.
- `term_f`: `int (*)(FILE *fout)`, Finishes the backend specific output format.
- `opticurve`: `int`, If this backend can output optimized curve information (true Bezier curves).

### Global Variables
#### `info`
```c
struct info_s info;
```
Global variable to store command-line options.

### Macros
#### `DIM_IN`
```c
#define DIM_IN (72)
```
Defines the number of points in an inch (72).

#### `DIM_CM`
```c
#define DIM_CM (72 / 2.54)
```
Defines the number of points in a centimeter.

#### `DIM_MM`
```c
#define DIM_MM (72 / 25.4)
```
Defines the number of points in a millimeter.

#### `DIM_PT`
```c
#define DIM_PT (1)
```
Defines the number of points in a point (1).

#### `DEFAULT_DIM`
```c
#ifdef USE_METRIC
#define DEFAULT_DIM DIM_CM
#else
#define DEFAULT_DIM DIM_IN
#endif
```
Defines the default dimension unit, either cm if `USE_METRIC` is defined or inches if it's not defined.

#### `DEFAULT_DIM_NAME`
```c
#ifdef USE_METRIC
#define DEFAULT_DIM_NAME "centimeters"
#else
#define DEFAULT_DIM_NAME "inches"
#endif
```
Defines the name of the default dimension, either "centimeters" if `USE_METRIC` is defined or "inches" otherwise.

#### `DEFAULT_PAPERWIDTH`
```c
#ifdef USE_A4
#define DEFAULT_PAPERWIDTH 595
#else
#define DEFAULT_PAPERWIDTH 612
#endif
```
Defines the default paper width, either A4 size if `USE_A4` is defined or letter size otherwise.

#### `DEFAULT_PAPERHEIGHT`
```c
#ifdef USE_A4
#define DEFAULT_PAPERHEIGHT 842
#else
#define DEFAULT_PAPERHEIGHT 792
#endif
```
Defines the default paper height, either A4 size if `USE_A4` is defined or letter size otherwise.

#### `DEFAULT_PAPERFORMAT`
```c
#ifdef USE_A4
#define DEFAULT_PAPERFORMAT "a4"
#else
#define DEFAULT_PAPERFORMAT "letter"
#endif
```
Defines the default paper format name, either "a4" if `USE_A4` is defined or "letter" otherwise.

#### `DEFAULT_PROGRESS_BAR`
```c
#ifdef DUMB_TTY
#define DEFAULT_PROGRESS_BAR progress_bar_simplified
#else
#define DEFAULT_PROGRESS_BAR progress_bar_vt100
#endif
```
Defines the default progress bar type, simplified if `DUMB_TTY` is defined or vt100 otherwise.

### Helper Functions
#### `backend_lookup`
```c
static int backend_lookup(const char *name, backend_t **bp);
```
Looks up a backend by its name, and returns it's corresponding `backend_t` structure.
- `name`: `const char *`, The name of the backend to look up.
- `bp`: `backend_t **`, Pointer where the located structure will be stored.
**Returns**:
`int`, 0 on success, 1 if not found, 2 if ambiguous.

#### `backend_list`
```c
static int backend_list(FILE *fout, int j, int linelen);
```
Prints a list of available backends to a file.
- `fout`: `FILE *`, File stream to output to.
- `j`: `int`, Current column number of text.
- `linelen`: `int`, Max length before a newline is needed.
**Returns:**
`int`, Column cursor is left at (may include multiple lines if linelength is shorter than a line), representing the position where to continue writing next.

#### `license`
```c
static void license(FILE *f);
```
Prints the license information.
- `f`: `FILE *`, The file to print to.

#### `show_defaults`
```c
static void show_defaults(FILE *f);
```
Prints default settings for command-line parameters.
- `f`: `FILE *`, The file to write defaults to.

#### `usage`
```c
static void usage(FILE *f);
```
Prints usage information.
- `f`: `FILE *`, The file to print to.

#### `parse_dimension`
```c
static dim_t parse_dimension(char *s, char **endptr);
```
Parses a dimension string (e.g. "1.5in", "7cm"), and returns the value in points and optionally consumes units in the given string.
- `s`: `char *`, Input dimension string.
- `endptr`: `char **`, Pointer where to store the position in string after parsing
**Returns**:
`dim_t`, The parsed dimension value

#### `parse_dimensions`
```c
static void parse_dimensions(char *s, char **endptr, dim_t *dxp, dim_t *dyp);
```
Parses a string containing two dimensions separated by 'x' char (e.g. "8.5x11in")
- `s`: `char *`, String containing dimensions to be parsed.
- `endptr`: `char **`, Pointer to where end of the parsed string is stored.
- `dxp`: `dim_t *`, First dimension, stores width
- `dyp`: `dim_t *`, Second dimension, stores height.

#### `double_of_dim`
```c
static inline double double_of_dim(dim_t d, double def);
```
Get the numerical value of a dimension, uses default if not specified.
- `d`: `dim_t`, Structure to get the dimension from
- `def`: `double`, Default value to use.
**Returns:**
`double`, The value in points.

#### `parse_color`
```c
static int parse_color(char *s);
```
Parses a color string to its integer representation
- `s`: `char *`, String representing a color in hex format ("#rrggbb").
**Returns:**
`int`, The color as RGB 0xrrggbb if successful, -1 on parsing error

#### `dopts`
```c
static void dopts(int ac, char *av[]);
```
Parses command-line options from the given arguments, and sets the global `info` variable.
- `ac`: `int`, Number of command line arguments
- `av`: `char **`, A pointer to the array of command line arguments

#### `my_fopen_read`
```c
static FILE *my_fopen_read(const char *filename);
```
Opens a file for reading or returns stdin if no filename or `-` is provided.
- `filename`: `const char *`, The filename or NULL or `-` for stdin.
**Returns:**
`FILE *`, A pointer to open stream.

#### `my_fopen_write`
```c
static FILE *my_fopen_write(const char *filename);
```
Opens a file for writing or returns stdout if no filename or `-` is provided.
- `filename`: `const char *`, The filename or NULL or `-` for stdout.
**Returns:**
`FILE *`, A pointer to open stream.

#### `my_fclose`
```c
static void my_fclose(FILE *f, const char *filename);
```
Closes a file, but does nothing is filename is NULL or "-".
- `f`: `FILE *`, The file to close.
- `filename`: `const char *`, The name of file, or NULL or "-" to do nothing.

#### `make_outfilename`
```c
static char *make_outfilename(const char *infile, const char *ext);
```
Creates a default output filename for input with a given extension.
- `infile`: `const char *`, The input filename.
- `ext`: `const char *`, The output filename extension.
**Returns:**
`char *`, The generated output filename string, or NULL if malloc fails.

### Calculations
#### `calc_dimensions`
```c
static void calc_dimensions(imginfo_t *imginfo, potrace_path_t *plist);
```
Calculates the dimensions of the output based on command line and
image dimensions, and optionally, based on the actual image outline.
- `imginfo`: `imginfo_t *`, the struct to output transformation information to.
- `plist`: `potrace_path_t *`, List of paths

### Input/Output
#### `process_file`
```c
static void process_file(backend_t *b, const char *infile, const char *outfile, FILE *fin, FILE *fout);
```
Processes a single file, containing one or more images, or stdin, performing tracing and writing the output to a file.
- `b`: `backend_t *`, The backend to use for output.
- `infile`: `const char *`, The name of the input file.
- `outfile`: `const char *`, The name of the output file.
- `fin`: `FILE *`, Input file descriptor.
- `fout`: `FILE *`, Output file descriptor.

### Main Function
#### `main`
```c
int main(int ac, char *av[]);
```
Entry point for command line tool that parses arguments, reads from input, traces, and outputs to a vector format.
- `ac`: `int`, Number of arguments in the command line.
- `av`: `char **`, Command line arguments.
**Returns:**
`int`, The exit code.


## File: main.h
```
This header file defines the main data structures and configurable defaults for the Potrace program. It includes necessary headers and declares the global `info` variable and structures used throughout the application.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `potracelib.h`: Core Potrace library definitions.
- `progress_bar.h`: Definitions for progress bar handling.
- `auxiliary.h`: Definitions for auxiliary types.
- `trans.h`: Definitions for transformations

### Structures
#### `dim_s`
```c
struct dim_s {
  double x; /* value */
  double d; /* dimension (in pt), or 0 if not given */
};
```
Represents a dimensioned value, where `x` is the numerical value and `d` is the dimension unit in points or 0 for pixel value.
- `x`: `double`, The numerical value
- `d`: `double`, The dimension unit in points or 0 for pixel value

#### `info_s`
```c
struct info_s {
  struct backend_s *backend;  /* type of backend (eps,ps,pgm etc) */
  potrace_param_t *param;  /* tracing parameters, see potracelib.h */
  int debug;         /* type of output (0-2) (for BACKEND_PS/EPS only) */
  dim_t width_d;     /* desired width of image */
  dim_t height_d;    /* desired height of image */
  double rx;         /* desired x resolution (in dpi) */
  double ry;         /* desired y resolution (in dpi) */
  double sx;         /* desired x scaling factor */
  double sy;         /* desired y scaling factor */
  double stretch;    /* ry/rx, if not otherwise determined */
  dim_t lmar_d, rmar_d, tmar_d, bmar_d;   /* margins */
  double angle;      /* rotate by this many degrees */
  int paperwidth, paperheight;  /* paper size for ps backend (in pt) */
  int tight;         /* should bounding box follow actual vector outline? */
  double unit;       /* granularity of output grid */
  int compress;      /* apply compression? */
  int pslevel;       /* postscript level to use: affects only compression */
  int color;         /* rgb color code 0xrrggbb: line color */
  int fillcolor;     /* rgb color code 0xrrggbb: fill color */
  double gamma;      /* gamma value for pgm backend */
  int longcoding;    /* do not optimize for file size? */
  char *outfile;     /* output filename, if given */
  char **infiles;    /* array of input filenames */
  int infilecount;   /* number of input filenames */
  int some_infiles;  /* do we process a list of input filenames? */
  double blacklevel; /* 0 to 1: black/white cutoff in input file */
  int invert;        /* invert bitmap? */
  int opaque;        /* paint white shapes opaquely? */
  int grouping;      /* 0=flat; 1=connected components; 2=hierarchical */
  int progress;      /* should we display a progress bar? */
  progress_bar_t *progress_bar;  /* which progress bar to use */
};
```
Holds command-line options and settings for processing bitmap images, including backend options and tracing parameters.
- `backend`: `struct backend_s *`, Type of backend (eps, ps, pgm etc.).
- `param`: `potrace_param_t *`, Tracing parameters (see `potracelib.h`).
- `debug`: `int`, Debug output level (0-2 for BACKEND_PS/EPS).
- `width_d`: `dim_t`, Desired width of image.
- `height_d`: `dim_t`, Desired height of image.
- `rx`: `double`, Desired x resolution (in dpi).
- `ry`: `double`, Desired y resolution (in dpi).
- `sx`: `double`, Desired x scaling factor.
- `sy`: `double`, Desired y scaling factor.
- `stretch`: `double`, Ry/rx, if not otherwise determined.
- `lmar_d`: `dim_t`, Left margin.
- `rmar_d`: `dim_t`, Right margin.
- `tmar_d`: `dim_t`, Top margin.
- `bmar_d`: `dim_t`, Bottom margin.
- `angle`: `double`, Rotation angle in degrees.
- `paperwidth`: `int`, Paper width for ps backend (in pt).
- `paperheight`: `int`, Paper height for ps backend (in pt).
- `tight`: `int`, Should bounding box follow actual vector outline.
- `unit`: `double`, Granularity of output grid.
- `compress`: `int`, Apply compression?
- `pslevel`: `int`, Postscript level to use.
- `color`: `int`, RGB color code (0xrrggbb): line color.
- `fillcolor`: `int`, RGB color code (0xrrggbb): fill color.
- `gamma`: `double`, Gamma value for pgm backend.
- `longcoding`: `int`, Do not optimize for file size?
- `outfile`: `char *`, Output filename, if given.
- `infiles`: `char **`, Array of input filenames.
- `infilecount`: `int`, Number of input filenames.
- `some_infiles`: `int`, Do we process a list of input filenames?
- `blacklevel`: `double`, Black/white cutoff in input file (0 to 1).
- `invert`: `int`, Invert bitmap?
- `opaque`: `int`, Paint white shapes opaquely?
- `grouping`: `int`, Grouping mode, 0=flat, 1=connected components, 2=hierarchical.
- `progress`: `int`, Should we display a progress bar?
- `progress_bar`: `progress_bar_t *`, Which progress bar to use.

#### `imginfo_s`
```c
struct imginfo_s {
  int pixwidth;        /* width of input pixmap */
  int pixheight;       /* height of input pixmap */
  double width;        /* desired width of image (in pt or pixels) */
  double height;       /* desired height of image (in pt or pixels) */
  double lmar, rmar, tmar, bmar;   /* requested margins (in pt) */
  trans_t trans;        /* specify relative position of a tilted rectangle */
};
```
Holds per-image information, including dimensions, margins, and transformation data.
- `pixwidth`: `int`, Width of input pixmap.
- `pixheight`: `int`, Height of input pixmap.
- `width`: `double`, Desired width of image (in pt or pixels).
- `height`: `double`, Desired height of image (in pt or pixels).
- `lmar`: `double`, Left margin in pt.
- `rmar`: `double`, Right margin in pt.
- `tmar`: `double`, Top margin in pt.
- `bmar`: `double`, Bottom margin in pt.
- `trans`: `trans_t`, Transformation specification (position, rotation, scaling).

### Global Variables
#### `info`
```c
extern info_t info;
```
An external global variable of type `info_t`, holding the parsed command-line options and settings, used for processing images throughout the Potrace application.

### Macros
#### `DIM_IN`
```c
#define DIM_IN (72)
```
Defines the number of points in an inch (72).

#### `DIM_CM`
```c
#define DIM_CM (72 / 2.54)
```
Defines the number of points in a centimeter.

#### `DIM_MM`
```c
#define DIM_MM (72 / 25.4)
```
Defines the number of points in a millimeter.

#### `DIM_PT`
```c
#define DIM_PT (1)
```
Defines the number of points in a point (1).

#### `DEFAULT_DIM`
```c
#ifdef USE_METRIC
#define DEFAULT_DIM DIM_CM
#else
#define DEFAULT_DIM DIM_IN
#endif
```
Defines the default dimension unit, either cm if `USE_METRIC` is defined or inches if it's not defined.

#### `DEFAULT_DIM_NAME`
```c
#ifdef USE_METRIC
#define DEFAULT_DIM_NAME "centimeters"
#else
#define DEFAULT_DIM_NAME "inches"
#endif
```
Defines the name of the default dimension, either "centimeters" if `USE_METRIC` is defined or "inches" otherwise.

#### `DEFAULT_PAPERWIDTH`
```c
#ifdef USE_A4
#define DEFAULT_PAPERWIDTH 595
#else
#define DEFAULT_PAPERWIDTH 612
#endif
```
Defines the default paper width, either A4 size if `USE_A4` is defined or letter size otherwise.

#### `DEFAULT_PAPERHEIGHT`
```c
#ifdef USE_A4
#define DEFAULT_PAPERHEIGHT 842
#else
#define DEFAULT_PAPERHEIGHT 792
#endif
```
Defines the default paper height, either A4 size if `USE_A4` is defined or letter size otherwise.

#### `DEFAULT_PAPERFORMAT`
```c
#ifdef USE_A4
#define DEFAULT_PAPERFORMAT "a4"
#else
#define DEFAULT_PAPERFORMAT "letter"
#endif
```
Defines the default paper format name, either "a4" if `USE_A4` is defined or "letter" otherwise.

#### `DEFAULT_PROGRESS_BAR`
```c
#ifdef DUMB_TTY
#define DEFAULT_PROGRESS_BAR progress_bar_simplified
#else
#define DEFAULT_PROGRESS_BAR progress_bar_vt100
#endif
```
Defines the default progress bar type, simplified if `DUMB_TTY` is defined or vt100 otherwise.


## File: potracelib.c
```
This file implements the core Potrace library functions, including initialization of parameters, tracing a bitmap, and freeing allocated resources.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdlib.h`: Standard memory allocation functions
- `string.h`: Standard string functions
- `potracelib.h`: Public definitions of structures and functions used in core library.
- `curve.h`: Definition of the private curve data structures used in this file
- `decompose.h`: Decompose a bitmap image into paths.
- `trace.h`: Transforms paths into smooth curves
- `progress.h`: Definition of the structure for progress tracking.

### Global Variables
#### `param_default`
```c
static const potrace_param_t param_default = {
  2,                             /* turdsize */
  POTRACE_TURNPOLICY_MINORITY,   /* turnpolicy */
  1.0,                           /* alphamax */
  1,                             /* opticurve */
  0.2,                           /* opttolerance */
  {
    NULL,                        /* callback function */
    NULL,                        /* callback data */
    0.0, 1.0,                    /* progress range */
    0.0,                         /* granularity */
  },
};
```
A static variable defining the default parameters for potrace, including turd size, turning policy, corner threshold, if curve optimization is enabled, curve optimization tolerance, and also defines the default settings for the progress bar.

### Functions
#### `potrace_param_default`
```c
potrace_param_t *potrace_param_default(void);
```
Returns a fresh copy of the set of default parameters.
**Returns:**
`potrace_param_t *`, A pointer to default parameters, or NULL on failure with errno set.

#### `potrace_param_free`
```c
void potrace_param_free(potrace_param_t *p);
```
Frees the memory allocated for Potrace parameters.
- `p`: `potrace_param_t *`, The parameters to be freed.

#### `potrace_trace`
```c
potrace_state_t *potrace_trace(const potrace_param_t *param, const potrace_bitmap_t *bm);
```
Traces a bitmap into a vector representation, using the given parameters and returning an object that stores status and results.
- `param`: `const potrace_param_t *`, The parameters for the tracing process.
- `bm`: `const potrace_bitmap_t *`, The bitmap to be traced.
**Returns:**
`potrace_state_t *`, The resulting potrace state, or NULL on error

#### `potrace_state_free`
```c
void potrace_state_free(potrace_state_t *st);
```
Frees the memory associated with the potrace state
- `st`: `potrace_state_t *`, The potrace state to be freed

#### `potrace_version`
```c
const char *potrace_version(void);
```
Returns the library version as a string.
**Returns:**
`const char *`, String representing the potracelib library version.


## File: potracelib.h
```c
This header file defines the public API for the core Potrace library. For a more
   detailed description of the API, see potracelib.pdf
```
### Includes
- None

### Structures
#### `potrace_progress_s`
```c
struct potrace_progress_s {
  void (*callback)(double progress, void *privdata); /* callback fn */
  void *data;          /* callback function's private data */
  double min, max;     /* desired range of progress, e.g. 0.0 to 1.0 */
  double epsilon;      /* granularity: can skip smaller increments */
};
```
Represents the structure for holding progress reporting callback data
- `callback`: `void (*)(double progress, void *privdata)`, Callback function called to provide updates for the process.
- `data`: `void *`, Private data to pass to the callback function.
- `min`: `double`, lower bound of progress range.
- `max`: `double`, upper bound of progress range.
- `epsilon`: `double`, granularity of progress reporting, updates are skipped if they are not larger than this value, resulting in fewer calls.

#### `potrace_param_s`
```c
struct potrace_param_s {
  int turdsize;        /* area of largest path to be ignored */
  int turnpolicy;      /* resolves ambiguous turns in path decomposition */
  double alphamax;     /* corner threshold */
  int opticurve;       /* use curve optimization? */
  double opttolerance; /* curve optimization tolerance */
  potrace_progress_t progress; /* progress callback function */
};
```
Represents the parameters that configure the tracing behavior of Potrace.
- `turdsize`: `int`, Maximum area of a path (connected pixels) to be ignored (speckle suppression).
- `turnpolicy`: `int`, Specifies how ambiguous turns during path decomposition should be resolved.
- `alphamax`: `double`, Corner threshold parameter.
- `opticurve`: `int`, Flag controlling the curve optimization.
- `opttolerance`: `double`, Tolerance value for the curve optimization algorithm.
- `progress`: `potrace_progress_t`, Progress monitoring settings.

#### `potrace_bitmap_s`
```c
struct potrace_bitmap_s {
  int w, h;              /* width and height, in pixels */
  int dy;                /* words per scanline (not bytes) */
  potrace_word *map;     /* raw data, dy*h words */
};
```
Represents a bitmap, storing its dimensions, scanline width and the raw pixel data.
- `w`: `int`, The width of bitmap (pixels).
- `h`: `int`, The height of bitmap (pixels).
- `dy`: `int`, Number of words (native word size) per scanline.
- `map`: `potrace_word *`, Raw bit data for the bitmap.

#### `potrace_dpoint_s`
```c
struct potrace_dpoint_s {
  double x, y;
};
```
Structure representing a point in 2D using doubles.
- `x`: `double`, X coordinate of point
- `y`: `double`, Y coordinate of point

#### Segment Tags
- `POTRACE_CURVETO`: A tag indicating the current path segment is a cubic Bezier curve.
- `POTRACE_CORNER`: A tag indicating the current path segment is a corner made of two straight lines

#### `potrace_curve_s`
```c
struct potrace_curve_s {
  int n;                    /* number of segments */
  int *tag;                 /* tag[n]: POTRACE_CURVETO or POTRACE_CORNER */
  potrace_dpoint_t (*c)[3]; /* c[n][3]: control points.
			       c[n][0] is unused for tag[n]=POTRACE_CORNER */
};
```
Structure to hold the curve data, consisting of an array of segments, each being a Bezier curve or a corner.
- `n`: `int`, The number of segments in the curve.
- `tag`: `int *`, Array of segment types `POTRACE_CORNER` or `POTRACE_CURVETO`.
- `c`: `potrace_dpoint_t (*)[3]`, 2D control points of segments of curve. For `POTRACE_CURVETO` there are 3 points (p1, p2, and p3), for `POTRACE_CORNER` c[1] represents one end of the corner and c[2] the other end of the corner (c[0] is unused).

#### `potrace_path_s`
```c
struct potrace_path_s {
  int area;                         /* area of the bitmap path */
  int sign;                         /* '+' or '-', depending on orientation */
  potrace_curve_t curve;            /* this path's vector data */

  struct potrace_path_s *next;      /* linked list structure */

  struct potrace_path_s *childlist; /* tree structure */
  struct potrace_path_s *sibling;   /* tree structure */

  struct potrace_privpath_s *priv;  /* private state */
};
```
Represents a traced path, including its area, orientation, curve data, linked list and tree structure information and private data used during calculations.
- `area`: `int`, Area of the path in the bitmap (used for filtering small paths).
- `sign`: `int`, Orientation of the path: '+' for counterclockwise, '-' for clockwise.
- `curve`: `potrace_curve_t`, The vector data of the curve/path
- `next`: `struct potrace_path_s *`,  Pointer to the next path in linked list of paths.
- `childlist`: `struct potrace_path_s *`, Pointer to linked list of child paths representing enclosed areas.
- `sibling`: `struct potrace_path_s *`, Pointer to next path in tree structure at the same depth.
- `priv`: `struct potrace_privpath_s *`, Pointer to the private path data structure used during path creation.

#### `potrace_state_s`
```c
struct potrace_state_s {
  int status;
  potrace_path_t *plist;            /* vector data */

  struct potrace_privstate_s *priv; /* private state */
};
```
Represents the overall state of Potrace processing.
- `status`: `int`, Status of tracing operation, 0 indicates `POTRACE_STATUS_OK` and 1 indicates `POTRACE_STATUS_INCOMPLETE`
- `plist`: `potrace_path_t *`, vector data of extracted paths
- `priv`: `struct potrace_privstate_s *`, private state

### API Functions
#### `potrace_param_default`
```c
potrace_param_t *potrace_param_default(void);
```
Gets the default parameters for Potrace tracing.
**Returns**:
`potrace_param_t *`, The Potrace default parameters, or `NULL` on error.

#### `potrace_param_free`
```c
void potrace_param_free(potrace_param_t *p);
```
Frees the memory allocated for a set of Potrace parameters.
- `p`: `potrace_param_t *`, The parameters to free.

#### `potrace_trace`
```c
potrace_state_t *potrace_trace(const potrace_param_t *param,
			       const potrace_bitmap_t *bm);
```
Traces a bitmap image using the given parameters.
- `param`: `const potrace_param_t *`, The tracing parameters.
- `bm`: `const potrace_bitmap_t *`, The bitmap to be traced.
**Returns**:
`potrace_state_t *`, The Potrace tracing state object, or NULL on failure (with errno set). The status inside this object may indicate that the tracing process is incomplete due to error during curve optimization.

#### `potrace_state_free`
```c
void potrace_state_free(potrace_state_t *st);
```
Frees all memory allocated for a Potrace state object.
- `st`: `potrace_state_t *`, The state object to free.

#### `potrace_version`
```c
const char *potrace_version(void);
```
Returns a static plain text version string identifying this version
   of potracelib
**Returns**:
`const char *`, The potracelib version string.


## File: platform.h
```
This header file contains platform-specific initializations for Potrace, including setting file I/O to binary mode on Windows, OS/2, and Cygwin platforms.
```

### Includes
- `config.h` (conditional): Provides configuration defines.

### Macros
####  Platform Specific Settings
- `__MINGW32__`: If MinGW32 (windows) is used, defines function for setting stdin and stdout in binary mode.
- `__CYGWIN__`: If Cygwin is used, defines function for setting stdin and stdout in binary mode.
- `__OS2__`: If OS2 is used, defines function for setting stdin and stdout in binary mode.
- Otherwise, defines an empty `platform_init` function that does not perform any operation.

### Functions
#### `platform_init`
```c
static inline void platform_init(void);
```
Performs any necessary platform-specific initialization, especially setting stdin/stdout to binary mode.


## File: getopt.c
```
This file provides the implementation of the `getopt` function, a part of the GNU C Library, used for parsing command-line options, along with related functionalities such as `_getopt_internal`, `exchange` and helper functions.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdio.h`: For standard input/output functions.
- `stdlib.h`: For standard memory allocation functions.
- `unistd.h` (conditional): For non-GNU libraries
- `string.h` (conditional): For some C standard library function
- `strings.h` (conditional): For systems that use strings.h rather than string.h
- `libintl.h` (conditional): For internationalized messages
- `getopt.h`: Declaration of getopt related data structures and interfaces.

### Global Variables
#### `optarg`
```c
char *optarg;
```
Stores the argument value of the matched option.

#### `optind`
```c
int optind = 1;
```
Index in ARGV of the next element to be scanned. It is used for communication to and from the caller and for communication between successive calls to `getopt`.

   On entry to `getopt`, zero means this is the first call; initialize.

   When `getopt` returns -1, this is the index of the first of the
   non-option elements that the caller should itself scan.

   Otherwise, `optind` communicates from one call to the next
   how much of ARGV has been scanned so far.

#### `__getopt_initialized`
```c
int __getopt_initialized;
```
A flag to check if the getopt function is initialized.

#### `nextchar`
```c
static char *nextchar;
```
The next char to be scanned in the option-element in which the last option character we returned was found.
   This allows us to pick up the scan where we left off.

#### `opterr`
```c
int opterr = 1;
```
Set to 0 to suppress error messages from `getopt` about unrecognized options.

#### `optopt`
```c
int optopt = '?';
```
Set to an option character which was unrecognized.

#### `ordering`
```c
static enum
{
  REQUIRE_ORDER, PERMUTE, RETURN_IN_ORDER
} ordering;
```
Describes how to deal with options that follow non-option ARGV-elements.

   If the caller did not specify anything,
   the default is REQUIRE_ORDER if the environment variable
   POSIXLY_CORRECT is defined, PERMUTE otherwise.

   REQUIRE_ORDER means don't recognize them as options;
   stop option processing when the first non-option is seen.
   This is what Unix does.
   This mode of operation is selected by either setting the environment
   variable POSIXLY_CORRECT, or using `+' as the first character
   of the list of option characters.

   PERMUTE is the default.  We permute the contents of ARGV as we scan,
   so that eventually all the non-options are at the end.  This allows options
   to be given in any order, even with programs that were not written to
   expect this.

   RETURN_IN_ORDER is an option available to programs that were written
   to expect options and other ARGV-elements in any order and that care about
   the ordering of the two.  We describe each non-option ARGV-element
   as if it were the argument of an option with character code 1.
   Using `-' as the first character of the list of option characters
   selects this mode of operation.

   The special argument `--' forces an end of option-scanning regardless
   of the value of `ordering'.  In the case of RETURN_IN_ORDER, only
   `--' can cause `getopt' to return -1 with `optind' != ARGC.

#### `posixly_correct`
```c
static char *posixly_correct;
```
Stores value of POSIXLY_CORRECT enviroment variable.

#### `first_nonopt`
```c
static int first_nonopt;
```
Index in ARGV of the first non-option argument.

#### `last_nonopt`
```c
static int last_nonopt;
```
Index in ARGV after last non-option argument.

#### `nonoption_flags_max_len`
```c
#ifdef _LIBC
static int nonoption_flags_max_len;
#endif
```
Variable related to `__getopt_nonoption_flags`. Only available in GNU libraries.

#### `nonoption_flags_len`
```c
#ifdef _LIBC
static int nonoption_flags_len;
#endif
```
Variable related to `__getopt_nonoption_flags`. Only available in GNU libraries.

#### `original_argc`
```c
#ifdef _LIBC
static int original_argc;
#endif
```
Variable to store original `argc` value. Only available in GNU libraries.

#### `original_argv`
```c
#ifdef _LIBC
static char *const *original_argv;
#endif
```
Variable to store original `argv` value. Only available in GNU libraries.

#### `__getopt_nonoption_flags`
```c
#ifdef _LIBC
extern char *__getopt_nonoption_flags;
#endif
```
Variable from bash 2.0 and related libraries for non options, used only in GNU libcs

### Functions
#### `exchange`
```c
#if defined __STDC__ && __STDC__
static void exchange (char **);
#endif
```
Exchange two adjacent subsequences of ARGV.
- `argv`: `char **`, list of string arguments

#### `_getopt_initialize`
```c
#if defined __STDC__ && __STDC__
static const char *_getopt_initialize (int, char *const *, const char *);
#endif
```
Initializes the internal getopt data before the first call.
- `argc`: `int`, The number of command-line arguments.
- `argv`: `char *const *`, An array of command-line argument strings.
- `optstring`: `const char *`, A string of short option characters.
**Returns:**
`const char *`, processed option string

#### `_getopt_internal`
```c
int _getopt_internal (int argc, char *const *argv, const char *shortopts,
			     const struct option *longopts, int *longind,
			     int long_only);
```
Scans elements of ARGV for option characters given in OPTSTRING.

   If an element of ARGV starts with '-', and is not exactly "-" or "--",
   then it is an option element.  The characters of this element
   (aside from the initial '-') are option characters.  If `getopt'
   is called repeatedly, it returns successively each of the option characters
   from each of the option elements.

   If there are no more option characters, `getopt' returns -1.
   Then `optind' is the index in ARGV of the first ARGV-element
   that is not an option.  (The ARGV-elements have been permuted
   so that those that are not options now come last.)

   OPTSTRING is a string containing the legitimate option characters.
   If an option character is seen that is not listed in OPTSTRING,
   return '?' after printing an error message.  If you set `opterr' to
   zero, the error message is suppressed but we still return '?'.

   If a char in OPTSTRING is followed by a colon, that means it wants an arg,
   so the following text in the same ARGV-element, or the text of the following
   ARGV-element, is returned in `optarg'.  Two colons mean an option that
   wants an optional arg; if there is text in the current ARGV-element,
   it is returned in `optarg', otherwise `optarg' is set to zero.

   If OPTSTRING starts with `-' or `+', it requests different methods of
   handling the non-option ARGV-elements.
   See the comments about RETURN_IN_ORDER and REQUIRE_ORDER, above.

   Long-named options begin with `--' instead of `-'.
   Their names may be abbreviated as long as the abbreviation is unique
   or is an exact match for some defined option.  If they have an
   argument, it follows the option name in the same ARGV-element, separated
   from the option name by a `=', or else the in next ARGV-element.
   When `getopt' finds a long-named option, it returns 0 if that option's
   `flag' field is nonzero, the value of the option's `val' field
   if the `flag' field is zero.
- `argc`: `int`, The number of command-line arguments.
- `argv`: `char *const *`, An array of command-line argument strings.
- `shortopts`: `const char *`, A string of short option characters.
- `longopts`: `const struct option *`, An array of `struct option` structs for long options.
- `longind`: `int *`, A pointer to an integer that will hold the index of the matched long option, within longopts array, or it's set to NULL if no long option was matched.
- `long_only`: `int`, If set to a value different than zero, allows a single dash to indicate a long option.
**Returns:**
`int`, The option character found, or -1 when no options are left.

#### `getopt`
```c
int getopt (int argc, char *const *argv, const char *optstring);
```
Parses command-line options, returning the option character and potentially setting `optarg`, reordering ARGV to place non-options after all options.
- `argc`: `int`, The number of command-line arguments.
- `argv`: `char *const *`, An array of command-line argument strings.
- `optstring`: `const char *`, A string of short option characters.
**Returns:**
`int`, The option character found, or -1 when no options are left.


## File: getopt1.c
```
This file provides the `getopt_long` and `getopt_long_only` entry points for GNU getopt, which is a function used for parsing command-line options. It is a part of the GNU C Library.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `getopt.h`: Header file for the getopt function.
- `stdio.h`: Standard input/output functions.
- `stdlib.h` (conditional): For GNU C library, contains definitions for standard library functions.

### Functions
#### `getopt_long`
```c
int getopt_long (int argc, char *const *argv, const char *options, const struct option *long_options, int *opt_index);
```
Parses command-line arguments, supporting both short and long options.
- `argc`: `int`, The number of command-line arguments.
- `argv`: `char *const *`, An array of command-line argument strings.
- `options`: `const char *`, A string of short option characters.
- `long_options`: `const struct option *`, An array of `struct option` structs for long options.
- `opt_index`: `int *`, A pointer to an integer that stores the index of the matched long option.

**Returns**:
`int` The option character found, or -1 if no more options or an error.

#### `getopt_long_only`
```c
int getopt_long_only (int argc, char *const *argv, const char *options, const struct option *long_options, int *opt_index);
```
Similar to `getopt_long`, but interprets '-' as a long option indicator as well.
- `argc`: `int`, The number of command-line arguments.
- `argv`: `char *const *`, An array of command-line argument strings.
- `options`: `const char *`, A string of short option characters.
- `long_options`: `const struct option *`, An array of `struct option` structs for long options.
- `opt_index`: `int *`, A pointer to an integer that stores the index of the matched long option.

**Returns**:
`int` The option character found, or -1 if no more options or an error.


## File: include/getopt/getopt.h
```
This is the header file for getopt. It defines structs and functions that allow a program to parse command line arguments.
```
### Includes
- `ctype.h` (conditional): This header includes character classification and conversion functions.

### Structure Definitions
#### `option`
```c
struct option
{
# if defined __STDC__ && __STDC__
  const char *name;
# else
  char *name;
# endif
  /* has_arg can't be an enum because some compilers complain about
     type mismatches in all the code that assumes it is an int.  */
  int has_arg;
  int *flag;
  int val;
};
```
Structure defining a long option for parsing command-line arguments.
- `name`: `char *`, The name of the option
- `has_arg`: `int`, Flag specifying if an argument is needed. Values `no_argument`, `required_argument`, `optional_argument`
- `flag`: `int *`, Pointer to flag that will be set if the long option is provided. If NULL, no flag will be set
- `val`: `int`, The value that will be returned if flag is NULL.

### Constants
#### `no_argument`
```c
# define no_argument		0
```
Indicates that an option does not accept an argument.

#### `required_argument`
```c
# define required_argument	1
```
Indicates that an option requires an argument.

#### `optional_argument`
```c
# define optional_argument	2
```
Indicates that an option can accept an optional argument.

### External Global Variables
#### `optarg`
```c
extern char *optarg;
```
Stores the argument value of the matched option.

#### `optind`
```c
extern int optind;
```
Index of the next ARGV-element to be scanned. It is a shared variable between the caller and getopt. It is set to `1` before calling getopt for the first time, and is modified by getopt each call to it, so that getopt continues from the next ARGV-element from last call. It is also set by getopt after all options are processed to index of the first non option argument, or ARGV size + 1 if all ARGV-elements have been processed.

#### `opterr`
```c
extern int opterr;
```
Set to 0 to suppress error messages from getopt about unrecognized options.

#### `optopt`
```c
extern int optopt;
```
Set to an option character which was unrecognized.

### Functions
#### `getopt`
```c
#if defined __STDC__ && __STDC__
# ifdef __GNU_LIBRARY__
extern int getopt (int argc, char *const *argv, const char *shortopts);
# else
extern int getopt ();
# endif
#else
extern int getopt ();
#endif
```
Parses command-line arguments, used for short option parsing.
- `argc`: `int`, The number of command-line arguments.
- `argv`: `char *const *`, An array of command-line argument strings.
- `shortopts`: `const char *`, A string of short option characters.
**Returns:**
`int`, The option character found, or -1 when no options are left.

#### `getopt_long`
```c
# ifndef __need_getopt
extern int getopt_long (int argc, char *const *argv, const char *shortopts,
		        const struct option *longopts, int *longind);
# endif
```
Parses command-line arguments, supporting both short and long options.
- `argc`: `int`, The number of command-line arguments.
- `argv`: `char *const *`, An array of command-line argument strings.
- `shortopts`: `const char *`, A string of short option characters.
- `longopts`: `const struct option *`, An array of `struct option` structs for long options.
- `longind`: `int *`, A pointer to an integer that will hold the index of the matched long option, within longopts array, or it's set to NULL if no long option was matched.
**Returns:**
`int`, The option character found, or -1 when no options are left.

#### `getopt_long_only`
```c
# ifndef __need_getopt
extern int getopt_long_only (int argc, char *const *argv,
			     const char *shortopts,
		             const struct option *longopts, int *longind);
# endif
```
Parses command-line arguments, supporting both short and long options, and treating both "-" and "--" as long option prefixes.
- `argc`: `int`, The number of command-line arguments.
- `argv`: `char *const *`, An array of command-line argument strings.
- `shortopts`: `const char *`, A string of short option characters.
- `longopts`: `const struct option *`, An array of `struct option` structs for long options.
- `longind`: `int *`, A pointer to an integer that will hold the index of the matched long option, within longopts array, or it's set to NULL if no long option was matched.
**Returns:**
`int`, The option character found, or -1 when no options are left.

#### `_getopt_internal`
```c
# ifndef __need_getopt
extern int _getopt_internal (int argc, char *const *argv,
			     const char *shortopts,
		             const struct option *longopts, int *longind,
			     int long_only);
# endif
```
Internal only.  Users should not call this directly.
- `argc`: `int`, The number of command-line arguments.
- `argv`: `char *const *`, An array of command-line argument strings.
- `shortopts`: `const char *`, A string of short option characters.
- `longopts`: `const struct option *`, An array of `struct option` structs for long options.
- `longind`: `int *`, A pointer to an integer that will hold the index of the matched long option, within longopts array, or it's set to NULL if no long option was matched.
- `long_only`: `int`, If set to a value different than zero, allows a single dash to indicate a long option.
**Returns:**
`int`, The option character found, or -1 when no options are left.


## File: getopt.h
```
This is the header file for the getopt function and its related data structures, used for parsing command-line arguments. It's a part of the GNU C Library.
```
### Includes
- `ctype.h` (conditional): This header includes character classification and conversion functions.

### Structure Definitions
#### `option`
```c
struct option
{
# if defined __STDC__ && __STDC__
  const char *name;
# else
  char *name;
# endif
  /* has_arg can't be an enum because some compilers complain about
     type mismatches in all the code that assumes it is an int.  */
  int has_arg;
  int *flag;
  int val;
};
```
Structure defining a long option for parsing command-line arguments.
- `name`: `char *`, The name of the option
- `has_arg`: `int`, Flag specifying if an argument is needed. Values `no_argument`, `required_argument`, `optional_argument`
- `flag`: `int *`, Pointer to flag that will be set if the long option is provided. If NULL, no flag will be set
- `val`: `int`, The value that will be returned if flag is NULL.

### Constants
#### `no_argument`
```c
# define no_argument		0
```
Indicates that an option does not accept an argument.

#### `required_argument`
```c
# define required_argument	1
```
Indicates that an option requires an argument.

#### `optional_argument`
```c
# define optional_argument	2
```
Indicates that an option can accept an optional argument.

### External Global Variables
#### `optarg`
```c
extern char *optarg;
```
Stores the argument value of the matched option.

#### `optind`
```c
extern int optind;
```
Index of the next ARGV-element to be scanned. It is a shared variable between the caller and getopt. It is set to `1` before calling getopt for the first time, and is modified by getopt each call to it, so that getopt continues from the next ARGV-element from last call. It is also set by getopt after all options are processed to index of the first non option argument, or ARGV size + 1 if all ARGV-elements have been processed.

#### `opterr`
```c
extern int opterr;
```
Set to 0 to suppress error messages from getopt about unrecognized options.

#### `optopt`
```c
extern int optopt;
```
Set to an option character which was unrecognized.

### Functions
#### `getopt`
```c
#if defined __STDC__ && __STDC__
# ifdef __GNU_LIBRARY__
extern int getopt (int argc, char *const *argv, const char *shortopts);
# else
extern int getopt ();
# endif
#else
extern int getopt ();
#endif
```
Parses command-line arguments, used for short option parsing.
- `argc`: `int`, The number of command-line arguments.
- `argv`: `char *const *`, An array of command-line argument strings.
- `shortopts`: `const char *`, A string of short option characters.
**Returns:**
`int`, The option character found, or -1 when no options are left.

#### `getopt_long`
```c
# ifndef __need_getopt
extern int getopt_long (int argc, char *const *argv, const char *shortopts,
		        const struct option *longopts, int *longind);
# endif
```
Parses command-line arguments, supporting both short and long options.
- `argc`: `int`, The number of command-line arguments.
- `argv`: `char *const *`, An array of command-line argument strings.
- `shortopts`: `const char *`, A string of short option characters.
- `longopts`: `const struct option *`, An array of `struct option` structs for long options.
- `longind`: `int *`, A pointer to an integer that will hold the index of the matched long option, within longopts array, or it's set to NULL if no long option was matched.
**Returns:**
`int`, The option character found, or -1 when no options are left.

#### `getopt_long_only`
```c
# ifndef __need_getopt
extern int getopt_long_only (int argc, char *const *argv,
			     const char *shortopts,
		             const struct option *longopts, int *longind);
# endif
```
Parses command-line arguments, supporting both short and long options, and treating both "-" and "--" as long option prefixes.
- `argc`: `int`, The number of command-line arguments.
- `argv`: `char *const *`, An array of command-line argument strings.
- `shortopts`: `const char *`, A string of short option characters.
- `longopts`: `const struct option *`, An array of `struct option` structs for long options.
- `longind`: `int *`, A pointer to an integer that will hold the index of the matched long option, within longopts array, or it's set to NULL if no long option was matched.
**Returns:**
`int`, The option character found, or -1 when no options are left.

#### `_getopt_internal`
```c
# ifndef __need_getopt
extern int _getopt_internal (int argc, char *const *argv,
			     const char *shortopts,
		             const struct option *longopts, int *longind,
			     int long_only);
# endif
```
Internal only.  Users should not call this directly.
- `argc`: `int`, The number of command-line arguments.
- `argv`: `char *const *`, An array of command-line argument strings.
- `shortopts`: `const char *`, A string of short option characters.
- `longopts`: `const struct option *`, An array of `struct option` structs for long options.
- `longind`: `int *`, A pointer to an integer that will hold the index of the matched long option, within longopts array, or it's set to NULL if no long option was matched.
- `long_only`: `int`, If set to a value different than zero, allows a single dash to indicate a long option.
**Returns:**
`int`, The option character found, or -1 when no options are left.


# Data Structures & Core Algorithms


## File: auxiliary.h
```
This header file defines general-purpose macros, inline functions, and types used in various parts of the Potrace project.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdlib.h`: For standard library functions.
- `potracelib.h`: Core Potrace library definitions.

### Structures
#### `point_s`
```c
struct point_s {
  long x;
  long y;
};
```
Represents a point using long integers for x and y coordinates.
- `x`: `long`, X-coordinate.
- `y`: `long`, Y-coordinate.

### Type Definitions
#### `dpoint_t`
```c
typedef potrace_dpoint_t dpoint_t;
```
Type definition for point structure with doubles.

### Functions
#### `dpoint`
```c
static inline dpoint_t dpoint(point_t p);
```
Converts a `point_t` to a `dpoint_t`.
- `p`: `point_t`, The input point.
**Returns**:
`dpoint_t`, The converted point with double coordinates.

#### `interval`
```c
static inline dpoint_t interval(double lambda, dpoint_t a, dpoint_t b);
```
Calculates a point on a line segment defined by a and b, using a parametric value between 0 and 1.
- `lambda`: `double`, The parameter for interpolation (0.0 yields `a`, 1.0 yields `b`).
- `a`: `dpoint_t`, The starting point.
- `b`: `dpoint_t`, The ending point.
**Returns**:
`dpoint_t`, The interpolated point.

### Macros
#### `mod`
```c
static inline int mod(int a, int n);
```
Calculates the modulo of `a` by `n`, handling negative numbers correctly.
- `a`: `int`, The input number.
- `n`: `int`, The divisor.
**Returns:**
`int`, a % n or equivalent value.

#### `floordiv`
```c
static inline int floordiv(int a, int n);
```
Calculates the integer floor of division.
- `a`: `int`, The dividend.
- `n`: `int`, The divisor.
**Returns:**
`int`, Result of integer division, floored to the nearest integer.

#### `sign`
```c
#define sign(x) ((x)>0 ? 1 : (x)<0 ? -1 : 0)
```
Determines the sign of a value
- `x`: Any numeric type, Value whose sign will be determined
**Returns:**
`int`, returns 1 if x>0, -1 if x<0, 0 if x==0.

#### `abs`
```c
#define abs(a) ((a)>0 ? (a) : -(a))
```
Calculates the absolute value of `a`.
- `a`: Any numeric type, The number to be checked
**Returns:**
Any numeric type, Result of the function.

#### `min`
```c
#define min(a,b) ((a)<(b) ? (a) : (b))
```
Returns the minimum value between `a` and `b`.
- `a`: Any numeric type, The first number to compare.
- `b`: Any numeric type, The second number to compare.
**Returns:**
Any numeric type, Minimum value between `a` and `b`.

#### `max`
```c
#define max(a,b) ((a)>(b) ? (a) : (b))
```
Returns the maximum value between `a` and `b`.
- `a`: Any numeric type, The first number to compare.
- `b`: Any numeric type, The second number to compare.
**Returns:**
Any numeric type, Maximum value between `a` and `b`.

#### `sq`
```c
#define sq(a) ((a)*(a))
```
Calculates the square of a value.
- `a`: Any numeric type, The number to be squared.
**Returns:**
Any numeric type, Result of the function.

#### `cu`
```c
#define cu(a) ((a)*(a)*(a))
```
Calculates the cube of a value.
- `a`: Any numeric type, The number to be cubed.
**Returns:**
Any numeric type, Result of the function.


## File: bbox.h
```
This header file defines data structures and functions related to bounding boxes and limits calculations on paths. It defines the interval type for storing min and max values along a given direction.
```

### Includes
- `potracelib.h`: Core Potrace library definitions.

### Structures
#### `interval_s`
```c
struct interval_s {
  double min, max;
};
```
Represents an interval defined by a minimum and maximum double value.
- `min`: `double`, The minimum value of the interval
- `max`: `double`, The maximum value of the interval

### Functions
#### `path_limits`
```c
void path_limits(potrace_path_t *path, potrace_dpoint_t dir, interval_t *i);
```
Calculates the limits (min and max) of the path along the specified direction.
- `path`: `potrace_path_t *`, The path to calculate limits for.
- `dir`: `potrace_dpoint_t`, The direction vector.
- `i`: `interval_t *`, A pointer to the output interval, where results are stored.


## File: bbox.c
```
This file provides the implementations for bounding box operations, and functions for calculating path limits along given directions.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `math.h`: Math related functions.
- `stdlib.h`:  For standard memory allocation functions
- `bbox.h`: Defines function prototypes related to bounding box operations
- `potracelib.h`: Core Potrace library definitions.
- `lists.h`: Definition for list data structure.

### Auxiliary Functions
#### `interval`
```c
static void interval(interval_t *i, double min, double max);
```
Initializes an interval with a min and max value.
- `i`: `interval_t *`, Pointer to interval to initialize.
- `min`: `double`, minimum value for the interval.
- `max`: `double`, maximum value for the interval.

#### `singleton`
```c
static inline void singleton(interval_t *i, double x);
```
Initializes the interval using a single value as both, min and max.
- `i`: `interval_t *`, Pointer to the interval to initialize.
- `x`: `double`, Value to create the interval with.

#### `extend`
```c
static inline void extend(interval_t *i, double x);
```
Extends the given interval to include a given value `x`.
- `i`: `interval_t *`, The interval to be extended.
- `x`: `double`, Value to be included in interval.

#### `in_interval`
```c
static inline int in_interval(interval_t *i, double x);
```
Checks if a value is within an interval.
- `i`: `interval_t *`, The interval to check against.
- `x`: `double`, The value to check.
**Returns:**
`int`, `1` if value x in the interval i, and 0 if not.

#### `iprod`
```c
static double iprod(dpoint_t a, dpoint_t b);
```
Computes the inner product between two vectors a and b.
- `a`: `dpoint_t`, Vector a.
- `b`: `dpoint_t`, Vector b.
**Returns:**
`double`, The result of the inner product.

#### `bezier`
```c
static inline double bezier(double t, double x0, double x1, double x2, double x3);
```
Calculates a point in bezier curve.
- `t`: `double`, Parameter used for interpolation on curve.
- `x0`: `double`, Control point 1.
- `x1`: `double`, Control point 2.
- `x2`: `double`, Control point 3.
- `x3`: `double`, Control point 4.
**Returns:**
`double`, Coordinate of the interpolated point on the bezier curve.

#### `bezier_limits`
```c
static void bezier_limits(double x0, double x1, double x2, double x3, interval_t *i);
```
Extends an interval to include the min and max of a given bezier segment with control points x0, x1, x2 and x3.
- `x0`: `double`, The first point.
- `x1`: `double`, The first control point
- `x2`: `double`, The second control point.
- `x3`: `double`, The end point.
- `i`: `interval_t *`, The interval to extend.

#### `segment_limits`
```c
static inline void segment_limits(int tag, dpoint_t a, dpoint_t c[3], dpoint_t dir, interval_t *i);
```
Extends the interval using segment limits, according to its tag type, either POTRACE_CORNER or POTRACE_CURVETO.
- `tag`: `int`, Type of segment
- `a`: `dpoint_t`, start position, used for Bezier segments
- `c`: `dpoint_t[3]`, Control points for the current segment
- `dir`: `dpoint_t`, direction vector
- `i`: `interval_t *`, interval to extend

#### `curve_limits`
```c
static void curve_limits(potrace_curve_t *curve, dpoint_t dir, interval_t *i);
```
Extends an interval using the limits of all the segments of a curve.
- `curve`: `potrace_curve_t *`, The curve object
- `dir`: `dpoint_t`, Direction vector
- `i`: `interval_t *`, The interval to extend

### Top-level Function
#### `path_limits`
```c
void path_limits(potrace_path_t *path, dpoint_t dir, interval_t *i);
```
Finds the extreme values of a given path, with respect to an associated direction.
- `path`: `potrace_path_t *`, Path list that represents the vector data
- `dir`: `dpoint_t`, Direction vector
- `i`: `interval_t *`, Output, the interval representing the min and max extents along the direction `dir`.


## File: bitmap.h
```
This header file defines data structures, and operations for bit-maps, mainly by using access macros, and helper function for allocation and deallocation.
```
### Includes
- `stdio.h`: For standard input/output functions.
- `bitmap.h`: For definitions of functions that handle bitmap operations
- `stdlib.h`: For standard memory allocation functions.
- `errno.h`: For error number definitions.
- `stddef.h`: For definitions like `ptrdiff_t`.
- `potracelib.h`: For definition of potrace_word and other core structures.

### Macros
#### Bitmap Dimension Macros
- `BM_WORDSIZE`: The size in bytes for potrace_word
- `BM_WORDBITS`: The size in bits for potrace_word
- `BM_HIBIT`: A bitmask with only the highest bit set in a potrace_word
- `BM_ALLBITS`: A bitmask where all bits are set.

#### Access Macros
- `bm_scanline(bm, y)`: Gets pointer to start of the y-th scanline of a given bitmap.
- `bm_index(bm, x, y)`: Gets pointer to the word containing the pixel (x,y).
- `bm_mask(x)`: Gets the bit mask needed to access bit at column x.
- `bm_range(x, a)`: Checks if a given index x is within the given boundary a.
- `bm_safe(bm, x, y)`: Checks if coordinates (x, y) are inside the bounds of the given bitmap.
- `BM_UGET(bm, x, y)`: Gets the value of the specified bit of a bitmap, without bounds checking, Returns 1 if set, otherwise 0.
- `BM_USET(bm, x, y)`: Sets the specified bit of a bitmap, without bounds checking.
- `BM_UCLR(bm, x, y)`: Clears the specified bit of a bitmap, without bounds checking.
- `BM_UINV(bm, x, y)`: Inverts the specified bit of a bitmap, without bounds checking.
- `BM_UPUT(bm, x, y, b)`: Sets the value of a bit to the specified value, without bounds checking. `b` should be 0 or 1.
- `BM_GET(bm, x, y)`: Gets the value of the specified bit of a bitmap, with bounds checking. Returns 1 if set, otherwise 0.
- `BM_SET(bm, x, y)`: Sets the specified bit of a bitmap, with bounds checking.
- `BM_CLR(bm, x, y)`: Clears the specified bit of a bitmap, with bounds checking.
- `BM_INV(bm, x, y)`: Inverts the specified bit of a bitmap, with bounds checking.
- `BM_PUT(bm, x, y, b)`: Sets the value of a bit to the specified value with bounds checking. `b` should be 0 or 1.

### Functions
#### `getsize`
```c
static inline ptrdiff_t getsize(int dy, int h);
```
Calculates the memory size in bytes needed for the data of a given bitmap.
- `dy`: `int`, Width of bitmap in words.
- `h`: `int`, Height of bitmap in pixels.
**Returns**:
`ptrdiff_t`, Returns size in bytes of bitmap memory, or -1 if size is too large and overflows `ptrdiff_t`

#### `bm_size`
```c
static inline ptrdiff_t bm_size(const potrace_bitmap_t *bm);
```
Gets the memory size required for a bitmap.
- `bm`: `const potrace_bitmap_t *`, The bitmap to get the size of
**Returns:**
`ptrdiff_t`, Returns size in bytes of bitmap memory, or -1 if size is too large and overflows `ptrdiff_t`

#### `bm_base`
```c
static inline potrace_word *bm_base(const potrace_bitmap_t *bm);
```
Gets the base pointer to the bitmap data.
- `bm`: `const potrace_bitmap_t *`, The bitmap to get base address from.
**Returns:**
`potrace_word *`, The base address of the bitmap data, considering the direction of scanlines

#### `bm_free`
```c
static inline void bm_free(potrace_bitmap_t *bm);
```
Frees the memory occupied by a bitmap.
- `bm`: `potrace_bitmap_t *`, The bitmap object to be freed.

#### `bm_new`
```c
static inline potrace_bitmap_t *bm_new(int w, int h);
```
Return new uninitialized bitmap.
- `w`: `int`, width of bitmap
- `h`: `int`, height of bitmap
**Returns**:
`potrace_bitmap_t *`, returns pointer to allocated bitmap, NULL with errno on error.

#### `bm_clear`
```c
static inline void bm_clear(potrace_bitmap_t *bm, int c);
```
Clear the given bitmap. Set all bits to c
- `bm`: `potrace_bitmap_t *`, The bitmap to be cleared.
- `c`: `int`, Bit value to set.

#### `bm_dup`
```c
static inline potrace_bitmap_t *bm_dup(const potrace_bitmap_t *bm);
```
Duplicate the given bitmap.
- `bm`: `const potrace_bitmap_t *`, Bitmap to be duplicated
**Returns**:
`potrace_bitmap_t *`, return the duplicated bitmap object, or NULL on error with errno set

#### `bm_invert`
```c
static inline void bm_invert(potrace_bitmap_t *bm);
```
Invert the given bitmap.
- `bm`: `potrace_bitmap_t *`, The bitmap to be inverted

#### `bm_flip`
```c
static inline void bm_flip(potrace_bitmap_t *bm);
```
Turn the given bitmap upside down
- `bm`: `potrace_bitmap_t *`, The bitmap to be flipped

#### `bm_resize`
```c
static inline int bm_resize(potrace_bitmap_t *bm, int h);
```
Resize the bitmap to the given new height
- `bm`: `potrace_bitmap_t *`, bitmap to be resized
- `h`: `int`, new height of the bitmap
**Returns**:
`int`, 0 on success, 1 on failure with errno set


## File: bitmap_io.h
```
This header file declares functions for reading and writing bitmaps, including functions for reading pbm files, and the necessary types
```
### Includes
- `stdio.h`: For standard input/output functions.
- `bitmap.h`: For the bitmap data structure

### Global Variables
#### `bm_read_error`
```c
extern const char *bm_read_error;
```
An external variable used for reporting errors during bitmap reading.

### Functions
#### `bm_read`
```c
int bm_read(FILE *f, double blacklevel, potrace_bitmap_t **bmp);
```
Reads a bitmap from a file, supporting PNM (PBM, PGM, PPM) and BMP formats.
- `f`: `FILE *`, The file to read from.
- `blacklevel`: `double`, Value from 0-1 used to convert to black or white for pixel data in greymap input.
- `bmp`: `potrace_bitmap_t **`, A pointer to the pointer where the allocated bitmap will be stored.
**Returns:**
`int`, 0 on success, -1 on system error, -2 on a corrupt file, -3 on empty files, -4 if wrong magic number, or 1 on a premature end of the file.

#### `bm_writepbm`
```c
void bm_writepbm(FILE *f, potrace_bitmap_t *bm);
```
Writes a bitmap to a file in the portable bitmap format.
- `f`: `FILE *`, The file to write to.
- `bm`: `potrace_bitmap_t *`, The bitmap to be written.

#### `bm_print`
```c
int bm_print(FILE *f, potrace_bitmap_t *bm);
```
Prints a bitmap to the console for debuging purposes.
- `f`: `FILE *`, The file to output to.
- `bm`: `potrace_bitmap_t *`, The bitmap to print.
**Returns:**
`int`, Returns 0 upon completion.


## File: bitmap_io.c
```
This file implements functions for reading and writing bitmaps, including functions for reading pbm files, and the necessary types
```
### Includes
- `stdio.h`: For standard input/output functions.
- `errno.h`: For error number definitions.
- `potracelib.h`: Core Potrace library definitions.
- `bitmap.h`: For the bitmap data structure.
- `bitops.h`: For bit manipulation functions.
```c
#ifdef HAVE_INTTYPES_H
#include <inttypes.h>
#endif
```

### Global Variables
#### `bm_read_error`
```c
extern const char *bm_read_error;
```
An external variable used for reporting errors during bitmap reading.

### Functions
#### `bm_read`
```c
int bm_read(FILE *f, double blacklevel, potrace_bitmap_t **bmp);
```
Reads a bitmap from a file, supporting PNM (PBM, PGM, PPM) and BMP formats.
- `f`: `FILE *`, The file to read from.
- `blacklevel`: `double`, Value from 0-1 used to convert to black or white for pixel data in greymap input.
- `bmp`: `potrace_bitmap_t **`, A pointer to the pointer where the allocated bitmap will be stored.
**Returns:**
`int`, 0 on success, -1 on system error, -2 on a corrupt file, -3 on empty files, -4 if wrong magic number, or 1 on a premature end of the file.

#### `bm_writepbm`
```c
void bm_writepbm(FILE *f, potrace_bitmap_t *bm);
```
Writes a bitmap to a file in the portable bitmap format.
- `f`: `FILE *`, The file to write to.
- `bm`: `potrace_bitmap_t *`, The bitmap to be written.

#### `bm_print`
```c
int bm_print(FILE *f, potrace_bitmap_t *bm);
```
Prints a bitmap to the console for debuging purposes.
- `f`: `FILE *`, The file to output to.
- `bm`: `potrace_bitmap_t *`, The bitmap to print.
**Returns:**
`int`, Returns 0 upon completion.

### Helper Functions
#### `fgetc_ws`
```c
static int fgetc_ws(FILE *f);
```
Reads next character from the file after skipping whitespace and comments.
- `f`: `FILE *`, Input file.
**Returns**:
`int`, The read character, or EOF on end of file or error.

#### `readnum`
```c
static int readnum(FILE *f);
```
Reads a non-negative integer from the file, skipping whitespace.
- `f`: `FILE *`, Input file.
**Returns:**
`int`, The read integer, or -1 on EOF or parse error.

#### `readbit`
```c
static int readbit(FILE *f);
```
Reads a single bit (0 or 1) from the file skipping comments and whitespace.
- `f`: `FILE *`, Input file.
**Returns:**
`int`, Returns `0` or `1` for the value read from file or -1 if end of file is reached.

### Auxiliary Bitmap Reading Functions
#### `bm_readbody_pnm`
```c
static int bm_readbody_pnm(FILE *f, double threshold, potrace_bitmap_t **bmp, int magic);
```
Reads the body of a PNM file (PBM, PGM, or PPM) after the magic number.
- `f`: `FILE *`, input file.
- `threshold`: `double`, threshold value for grey to black/white conversion
- `bmp`: `potrace_bitmap_t **`, Pointer to a pointer where the created bitmap will be stored.
- `magic`: `int`, Magic number (format of PNM file (P1-P6)).
**Returns:**
`int`, 0 on success, -1 on error with errno set, -2 on bad file format, and 1 on premature end of file.

#### `bm_readbody_bmp`
```c
static int bm_readbody_bmp(FILE *f, double threshold, potrace_bitmap_t **bmp);
```
Reads the body of a BMP file after the magic number.
- `f`: `FILE *`, Input file.
- `threshold`: `double`, cutoff value to convert greyscale to black/white values
- `bmp`: `potrace_bitmap_t **`, Pointer to where the new bitmap is to be stored.
**Returns:**
`int`, 0 on success, -1 on error with errno set, -2 on bad file format, and 1 on premature end of file.

### Helper Functions for BMP Reading

#### `bmp_readint`
```c
static int bmp_readint(FILE *f, int n, unsigned int *p);
```
Read `n`-byte little-endian integer
- `f`: `FILE *`, Input file
- `n`: `int`, number of bytes
- `p`: `unsigned int *`, pointer to store read integer.
**Returns**:
`int`, 1 on EOF or error, otherwise 0.

#### `bmp_pad_reset`
```c
static void bmp_pad_reset(void);
```
Resets padding byte counter for reading bitmaps.
- None

#### `bmp_pad`
```c
static int bmp_pad(FILE *f);
```
Read padding bytes up to a 4 byte boundary.
- `f`: `FILE *`, Input file
**Returns**:
`int`, returns 1 on EOF or error, otherwise 0

#### `bmp_forward`
```c
static int bmp_forward(FILE *f, int pos);
```
Reads bytes from the file until the file position is at the position specified by `pos`
- `f`: `FILE *`, input file stream.
- `pos`: `int`, target file position
**Returns:**
`int`, 1 on EOF or error, otherwise 0

### Local Variables
#### `col1`
```c
static int col1[2];
```
An array that will be used to store color information in old style OS/2 bitmaps where color table is present.


## File: curve.h
```
This header file defines the data structures used for representing curves in Potrace, including private structures for storing additional data during path processing.
```
### Includes
- `auxiliary.h`: Header defining auxiliary types and macros

### Structures
#### `privcurve_s`
```c
struct privcurve_s {
  int n;            /* number of segments */
  int *tag;         /* tag[n]: POTRACE_CORNER or POTRACE_CURVETO */
  dpoint_t (*c)[3]; /* c[n][i]: control points.
		       c[n][0] is unused for tag[n]=POTRACE_CORNER */
  /* the remainder of this structure is special to privcurve, and is
     used in EPS debug output and special EPS "short coding". These
     fields are valid only if "alphacurve" is set. */
  int alphacurve;   /* have the following fields been initialized? */
  dpoint_t *vertex; /* for POTRACE_CORNER, this equals c[1] */
  double *alpha;    /* only for POTRACE_CURVETO */
  double *alpha0;   /* "uncropped" alpha parameter - for debug output only */
  double *beta;
};
```
Represents a private curve structure, holding segment tags, control points, and additional data specific to curve processing for the trace function.
- `n`: `int`, Number of segments in the curve.
- `tag`: `int *`, Tag for each segment, either `POTRACE_CORNER` or `POTRACE_CURVETO`.
- `c`: `dpoint_t (*)[3]`, Array of control points for each curve.
- `alphacurve`: `int`, Flag indicating if the following fields have been initialized or not.
- `vertex`: `dpoint_t *`, Vertices of curve.
- `alpha`: `double *`, The alpha parameter for curve segments.
- `alpha0`: `double *`, The original "uncropped" alpha parameter for debug output only.
- `beta`: `double *`, The beta parameter of curve.

#### `sums_s`
```c
struct sums_s {
  double x;
  double y;
  double x2;
  double xy;
  double y2;
};
```
Stores pre-calculated sums of x, y and x^2, xy, y^2 for a sequence of points.
- `x`: `double`, Sum of x coordinates
- `y`: `double`, Sum of y coordinates
- `x2`: `double`, Sum of x coordinates squared
- `xy`: `double`, Sum of products of x and y
- `y2`: `double`, Sum of y coordinates squared.

#### `potrace_privpath_s`
```c
struct potrace_privpath_s {
  int len;
  point_t *pt;     /* pt[len]: path as extracted from bitmap */
  int *lon;        /* lon[len]: (i,lon[i]) = longest straight line from i */

  int x0, y0;      /* origin for sums */
  sums_t *sums;    /* sums[len+1]: cache for fast summing */

  int m;           /* length of optimal polygon */
  int *po;         /* po[m]: optimal polygon */

  privcurve_t curve;   /* curve[m]: array of curve elements */
  privcurve_t ocurve;  /* ocurve[om]: array of curve elements */
  privcurve_t *fcurve;  /* final curve: this points to either curve or
		       ocurve. Do not free this separately. */
};
```
Structure to hold internal data during tracing calculations.
- `len`: `int`, Number of points in the path.
- `pt`: `point_t *`, Array of points extracted directly from the bitmap.
- `lon`: `int *`, Array representing the longest straight subpaths in the list of points.
- `x0`, `y0`: `int`, Origin for sums calculations.
- `sums`: `sums_t *`, Array of precalculated sum for each point in the path.
- `m`: `int`, Number of vertices in the optimal polygon.
- `po`: `int *`, Array storing the indices of points that forms the optimal polygon vertices
- `curve`: `privcurve_t`, The curve object generated by smoothing and analysis
- `ocurve`: `privcurve_t`, The optimized curve object.
- `fcurve`: `privcurve_t *`, A pointer to the curve (either `curve` or `ocurve`), this is the final version of curve to use, but this memory must not be freed.

### Type Definitions
#### `privpath_t`
```c
typedef potrace_privpath_t privpath_t;
```
Alias for the structure that represents internal representation of a path being traced.

#### `path_t`
```c
typedef potrace_path_t path_t;
```
Alias for the potrace public path structure.

### Functions
#### `path_new`
```c
path_t *path_new(void);
```
Creates a new `path_t` object by allocating memory.
**Returns:**
`path_t *`, The newly created path object, or NULL on error with errno set.

#### `path_free`
```c
void path_free(path_t *p);
```
Frees all the memory allocated to the given path object.
- `p`: `path_t *`, The path to free.

#### `pathlist_free`
```c
void pathlist_free(path_t *plist);
```
Frees all paths in a given linked list.
- `plist`: `path_t *`, The start of the linked list of paths.

#### `privcurve_init`
```c
int privcurve_init(privcurve_t *curve, int n);
```
Initializes a private curve object, setting internal members to a given size `n`.
- `curve`: `privcurve_t *`, The curve to be initialized
- `n`: `int`, The number of segments in the curve
**Returns:**
`int`, Returns 0 on success or 1 on error (with errno set).

#### `privcurve_to_curve`
```c
void privcurve_to_curve(privcurve_t *pc, potrace_curve_t *c);
```
Copies the data stored in a private curve to a public curve object.
- `pc`: `privcurve_t *`, Pointer to the private curve object
- `c`: `potrace_curve_t *`, Pointer to the public curve object.


## File: curve.c
```
This file implements functions for managing path and curve data structures within the Potrace library, including allocation, freeing, and initializing curve structures.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdio.h`: Standard input/output functions.
- `stdlib.h`: Standard memory allocation functions.
- `string.h`: Standard string functions.
- `potracelib.h`: Core Potrace library definitions.
- `lists.h`: Definitions for list data structure.
- `curve.h`: Definitions for private curve and path structures.

### Macros
#### `SAFE_CALLOC`
```c
#define SAFE_CALLOC(var, n, typ) \
  if ((var = (typ *)calloc(n, sizeof(typ))) == NULL) goto calloc_error
```
Safely allocates memory using calloc and jumps to calloc_error label if allocation fails.

### Auxiliary Functions
#### `privcurve_free_members`
```c
static void privcurve_free_members(privcurve_t *curve);
```
Frees the members of the given private curve structure. This function does not free `curve` itself.
- `curve`: `privcurve_t *`, The curve to free.

### Path Object Functions
#### `path_new`
```c
path_t *path_new(void);
```
Allocates and initializes a new `path_t` object with associated private data.
**Returns:**
`path_t *`, a new path, or NULL on error (with errno set)

#### `path_free`
```c
void path_free(path_t *p);
```
Frees a path object, including its private data and components.
- `p`: `path_t *`, The path object to free.

#### `pathlist_free`
```c
void pathlist_free(path_t *plist);
```
Frees all the path objects in the given list.
- `plist`: `path_t *`, The linked list of paths.

### Curve Object Functions
#### `privcurve_init`
```c
int privcurve_init(privcurve_t *curve, int n);
```
Initializes the members of a given private curve structure to size `n`.
- `curve`: `privcurve_t *`, The curve to initialize.
- `n`: `int`, Number of curve segments.
**Returns:**
`int` returns 0 on success or 1 on failure with errno set.

#### `privcurve_to_curve`
```c
void privcurve_to_curve(privcurve_t *pc, potrace_curve_t *c);
```
Copies data from private curve structure to a public curve structure.
- `pc`: `privcurve_t *`, The private curve source structure.
- `c`: `potrace_curve_t *`, The public curve destination structure.


## File: decompose.h
```
This header file declares the `bm_to_pathlist` function, which decomposes a bitmap image into a list of paths based on tracing parameters, for use in the potrace algorithm.
```
### Includes
- `potracelib.h`: Core Potrace library definitions.
- `progress.h`: Definition for progress reporting structures.
- `curve.h`: Definition for path and curve structures.

### Functions
#### `bm_to_pathlist`
```c
int bm_to_pathlist(const potrace_bitmap_t *bm, path_t **plistp, const potrace_param_t *param, progress_t *progress);
```
Decomposes a bitmap into a list of paths based on given parameters.
- `bm`: `const potrace_bitmap_t *`, The bitmap to be decomposed.
- `plistp`: `path_t **`, Pointer to a pointer that stores the linked list of paths.
- `param`: `const potrace_param_t *`, The parameters for the path decomposition algorithm.
- `progress`: `progress_t *`, Pointer to progress bar object.

**Returns:**
`int` Returns 0 on success, or a nonzero value (usually 1) on failure with errno set


## File: decompose.c
```
This file implements functions that decompose a bitmap into a list of paths, calculating winding and applying filters to minimize unwanted paths.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdio.h`: For standard input/output functions.
- `stdlib.h`: For standard memory allocation functions.
- `string.h`: For string functions.
- `limits.h`: Integer limits.
- `inttypes.h` (conditional): For portable integer types.
- `potracelib.h`: Core Potrace library definitions.
- `curve.h`: Definitions for curve structures.
- `lists.h`: Definitions for list data structure.
- `bitmap.h`: For functions related to bitmap handling.
- `decompose.h`: Declaration of function prototypes for the bitmap decomposition.
- `progress.h`: For progress reporting structures.

### Auxiliary Functions
#### `detrand`
```c
static inline int detrand(int x, int y);
```
Generates a deterministic pseudo-random bit based on coordinates x,y.
- `x`: `int`, x-coordinate
- `y`: `int`, y-coordinate
**Returns:**
`int`, A pseudo random bit value (either 0 or 1).

### Bitmap Manipulation Functions
#### `bm_clearexcess`
```c
static void bm_clearexcess(potrace_bitmap_t *bm);
```
Clears any unused bits at the end of each scanline.
- `bm`: `potrace_bitmap_t *`, The bitmap to be processed

#### `bbox_s`
```c
struct bbox_s {
  int x0, x1, y0, y1;    /* bounding box */
};
```
Structure representing the bounding box of the image, using integers for x0, x1, y0 and y1.

#### `clear_bm_with_bbox`
```c
static void clear_bm_with_bbox(potrace_bitmap_t *bm, bbox_t *bbox);
```
Clears an area within a bitmap, using the provided bounding box.
- `bm`: `potrace_bitmap_t *`, The bitmap to process.
- `bbox`: `bbox_t *`, The bounding box of the area to be cleared.

### Auxiliary Functions
#### `majority`
```c
static int majority(potrace_bitmap_t *bm, int x, int y);
```
Calculates majority pixel value at given coordinates within the given bitmap.
- `bm`: `potrace_bitmap_t *`, Bitmap where to perform majority pixel check.
- `x`: `int`, x-coordinate of the pixel to test around.
- `y`: `int`, y-coordinate of the pixel to test around.
**Returns:**
`int`, 1 if majority of the pixels are set, 0 if majority of pixels are unset.

### Path Decomposition Functions
#### `xor_to_ref`
```c
static void xor_to_ref(potrace_bitmap_t *bm, int x, int y, int xa);
```
Inverts bits in bitmap between given x and xa coordinates, with efficient bulk bit flips on 32-bit integer values.
- `bm`: `potrace_bitmap_t *`, The bitmap where bits should be flipped
- `x`: `int`, The starting x coordinate
- `y`: `int`, The y coordinate
- `xa`: `int`, The target x coordinate.

#### `xor_path`
```c
static void xor_path(potrace_bitmap_t *bm, path_t *p);
```
XORs the bitmap with the area enclosed by the given path.
- `bm`: `potrace_bitmap_t *`, The bitmap to be modified.
- `p`: `path_t *`, The path to be drawn.

#### `setbbox_path`
```c
static void setbbox_path(bbox_t *bbox, path_t *p);
```
Computes the bounding box of a given path.
- `bbox`: `bbox_t *`, The bounding box to be updated.
- `p`: `path_t *`, The path to determine bounding box for.

#### `findpath`
```c
static path_t *findpath(potrace_bitmap_t *bm, int x0, int y0, int sign, int turnpolicy);
```
Traces a path using a given bitmap, starting from a given position with a given initial direction.
- `bm`: `potrace_bitmap_t *`, The bitmap to trace
- `x0`: `int`, Initial x position
- `y0`: `int`, Initial y position
- `sign`: `int`, initial sign of path
- `turnpolicy`: `int`, policy for determining direction when tracing a path
**Returns:**
`path_t *`, Pointer to newly created path object, or NULL on error

#### `pathlist_to_tree`
```c
static void pathlist_to_tree(path_t *plist, potrace_bitmap_t *bm);
```
Transforms the given path list into a tree structure using insideness tests.
- `plist`: `path_t *`, The start of the linked list of paths.
- `bm`: `potrace_bitmap_t *`, The temporary bitmap data

#### `findnext`
```c
static int findnext(potrace_bitmap_t *bm, int *xp, int *yp);
```
Find the next set pixel in a bitmap (with y<=yp), starting from coordinate (xp, yp). Returns zero if one is found, and stores the coordinates in xp and yp.
- `bm`: `potrace_bitmap_t *`, The bitmap to be checked.
- `xp`: `int *`, A pointer to the x position where a set pixel was found, or the next x position from where to continue searching.
- `yp`: `int *`,  A pointer to the y position where a set pixel was found, or next y position to continue searching.
**Returns:**
`int`, Returns 0 when the next set pixel is found, 1 if no more set pixels were found.

### Top Level Functions
#### `bm_to_pathlist`
```c
int bm_to_pathlist(const potrace_bitmap_t *bm, path_t **plistp, const potrace_param_t *param, progress_t *progress);
```
Main function to generate a pathlist from a bitmap, applying filters and checks based on parameters.
- `bm`: `const potrace_bitmap_t *`, Bitmap to trace
- `plistp`: `path_t **`, Pointer to list of paths.
- `param`: `const potrace_param_t *`, Parameter for the tracing.
- `progress`: `progress_t *`, Progress reporting object.
**Returns:**
`int`, returns 0 on success, -1 on error with errno set.


## File: trace.h
```
This header file declares the `process_path` function which is used to transform extracted paths into smooth curves.
```
### Includes
- `potracelib.h`: Core Potrace library definitions.
- `progress.h`: Definition for progress tracking.
- `curve.h`: Declaration of data structures and related functions

### Functions
#### `process_path`
```c
int process_path(path_t *plist, const potrace_param_t *param, progress_t *progress);
```
Processes the path, calling the relevant functions to calculate sums, longest subpaths, best polygon, correct vertices, smooth curves, and optimize curves as specified in the parameters.
- `plist`: `path_t *`, The linked list of paths.
- `param`: `const potrace_param_t *`, The parameters for the path processing.
- `progress`: `progress_t *`, Progress bar struct to update,

**Returns**:
`int`, 0 on success, 1 on error with errno set.


## File: trace.c
```
This file implements functions to transform jaggy paths extracted from a bitmap into smooth curves, utilizing various optimization and curve-fitting algorithms.
```

### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdio.h`: For standard input/output.
- `math.h`: For mathematical functions.
- `stdlib.h`: For memory allocation functions.
- `string.h`: For string manipulation functions.
- `potracelib.h`: Core Potrace library definitions.
- `curve.h`:  Definitions for curve structures and operations.
- `lists.h`: Definitions for list data structure.
- `auxiliary.h`: Auxiliary type definitions.
- `trace.h`: Declaration of the functions implemented in this file.
- `progress.h`: Definition of the structure for progress tracking.

### Macros
#### `SAFE_CALLOC`
```c
#define SAFE_CALLOC(var, n, typ) \
  if ((var = (typ *)calloc(n, sizeof(typ))) == NULL) goto calloc_error
```
Safely allocates memory using calloc, jumping to the `calloc_error` label if allocation fails.

### Auxiliary Functions
#### `dorth_infty`
```c
static inline point_t dorth_infty(dpoint_t p0, dpoint_t p2);
```
Calculates a direction orthogonal to (p2 - p0), restricting it to one of the major wind directions.
- `p0`: `dpoint_t`, Starting point.
- `p2`: `dpoint_t`, Ending point.
**Returns**:
`point_t`, The orthogonal direction.

#### `dpara`
```c
static inline double dpara(dpoint_t p0, dpoint_t p1, dpoint_t p2);
```
Calculates the area of the parallelogram formed by vectors (p1 - p0) and (p2 - p0).
- `p0`: `dpoint_t`, The base point.
- `p1`: `dpoint_t`, One of the other points.
- `p2`: `dpoint_t`, One of the other points.
**Returns**:
`double`, The area of the parallelogram.

#### `ddenom`
```c
static inline double ddenom(dpoint_t p0, dpoint_t p2);
```
Calculates a value used with dpara for checking line segment intersections, related to the distance from a line.
- `p0`: `dpoint_t`, The base point.
- `p2`: `dpoint_t`, The other point for the line segment.
**Returns**:
`double`, The value.

#### `cyclic`
```c
static inline int cyclic(int a, int b, int c);
```
Checks if 'b' is between 'a' and 'c' in a cyclic sense.
- `a`: `int`, Lower bound (cyclic).
- `b`: `int`, Value to check.
- `c`: `int`, Upper bound (cyclic).
**Returns**:
`int`, 1 if `a <= b < c` cyclically, 0 otherwise.

#### `pointslope`
```c
static void pointslope(privpath_t *pp, int i, int j, dpoint_t *ctr, dpoint_t *dir);
```
Calculates the center point and slope of a line defined by the points in the `privpath_t` structure at indices `i` and `j`.
- `pp`: `privpath_t *`, Path data containing points and sums.
- `i`: `int`, The start index.
- `j`: `int`, The end index.
- `ctr`: `dpoint_t *`, Pointer to store the calculated center point.
- `dir`: `dpoint_t *`, Pointer to store the calculated direction.

#### `quadform`
```c
static inline double quadform(quadform_t Q, dpoint_t w);
```
Applies a quadratic form matrix Q to a vector w.
- `Q`: `quadform_t`, The quadratic form matrix (a 3x3 matrix represented as a double[3][3]).
- `w`: `dpoint_t`, The vector to which the quadratic form is applied.
**Returns**:
`double`, Result of the quadratic form applied to the vector.

#### `xprod`
```c
static inline int xprod(point_t p1, point_t p2);
```
Calculates the cross product of two `point_t` vectors.
- `p1`: `point_t`, The first vector
- `p2`: `point_t`, The second vector
**Returns:**
`int`, The resulting cross product.

#### `cprod`
```c
static inline double cprod(dpoint_t p0, dpoint_t p1, dpoint_t p2, dpoint_t p3);
```
Calculates the cross product of two vectors (p1 - p0) x (p3 - p2).
- `p0`: `dpoint_t`, Start of the first vector.
- `p1`: `dpoint_t`, End of the first vector.
- `p2`: `dpoint_t`, Start of the second vector.
- `p3`: `dpoint_t`, End of the second vector.
**Returns**:
`double`, Result of the cross product.

#### `iprod`
```c
static inline double iprod(dpoint_t p0, dpoint_t p1, dpoint_t p2);
```
Calculates the inner product (dot product) between vectors (p1 - p0) and (p2 - p0).
- `p0`: `dpoint_t`, The base point.
- `p1`: `dpoint_t`, The end point of the first vector.
- `p2`: `dpoint_t`, The end point of the second vector.
**Returns**:
`double`, The result of the inner product.

#### `iprod1`
```c
static inline double iprod1(dpoint_t p0, dpoint_t p1, dpoint_t p2, dpoint_t p3);
```
Calculates the inner product of vectors (p1 - p0) and (p3 - p2).
- `p0`: `dpoint_t`, Start of the first vector.
- `p1`: `dpoint_t`, End of the first vector.
- `p2`: `dpoint_t`, Start of the second vector.
- `p3`: `dpoint_t`, End of the second vector.
**Returns**:
`double`, Result of the inner product.

#### `ddist`
```c
static inline double ddist(dpoint_t p, dpoint_t q);
```
Calculates the Euclidean distance between points p and q.
- `p`: `dpoint_t`, The first point.
- `q`: `dpoint_t`, The second point.
**Returns**:
`double`, The distance between p and q.

#### `bezier`
```c
static inline dpoint_t bezier(double t, dpoint_t p0, dpoint_t p1, dpoint_t p2, dpoint_t p3);
```
Calculates a point on the Bezier curve defined by the four control points.
- `t`: `double`, The parametric value between 0 and 1.
- `p0`: `dpoint_t`, The start point.
- `p1`: `dpoint_t`, The first control point.
- `p2`: `dpoint_t`, The second control point.
- `p3`: `dpoint_t`, The end point.
**Returns**:
`dpoint_t`, Point on the Bezier curve.

#### `tangent`
```c
static double tangent(dpoint_t p0, dpoint_t p1, dpoint_t p2, dpoint_t p3, dpoint_t q0, dpoint_t q1);
```
Calculates tangent on a bezier curve by finding the point in [0,1] on the Bezier curve where it is tangent to the vector (q1-q0).
- `p0`: `dpoint_t`, The first bezier curve control point.
- `p1`: `dpoint_t`, The second bezier curve control point.
- `p2`: `dpoint_t`, The third bezier curve control point.
- `p3`: `dpoint_t`, The fourth bezier curve control point.
- `q0`: `dpoint_t`, Start of the direction vector.
- `q1`: `dpoint_t`, End of the direction vector.
**Returns**:
`double` - The parameter `t` value where the bezier curve is tangent to the given vector or -1.0 if no solution is found in [0,1]

### Stage 1 - Straight Subpaths Functions

#### `calc_sums`
```c
static int calc_sums(privpath_t *pp);
```
Pre-calculates sums of path point coordinates and related fields in a path for quick access.
- `pp`: `privpath_t *`, The path data.
**Returns**:
`int`, 0 on success, or 1 with errno set on failure.

#### `calc_lon`
```c
static int calc_lon(privpath_t *pp);
```
Calculates the longest straight subpaths of a given path, storing them in `lon` component.
- `pp`: `privpath_t *`, The path data.
**Returns**:
`int`, 0 on success, 1 on failure with errno set.

### Stage 2 - Optimal Polygon Functions

#### `penalty3`
```c
static double penalty3(privpath_t *pp, int i, int j);
```
Calculates the penalty of an edge in a path between point at index i and j. This function requires the 'lon' and 'sums' data.
- `pp`: `privpath_t *`, The path data.
- `i`: `int`, Starting point index.
- `j`: `int`, Ending point index.
**Returns**:
`double`, The calculated penalty.

#### `bestpolygon`
```c
static int bestpolygon(privpath_t *pp);
```
Determines the optimal polygon that approximates the given path.
- `pp`: `privpath_t *`, The path data to process.
**Returns**:
`int`, 0 on success or 1 with errno set on failure.

### Stage 3 - Vertex Adjustment Functions

#### `adjust_vertices`
```c
static int adjust_vertices(privpath_t *pp);
```
Adjusts the vertices of the optimal polygon to find intersections between line segments.
- `pp`: `privpath_t *`, The path data.
**Returns**:
`int`, 0 on success or 1 on error with errno set.

### Stage 4 - Smoothing and Corner Analysis Functions

#### `reverse`
```c
static void reverse(privcurve_t *curve);
```
Reverses the order of vertices in a private curve.
- `curve`: `privcurve_t *`, The curve structure.

#### `smooth`
```c
static void smooth(privcurve_t *curve, double alphamax);
```
Smooths a curve by calculating and adjusting control points, and identify corner points.
- `curve`: `privcurve_t *`, The curve to be smoothed.
- `alphamax`: `double`, Threshold value for corner detection.

### Stage 5 - Curve Optimization Functions
#### `opti_s`
```c
struct opti_s {
  double pen;	   /* penalty */
  dpoint_t c[2];   /* curve parameters */
  double t, s;	   /* curve parameters */
  double alpha;	   /* curve parameter */
};
```
Defines a struct for optimization results.
- `pen`: `double`, Penalty of this optimization.
- `c`: `dpoint_t[2]`, Control points for the optimized curve
- `t`, `s`: `double`, Bezier curve parameters for the curve
- `alpha`: `double`, overall alpha value for the optimized curve

#### `opti_penalty`
```c
static int opti_penalty(privpath_t *pp, int i, int j, opti_t *res, double opttolerance, int *convc, double *areac);
```
Calculates the best fit for an optimal curve, based on given parameters, by evaluating whether it can join two segments of a path with a minimal penalty.
- `pp`: `privpath_t *`, The path data.
- `i`: `int`, Start index for the section to optimize.
- `j`: `int`, End index for the section to optimize.
- `res`: `opti_t *`, Pointer to the struct where results will be stored.
- `opttolerance`: `double`, Tolerance value for curve optimization.
- `convc`: `int *`, Array indicating convexity (+1 for right turn, -1 left turn, 0 for corner)
- `areac`: `double *`, Cumulative area cache for fast area computation.
**Returns**:
`int`, 0 on success and sets parameters in `res`, 1 if optimization is impossible.

#### `opticurve`
```c
static int opticurve(privpath_t *pp, double opttolerance);
```
Optimizes the curve of a path to reduce the number of Bezier segments using a given tolerance.
- `pp`: `privpath_t *`, The path data.
- `opttolerance`: `double`, Tolerance value for curve optimization.
**Returns**:
`int`, 0 on success, 1 with errno set on failure.

### Top Level Functions

#### `process_path`
```c
int process_path(path_t *plist, const potrace_param_t *param, progress_t *progress);
```
Processes the path, calling the relevant functions to calculate sums, longest subpaths, best polygon, correct vertices, smooth curves, and optimize curves as specified in the parameters.
- `plist`: `path_t *`, The linked list of paths.
- `param`: `const potrace_param_t *`, The parameters for the path processing.
- `progress`: `progress_t *`, Progress bar struct to update,
**Returns**:
`int`, 0 on success, 1 on error with errno set.


## File: lists.h
```
This header file defines macros for handling singly-linked lists, providing functionalities for traversal, insertion, removal, and manipulation, with hooks and conditionals for complex list operations.
```
### Includes
- None

### Macros
#### `MACRO_BEGIN`
```c
#define MACRO_BEGIN do {
```
Marks the beginning of a multi-statement macro block.

#### `MACRO_END`
```c
#define MACRO_END   } while (0)
```
Marks the end of a multi-statement macro block.

### Singly-Linked List Macros
#### `list_forall`
```c
#define list_forall(elt, list)   for (elt=list; elt!=NULL; elt=elt->next)
```
Iterates through a singly linked list.
- `elt`: loop variable that gets current element during iteration
- `list`: start of list
#### `list_find`
```c
#define list_find(elt, list, c) \
  MACRO_BEGIN list_forall(elt, list) if (c) break; MACRO_END
```
Finds the first element in a list that matches a condition `c`.
- `elt`: loop variable to hold current element, is set to found element after completion of loop or NULL if no element was found.
- `list`: start of the list.
- `c`: condition that current element should comply to.
#### `list_forall2`
```c
#define list_forall2(elt, list, hook) \
  for (elt=list, hook=&list; elt!=NULL; hook=&elt->next, elt=elt->next)
```
Iterates through a linked list, maintaining a pointer to the previous element.
- `elt`: loop variable to hold current element.
- `list`: start of the list.
- `hook`: pointer to pointer to the element before current, used to be able to insert new elements.
#### `list_find2`
```c
#define list_find2(elt, list, c, hook) \
  MACRO_BEGIN list_forall2(elt, list, hook) if (c) break; MACRO_END
```
Finds the first element in a list that satisfies condition `c`, also storing pointer to pointer of previous element in `hook`.
- `elt`: loop variable to hold current element, is set to found element after completion of loop or NULL if no element was found.
- `list`: start of the list.
- `c`: condition that current element should comply to.
- `hook`: pointer to pointer to the element before current, used to be able to insert new elements.

#### `_list_forall_hook`
```c
#define _list_forall_hook(list, hook) \
  for (hook=&list; *hook!=NULL; hook=&(*hook)->next)
```
Iterates over the list, but only updates `hook`.
- `list`: start of the list.
- `hook`: pointer to pointer to the element before current.

#### `_list_find_hook`
```c
#define _list_find_hook(list, c, hook) \
  MACRO_BEGIN _list_forall_hook(list, hook) if (c) break; MACRO_END
```
Finds the first element with the hook, according to given condition `c`.
- `list`: start of the list.
- `c`: condition that current element should comply to.
- `hook`: pointer to pointer to the element before current.

#### `list_insert_athook`
```c
#define list_insert_athook(elt, hook) \
  MACRO_BEGIN elt->next = *hook; *hook = elt; MACRO_END
```
Inserts a new element into the list at the position given by the hook.
- `elt`: pointer to new element
- `hook`: pointer to the element before the location to insert.
#### `list_insert_beforehook`
```c
#define list_insert_beforehook(elt, hook) \
  MACRO_BEGIN elt->next = *hook; *hook = elt; hook=&elt->next; MACRO_END
```
Inserts a new element in a list, immediately before the position of the given hook.
- `elt`: pointer to new element
- `hook`: pointer to pointer to the element before insertion.
#### `list_unlink_athook`
```c
#define list_unlink_athook(list, elt, hook) \
  MACRO_BEGIN \
  elt = hook ? *hook : NULL; if (elt) { *hook = elt->next; elt->next = NULL; }\
  MACRO_END
```
Unlinks the element after the current hook in the given linked list. The unlinked element is stored in `elt`, and the given `hook` remains pointing to the element before that.
- `list`: start of the list.
- `elt`: pointer to hold the removed element or NULL.
- `hook`: pointer to the pointer of the element to be removed.

#### `list_unlink`
```c
#define list_unlink(listtype, list, elt)      \
  MACRO_BEGIN  	       	       	       	      \
  listtype **_hook;			      \
  _list_find_hook(list, *_hook==elt, _hook);  \
  list_unlink_athook(list, elt, _hook);	      \
  MACRO_END
```
Removes an element from the list if it is found, otherwise `elt` is set to NULL.
- `listtype`: Type of the list element.
- `list`: start of the list.
- `elt`: element to be removed
#### `list_prepend`
```c
#define list_prepend(list, elt) \
  MACRO_BEGIN elt->next = list; list = elt; MACRO_END
```
Prepends a given element to the beginning of a list.
- `list`: start of the list.
- `elt`: element to be added to the start of list

#### `list_append`
```c
#define list_append(listtype, list, elt)     \
  MACRO_BEGIN                                \
  listtype **_hook;                          \
  _list_forall_hook(list, _hook) {}          \
  list_insert_athook(elt, _hook);            \
  MACRO_END
```
Appends an element to the end of the list.
- `listtype`: Type of the list element.
- `list`: start of the list.
- `elt`: element to be added to the end of the list
#### `list_unlink_cond`
```c
#define list_unlink_cond(listtype, list, elt, c)     \
  MACRO_BEGIN                                        \
  listtype **_hook;			  	     \
  list_find2(elt, list, c, _hook);                   \
  list_unlink_athook(list, elt, _hook);              \
  MACRO_END
```
Removes the first element satisfying a given condition.
- `listtype`: Type of the list element
- `list`: start of the list
- `elt`: variable to store the removed element.
- `c`: condition of the element to remove.

#### `list_nth`
```c
#define list_nth(elt, list, n)                                \
  MACRO_BEGIN                                                 \
  int _x;  /* only evaluate n once */                         \
  for (_x=(n), elt=list; _x && elt; _x--, elt=elt->next) {}   \
  MACRO_END
```
Assigns the element at given position in the linked list to variable `elt`.
- `elt`: pointer to element. If element at index `n` is found in `list` then assigned to this variable, or NULL if not.
- `list`: pointer to list start
- `n`: the index of element in the linked list to find

#### `list_nth_hook`
```c
#define list_nth_hook(elt, list, n, hook)                     \
  MACRO_BEGIN                                                 \
  int _x;  /* only evaluate n once */                         \
  for (_x=(n), elt=list, hook=&list; _x && elt; _x--, hook=&elt->next, elt=elt->next) {}   \
  MACRO_END
```
Assigns the element at given position in the linked list and its corresponding hook to given variable.
- `elt`: pointer to element. If element at index `n` is found in `list` then assigned to this variable, or NULL if not.
- `list`: pointer to list start
- `n`: the index of element in the linked list to find
- `hook`: pointer to a pointer to element before current, or the list itself if the element found is at the head.
#### `list_length`
```c
#define list_length(listtype, list, n)                   \
  MACRO_BEGIN          	       	       	       	       	 \
  listtype *_elt;   			 		 \
  n=0;					 		 \
  list_forall(_elt, list) 		 		 \
    n++;				 		 \
  MACRO_END
```
Calculates the length of the linked list.
- `listtype`: Type of the list element.
- `list`: pointer to the list to calculate the size of.
- `n`: variable where the length will be stored.

#### `list_index`
```c
#define list_index(list, n, elt, c)                      \
  MACRO_BEGIN				 		 \
  n=0;					 		 \
  list_forall(elt, list) {		 		 \
    if (c) break;			 		 \
    n++;				 		 \
  }					 		 \
  if (!elt)				 		 \
    n=-1;				 		 \
  MACRO_END
```
Searches for an element in the list that satisfies a certain condition and returns its index and element in their respective variables.
- `list`: pointer to list
- `n`: output variable for element index, or -1 if element not found
- `elt`: element pointer that will store the found element or NULL if element not found.
- `c`: condition for the element to be found.

#### `list_count`
```c
#define list_count(list, n, elt, c)                      \
  MACRO_BEGIN				 		 \
  n=0;					 		 \
  list_forall(elt, list) {		 		 \
    if (c) n++;				 		 \
  }                                                      \
  MACRO_END
```
Counts the number of elements that satisfy a given condition.
- `list`: pointer to the list.
- `n`:  variable where the count will be stored
- `elt`: loop variable used to iterate through list
- `c`: condition for the element to be counted

#### `list_forall_unlink`
```c
#define list_forall_unlink(elt, list) \
  for (elt=list; elt ? (list=elt->next, elt->next=NULL), 1 : 0; elt=list)
```
Iterates through a list, unlinking each element.
- `elt`: loop variable that gets current element during iteration, is set to `NULL` after completing the loop
- `list`: start of list, is set to NULL after the loop.

#### `list_reverse`
```c
#define list_reverse(listtype, list)            \
  MACRO_BEGIN				 	\
  listtype *_list1=NULL, *elt;			\
  list_forall_unlink(elt, list) 		\
    list_prepend(_list1, elt);			\
  list = _list1;				\
  MACRO_END
```
Reverses a linked list
- `listtype`: the type of element in the list
- `list`: start of the list, when procedure is complete it points to reversed list.

#### `list_insert_ordered`
```c
#define list_insert_ordered(listtype, list, elt, tmp, cond) \
  MACRO_BEGIN                                               \
  listtype **_hook;                                         \
  _list_find_hook(list, (tmp=*_hook, (cond)), _hook);       \
  list_insert_athook(elt, _hook);                           \
  MACRO_END
```
Inserts a new element into an ordered linked list, based on provided condition.
- `listtype`: type of elements in the list.
- `list`: start of list
- `elt`: element to be inserted
- `tmp`: element from list that will be used to test the condidtion against the new element.
- `cond`: condition, to compare new element with elements from the list, if condition is false, the next list element will be tested and so on. The new element is inserted before the first element that makes this condition false.
#### `list_sort`
```c
#define list_sort(listtype, list, a, b, cond)            \
  MACRO_BEGIN                                            \
  listtype *_newlist=NULL;                               \
  list_forall_unlink(a, list)                            \
    list_insert_ordered(listtype, _newlist, a, b, cond); \
  list = _newlist;                                       \
  MACRO_END
```
Sorts the list using insertion sort, based on the given comparison condition.
- `listtype`: Type of elements in the list
- `list`: pointer to the start of list, updated by this call to represent sorted list.
- `a`: loop variable, that gets the current element
- `b`: element from list to compare `a` to using condition `cond`.
- `cond`: the comparison condition of elements `a` and `b`.
#### `list_mergesort`
```c
#define list_mergesort(listtype, list, a, b, cond)              \
  MACRO_BEGIN						        \
  listtype *_elt, **_hook1;				    	\
							    	\
  for (_elt=list; _elt; _elt=_elt->next1) {			\
    _elt->next1 = _elt->next;				    	\
    _elt->next = NULL;					    	\
  }							    	\
  do {			                               	    	\
    _hook1 = &(list);				    	    	\
    while ((a = *_hook1) != NULL && (b = a->next1) != NULL ) {  \
      _elt = b->next1;					    	\
      _list_merge_cond(listtype, a, b, cond, *_hook1);      	\
      _hook1 = &((*_hook1)->next1);			    	\
      *_hook1 = _elt;				            	\
    }							    	\
  } while (_hook1 != &(list));                                 	\
  MACRO_END
```
Sorts a list in place using merge sort, based on the given comparison condition.
- `listtype`: Type of list elements.
- `list`: Pointer to the start of list, which when the method is finished, points to the sorted list
- `a`: Loop variable
- `b`: second loop variable, will represent the second half of list when merging
- `cond`: comparison condition.
#### `_list_merge_cond`
```c
#define _list_merge_cond(listtype, a, b, cond, result)   \
  MACRO_BEGIN                                            \
  listtype **_hook;					 \
  _hook = &(result);					 \
  while (1) {                                            \
     if (a==NULL) {					 \
       *_hook = b;					 \
       break;						 \
     } else if (b==NULL) {				 \
       *_hook = a;					 \
       break;						 \
     } else if (cond) {					 \
       *_hook = a;					 \
       _hook = &(a->next);				 \
       a = a->next;					 \
     } else {						 \
       *_hook = b;					 \
       _hook = &(b->next);				 \
       b = b->next;					 \
     }							 \
  }							 \
  MACRO_END
```
Merges two sorted list based on the given comparison function `cond`.
- `listtype`: Type of list elements.
- `a`: pointer to the start of the first list.
- `b`: pointer to the start of the second list
- `cond`: comparison function.
- `result`: pointer to where merged list will be stored.

### Doubly-Linked List Macros
#### `dlist_append`
```c
#define dlist_append(head, end, elt)                    \
  MACRO_BEGIN  	       	       	       	       	       	 \
  elt->prev = end;					 \
  elt->next = NULL;					 \
  if (end) {						 \
    end->next = elt;					 \
  } else {  						 \
    head = elt;						 \
  }	    						 \
  end = elt;						 \
  MACRO_END
```
Appends an element to the end of a doubly linked list.
- `head`: pointer to head of list
- `end`: pointer to end of list
- `elt`: element to be appended

#### `dlist_forall_unlink`
```c
#define dlist_forall_unlink(elt, head, end) \
  for (elt=head; elt ? (head=elt->next, elt->next=NULL, elt->prev=NULL), 1 : (end=NULL, 0); elt=head)
```
Iterates over a doubly-linked list and unlinks all elements. The last item will also set `end` to null
- `elt`: loop variable for element during iteration.
- `head`: start of list
- `end`: end of list

#### `dlist_unlink_first`
```c
#define dlist_unlink_first(head, end, elt)               \
  MACRO_BEGIN				       	       	 \
  elt = head;						 \
  if (head) {						 \
    head = head->next;					 \
    if (head) {						 \
      head->prev = NULL;				 \
    } else {						 \
      end = NULL;					 \
    }    						 \
    elt->prev = NULL;					 \
    elt->next = NULL;					 \
  }							 \
  MACRO_END
```
Unlinks the first element from doubly linked list.
- `head`: pointer to list head, becomes next element after the first is removed
- `end`: pointer to the last element of the list, may be set to NULL
- `elt`: variable to hold the removed item.


## File: progress.h
```
This header file defines functions and structures for managing progress reporting in Potrace. It provides a way to track the completion of tasks and report progress using callbacks, aiming for minimal performance overhead when no progress monitoring is required.
```
### Includes
- (None)

### Structures
#### `progress_s`
```c
struct progress_s {
  void (*callback)(double progress, void *privdata); /* callback fn */
  void *data;          /* callback function's private data */
  double min, max;     /* desired range of progress, e.g. 0.0 to 1.0 */
  double epsilon;      /* granularity: can skip smaller increments */
  double b;            /* upper limit of subrange in superrange units */
  double d_prev;       /* previous value of d */
};
```
Represents the state for progress bar operations and a container for callback data.
- `callback`: `void (*)(double progress, void *privdata)`, Callback function for updating progress.
- `data`: `void *`, Private data for the callback function.
- `min`: `double`, Minimum progress value (e.g. 0.0).
- `max`: `double`, Maximum progress value (e.g. 1.0).
- `epsilon`: `double`, Minimum change needed before progress update callback.
- `b`: `double`, The upper limit of the subrange, relative to super range units.
- `d_prev`: `double`, The previous `d` value to prevent excessive updates.

### Functions
#### `progress_update`
```c
static inline void progress_update(double d, progress_t *prog);
```
Updates the progress and calls the callback function when appropriate. Note, `d` should be within the 0.0 to 1.0 range.
- `d`: `double`, The current progress value from 0.0 to 1.0.
- `prog`: `progress_t *`, The progress tracker object

#### `progress_subrange_start`
```c
static inline void progress_subrange_start(double a, double b, const progress_t *prog, progress_t *sub);
```
Initializes a sub-range progress tracker, derived from a parent progress tracker.
- `a`: `double`, The start of the subrange within the parent range (0.0 - 1.0).
- `b`: `double`, The end of the subrange within the parent range (0.0 - 1.0).
- `prog`: `const progress_t *`, The parent progress tracker object.
- `sub`: `progress_t *`, The subrange progress tracker object.

#### `progress_subrange_end`
```c
static inline void progress_subrange_end(progress_t *prog, progress_t *sub);
```
Signals the end of the sub-range, updating the parent range if needed.
- `prog`: `progress_t *`, The parent progress tracker object.
- `sub`: `progress_t *`, The subrange progress tracker object.


## File: progress_bar.h
```
This header file defines the interface and structures for rendering progress bars in the Potrace application.
```
### Includes
- `potracelib.h`: Core Potrace library definitions.

### Structures
#### `progress_bar_s`
```c
struct progress_bar_s {
  int (*init)(potrace_progress_t *prog, const char *filename, int count);
  void (*term)(potrace_progress_t *prog);
};
```
Defines the structure for representing a progress bar interface.
- `init`: `int (*)(potrace_progress_t *prog, const char *filename, int count)`, Function to initialize the progress bar.
    -`prog`: `potrace_progress_t *`, The progress bar object.
    -`filename`: `const char *`, The name of the input file that is to be processed.
    -`count`: `int`, A number representing what is the index of file being processed when processing more than one file
    **Returns**: `int`, return `0` on success, `1` on error with errno set.
- `term`: `void (*)(potrace_progress_t *prog)`, Function to terminate/clean-up the progress bar.

### Global Variables
#### `progress_bar_vt100`
```c
extern progress_bar_t *progress_bar_vt100;
```
A pointer to the standard vt100 terminal implementation of the progress bar.

#### `progress_bar_simplified`
```c
extern progress_bar_t *progress_bar_simplified;
```
A pointer to the simplified implementation of the progress bar for dumb terminals.


## File: progress_bar.c
```
This file implements two progress bar rendering functions, one for vt100-compatible terminals and a simplified one for dumb terminals. It also implements the corresponding helper functions to use when setting up the interfaces.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdio.h`: For standard input/output functions.
- `math.h`: For mathematical functions.
- `stdlib.h`: For memory allocation functions.
- `string.h`: For string functions.
- `potracelib.h`: For type definitions of progress struct
- `progress_bar.h`: Header file for function declarations of the progress bar

### Constants
#### `COL0`
```c
#define COL0 "\033[G"  /* reset cursor to column 0 */
```
Defines the ANSI escape sequence to move the cursor to column 0.

### Structures
#### `vt100_progress_s`
```c
struct vt100_progress_s {
  char name[22];          /* filename for status bar */
  double dnext;           /* threshold value for next tick */
};
```
Structure to hold the state for the vt100-style progress bar.
- `name`: `char[22]`, The filename associated with progress.
- `dnext`: `double`, Threshold for next tick on progress bar.

#### `simplified_progress_s`
```c
struct simplified_progress_s {
  int n;                  /* number of ticks displayed so far */
  double dnext;           /* threshold value for next tick */
};
```
Structure to hold the state for the simplified progress bar for dumb terminals
- `n`: `int`, The current number of ticks drawn to screen.
- `dnext`: `double`, threshold value for next tick.

### VT100 Progress Bar Functions
#### `vt100_progress`
```c
static void vt100_progress(double d, void *data);
```
Prints a progress bar using VT100 control codes.
- `d`: `double`, Progress fraction between 0 and 1.
- `data`: `void *`, A pointer to the progress bar data structure (vt100_progress_t).

#### `init_vt100_progress`
```c
static int init_vt100_progress(potrace_progress_t *prog, const char *filename, int count);
```
Initializes a progress bar object, writing the initial progress bar to file.
- `prog`: `potrace_progress_t *`, The progress bar object.
- `filename`: `const char *`, The name of file currently being processed.
- `count`: `int`, Index number of current progress bar if multiple files are being processed.
**Returns:**
`int`, 0 upon success, 1 on failure with errno set

#### `term_vt100_progress`
```c
static void term_vt100_progress(potrace_progress_t *prog);
```
Terminates a vt100 progress bar by outputting a final newline, and freeing the data.
- `prog`: `potrace_progress_t *`, The progress bar object

### Simplified Progress Bar Functions
#### `simplified_progress`
```c
static void simplified_progress(double d, void *data);
```
Prints a progress bar using a series of `=` characters.
- `d`: `double`, Progress fraction between 0 and 1.
- `data`: `void *`, Pointer to the data for progress bar (simplified_progress_t).

#### `init_simplified_progress`
```c
static int init_simplified_progress(potrace_progress_t *prog, const char *filename, int count);
```
Initializes the simplified progress bar outputting the beginning of the progress bar.
- `prog`: `potrace_progress_t *`, The progress bar object.
- `filename`: `const char *`, The filename currently being processed.
- `count`: `int`, index of bitmap if processing multiple files.
**Returns:**
`int`, Returns 0 on success or 1 on error with errno set.

#### `term_simplified_progress`
```c
static void term_simplified_progress(potrace_progress_t *prog);
```
Terminates simplified progress bar outputting the completion part of the progress bar.
- `prog`: `potrace_progress_t *`, The progress bar object to terminate.

### Progress Bar Interface Structures
#### `progress_bar_vt100_struct`
```c
static progress_bar_t progress_bar_vt100_struct = {
  init_vt100_progress,
  term_vt100_progress,
};
```
Structure of the vt100 progress bar object.

#### `progress_bar_vt100`
```c
progress_bar_t *progress_bar_vt100 = &progress_bar_vt100_struct;
```
Pointer to the vt100 progress bar object.

#### `progress_bar_simplified_struct`
```c
static progress_bar_t progress_bar_simplified_struct = {
  init_simplified_progress,
  term_simplified_progress,
};
```
Structure of the simplified progress bar object.

#### `progress_bar_simplified`
```c
progress_bar_t *progress_bar_simplified = &progress_bar_simplified_struct;
```
Pointer to the simplified progress bar object.


## File: lzw.h
```
This header file declares types and functions for LZW (Lempel-Ziv-Welch) compression. It defines the structure for the LZW stream and provides functions for initialization, compression, and deallocation.
```
### Includes
- None

### Macros
#### `LZW_NORMAL`
```c
#define LZW_NORMAL 0
```
Macro used for `lzw_compress` to indicate normal mode.

#### `LZW_EOD`
```c
#define LZW_EOD 1
```
Macro used for `lzw_compress` to indicate that this is the end of the data and the buffer should be flushed.

### Structures
#### `lzw_stream_s`
```c
struct lzw_stream_s {
  const char *next_in; /* pointer to next input character */
  int avail_in;        /* number of input chars available */
  char *next_out;      /* pointer to next free byte in output buffer */
  int avail_out;       /* remaining size of output buffer */

  void *internal;      /* internal state, not user accessible */
};
```
Represents a stream for LZW compression
- `next_in`: `const char *`, points to the beginning of the uncompressed input data buffer.
- `avail_in`: `int`, represents size of the input data buffer
- `next_out`: `char *`, points to the next free byte in output buffer
- `avail_out`: `int`, represents the remaining size of the output buffer
- `internal`: `void *`, holds internal compression state, not user accessible

### Functions
#### `lzw_init`
```c
lzw_stream_t *lzw_init(void);
```
Initializes the LZW compression state, and returns the stream object to be used by compress function
**Returns:**
`lzw_stream_t *`, A pointer to the new LZW stream, or NULL on error with errno set.

#### `lzw_compress`
```c
int lzw_compress(lzw_stream_t *s, int mode);
```
Compresses data using the LZW algorithm, processing as much input as possible.
- `s`: `lzw_stream_t *`, The LZW compression stream data.
- `mode`: `int`, The mode to use. LZW_NORMAL or LZW_EOD
**Returns**:
`int`, 0 on success or 1 on error with errno set.

#### `lzw_free`
```c
void lzw_free(lzw_stream_t *s);
```
Frees an LZW compression stream object.
- `s`: `lzw_stream_t *`, The LZW compression stream to be freed.


## File: lzw.c
```
This file implements the adaptive LZW (Lempel-Ziv-Welch) compression algorithm, as used in PostScript and PDF. It also manages a bit buffer for efficient bitstream writing.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdlib.h`: For memory allocation functions.
- `stdio.h`: For standard input/output functions.
- `errno.h`: For error number definitions.
- `string.h`: For string manipulation functions.
- `lists.h`: Definitions for linked list data structures.
- `bitops.h`: Definitions for bit manipulation functions.
- `lzw.h`: Definitions for data structures and function prototypes specific to LZW compression

### Macros
#### `BITBUF_TYPE`
```c
#define BITBUF_TYPE unsigned int
```
Defines the type of the bit buffer.

### Structures
#### `lzw_dict_s`
```c
struct lzw_dict_s {
  char c;            /* last character of string represented by this entry */
  unsigned int code; /* code for the string represented by this entry */
  int freq;          /* how often searched? For optimization only */
  struct lzw_dict_s *children;  /* list of sub-entries */
  struct lzw_dict_s *next;      /* for making a linked list */
};
```
Represents a dictionary entry in the LZW compression algorithm.
- `c`: `char`, Last character of string represented by this entry
- `code`: `unsigned int`, Code associated with this string.
- `freq`: `int`, Frequency of search, used for optimization.
- `children`: `struct lzw_dict_s *`, List of sub-entries.
- `next`: `struct lzw_dict_s *`, Pointer to the next sibling in a linked list.

#### `lzw_state_s`
```c
struct lzw_state_s {
  /* dictionary state */
  int n;           /* current size of the dictionary */
  lzw_dict_t *d;   /* pointer to dictionary */
  lzw_dict_t *s;   /* pointer to current string, or NULL at beginning */

  /* buffers for pending output */
  BITBUF_TYPE buf; /* bits scheduled for output - left aligned, 0 padded */
  int bufsize;     /* number of bits scheduled for output. */
  int eod;         /* flush buffer? */
};
```
Represents the state of the LZW compression algorithm, holding both dictionary and output state.
- `n`: `int`, Current dictionary size.
- `d`: `lzw_dict_t *`, Pointer to the root of the LZW dictionary
- `s`: `lzw_dict_t *`,  Pointer to current string, or NULL at beginning.
- `buf`: `BITBUF_TYPE`, The bit buffer for pending output bits.
- `bufsize`: `int`, The current number of bits in buffer.
- `eod`: `int`, A flag indicating if the end of data marker has been reached and the buffer needs to be flushed.

### Auxiliary Functions
#### `lzw_free_dict`
```c
static void lzw_free_dict(lzw_dict_t *s);
```
Recursively free an lzw_dict_t object.
- `s`: `lzw_dict_t *`, dictionary node to free

#### `lzw_clear_table`
```c
static void lzw_clear_table(lzw_state_t *st);
```
Re-initialize the lzw state's dictionary state to "newdict", freeing any old dictionary.
- `st`: `lzw_state_t *`, The LZW state object to clear

#### `lzw_emit`
```c
static inline void lzw_emit(unsigned int code, lzw_state_t *st);
```
Write code to bit buffer. Precondition st->bufsize <= 7.
- `code`: `unsigned int`, Code to emit
- `st`: `lzw_state_t *`, LZW state object

#### `lzw_read_bitbuf`
```c
static inline void lzw_read_bitbuf(lzw_stream_t *s);
```
Transfer one byte from bit buffer to output. Precondition:
   s->avail_out > 0
- `s`: `lzw_stream_t *`, LZW output stream.

### State Machine Functions
#### `lzw_encode_char`
```c
static int lzw_encode_char(lzw_state_t *st, char c);
```
Perform state transition of the state st on input character ch. Updates the dictionary state and/or writes to the bit buffer. Precondition: st->bufsize <= 7.
- `st`: `lzw_state_t *`, Current LZW state.
- `c`: `char`, character to be processed.
**Returns:**
`int`, returns 0 on success, or 1 on error with errno set

#### `lzw_encode_eod`
```c
static void lzw_encode_eod(lzw_state_t *st);
```
Perform state transition of the state st on input EOD.  The leaves
   the dictionary state undefined and writes to the bit buffer.
   Precondition: st->bufsize <= 7. This function must be called
   exactly once, at the end of the stream
- `st`: `lzw_state_t *`, current LZW state.

### User Visible Functions
#### `lzw_init`
```c
lzw_stream_t *lzw_init(void);
```
Initializes the lzw state, and returns the stream object to be used by compress function
**Returns:**
`lzw_stream_t *`, A pointer to the new LZW stream, or NULL on error with errno set.

#### `lzw_compress`
```c
int lzw_compress(lzw_stream_t *s, int mode);
```
Compresses data using LZW algorithm and writes to the output buffer
- `s`: `lzw_stream_t *`, The LZW compression stream.
- `mode`: `int`, The LZW mode (LZW_NORMAL or LZW_EOD).
**Returns**:
`int`, 0 on success, or 1 on error with errno set

#### `lzw_free`
```c
void lzw_free(lzw_stream_t *s);
```
Frees an LZW compression stream object.
- `s`: `lzw_stream_t *`, The LZW compression stream to be freed.


## File: flate.h
```
This header file declares functions for compressing data for various backends (e.g., PostScript), and particularly Postscript Level 2 and Level 3 compression using LZW and flate/zlib algorithms respectively.
```
### Includes
- None

### Functions
#### `dummy_xship`
```c
int dummy_xship(FILE *f, int filter, const char *s, int len);
```
A dummy no-op function for shipping data without encoding, just writes the data to stream `f`.
- `f`: `FILE *`, The output file stream.
- `filter`: `int`, Filter flag.
- `s`: `const char *`, The data buffer to output.
- `len`: `int`, The number of bytes from the data buffer to output.
**Returns:**
`int`, The number of characters written.

#### `flate_xship`
```c
int flate_xship(FILE *f, int filter, const char *s, int len);
```
Ships data to a stream and optionally compress it using flate (zlib).
- `f`: `FILE *`, Output file stream.
- `filter`: `int`, Flag indicating to compress data or to output verbatim.
- `s`: `const char *`, Data buffer to be compressed
- `len`: `int`, Number of bytes of data to be compressed.
**Returns:**
`int`, The number of characters written.

#### `pdf_xship`
```c
int pdf_xship(FILE *f, int filter, const char *s, int len);
```
Ships data to a stream and optionally compresses it with flate/zlib specifically for PDF output (no ASCII85 encoding)
- `f`: `FILE *`, Output file stream.
- `filter`: `int`, Flag indicating to compress data or to output verbatim.
- `s`: `const char *`, Data buffer to be compressed
- `len`: `int`, Number of bytes of data to be compressed.
**Returns:**
`int`, The number of characters written.

#### `lzw_xship`
```c
int lzw_xship(FILE *f, int filter, const char *s, int len);
```
Ships data to a stream and optionally compresses it using LZW (PostScript Level 2).
- `f`: `FILE *`, Output file stream.
- `filter`: `int`, Flag indicating to compress data or output verbatim.
- `s`: `const char *`, Data buffer to be compressed
- `len`: `int`, Number of bytes of data to be compressed.
**Returns:**
`int`, The number of characters written.

#### `a85_xship`
```c
int a85_xship(FILE *f, int filter, const char *s, int len);
```
Ships data to a stream and optionally encodes it using ASCII85 without compression.
- `f`: `FILE *`, Output file stream.
- `filter`: `int`, Flag indicating to apply ASCII85 encoding or output verbatim.
- `s`: `const char *`, Data buffer to be encoded.
- `len`: `int`, Number of bytes of data to be encoded.
**Returns:**
`int`, The number of characters written.


## File: flate.c
```
This file implements functions to compress data using zlib (flate) and lzw algorithms and to ship the result to a file, using base85 encoding.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdio.h`: For standard input/output functions.
- `string.h`: For string functions.
- `stdlib.h`: For standard memory allocation functions.
- `errno.h`: For system error number
- `zlib.h` (conditional): For zlib compression library.
- `flate.h`: Header file containing function declarations for data shipping.
- `lzw.h`: Header file for the LZW compression.

### Macros
#### `OUTSIZE`
```c
#define OUTSIZE 1000
```
Defines the size of output buffer, for compression operations

### Functions
#### `dummy_xship`
```c
int dummy_xship(FILE *f, int filter, const char *s, int len);
```
Ships data to a file without any encoding, directly copying bytes to output stream.
- `f`: `FILE *`, output stream.
- `filter`: `int`, always ignored, present to comply with the shipping interface.
- `s`: `const char *`, input data buffer.
- `len`: `int`, number of bytes to ship.
**Returns:**
`int`, The number of characters written.

#### `pdf_xship`
```c
int pdf_xship(FILE *f, int filter, const char *s, int len);
```
Ships data to a file and optionally compresses using zlib. Used for PDF documents output.
- `f`: `FILE *`, The output stream.
- `filter`: `int`, If set to a non-zero value, data will be compressed.
- `s`: `const char *`, Input data buffer.
- `len`: `int`, Number of bytes to ship
**Returns:**
`int`, The number of characters written.

#### `flate_xship`
```c
int flate_xship(FILE *f, int filter, const char *s, int len);
```
Ships data to a file, optionally compressing the data using zlib's flate algorithm using ASCII85.
- `f`: `FILE *`, output stream.
- `filter`: `int`, If 1 data will be compressed with ASCII85 encoding, if 0 data will be written without changes.
- `s`: `const char *`, The data to output to file.
- `len`: `int`, Number of bytes to ship.
**Returns:**
`int`, The number of characters written to file.

#### `lzw_xship`
```c
int lzw_xship(FILE *f, int filter, const char *str, int len);
```
Ships data to a file, optionally using LZW compression, encoded to ASCII85.
- `f`: `FILE *`, The output stream.
- `filter`: `int`, if non-zero, perform LZW compression and base85 encoding. if 0, send data without changes.
- `str`: `const char *`, The data buffer to send to stream.
- `len`: `int`, Number of bytes of data.
**Returns**:
`int`, The number of characters written.

#### `a85_xship`
```c
int a85_xship(FILE *f, int filter, const char *s, int len);
```
Ships data to a file using a85 encoding only.
- `f`: `FILE *`, Output file stream.
- `filter`: `int`, If 1 data is encoded using ASCII85, otherwise raw data is output
- `s`: `const char *`, data to be shipped.
- `len`: `int`, The length in bytes of the data to be shipped.
**Returns:**
`int`, The number of characters written

### Internal ASCII85 Backend
#### `a85init`
```c
static int a85init(FILE *f);
```
Initializes the ASCII85 encoder.
- `f`: `FILE *`, Output stream.
**Returns:**
`int`, Always returns 0

#### `a85finish`
```c
static int a85finish(FILE *f);
```
Finishes ASCII85 encoding by padding the rest of the buffer.
- `f`: `FILE *`, Output stream
**Returns:**
`int`, The number of characters written.

#### `a85write`
```c
static int a85write(FILE *f, const char *buf, int n);
```
Write to buffer and encode using ASCII85, calling `a85out` if buffer is full.
- `f`: `FILE *`, Output file stream
- `buf`: `const char *`, input buffer containing data to encode and write
- `n`: `int`, length of data in buffer
**Returns**:
`int`, The number of bytes written.

#### `a85out`
```c
static int a85out(FILE *f, int n);
```
Encodes the stored buffer, and sends it to the specified file descriptor.
- `f`: `FILE *`, Output stream to write to.
- `n`: `int`, Number of bytes in buffer.
**Returns**:
`int`, The number of bytes written.

#### `a85spool`
```c
static int a85spool(FILE *f, char c);
```
Spools one character to the output stream, adding newlines if column is longer than 70.
- `f`: `FILE *`, Output file stream
- `c`: `char`, Character to write to stream
**Returns**:
`int`, Number of characters written to file (including line breaks).


## File: render.h
```
This header file defines the structure and functions related to rendering of vector graphics on to the greyscale images for Potrace.
```
### Includes
- `greymap.h`: Header file containing declarations for the greyscale images

### Structures
#### `render_s`
```c
struct render_s {
  greymap_t *gm;
  double x0, y0, x1, y1;
  int x0i, y0i, x1i, y1i;
  double a0, a1;
  int *incrow_buf;
};
```
Represents the state for the rendering process.
- `gm`: `greymap_t *`, The greyscale image that we render into.
- `x0`, `y0`: `double`, previous initial coordinates in floating point
- `x1`, `y1`: `double`, current coordinates in floating point
- `x0i`, `y0i`: `int`, integer part of the previous initial coordinates
- `x1i`, `y1i`: `int`, integer part of the current coordinates
- `a0`, `a1`: `double`, floating point accumulators for changes in color
- `incrow_buf`: `int *`, Buffer used to cache changes for the rows, to be applied at a later point.

### Functions
#### `render_new`
```c
render_t *render_new(greymap_t *gm);
```
Initializes a new render_s object for rendering into the specified greyscale image.
- `gm`: `greymap_t *`, The greymap to render into.
**Returns**:
`render_t *`, returns a pointer to initialized render data structure, or NULL if memory allocation fails.

#### `render_free`
```c
void render_free(render_t *rm);
```
Frees a rendering state object.
- `rm`: `render_t *`, The rendering state object.

#### `render_close`
```c
void render_close(render_t *rm);
```
Completes the current path.
- `rm`: `render_t *`, The rendering state object.

#### `render_moveto`
```c
void render_moveto(render_t *rm, double x, double y);
```
Sets the current position, starting a new path.
- `rm`: `render_t *`, The rendering state object.
- `x`: `double`, The x-coordinate to move to.
- `y`: `double`, The y-coordinate to move to.

#### `render_lineto`
```c
void render_lineto(render_t *rm, double x, double y);
```
Draws a straight line from the current position to a new position.
- `rm`: `render_t *`, The rendering state object.
- `x2`: `double`, The x-coordinate of the new position to draw to.
- `y2`: `double`, The y-coordinate of the new position to draw to.

#### `render_curveto`
```c
void render_curveto(render_t *rm, double x2, double y2, double x3, double y3, double x4, double y4);
```
Draws a bezier curve from the current position using two control points and an end point.
- `rm`: `render_t *`, The rendering state object.
- `x2`: `double`, The x-coordinate of first control point.
- `y2`: `double`, The y-coordinate of first control point.
- `x3`: `double`, The x-coordinate of second control point.
- `y3`: `double`, The y-coordinate of second control point.
- `x4`: `double`, The x-coordinate of the end point.
- `y4`: `double`, The y-coordinate of the end point.


## File: render.c
```
This file provides functions for rendering vector paths onto greymaps with anti-aliasing, using a custom rendering algorithm.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdio.h`: For standard input/output functions.
- `stdlib.h`: For memory allocation functions.
- `math.h`: For math functions.
- `string.h`: For string functions.
- `render.h`: Header defining the interfaces for path rendering.
- `greymap.h`: Header containing the declarations for the greymap data structure.
- `auxiliary.h`:  Header containing useful auxiliary types and macros.

### Structures
#### `render_s`
```c
struct render_s {
  greymap_t *gm;
  double x0, y0, x1, y1;
  int x0i, y0i, x1i, y1i;
  double a0, a1;
  int *incrow_buf;
};
```
The structure representing the state for the rendering process.
- `gm`: `greymap_t *`, Pointer to greyscale image to render to
- `x0`, `y0`: `double`, previous initial x and y coordinates
- `x1`, `y1`: `double`, current x and y coordinates
- `x0i`, `y0i`: `int`, integer part of the initial x and y coordinates
- `x1i`, `y1i`: `int`, integer part of the current x and y coordinates
- `a0`, `a1`: `double`, accumulators for alpha values
- `incrow_buf`: `int *`, Buffer used to cache changes for the rows.

### Functions
#### `render_new`
```c
render_t *render_new(greymap_t *gm);
```
Allocates and initializes a new render state object.
- `gm`: `greymap_t *`, The greymap to be rendered to.
**Returns:**
`render_t *`, pointer to the allocated render state or NULL on error.

#### `render_free`
```c
void render_free(render_t *rm);
```
Frees a rendering state object.
- `rm`: `render_t *`, The rendering state object.

#### `render_close`
```c
void render_close(render_t *rm);
```
Closes current path, by drawing a line to original position.
- `rm`: `render_t *`, The rendering state object.

#### `render_moveto`
```c
void render_moveto(render_t *rm, double x, double y);
```
Sets the current position for drawing, effectively starting a new path.
- `rm`: `render_t *`, The rendering state object.
- `x`: `double`, The new x-coordinate to move to.
- `y`: `double`, The new y-coordinate to move to.

#### `incrow`
```c
static void incrow(render_t *rm, int x, int y, int b);
```
Increments/decrements all the pixels from point `(x, y)` to right of it, using an `incrow_buf`.
- `rm`: `render_t *`, The rendering state.
- `x`: `int`, The x-coordinate of the start point.
- `y`: `int`, The y-coordinate of the row.
- `b`: `int`, Increment/decrement value.

#### `render_lineto`
```c
void render_lineto(render_t *rm, double x2, double y2);
```
Draws a straight line from current position to the new position provided.
- `rm`: `render_t *`, The rendering state object.
- `x2`: `double`, The destination x-coordinate.
- `y2`: `double`, The destination y-coordinate.

#### `render_curveto`
```c
void render_curveto(render_t *rm, double x2, double y2, double x3, double y3, double x4, double y4);
```
Draws a Bezier curve, from current position to a specified point using two control points.
- `rm`: `render_t *`, The rendering state object.
- `x2`: `double`, X-coordinate of the first control point.
- `y2`: `double`, Y-coordinate of the first control point.
- `x3`: `double`, X-coordinate of the second control point.
- `y3`: `double`, Y-coordinate of the second control point.
- `x4`: `double`, X-coordinate of the ending point.
- `y4`: `double`, Y-coordinate of the ending point.


## File: bitops.h
```
This header file provides macros and inline functions for bit manipulation, including platform-specific optimized versions where possible. It defines functions for extracting the rightmost and leftmost set bits in an integer.
```
### Includes
- `config.h` (conditional): Provides configuration defines.

### Functions
#### `lobit`
```c
static inline unsigned int lobit(unsigned int x);
```
Returns the position (0-based index) of the rightmost set bit in an integer, or 32 if none.
- `x`: `unsigned int`, The integer to inspect.
**Returns:**
`unsigned int`, The bit position (0-based) of the rightmost set bit, or 32 if no set bit was found.

#### `hibit`
```c
static inline unsigned int hibit(unsigned int x);
```
Returns one plus the position of the leftmost set bit in an integer, or 0 if none.
- `x`: `unsigned int`, The integer to inspect.
**Returns**:
`unsigned int`, The bit position (1-based) of the leftmost set bit, or 0 if no set bit was found.


## File: trans.h
```
This header file defines structures and functions to handle coordinate transformations in Potrace. This includes rotation, scaling, and bounding box adjustments.
```
### Includes
- `auxiliary.h`: Definitions for auxiliary types.

### Structures
#### `trans_s`
```c
struct trans_s {
  double bb[2];    /* dimensions of bounding box */
  double orig[2];  /* origin relative to bounding box */
  double x[2];     /* basis vector for the "x" direction */
  double y[2];     /* basis vector for the "y" direction */
  double scalex, scaley;  /* redundant info for some backends' benefit */
};
```
Represents a coordinate transformation, storing bounding box, origin, basis vectors, and scaling factors.
- `bb`: `double[2]`, Dimensions of the bounding box (width and height).
- `orig`: `double[2]`, Origin of the transformation relative to the bounding box.
- `x`: `double[2]`, Basis vector for the x-direction.
- `y`: `double[2]`, Basis vector for the y-direction.
-  `scalex`: `double`, Scaling factor in x-direction.
- `scaley`: `double`, Scaling factor in y-direction.

### Functions
#### `trans`
```c
static inline dpoint_t trans(dpoint_t p, trans_t t);
```
Applies a coordinate transformation to a point.
- `p`: `dpoint_t`, The point to be transformed.
- `t`: `trans_t`, The coordinate transformation parameters.
**Returns**:
`dpoint_t`, The transformed point.

#### `trans_rotate`
```c
void trans_rotate(trans_t *r, double alpha);
```
Rotates the coordinate system counterclockwise by alpha degrees. The
   new bounding box will be the smallest box containing the rotated
   old bounding box
- `r`: `trans_t *`, Pointer to transformation data.
- `alpha`: `double`, Rotation angle in degrees.

#### `trans_from_rect`
```c
void trans_from_rect(trans_t *r, double w, double h);
```
Return the standard cartesian coordinate system for an w x h rectangle.
- `r`: `trans_t *`, Pointer to transformation data.
- `w`: `double`, Width of the rectangle.
- `h`: `double`, Height of the rectangle.

#### `trans_rescale`
```c
void trans_rescale(trans_t *r, double sc);
```
Rescale the coordinate system r by factor sc >= 0.
- `r`: `trans_t *`, Pointer to the transformation data.
- `sc`: `double`, Scaling factor.

#### `trans_scale_to_size`
```c
void trans_scale_to_size(trans_t *r, double w, double h);
```
Rescale the coordinate system to size w x h
- `r`: `trans_t *`, Pointer to the transformation data.
- `w`: `double`, Target width.
- `h`: `double`, Target height.

#### `trans_tighten`
```c
void trans_tighten(trans_t *r, potrace_path_t *plist);
```
Adjusts the bounding box to the actual vector outline.
- `r`: `trans_t *`, The transformation data to be adjusted.
- `plist`: `potrace_path_t *`, The list of path to determine boundaries.


## File: trans.c
```
This file implements functions related to coordinate transformations and bounding box adjustments for Potrace, including rotation, scaling, and tightening bounding boxes based on vector outlines.
```

### Includes
- `config.h` (conditional): Provides configuration defines.
- `math.h`: For math functions.
- `string.h`: For string functions.
- `trans.h`: Header containing the declarations of transformation related functions and data structures.
- `bbox.h`: Declaration for bounding box structures and functions

### Functions
#### `trans_rotate`
```c
void trans_rotate(trans_t *r, double alpha);
```
Rotates a coordinate system counterclockwise by a given angle (in degrees).
- `r`: `trans_t *`, Pointer to the transformation settings.
- `alpha`: `double`, The rotation angle in degrees.

#### `trans_from_rect`
```c
void trans_from_rect(trans_t *r, double w, double h);
```
Initializes a coordinate transformation to represent a rectangle.
- `r`: `trans_t *`, Pointer to the transformation settings to be initialized.
- `w`: `double`, The width of the rectangle.
- `h`: `double`, The height of the rectangle.

#### `trans_rescale`
```c
void trans_rescale(trans_t *r, double sc);
```
Rescales the current coordinate system by a given factor.
- `r`: `trans_t *`, Pointer to transformation settings to be rescaled
- `sc`: `double`, Scaling factor.

#### `trans_scale_to_size`
```c
void trans_scale_to_size(trans_t *r, double w, double h);
```
Scales a coordinate system to a specific size, maintaining aspect ratio.
- `r`: `trans_t *`, Pointer to the transformation settings.
- `w`: `double`, The target width of the transformed bounding box
- `h`: `double`, The target height of the transformed bounding box

#### `trans_tighten`
```c
void trans_tighten(trans_t *r, potrace_path_t *plist);
```
Adjusts the given coordinate system by fitting the bounding box to actual vector outline.
- `r`: `trans_t *`, Pointer to the transformation settings to be adjusted.
- `plist`: `potrace_path_t *`, The linked list of paths representing the outline of an object.


## File: greymap.h
```
This header file defines data structures and functions for handling greymaps (grayscale images) in Potrace.
```
### Includes
- `stdio.h`: Standard input/output functions.
- `stdlib.h`: For standard memory allocation functions.
- `stddef.h`: For definitions like `ptrdiff_t`.

### Type Definitions
#### `gm_sample_t`
```c
typedef signed short int gm_sample_t;
```
Represents a single sample (pixel) value in the greymap.

### Macros
#### `GM_SAMPLESIZE`
```c
#define GM_SAMPLESIZE (sizeof(gm_sample_t))
```
Defines the size (in bytes) of a single sample in the greymap, derived from the size of the type `gm_sample_t`.
#### Access Macros
- `gm_scanline(gm, y)`: Gets pointer to start of the y-th scanline of a given greymap
- `gm_index(gm, x, y)`: Gets pointer to the pixel at location (x,y)
- `gm_safe(gm, x, y)`: Checks if (x,y) is a valid location
- `gm_bound(x, m)`: Limits an index `x` to be within a range 0 and m-1
- `GM_UGET(gm, x, y)`: Gets the pixel value at (x,y) without bounds checking
- `GM_UINC(gm, x, y, b)`: Increments the pixel at (x,y) by b without bounds checking
- `GM_UINV(gm, x, y)`: Inverts the pixel at (x,y) without bounds checking
- `GM_UPUT(gm, x, y, b)`: Sets the pixel at (x,y) to b without bounds checking
- `GM_GET(gm, x, y)`: Gets the pixel value at (x,y) with bounds checking
- `GM_INC(gm, x, y, b)`: Increments the pixel at (x,y) by b with bounds checking
- `GM_INV(gm, x, y)`: Inverts the pixel at (x,y) with bounds checking
- `GM_PUT(gm, x, y, b)`: Sets the pixel at (x,y) to b with bounds checking
- `GM_BGET(gm, x, y)`: Gets value of pixel at (x, y) with bounds clipping

#### GM_MODE Constants
- `GM_MODE_NONZERO`: Use the non-zero winding rule
- `GM_MODE_ODD`: Use the odd winding rule
- `GM_MODE_POSITIVE`: Use the positive winding rule
- `GM_MODE_NEGATIVE`: Use the negative winding rule

### Global Variables
#### `gm_read_error`
```c
extern const char *gm_read_error;
```
A global error string that will be set to error description in case of failure during reading of a greyscale image file

### Structures
#### `greymap_s`
```c
struct greymap_s {
  int w;              /* width, in pixels */
  int h;              /* height, in pixels */
  int dy;             /* offset between scanlines (in samples);
                         can be negative */
  gm_sample_t *base;  /* root of allocated data */
  gm_sample_t *map;   /* points to the lower left pixel */
};
```
Represents a greyscale image, storing dimensions, scanline offset, base pixel address, and current pixel map address.
- `w`: `int`, Width of the greymap in pixels.
- `h`: `int`, Height of the greymap in pixels.
- `dy`: `int`, Offset (in samples) between successive scanlines. Can be negative to flip the bitmap vertically.
- `base`: `gm_sample_t *`, The base pointer of allocated pixel data.
- `map`: `gm_sample_t *`, The currently active pointer to pixel data (can change if flipped).

### Functions
#### `gm_new`
```c
greymap_t *gm_new(int w, int h);
```
Creates a new greymap and allocates memory for its pixel data.
- `w`: `int`, The width of the greymap (pixels).
- `h`: `int`, The height of the greymap (pixels).
**Returns:**
`greymap_t *`, A pointer to the newly allocated greymap or NULL with errno set on allocation failure

#### `gm_dup`
```c
greymap_t *gm_dup(greymap_t *gm);
```
Creates a deep copy (duplicate) of an existing greymap
- `gm`: `greymap_t *`, The source greymap.
**Returns:**
`greymap_t *`, A pointer to the newly duplicated greymap or NULL with errno set on allocation failure.

#### `gm_free`
```c
void gm_free(greymap_t *gm);
```
Frees the memory allocated for a greymap.
- `gm`: `greymap_t *`, The greymap to be freed.

#### `gm_clear`
```c
void gm_clear(greymap_t *gm, int b);
```
Fills a greymap with a single color value.
- `gm`: `greymap_t *`, The greymap to clear.
- `b`: `int`, The color value to clear with.

#### `gm_read`
```c
int gm_read(FILE *f, greymap_t **gmp);
```
Reads a greymap from a file, supporting PNM (PBM, PGM, PPM) and BMP formats.
- `f`: `FILE *`, The input file descriptor.
- `gmp`: `greymap_t **`, Pointer to a pointer to the allocated greymap.
**Returns:**
`int`, 0 on success, -1 on error with errno set, -2 on bad file format, -3 on empty file, -4 on wrong magic number, or 1 on premature end of file.

#### `gm_writepgm`
```c
int gm_writepgm(FILE *f, greymap_t *gm, const char *comment, int raw, int mode, double gamma);
```
Writes a greymap to a file in PGM format.
- `f`: `FILE *`, The output file descriptor
- `gm`: `greymap_t *`, The greymap to write
- `comment`: `const char *`, Optional comment string.
- `raw`: `int`, Flag to specify raw or ascii output format (1 means raw).
- `mode`: `int`, Mode of how to cut off out-of-range color values (`GM_MODE_NONZERO`, `GM_MODE_ODD`, `GM_MODE_POSITIVE`, `GM_MODE_NEGATIVE`).
- `gamma`: `double`, Gamma value (1.0 for no gamma correction).
**Returns:**
`int`, Always returns 0

#### `gm_print`
```c
int gm_print(FILE *f, greymap_t *gm);
```
Prints a basic text-based representation of a greymap (used for debugging purposes).
- `f`: `FILE *`, The output file descriptor
- `gm`: `greymap_t *`, The greymap to print.
**Returns:**
`int`, Always returns 0


### DXF Output Synthesis
#### `ship`
```c
static int ship(FILE *fout, int gc, const char *fmt, ...);
```
Writes a DXF group code and a value in the given format to a file.
- `fout`: `FILE *`, The output file pointer.
- `gc`: `int`, DXF group code.
- `fmt`: `const char *`, Format string (like printf).
- `...`: variable arguments
**Returns**:
`int`, The number of characters written, or a negative value if there was an error.

#### `ship_polyline`
```c
static void ship_polyline(FILE *fout, const char *layer, int closed);
```
Writes the header of a DXF polyline to a file.
- `fout`: `FILE *`, Output file pointer.
- `layer`: `const char *`, Name of the layer.
- `closed`: `int`, Boolean value indicating if the polyline is closed (1 if it is)

#### `ship_vertex`
```c
static void ship_vertex(FILE *fout, const char *layer, dpoint_t v, double bulge);
```
Writes a DXF vertex to a file.
- `fout`: `FILE *`, Output file pointer.
- `layer`: `const char *`, Name of the layer.
- `v`: `dpoint_t`, Coordinates of the vertex.
- `bulge`: `double`, Bulge factor of this point

#### `ship_seqend`
```c
static void ship_seqend(FILE *fout);
```
Writes the end-of-polyline sequence to a file.
- `fout`: `FILE *`, Output file pointer.

#### `ship_comment`
```c
static void ship_comment(FILE *fout, const char *comment);
```
Writes a DXF comment to a file.
- `fout`: `FILE *`, Output file pointer.
- `comment`: `const char *`, The comment to be written.

#### `ship_section`
```c
static void ship_section(FILE *fout, const char *name);
```
Writes the beginning of a DXF section to a file.
- `fout`: `FILE *`, Output file pointer.
- `name`: `const char *`, Name of the section.

#### `ship_endsec`
```c
static void ship_endsec(FILE *fout);
```
Writes the end of a DXF section to a file.
- `fout`: `FILE *`, Output file pointer.

#### `ship_eof`
```c
static void ship_eof(FILE *fout);
```
Writes the end-of-file marker to a DXF file.
- `fout`: `FILE *`, Output file pointer.

### Simulated Quadratic and Bezier Curves
#### `pseudo_quad`
```c
static void pseudo_quad(FILE *fout, const char *layer, dpoint_t A, dpoint_t C, dpoint_t B);
```
Simulates a quadratic Bezier curve using two circular arcs.
- `fout`: `FILE *`, Output file pointer.
- `layer`: `const char *`, Name of the layer.
- `A`: `dpoint_t`, Start point.
- `C`: `dpoint_t`, Control point.
- `B`: `dpoint_t`, End point.

#### `pseudo_bezier`
```c
static void pseudo_bezier(FILE *fout, const char *layer, dpoint_t A, dpoint_t B, dpoint_t C, dpoint_t D);
```
Simulates a cubic Bezier curve using pseudo-quadratic curves.
- `fout`: `FILE *`, Output file pointer.
- `layer`: `const char *`, Name of the layer.
- `A`: `dpoint_t`, Start point of the curve.
- `B`: `dpoint_t`, First control point of the curve.
- `C`: `dpoint_t`, Second control point of the curve.
- `D`: `dpoint_t`, End point of the curve.

### Path Conversion
#### `dxf_path`
```c
static int dxf_path(FILE *fout, const char *layer, potrace_curve_t *curve, trans_t t);
```
Converts a single Potrace curve into a DXF polyline representation.
- `fout`: `FILE *`, Output file pointer.
- `layer`: `const char *`, Name of the layer.
- `curve`: `potrace_curve_t *`, The curve object to convert.
- `t`: `trans_t`, The transformation parameters.
**Returns**:
`int`, 0 on success or error with errno set.

### Backend
#### `page_dxf`
```c
int page_dxf(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Generates the DXF output to a specified file.
- `fout`: `FILE *`, Output file descriptor.
- `plist`: `potrace_path_t *`, List of paths that represents object of interest.
- `imginfo`: `imginfo_t *`, image informations such as image dimensions and margins.
**Returns**:
`int`, 0 on success or 1 on error with errno set


## File: greymap.c
```
This file implements functions for manipulating greymaps, including reading pgm files. We only deal with greymaps of depth 8 bits.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdlib.h`: For standard memory allocation functions.
- `string.h`: For string functions
- `math.h`: For math related functions
- `errno.h`: For system error definitions.
- `stddef.h`: For definitions like `ptrdiff_t`.
```c
#ifdef HAVE_INTTYPES_H
#include <inttypes.h>
#endif
```
- `greymap.h`: Header file that contains type definitions and function declarations for a greyscale image.
- `bitops.h`: For bit manipulation functions

### Macros
#### `INTBITS`
```c
#define INTBITS (8*sizeof(int))
```
Defines the number of bits in an integer.

#### `mod`
```c
#define mod(a,n) ((a)>=(n) ? (a)%(n) : (a)>=0 ? (a) : (n)-1-(-1-(a))%(n))
```
Calculates the modulo with correct behavior for negative numbers.
- `a`: `int`, The number to calculate modulo of.
- `n`: `int`, The divisor.
**Returns:**
`int`, The result of the modulo operation.

### Static Functions
#### `gm_readbody_pnm`
```c
static int gm_readbody_pnm(FILE *f, greymap_t **gmp, int magic);
```
Reads the body of a pnm greymap from the provided file.
- `f`: `FILE *`, input file
- `gmp`: `greymap_t **`, a pointer to a pointer of where greyscale image will be created and stored to
- `magic`: `int`, integer identifier of the file type that indicates which type of file is being read

#### `gm_readbody_bmp`
```c
static int gm_readbody_bmp(FILE *f, greymap_t **gmp);
```
Reads the body of a bmp greymap from provided file.
- `f`: `FILE *`, input file.
- `gmp`: `greymap_t **`, a pointer to a pointer of where greyscale image will be created and stored to

#### `fgetc_ws`
```c
static int fgetc_ws(FILE *f);
```
Reads next character from file, skipping whitespace and comments.
- `f`: `FILE *`, File to read from
**Returns:**
`int`, Next character from stream or EOF

#### `readnum`
```c
static int readnum(FILE *f);
```
Reads a non-negative decimal number from the stream, skipping whitespace and comments, returning -1 on EOF.
- `f`: `FILE *`, Input file stream
**Returns**:
`int`, A positive number read from input stream, or -1 on EOF.

#### `readbit`
```c
static int readbit(FILE *f);
```
Read a single 0 or 1, skipping comments and whitespace.
- `f`: `FILE *`, Input file stream
**Returns**:
`int`, 0 or 1, read from stream, or -1 if EOF

### Global Variables
#### `gm_read_error`
```c
const char *gm_read_error;
```
Variable storing last read error message in case of format errors while reading greymaps.

### Functions
#### `gm_new`
```c
greymap_t *gm_new(int w, int h);
```
Creates a new greymap with given width and height, initialized to 0.
- `w`: `int`, width of the greymap
- `h`: `int`, height of the greymap
**Returns:**
`greymap_t *`, Returns a pointer to allocated greymap structure or `NULL` on failure with errno set.

#### `gm_dup`
```c
greymap_t *gm_dup(greymap_t *gm);
```
Creates a deep copy of provided greyscale image object
- `gm`: `greymap_t *`, greyscale image to duplicate
**Returns:**
`greymap_t *`, Returns a pointer to duplicate, or NULL on failure with errno set.

#### `gm_free`
```c
void gm_free(greymap_t *gm);
```
Frees memory allocated to a greyscale image structure.
- `gm`: `greymap_t *`, The greyscale image to free.

#### `gm_clear`
```c
void gm_clear(greymap_t *gm, int b);
```
Fills the entire greyscale image with the provided value
- `gm`: `greymap_t *`, Greyscale image to be cleared.
- `b`: `int`, The value to set for all pixels.

#### `gm_flip`
```c
static inline void gm_flip(greymap_t *gm);
```
Flips a greymap vertically.
- `gm`: `greymap_t *`, The greymap object.

#### `gm_resize`
```c
static inline int gm_resize(greymap_t *gm, int h);
```
Resizes a greyscale image structure to given new height, keeping data bottom or top aligned depending on dy value.
- `gm`: `greymap_t *`, The greyscale image to resize.
- `h`: `int`, The new height.
**Returns**:
`int`, returns 0 on success or 1 on error with errno set

#### `gm_read`
```c
int gm_read(FILE *f, greymap_t **gmp);
```
Reads the greyscale image from the given stream, handles PNM (PBM, PGM, PPM) and BMP files.
- `f`: `FILE *`, Input file.
- `gmp`: `greymap_t **`, pointer to where the greyscale image will be stored.
**Returns:**
`int`, 0 on success, -1 on error with errno set, -2 on bad file format, and 1 on premature end of file, -3 on empty file, or -4 if wrong magic number. If the return value is >=0, *gmp is valid.

#### `gm_writepgm`
```c
int gm_writepgm(FILE *f, greymap_t *gm, const char *comment, int raw, int mode, double gamma);
```
Outputs the greymap as Portable Grey Map, including optional comment
- `f`: `FILE *`, Output file stream.
- `gm`: `greymap_t *`, The greyscale image to be written.
- `comment`: `const char *`, Optional comment to add to file.
- `raw`: `int`, If 1 output is done using raw format, otherwise the data will be outputted using ascii format.
- `mode`: `int`, Mode of how to convert invalid data values, `GM_MODE_POSITIVE`, `GM_MODE_NEGATIVE`, `GM_MODE_ODD`, `GM_MODE_NONZERO`
- `gamma`: `double`, Gamma correction.
**Returns:**
`int`, Returns 0 on completion.

#### `gm_print`
```c
int gm_print(FILE *f, greymap_t *gm);
```
Prints a simple text representation of a greyscale image.
- `f`: `FILE *`, Output file stream.
- `gm`: `greymap_t *`, The greyscale image to output.
**Returns:**
`int`, 0 on success


# Backends (Output Formats)


# Backends (Output Formats)


## File: backend_eps.h
```
This header file defines the interface for the PostScript (EPS) backend of Potrace, including functions for initialization, output of paths, and finalization.
```
### Includes
- `potracelib.h`: Core Potrace library definitions.
- `main.h`: Main application data structure.

### Functions
#### `init_ps`
```c
int init_ps(FILE *fout);
```
Initializes a PostScript file by writing the header.
- `fout`: `FILE *`, Output file descriptor.
**Returns**:
`int`, Returns 0 on success or non-zero on error with errno set.

#### `page_ps`
```c
int page_ps(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Converts Potrace paths to a PostScript (PS) page.
- `fout`: `FILE *`, Output file descriptor.
- `plist`: `potrace_path_t *`, The linked list of paths for rendering.
- `imginfo`: `imginfo_t *`, Image related information.
**Returns**:
`int`, Returns 0 on success or non-zero on error with errno set.

#### `term_ps`
```c
int term_ps(FILE *fout);
```
Finalizes the PostScript file with a trailer and EOF mark.
- `fout`: `FILE *`, Output file descriptor.
**Returns**:
`int`, Returns 0 on success or non-zero on error with errno set.

#### `page_eps`
```c
int page_eps(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Outputs the Potrace paths as an Encapsulated PostScript document.
- `fout`: `FILE *`, The output file stream.
- `plist`: `potrace_path_t *`, The linked list of paths to output.
- `imginfo`: `imginfo_t *`, The image information, such as dimensions and transformations.
**Returns**:
`int`, returns 0 on success, and non-zero on error.


## File: backend_eps.c
```
This file implements the PostScript backend of Potrace, capable of generating both PostScript (.ps) and Encapsulated PostScript (.eps) files, with optional support for LZW and flate compression. This implementation also support different kinds of graphical debugging output.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdio.h`: Standard input/output functions.
- `stdarg.h`: Variable arguments handling.
- `string.h`: String manipulation functions.
- `math.h`: Math functions.
- `stdlib.h`: For standard memory allocation functions
- `main.h`: Main data structure
- `backend_eps.h`: Declares function prototypes specific to EPS backend.
- `flate.h`: Compression related functions declaration
- `lists.h`: Linked list structure definitions.
- `potracelib.h`: Core Potrace library definitions.
- `auxiliary.h`: Auxiliary data structure definitions

### Macros
#### `SAFE_CALLOC`
```c
#define SAFE_CALLOC(var, n, typ) \
  if ((var = (typ *)calloc(n, sizeof(typ))) == NULL) goto calloc_error
```
Safely allocates memory using calloc, and jumps to the `calloc_error` label if allocation fails.

### Global Variables
#### `eps_color`
```c
static color_t eps_color = -1;
```
A static global variable to cache the last stroke color.

#### `eps_width`
```c
static double eps_width = -1;
```
A static global variable to cache the last stroke width.

### Functions for interfacing with compression backend
#### `xship`
```c
static int (*xship)(FILE *f, int filter, const char *s, int len);
```
A static function pointer used to ship data to file output using selected compression method.

#### `xship_file`
```c
static FILE *xship_file;
```
A static file pointer to the output file.

#### `ship`
```c
static int ship(const char *fmt, ...);
```
Writes a formatted string to output using the selected compression method.
- `fmt`: `const char *`, format string to output to stream
- `...`: optional variable arguments
**Returns:**
`int`, Returns 0 upon completion.

#### `shipcom`
```c
static int shipcom(const char *fmt, ...);
```
Writes a formatted string comment (without compression) to output.
- `fmt`: `const char *`, format string to output to stream
- `...`: optional variable arguments
**Returns:**
`int`, Returns 0 upon completion.

#### `eps_callbacks`
```c
static void eps_callbacks(FILE *fout);
```
Sets up callback functions to perform appropriate type of compression (if requested).
- `fout`: `FILE *`, Output file pointer.

### Path Drawing
#### `unit`
```c
static inline point_t unit(dpoint_t p);
```
Applies coordinate quantization to the point `p`, using defined global unit.
- `p`: `dpoint_t`, Point to convert
**Returns:**
`point_t`, Quantized point

#### `eps_coords`
```c
static void eps_coords(dpoint_t p);
```
Applies coordinate quantization and ships coordinates, used for absolute coordinates.
- `p`: `dpoint_t`, Point to ship.

#### `eps_rcoords`
```c
static void eps_rcoords(dpoint_t p);
```
Applies coordinate quantization and ships coordinates, used for relative coordinates.
- `p`: `dpoint_t`, Point to ship

#### `eps_moveto`
```c
static void eps_moveto(dpoint_t p);
```
Writes a PostScript `moveto` command to output, for absolute coordinates
- `p`: `dpoint_t`, Point to move to

#### `eps_moveto_offs`
```c
static void eps_moveto_offs(dpoint_t p, double xoffs, double yoffs);
```
Writes a PostScript `moveto` command with a given offset, for absolute coordinates
- `p`: `dpoint_t`, Point to move to
- `xoffs`: `double`, Offset for the x coordinate
- `yoffs`: `double`, Offset for the y coordinate

#### `eps_lineto`
```c
static void eps_lineto(dpoint_t p);
```
Writes a PostScript `rlineto` command to output.
- `p`: `dpoint_t`, Point to draw line to.

#### `eps_curveto`
```c
static void eps_curveto(dpoint_t p1, dpoint_t p2, dpoint_t p3);
```
Writes a PostScript `rcurveto` command to output.
- `p1`: `dpoint_t`, Bezier control point 1.
- `p2`: `dpoint_t`, Bezier control point 2.
- `p3`: `dpoint_t`, Bezier end point

#### `eps_colorstring`
```c
static const char *eps_colorstring(const color_t col);
```
Returns a statically allocated color string depending on the given color code.
- `col`: `color_t`, The color to create a string representation for
**Returns:**
`const char *`, returns the color string

#### `eps_setcolor`
```c
static void eps_setcolor(const color_t col);
```
Sets the color for the EPS output, using PostScript `setrgbcolor` command.
- `col`: `color_t`, The color to be set.

#### `eps_linewidth`
```c
static void eps_linewidth(double w);
```
Sets the line width for EPS output using PostScript `setlinewidth` command.
- `w`: `double`, The line width.

### Path Conversion
#### `eps_path_long`
```c
static int eps_path_long(privcurve_t *curve);
```
Generates PostScript path data with explicit encoding of all data.
- `curve`: `privcurve_t *`, The private curve to generate Postscript path from.
**Returns:**
`int`, Returns 0 upon successful completion

#### `eps_path_short`
```c
static int eps_path_short(privcurve_t *curve);
```
Generates PostScript path data using size-optimized encoding.
- `curve`: `privcurve_t *`, The private curve to generate Postscript path from.
**Returns:**
`int`, Returns 0 upon successful completion, or 1 if calloc failed.

#### `eps_path`
```c
static int eps_path(privcurve_t *curve);
```
Dispatches the path generation to appropriate function based on if curve optimization should be used.
- `curve`: `privcurve_t *`, The private curve to generate Postscript path from.
**Returns:**
`int`, Returns 0 upon successful completion, or 1 if calloc failed during `eps_path_short`.

### Debug Output
#### `eps_jaggy`
```c
static void eps_jaggy(potrace_path_t *plist);
```
Outputs the original jaggie paths from a linked list of paths.
- `plist`: `potrace_path_t *`, List of paths.

#### `eps_polygon`
```c
static void eps_polygon(privcurve_t *curve, const color_t col);
```
Outputs the vertices of an optimal polygon.
- `curve`: `privcurve_t *`, The curve to render the optimal polygon for
- `col`: `color_t`, Color of the polygon.

#### `eps_L`
```c
static void eps_L(privcurve_t *curve, const color_t col);
```
Output the control points of Bezier curves
- `curve`: `privcurve_t *`, curve to use for drawing the control points
- `col`: `color_t`, color of the lines.

### PostScript Macros
#### `optimacros`
```c
static const char *optimacros =
  "/D{bind def}def\n"
  "/R{roll}D\n"
  "/K{copy}D\n"
  "/P{pop}D\n"
  "/p{3 2 R add 3 1 R add exch}D\n"
  "/t{dup 4 3 R mul 3 1 R mul}D\n"
  "/a{dup 1 sub neg 4 1 R t 5 2 R t p}D\n"
  "/m{2 K le{exch}if P}D\n"
  "/n{abs exch abs m}D\n"
  "/d{-1 t p n}D\n"
  "/s{[4 2 R] cvx def}D\n"
  "/g{7 K P 4 K P P d 5 1 R d 10 m m div 5 K 12 8 R 5 4 R a 9 4 R 3 2 R a 6 4 R curveto}D\n"
  "/e{4 2 R lineto lineto P P}D\n"
  "/q{3 K P n 10 m div}D\n"
  "/f{x y 7 4 R 5 1 R 4 K p /y s 7 2 R 2 K 9 7 R 7 6 R t p 2 K /x s}D\n"
  "/C{4 1 R q f 7 6 R g}D\n"
  "/V{q f e}D\n"
  "/c{3 1 R .5 f 7 6 R g}D\n"
  "/v{.5 f e}D\n"
  "/j{5 K P p /y s 3 K t 7 5 R p /x s x moveto P}D\n"
  "/i{.5 j}D\n"
  "/I{dup 6 1 R q j 3 2 R}D\n"
  "/z{closepath}D\n"
  "/b{%s z fill}D\n"
  "/w{%s z fill}D\n";
```
Defines a set of PostScript macros for size-optimized path rendering.

#### `debugmacros`
```c
static const char *debugmacros =
  "/unit { %f } def\n"
  "/box { newpath 0 0 moveto 0 1 lineto 1 1 lineto 1 0 lineto closepath } def\n"
  "/circ { newpath 0 0 1 0 360 arc closepath } def\n"
  "/dot { gsave .15 mul dup scale circ fill grestore } def\n"
  "/sq { gsave unit unit scale -.5 -.5 translate box .02 setlinewidth stroke grestore } def\n"
  "/sq1 { gsave translate sq unit .6 mul dot grestore } def\n"
  "/dot2 { gsave translate unit dot grestore } def\n"
  "/usq { gsave unit unit scale -.5 -.5 rmoveto 0 1 rlineto 1 0 rlineto 0 -1 rlineto closepath .02 setlinewidth stroke grestore } def\n"
  "/dot1 { gsave translate unit .3 mul dup scale circ fill grestore } def\n"
  "/times { /Times-Roman findfont unit .3 mul scalefont setfont } def\n"
  "/times1 { /Times-Roman findfont unit 10 mul scalefont setfont 0 0 0 setrgbcolor } def\n"
  "/times2 { /Times-Roman findfont unit 2 mul scalefont setfont 0 0 0 setrgbcolor } def\n";
```
Defines a set of PostScript macros for debug output.

### Backend Functions
#### `render0`
```c
static int render0(potrace_path_t *plist);
```
Renders paths using normal output mode (black fill on transparent).
- `plist`: `potrace_path_t *`, List of paths that represents object of interest.
**Returns**:
`int`, Returns 0 on success, non-zero value on failure with errno set

#### `render0_opaque`
```c
static int render0_opaque(potrace_path_t *plist);
```
Renders paths with opaque filling by alternating between a foreground color and a background color.
- `plist`: `potrace_path_t *`, List of paths that represents object of interest.
**Returns**:
`int`, Returns 0 on success, non-zero value on failure with errno set

#### `render1`
```c
static int render1(potrace_path_t *plist);
```
Renders paths with debug information, showing jaggies and polygons for debugging, for `debug = 1` case.
- `plist`: `potrace_path_t *`, List of paths that represents object of interest.
**Returns**:
`int`, Returns 0 on success, non-zero value on failure with errno set

#### `render2`
```c
static int render2(potrace_path_t *plist);
```
Renders paths with debug information, showing original paths, corrected polygons, curve control point lines and other elements, for `debug = 2` or `debug=3` cases.
- `plist`: `potrace_path_t *`, List of paths that represents object of interest.
**Returns**:
`int`, Returns 0 on success, non-zero value on failure with errno set

#### `render_debug`
```c
static int render_debug(potrace_path_t *plist);
```
Renders paths with debugging info for cases other than 0,1,2 and 3.
- `plist`: `potrace_path_t *`, List of paths that represents object of interest.
**Returns**:
`int`, Returns 0 on success, non-zero value on failure with errno set

#### `eps_render`
```c
static int eps_render(potrace_path_t *plist);
```
Dispatches rendering to the correct function, based on the debug mode setting.
- `plist`: `potrace_path_t *`, List of paths that represents object of interest.
**Returns**:
`int`, Returns 0 on success, non-zero value on failure with errno set

### EPS Header and Footer
#### `eps_init`
```c
static int eps_init(imginfo_t *imginfo);
```
Initializes a Potrace EPS output by writing header information to output stream
- `imginfo`: `imginfo_t *`, The image information to create header from
**Returns:**
`int`, Returns 0 on success or 1 if failure.

#### `eps_term`
```c
static void eps_term(void);
```
Writes EPS trailer data and EOF marker.

#### `eps_pagenumber`
```c
static int eps_pagenumber;
```
A static variable to keep track of page numbers in ps documents.

#### `init_ps`
```c
int init_ps(FILE *fout);
```
Initializes the PostScript output file with headers and setup commands.
- `fout`: `FILE *`, Output file descriptor.
**Returns**:
`int`, Returns 0 on success or 1 on error with errno set.

#### `term_ps`
```c
int term_ps(FILE *fout);
```
Terminates a PostScript file by writing trailer information.
- `fout`: `FILE *`, Output file descriptor.
**Returns**:
`int`, Returns 0 on success or 1 on error with errno set.

#### `eps_pageinit_ps`
```c
static void eps_pageinit_ps(imginfo_t *imginfo);
```
Initializes a PostScript page.
- `imginfo`: `imginfo_t *`, Image information structure.

#### `eps_pageterm_ps`
```c
static void eps_pageterm_ps(void);
```
Terminates a PostScript page by writing necessary commands.

#### `page_eps`
```c
int page_eps(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Outputs Potrace paths as an Encapsulated PostScript document.
- `fout`: `FILE *`, The output file stream.
- `plist`: `potrace_path_t *`, The linked list of paths to output as EPS.
- `imginfo`: `imginfo_t *`, The image information, such as dimensions and transformations.
**Returns**:
`int`, Returns 0 on success or 1 on error with errno set.


## File: backend_pdf.h
```
This header file defines functions for the PDF backend, used for generating PDF documents with optional compression. It provides prototypes for initialization, handling individual pages, and finalization.
```
### Includes
- `potracelib.h`: Core Potrace library definitions.
- `main.h`: Main application data structure.

### Functions
#### `init_pdf`
```c
int init_pdf(FILE *fout);
```
Initializes a PDF document, writing the initial header information.
- `fout`: `FILE *`, Output file descriptor.
**Returns**:
`int`, Returns 0 on success, or 1 on error with errno set.

#### `page_pdf`
```c
int page_pdf(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Outputs a single PDF page using the given path data and image info.
- `fout`: `FILE *`, Output file descriptor.
- `plist`: `potrace_path_t *`, The linked list of paths for rendering.
- `imginfo`: `imginfo_t *`, Image related information.
**Returns**:
`int`, Returns 0 on success, or 1 on error with errno set

#### `term_pdf`
```c
int term_pdf(FILE *fout);
```
Finalizes a PDF document, writing all trailer information at the end.
- `fout`: `FILE *`, Output file descriptor.
**Returns**:
`int`, Returns 0 on success or 1 on error with errno set.

#### `page_pdf`
```c
int page_pdf(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Outputs Potrace paths as a single page PDF document.
- `fout`: `FILE *`, output file descriptor
- `plist`: `potrace_path_t *`, linked list of paths that represents object of interest.
- `imginfo`: `imginfo_t *`, image informations such as image dimensions and margins
**Returns**:
`int`, returns 0 on success, or 1 on error with errno set.

#### `page_pdfpage`
```c
int page_pdfpage(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Outputs Potrace paths as a single page in a PDF document with defined page size.
- `fout`: `FILE *`, output file descriptor
- `plist`: `potrace_path_t *`, linked list of paths that represents object of interest.
- `imginfo`: `imginfo_t *`, image informations such as image dimensions and margins
**Returns:**
`int`, Returns 0 on success or 1 on error with errno set.


## File: backend_pdf.c
```
This file implements the PDF backend for Potrace, which produces output in the Portable Document Format (.pdf). It includes functions for managing PDF structures and using flate compression.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdio.h`: For standard input/output functions.
- `stdarg.h`: For variable arguments list.
- `string.h`: For string functions.
- `math.h`: For math functions.
- `stdlib.h`: For memory allocation functions.
- `main.h`: Main application data structure.
- `backend_pdf.h`: Declarations specific to PDF backend
- `flate.h`: Declares function prototypes related to compression
- `lists.h`: Definition for list data structure.
- `potracelib.h`: Core Potrace library definitions.
- `auxiliary.h`: Auxiliary type definitions.

### Data Structures
#### `intarray_s`
```c
struct intarray_s {
  int size;
  int *data;
};
```
A growable integer array
- `size`: `int`, Size of allocated array.
- `data`: `int *`, Actual array of integers.

### Global Variables
#### `xref`
```c
static intarray_t xref;
```
A static global `intarray_t` variable that stores xref table data.

#### `nxref`
```c
static int nxref = 0;
```
Static global variable indicating the next entry for `xref`

#### `pages`
```c
static intarray_t pages;
```
A static global `intarray_t` that stores page information

#### `npages`
```c
static int npages;
```
Static global variable indicating next available page number in `pages`.

#### `streamofs`
```c
static int streamofs;
```
Static global variable for storing position of beginning of stream of content.

#### `outcount`
```c
static size_t outcount;
```
Static global variable representing current position in output file stream.

### Auxiliary Functions
#### `intarray_init`
```c
static inline void intarray_init(intarray_t *ar);
```
Initializes a growing integer array.
- `ar`: `intarray_t *`, The integer array.

#### `intarray_term`
```c
static inline void intarray_term(intarray_t *ar);
```
Frees memory used by integer array, and sets the size to 0 and data pointer to NULL.
- `ar`: `intarray_t *`, The integer array to be freed.

#### `intarray_set`
```c
static inline int intarray_set(intarray_t *ar, int n, int val);
```
Sets a value in a growing integer array.
- `ar`: `intarray_t *`, The integer array.
- `n`: `int`, Index in the array to store the value at
- `val`: `int`, Value to set in array.
**Returns**:
`int`, 0 on success, or -1 on failure with errno set.

### Functions for interfacing with compression backend
#### `xship`
```c
static int (*xship)(FILE *f, int filter, const char *s, int len);
```
Function pointer for shipping the provided data, according to specified compression method.

#### `xship_file`
```c
static FILE *xship_file;
```
File pointer for the output file stream.

#### `ship`
```c
static int ship(const char *fmt, ...);
```
Writes a formatted string to the output stream, using a configured compression method.
- `fmt`: `const char *`, format string to output to stream.
- `...`: variable arguments
**Returns**:
`int`, Returns 0 upon completion.

#### `shipclear`
```c
static int shipclear(const char *fmt, ...);
```
Writes a formatted string to the output stream, without compression.
- `fmt`: `const char *`, format string to output to stream.
- `...`: variable arguments
**Returns**:
`int`, Returns 0 upon completion

#### `pdf_callbacks`
```c
static void pdf_callbacks(FILE *fout);
```
Configures the callback function (xship) based on whether compression is enabled.
- `fout`: `FILE *`, The output file stream.

### PDF path-drawing auxiliary functions
#### `unit`
```c
static inline point_t unit(dpoint_t p);
```
Applies coordinate quantization to the given point, using global unit definition.
- `p`: `dpoint_t`, The point to quantize.
**Returns:**
`point_t`, The quantized point.

#### `pdf_coords`
```c
static void pdf_coords(dpoint_t p);
```
Applies coordinate quantization and ship the coordinate as part of the path construction
- `p`: `dpoint_t`, The coordinate to format and output.

#### `pdf_moveto`
```c
static void pdf_moveto(dpoint_t p);
```
Writes a move-to command (in PDF syntax) to output, using configured transformation.
- `p`: `dpoint_t`, The coordinates to move to.

#### `pdf_lineto`
```c
static void pdf_lineto(dpoint_t p);
```
Writes a line-to command (in PDF syntax) to output, using configured transformation.
- `p`: `dpoint_t`, The coordinates to draw to.

#### `pdf_curveto`
```c
static void pdf_curveto(dpoint_t p1, dpoint_t p2, dpoint_t p3);
```
Writes a curve-to command (in PDF syntax) to the output, using configured transformation.
- `p1`: `dpoint_t`, The first bezier curve control point.
- `p2`: `dpoint_t`, The second bezier curve control point.
- `p3`: `dpoint_t`, The destination point.

#### `pdf_colorstring`
```c
static const char *pdf_colorstring(const color_t col);
```
Returns a statically allocated string representation of a color for PDF path drawing.
- `col`: `color_t`, The color (rgb).
**Returns:**
`const char *`, The statically allocated string for the color representation.

#### `pdf_setcolor`
```c
static void pdf_setcolor(const color_t col);
```
Sets the current stroke color, and emits the appropriate code only if the color has changed.
- `col`: `color_t`, The color (rgb) to be set.

#### `pdf_path`
```c
static int pdf_path(potrace_curve_t *curve);
```
Generates PDF path commands from the given Potrace curve.
- `curve`: `potrace_curve_t *`, The curve to render.
**Returns:**
`int`, 0 upon completion.

### Backends
#### `render0`
```c
static int render0(potrace_path_t *plist);
```
Renders the path list for transparent rendering.
- `plist`: `potrace_path_t *`, linked list of paths that represents object of interest.
**Returns:**
`int`, returns 0 on success or error with errno set

#### `render0_opaque`
```c
static int render0_opaque(potrace_path_t *plist);
```
Renders the path list for opaque rendering.
- `plist`: `potrace_path_t *`, linked list of paths that represents object of interest.
**Returns:**
`int`, returns 0 on success or error with errno set

#### `pdf_render`
```c
static int pdf_render(potrace_path_t *plist);
```
Chooses and runs the appropriate rendering function, based on `opaque` setting.
- `plist`: `potrace_path_t *`, linked list of paths that represents object of interest.
**Returns:**
`int`, returns 0 on success or error with errno set

### PDF Header and Footer Functions

#### `init_pdf`
```c
int init_pdf(FILE *fout);
```
Initializes a PDF file and performs necessary header creation.
- `fout`: `FILE *`, The output file stream.
**Returns**:
`int`, Returns 0 on success or 1 on error with errno set

#### `term_pdf`
```c
int term_pdf(FILE *fout);
```
Terminates a PDF document by writing trailer information and freeing resources.
- `fout`: `FILE *`, The output file stream.
**Returns:**
`int`, Returns 0 on success or 1 on error with errno set.

#### `pdf_pageinit`
```c
static int pdf_pageinit(imginfo_t *imginfo, int largebbox);
```
Initializes a new PDF page, and constructs the necessary page object.
- `imginfo`: `imginfo_t *`, image informations such as image dimensions and margins
- `largebbox`: `int`, determines whether bounding box should be pagesize.
**Returns**:
`int`, 0 on success and 1 on error with errno set

#### `pdf_pageterm`
```c
static int pdf_pageterm(void);
```
Finalizes a PDF page by closing the content stream.
**Returns**:
`int`, 0 on success and 1 on error with errno set

#### `page_pdf`
```c
int page_pdf(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Outputs Potrace paths as a single page PDF document.
- `fout`: `FILE *`, output file descriptor
- `plist`: `potrace_path_t *`, linked list of paths that represents object of interest.
- `imginfo`: `imginfo_t *`, image informations such as image dimensions and margins
**Returns**:
`int`, returns 0 on success or 1 on error with errno set.

#### `page_pdfpage`
```c
int page_pdfpage(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Outputs Potrace paths as a single page in a PDF document with defined page size.
- `fout`: `FILE *`, output file descriptor
- `plist`: `potrace_path_t *`, linked list of paths that represents object of interest.
- `imginfo`: `imginfo_t *`, image informations such as image dimensions and margins.
**Returns:**
`int`, Returns 0 on success or 1 on error with errno set


## File: backend_pgm.h
```
This header file defines functions specific to the PGM backend, which renders traced paths into grayscale PGM (Portable Graymap) images.
```
### Includes
- `stdio.h`: Standard input/output functions.
- `potracelib.h`: Core Potrace library definitions.
- `main.h`: Main application data structure.

### Functions
#### `page_pgm`
```c
int page_pgm(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Generates a PGM image from the provided paths.
- `fout`: `FILE *`, output file descriptor.
- `plist`: `potrace_path_t *`, List of paths to convert to a greyscale image
- `imginfo`: `imginfo_t *`, Data about the source image, such as dimensions and margins.
**Returns:**
`int`, 0 on success or a non-zero number on error with errno set.


## File: backend_pgm.c
```
This file implements the PGM backend for Potrace, which renders Bezier curves and outputs the result as a greymap file (.pgm).
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `math.h`: Math functions
- `backend_pgm.h`: Declares function prototypes specific to PGM backend.
- `potracelib.h`: Core Potrace library definitions.
- `lists.h`: Definition for list data structure.
- `greymap.h`: Definition for greymap structure.
- `render.h`: Rendering-related data structures and functions.
- `main.h`: Main application data structure.
- `auxiliary.h`: Auxiliary type definitions.
- `trans.h`: Transformation definitions.

### Functions

#### `pgm_path`
```c
static void pgm_path(potrace_curve_t *curve, trans_t t, render_t *rm);
```
Renders a single path as a greyscale drawing using render_t.
- `curve`: `potrace_curve_t *`, The curve structure containing path data.
- `t`: `trans_t`, The coordinate transformation settings.
- `rm`: `render_t *`, The rendering state.

#### `page_pgm`
```c
int page_pgm(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Main function to write the PGM file to `fout`.
- `fout`: `FILE *`, output file descriptor.
- `plist`: `potrace_path_t *`, linked list of paths that represents object of interest.
- `imginfo`: `imginfo_t *`, image informations such as image dimensions and margins.

**Returns:**
`int` returns 0 on success, or a non-zero number on error


## File: backend_svg.h
```
This header file declares functions specific to the SVG backend, which generates output in Scalable Vector Graphics (.svg) format.
```
### Includes
- `potracelib.h`: Core Potrace library definitions.
- `main.h`: Main application data structure.

### Functions
#### `page_svg`
```c
int page_svg(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Generates the SVG file
- `fout`: `FILE *`, The output file stream.
- `plist`: `potrace_path_t *`,  The list of paths to output as SVG.
- `imginfo`: `imginfo_t *`, Image information like dimensions, transformations.

#### `page_gimp`
```c
int page_gimp(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Generates the Gimppath output, a variation of SVG for use in the Gimp.
- `fout`: `FILE *`, The output file stream.
- `plist`: `potrace_path_t *`, The list of paths to output as Gimppath SVG.
- `imginfo`: `imginfo_t *`, Image information like dimensions, transformations.


## File: backend_svg.c
```
This file implements the SVG backend for Potrace, responsible for generating Scalable Vector Graphics (.svg) files from traced bitmaps.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdio.h`: For standard input/output functions.
- `stdarg.h`: For variable arguments list.
- `string.h`: For string functions.
- `math.h`: For math functions.
- `potracelib.h`: Core Potrace library definitions.
- `curve.h`: Definitions for curve data structure.
- `main.h`: Main application data structure.
- `backend_svg.h`: Header file containing function declarations for the SVG backend.
- `lists.h`: Definition for list data structure.
- `auxiliary.h`: Auxiliary type definitions.

### Auxiliary Functions
#### `bezier`
```c
static inline double bezier(double t, double x0, double x1, double x2, double x3);
```
Calculates a point on a 1-dimensional Bezier segment for curve approximation.
- `t`: `double`, The parameter at which the curve is evaluated.
- `x0`: `double`, The start point.
- `x1`: `double`, The first control point.
- `x2`: `double`, The second control point.
- `x3`: `double`, The end point.
**Returns:**
`double`, the interpolated point along the bezier curve.

#### `round_to_unit`
```c
static char *round_to_unit(double x);
```
Formats the given double to a string, using a pre-determined format.
   Returns one of a small number of statically allocated strings.
- `x`: `double`, The value to format.
**Returns:**
`char *`, One of a small number of statically allocated strings, containing the formatted representation of the input.

#### `set_format`
```c
static void set_format(trans_t tr);
```
Selects a print format for floating point numbers, appropriate for the given scaling and info.unit. Note: the format must be so that the resulting number fits into a buffer of size 100.
- `tr`: `trans_t`, The transformation data, used to determine the scale factor to create the format string

### Path-drawing auxiliary functions
#### `shiptoken`
```c
static void shiptoken(FILE *fout, const char *token);
```
Writes a token to the file, updating the column and newline status.
- `fout`: `FILE *`, the output file stream.
- `token`: `const char *`, the string token to be output
**Returns:**
`void`, this function does not return any value
#### Local variables in shiptoken
- `c`: `int`, Size of the string to write
- `column`: `static int`, position of last output in row, tracked for newline purposes.
- `newline`: `static int`, A flag to indicate if output should start at the next row or not

#### `ship`
```c
static void ship(FILE *fout, const char *fmt, ...);
```
Writes a formatted string to a file, breaking long lines using shiptoken.
- `fout`: `FILE *`, The output file stream.
- `fmt`: `const char *`, The format string to use.
- `...`: Variable arguments corresponding to format string.
**Returns:**
`void`, this function does not return any value
#### Local variables in `ship`
- `buf`: `static char[]`, Statically allocated character array for creating format string
- `p`, `q`:  `char *`, temporary pointers for string parsing

#### `svg_moveto`
```c
static void svg_moveto(FILE *fout, dpoint_t p);
```
Writes a SVG "moveto" command, moving the current cursor, to the specified location.
- `fout`: `FILE *`, The output file stream.
- `p`: `dpoint_t`, The coordinates of the move operation.
**Returns:**
`void`, this function does not return any value

#### `svg_rmoveto`
```c
static void svg_rmoveto(FILE *fout, dpoint_t p);
```
Writes a SVG relative "moveto" command, moving the current cursor, by a specified offset.
- `fout`: `FILE *`, The output file stream.
- `p`: `dpoint_t`, The coordinates of the move operation relative to the current location
**Returns:**
`void`, this function does not return any value

#### `svg_lineto`
```c
static void svg_lineto(FILE *fout, dpoint_t p);
```
Writes a SVG relative "lineto" command from the current point to the specified point.
- `fout`: `FILE *`, The output file stream.
- `p`: `dpoint_t`, The coordinates of the draw to operation relative to the current position
**Returns:**
`void`, this function does not return any value

#### `svg_curveto`
```c
static void svg_curveto(FILE *fout, dpoint_t p1, dpoint_t p2, dpoint_t p3);
```
Writes a relative SVG "curveto" command, drawing a Bezier curve with control points.
- `fout`: `FILE *`, The output file stream.
- `p1`: `dpoint_t`, The first Bezier control point, relative to current location
- `p2`: `dpoint_t`, The second Bezier control point, relative to current location
- `p3`: `dpoint_t`, The end point of the Bezier curve, relative to current location.
**Returns:**
`void`, this function does not return any value

### Path Conversion
#### `svg_path`
```c
static int svg_path(FILE *fout, potrace_curve_t *curve, int abs);
```
Converts a `potrace_curve_t` object to an SVG path element with absolute or relative positions.
- `fout`: `FILE *`, output file descriptor.
- `curve`: `potrace_curve_t *`, The curve to be output
- `abs`: `int`, If set to 1 the path starts at absolute position, otherwise a relative move command is issued.
**Returns:**
`int`, 0 if path was successfully written

#### `svg_jaggy_path`
```c
static int svg_jaggy_path(FILE *fout, point_t *pt, int n, int abs);
```
Outputs a jagged path, for debugging purposes only, where each node is connected by a straight line.
- `fout`: `FILE *`, output file descriptor.
- `pt`: `point_t *`, The list of points forming the path.
- `n`: `int`, Number of points in the path
- `abs`: `int`, If set to 1 the path starts at absolute position, otherwise a relative move command is issued and the path is traversed in the reverse direction.
**Returns:**
`int`, returns 0 upon successful completion

#### `write_paths_opaque`
```c
static void write_paths_opaque(FILE *fout, potrace_path_t *tree);
```
Writes paths with opaque filling to the file in the form of SVG tags.
- `fout`: `FILE *`, The output file stream.
- `tree`: `potrace_path_t *`, A linked list of paths.

#### `write_paths_transparent_rec`
```c
static void write_paths_transparent_rec(FILE *fout, potrace_path_t *tree);
```
Recursively writes paths to a file as an SVG tree structure, using relative moves, transparent rendering, and without fill.
- `fout`: `FILE *`, The output file stream.
- `tree`: `potrace_path_t *`, The linked list of paths.

#### `write_paths_transparent`
```c
static void write_paths_transparent(FILE *fout, potrace_path_t *tree);
```
Writes paths in transparent mode to output stream.
- `fout`: `FILE *`, Output file stream.
- `tree`: `potrace_path_t *`, path structure.

### Backend
#### `page_svg`
```c
int page_svg(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Main function for producing SVG output, by producing XML header, viewport, metadata and paths.
- `fout`: `FILE *`, The output file stream.
- `plist`: `potrace_path_t *`, The list of paths to convert.
- `imginfo`: `imginfo_t *`, The image information, such as dimensions and transformation.
**Returns:**
`int`, Always returns 0.

#### `page_gimp`
```c
int page_gimp(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Main function for producing a Gimp compatible SVG path output, by disabling `opaque` mode and setting grouping to `flat`, and calling `page_svg` method.
- `fout`: `FILE *`, The output file stream.
- `plist`: `potrace_path_t *`, The list of paths to convert.
- `imginfo`: `imginfo_t *`, The image information, such as dimensions and transformation.
**Returns:**
`int`, Returns the result of `page_svg` method.


## File: backend_xfig.h
```
This header file defines the interface for the XFig backend of Potrace, providing a function prototype to output vector data in XFig format (.fig).
```
### Includes
- `potracelib.h`: Core Potrace library definitions.
- `main.h`: Main application data structure.

### Functions
#### `page_xfig`
```c
int page_xfig(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Generates the XFig output for the given paths.
- `fout`: `FILE *`, The output file stream.
- `plist`: `potrace_path_t *`, List of paths to be output as xfig.
- `imginfo`: `imginfo_t *`, Image information like dimensions, transformations.
**Returns:**
`int`, 0 on success or 1 on error with errno set.


## File: backend_xfig.c
```
This file implements the xfig backend for Potrace, which generates vector graphics in the format readable by the xfig drawing program (.fig).
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdio.h`: For standard input/output functions.
- `stdarg.h`: For variable arguments list.
- `string.h`: For string functions.
- `math.h`: For math functions.
- `main.h`: Main application data structure.
- `backend_xfig.h`: Declarations specific to the XFig backend
- `potracelib.h`: Core Potrace library definitions.
- `lists.h`: Definition for list data structure.
- `auxiliary.h`: Auxiliary type definitions.
- `trans.h`: Transformation definitions.

### Structures
#### `pageformat_s`
```c
struct pageformat_s {
  const char *name;
  int w, h;
};
```
Represents a page format with its dimensions.
- `name`: `const char *`, The name of page format
- `w`: `int`, Width in PostScript points.
- `h`: `int`, Height in PostScript points.

### Auxiliary Functions
#### `unit`
```c
static inline point_t unit(dpoint_t p);
```
Applies coordinate quantization to a given point by rounding it to nearest integers
- `p`: `dpoint_t`, Point to quantize
**Returns:**
`point_t`, The quantized point with long integer coordinates.

#### `xfig_point`
```c
static void xfig_point(FILE *fout, dpoint_t p, trans_t t);
```
Outputs a point to the given file with transformation applied.
- `fout`: `FILE *`, The output file stream.
- `p`: `dpoint_t`, Point to be converted.
- `t`: `trans_t`, Transformation data.

### Path Conversion
#### `npoints`
```c
static int npoints(potrace_curve_t *curve, int m);
```
Calculates number of control points that are in a path.
- `curve`: `potrace_curve_t *`,  Curve object to check control points of
- `m`: `int`, Length of curve data.
**Returns:**
`int`, Number of control points.

#### `xfig_path`
```c
static void xfig_path(FILE *fout, potrace_curve_t *curve, trans_t t, int sign, int depth);
```
Converts a single Potrace curve into XFig format output.
- `fout`: `FILE *`, Output file stream.
- `curve`: `potrace_curve_t *`, Curve object to convert.
- `t`: `trans_t`, Transformation data
- `sign`: `int`, A number that represents if curve is positive or negative.
- `depth`: `int`, Depth in the tree structure

#### `xfig_write_paths`
```c
static void xfig_write_paths(FILE *fout, potrace_path_t *plist, trans_t t, int depth);
```
Recursively writes a tree of paths to an XFig output file.
- `fout`: `FILE *`, Output file stream
- `plist`: `potrace_path_t *`, the tree of paths to be converted.
- `t`: `trans_t`, transformation to apply
- `depth`: `int`, a depth limiter value for drawing paths

#### `xfig_get_depth`
```c
static int xfig_get_depth(potrace_path_t *plist);
```
Calculates the depth of a path tree.
- `plist`: `potrace_path_t *`, Start of path list.
**Returns:**
`int`, depth of path

### Backend
#### `page_xfig`
```c
int page_xfig(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Main interface to output a single page of paths in xfig format.
- `fout`: `FILE *`, Output file stream.
- `plist`: `potrace_path_t *`, List of paths to be converted to fig output
- `imginfo`: `imginfo_t *`, image informations such as image dimensions and margins.
**Returns:**
`int`, Returns 0 on success, or non-zero on failure with errno set


## File: backend_dxf.h
```
This header file defines the function prototype for the DXF backend, used to write traced data in Drawing Interchange Format for CAD applications.
```
### Includes
- `potracelib.h`: Core Potrace library definitions.
- `main.h`: Main application data structure.

### Functions
#### `page_dxf`
```c
int page_dxf(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Generates the DXF output.
- `fout`: `FILE *`, The file stream to write to.
- `plist`: `potrace_path_t *`, The list of paths to convert.
- `imginfo`: `imginfo_t *`, The image information, such as dimensions and transformation.


## File: backend_dxf.c
```
This file implements the DXF backend for Potrace, which outputs tracing results in AutoCAD's DXF format (Drawing Interchange Format), commonly used for CAD vector drawings.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdio.h`: For standard input/output functions.
- `stdarg.h`: For variable arguments list.
- `string.h`: For string functions.
- `math.h`: For math functions.
- `main.h`: Main application data structure.
- `backend_dxf.h`:  Declarations specific to DXF backend.
- `potracelib.h`: Core Potrace library definitions.
- `lists.h`: Definition for list data structure.
- `auxiliary.h`: Auxiliary type definitions.
- `trans.h`: Transformation definitions.

### Auxiliary Functions
#### `sub`
```c
static dpoint_t sub(dpoint_t v, dpoint_t w);
```
Subtracts vector `w` from vector `v`.
- `v`: `dpoint_t`, The first vector.
- `w`: `dpoint_t`, The second vector to subtract.
**Returns**:
`dpoint_t`, Result of the subtraction.

#### `iprod`
```c
static double iprod(dpoint_t v, dpoint_t w);
```
Calculates the inner product of two vectors.
- `v`: `dpoint_t`, The first vector.
- `w`: `dpoint_t`, The second vector.
**Returns:**
`double`, The calculated inner product.

#### `xprod`
```c
static double xprod(dpoint_t v, dpoint_t w);
```
Calculates the cross product of two vectors.
- `v`: `dpoint_t`, The first vector.
- `w`: `dpoint_t`, The second vector.
**Returns:**
`double`, The calculated cross product.

#### `bulge`
```c
static double bulge(dpoint_t v, dpoint_t w);
```
Calculates the bulge factor based on two vectors v and w. The bulge factor corresponds to an angle between two vectors used to draw an arc.
- `v`: `dpoint_t`, The first vector.
- `w`: `dpoint_t`, The second vector.
**Returns**:
`double`, The calculated bulge, or 0.0 if the cross product of the vectors is 0.0.

### DXF Output Synthesis
#### `ship`
```c
static int ship(FILE *fout, int gc, const char *fmt, ...);
```
Writes a DXF group code and a value in the given format to a file.
- `fout`: `FILE *`, The output file pointer.
- `gc`: `int`, DXF group code.
- `fmt`: `const char *`, Format string (like printf).
- `...`: variable arguments
**Returns**:
`int`, The number of characters written, or a negative value if there was an error.

#### `ship_polyline`
```c
static void ship_polyline(FILE *fout, const char *layer, int closed);
```
Writes the header of a DXF polyline to a file.
- `fout`: `FILE *`, Output file pointer.
- `layer`: `const char *`, Name of the layer.
- `closed`: `int`, Boolean value indicating if the polyline is closed (1 if it is)

#### `ship_vertex`
```c
static void ship_vertex(FILE *fout, const char *layer, dpoint_t v, double bulge);
```
Writes a DXF vertex to a file.
- `fout`: `FILE *`, Output file pointer.
- `layer`: `const char *`, Name of the layer.
- `v`: `dpoint_t`, Coordinates of the vertex.
- `bulge`: `double`, Bulge factor of this point

#### `ship_seqend`
```c
static void ship_seqend(FILE *fout);
```
Writes the end-of-polyline sequence to a file.
- `fout`: `FILE *`, Output file pointer.

#### `ship_comment`
```c
static void ship_comment(FILE *fout, const char *comment);
```
Writes a DXF comment to a file.
- `fout`: `FILE *`, Output file pointer.
- `comment`: `const char *`, The comment to be written.

#### `ship_section`
```c
static void ship_section(FILE *fout, const char *name);
```
Writes the beginning of a DXF section to a file.
- `fout`: `FILE *`, Output file pointer.
- `name`: `const char *`, Name of the section.

#### `ship_endsec`
```c
static void ship_endsec(FILE *fout);
```
Writes the end of a DXF section to a file.
- `fout`: `FILE *`, Output file pointer.

#### `ship_eof`
```c
static void ship_eof(FILE *fout);
```
Writes the end-of-file marker to a DXF file.
- `fout`: `FILE *`, Output file pointer.

### Simulated Quadratic and Bezier Curves
#### `pseudo_quad`
```c
static void pseudo_quad(FILE *fout, const char *layer, dpoint_t A, dpoint_t C, dpoint_t B);
```
Simulates a quadratic Bezier curve using two circular arcs.
- `fout`: `FILE *`, Output file pointer.
- `layer`: `const char *`, Name of the layer.
- `A`: `dpoint_t`, Start point.
- `C`: `dpoint_t`, Control point.
- `B`: `dpoint_t`, End point.

#### `pseudo_bezier`
```c
static void pseudo_bezier(FILE *fout, const char *layer, dpoint_t A, dpoint_t B, dpoint_t C, dpoint_t D);
```
Simulates a cubic Bezier curve using pseudo-quadratic curves.
- `fout`: `FILE *`, Output file pointer.
- `layer`: `const char *`, Name of the layer.
- `A`: `dpoint_t`, Start point of the curve.
- `B`: `dpoint_t`, First control point of the curve.
- `C`: `dpoint_t`, Second control point of the curve.
- `D`: `dpoint_t`, End point of the curve.

### Path Conversion
#### `dxf_path`
```c
static int dxf_path(FILE *fout, const char *layer, potrace_curve_t *curve, trans_t t);
```
Converts a single Potrace curve into a DXF polyline representation.
- `fout`: `FILE *`, Output file pointer.
- `layer`: `const char *`, Name of the layer.
- `curve`: `potrace_curve_t *`, The curve object to convert.
- `t`: `trans_t`, The transformation parameters.
**Returns**:
`int`, 0 on success or 1 on error with errno set.

### Backend
#### `page_dxf`
```c
int page_dxf(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Generates the DXF output to a specified file.
- `fout`: `FILE *`, Output file descriptor.
- `plist`: `potrace_path_t *`, List of paths that represents object of interest.
- `imginfo`: `imginfo_t *`, image informations such as image dimensions and margins.
**Returns**:
`int`, 0 on success or 1 on error with errno set


## File: backend_geojson.h
```
This header file declares functions specific to the GeoJSON backend, which outputs traced data as GeoJSON format.
```
### Includes
- `potracelib.h`: Core Potrace library definitions.
- `main.h`: Main application data structure.

### Functions
#### `page_geojson`
```c
int page_geojson(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Generates the GeoJSON output to the specified file.
- `fout`: `FILE *`, The file stream to write to.
- `plist`: `potrace_path_t *`, The list of paths to convert.
- `imginfo`: `imginfo_t *`, The image information, such as dimensions and transformation.


## File: backend_geojson.c
```
This file implements the GeoJSON backend of Potrace, which outputs traced paths as GeoJSON features.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdio.h`: For standard input/output functions.
- `stdarg.h`: For variable arguments list.
- `string.h`: For string functions.
- `math.h`: For math functions.
- `potracelib.h`: Core Potrace library definitions.
- `curve.h`: Definitions for curve data structure.
- `main.h`: Main application data structure.
- `backend_geojson.h`: Declares function prototypes specific to the GeoJSON backend.
- `lists.h`: Definition for list data structure.
- `auxiliary.h`: Auxiliary type definitions.

### Auxiliary Functions
#### `bezier`
```c
static inline double bezier(double t, double x0, double x1, double x2, double x3);
```
Calculates a point on a 1-dimensional Bezier segment for curve approximation.
- `t`: `double`, The parameter at which the curve is evaluated.
- `x0`: `double`, The starting point.
- `x1`: `double`, The first control point.
- `x2`: `double`, The second control point.
- `x3`: `double`, The ending point.
**Returns**:
`double`, The coordinate of the Bezier curve at the parameter `t`.

#### `round_to_unit`
```c
static char *round_to_unit(double x);
```
Formats the given double to a string with the current format specification. Returns one of a small number of statically allocated strings.
- `x`: `double`, The value to format.
**Returns:**
`char *`, The formatted string, returned from a small number of statically allocated strings.

#### `set_format`
```c
static void set_format(trans_t tr);
```
Selects and sets the appropriate format for printing floating point numbers in JSON output.
- `tr`: `trans_t`, Transformation parameters for extracting scaling factors

### Path-drawing Auxiliary Functions
#### `geojson_moveto`
```c
static void geojson_moveto(FILE *fout, dpoint_t p, trans_t tr);
```
Outputs a "moveTo" command to the given file for an SVG output.
- `fout`: `FILE *`, The output file stream.
- `p`: `dpoint_t`, The target coordinates.
- `tr`: `trans_t`, The transformation to apply.
**Returns:**
`void`, this function does not return any value

#### `geojson_lineto`
```c
static void geojson_lineto(FILE *fout, dpoint_t p, trans_t tr);
```
Outputs a "lineTo" command to the given file for an SVG output.
- `fout`: `FILE *`, The output file stream.
- `p`: `dpoint_t`, The target coordinates.
- `tr`: `trans_t`, The transformation to apply.
**Returns:**
`void`, this function does not return any value

#### `geojson_curveto`
```c
static void geojson_curveto(FILE *fout, dpoint_t p1, dpoint_t p2, dpoint_t p3, trans_t tr);
```
Simulates a curve-to command, approximating a Bezier curve with short lines, for geojson output.
- `fout`: `FILE *`, The output file stream.
- `p1`: `dpoint_t`, Coordinates of first control point of Bezier curve.
- `p2`: `dpoint_t`, Coordinates of second control point of Bezier curve.
- `p3`: `dpoint_t`, End point of Bezier curve.
- `tr`: `trans_t`, The transformation to apply.
**Returns:**
`void`, this function does not return any value

### Path Conversion
#### `geojson_path`
```c
static int geojson_path(FILE *fout, potrace_curve_t *curve, trans_t tr);
```
Converts a `potrace_curve_t` object into a GeoJSON polygon coordinate array format.
- `fout`: `FILE *`, The output file stream.
- `curve`: `potrace_curve_t *`, The curve object to convert
- `tr`: `trans_t`, The coordinate transformation settings.
**Returns:**
`int` 0 on success

#### `write_polygons`
```c
static void write_polygons(FILE *fout, potrace_path_t *tree, trans_t tr, int first);
```
Recursively writes a tree of `potrace_path_t` into a GeoJSON structure
- `fout`: `FILE *`, Output file stream
- `tree`: `potrace_path_t *`, List of path items representing a tree
- `tr`: `trans_t`, Transformation to apply to points
- `first`: `int`, Whether it is first path (no leading comma)

### Backend
#### `page_geojson`
```c
int page_geojson(FILE *fout, potrace_path_t *plist, imginfo_t *imginfo);
```
Produces GeoJSON output for the given path data.
- `fout`: `FILE *`, The output file stream.
- `plist`: `potrace_path_t *`, The linked list of paths to output as GeoJSON.
- `imginfo`: `imginfo_t *`, The image information, such as dimensions and transformations.
**Returns:**
`int`, 0 on success, 1 if failed.


# Utilities & Demos


## File: mkbitmap.c
```
This file contains the implementation of `mkbitmap`, a standalone program for converting greymaps to bitmaps, with optional enhancements such as highpass/lowpass filtering, scaling, and inversion.
```

### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdio.h`: For standard input/output functions.
- `errno.h`: For error number definitions.
- `string.h`: For string functions
- `stdlib.h`: For standard memory allocation functions.
- `math.h`: For math functions.
- `getopt.h`: For command-line option parsing
- `greymap.h`: Declares function prototypes specific to greymap.
- `bitmap_io.h`: Declares function prototypes specific to bitmap I/O.
- `platform.h`: Platform-specific functionality definition.

### Macros
#### `SAFE_CALLOC`
```c
#define SAFE_CALLOC(var, n, typ) \
  if ((var = (typ *)calloc(n, sizeof(typ))) == NULL) goto calloc_error
```
Safely allocates memory using calloc, jumping to `calloc_error` label on allocation failure

### Structures
#### `info_s`
```c
struct info_s {
  char *outfile;      /* output file */
  char **infiles;     /* input files */
  int infilecount;    /* how many input files? */
  int invert;         /* invert input? */
  int highpass;       /* use highpass filter? */
  double lambda;      /* highpass filter radius */
  int lowpass;        /* use lowpass filter? */
  double lambda1;     /* lowpass filter radius */
  int scale;          /* scaling factor */
  int linear;         /* linear scaling? */
  int bilevel;        /* convert to bilevel? */
  double level;       /* cutoff grey level */
  const char *outext; /* default output file extension */
};
```
Holds command-line options and settings for processing bitmap images.
- `outfile`: `char *`, Output filename
- `infiles`: `char **`, Array of input filenames
- `infilecount`: `int`, Number of input files
- `invert`: `int`, Invert input flag
- `highpass`: `int`, Highpass filter flag
- `lambda`: `double`, Highpass filter radius
- `lowpass`: `int`, Lowpass filter flag
- `lambda1`: `double`, Lowpass filter radius
- `scale`: `int`, Scaling factor
- `linear`: `int`, Linear interpolation flag
- `bilevel`: `int`, Bilevel conversion flag
- `level`: `double`, Threshold for bilevel conversion
- `outext`: `const char *`, Output file extension

### Global Variables
#### `info`
```c
static info_t info;
```
Static global variable used to store parsed command-line arguments

### Functions
#### `lowpass`
```c
static void lowpass(greymap_t *gm, double lambda);
```
Applies a lowpass filter (gaussian blur) to the greymap image.
- `gm`: `greymap_t *`, The greymap to be processed.
- `lambda`: `double`, Standard deviation of the kernel/approximate filter radius

#### `highpass`
```c
static int highpass(greymap_t *gm, double lambda);
```
Applies a highpass filter to a greymap to enhance edges.
- `gm`: `greymap_t *`, The greymap to be processed.
- `lambda`: `double`, Filter radius.
**Returns**:
`int`, 0 on success and 1 on failure (with errno set).

#### `threshold`
```c
static potrace_bitmap_t *threshold(greymap_t *gm, double c);
```
Converts a greymap to a bitmap using a given threshold.
- `gm`: `greymap_t *`, The source greymap.
- `c`: `double`, The threshold (0 for black, 1 for white).
**Returns**:
`potrace_bitmap_t *`, The converted bitmap, or NULL on error with errno set.

#### `interpolate_linear`
```c
static void *interpolate_linear(greymap_t *gm, int s, int bilevel, double c);
```
Scales a greymap using linear interpolation, resulting in bitmap if `bilevel` is true, otherwise a greyscale image.
- `gm`: `greymap_t *`, The greymap to be scaled.
- `s`: `int`, Scaling factor.
- `bilevel`: `int`, Flag to convert to bitmap if set to 1.
- `c`: `double`, Threshold value for bilevel conversion.
**Returns**:
`void *`, Pointer to the scaled greymap or bitmap, or NULL on error with errno set.

#### `interpolate_cubic`
```c
static void *interpolate_cubic(greymap_t *gm, int s, int bilevel, double c);
```
Scales a greymap using cubic interpolation, resulting in bitmap if `bilevel` is true, otherwise a greyscale image.
- `gm`: `greymap_t *`, The greymap to be scaled.
- `s`: `int`, Scaling factor.
- `bilevel`: `int`, Flag to convert to bitmap if set to 1.
- `c`: `double`, Threshold value for bilevel conversion.
**Returns**:
`void *`, Pointer to the scaled greymap or bitmap, or NULL on error with errno set.

#### `process_file`
```c
static void process_file(FILE *fin, FILE *fout, const char *infile, const char *outfile);
```
Processes a single file containing one or more images, transforming them and writing the result to the output.
- `fin`: `FILE *`, The input file descriptor.
- `fout`: `FILE *`, The output file descriptor.
- `infile`: `const char *`, Input filename
- `outfile`: `const char *`, Output filename

#### `license`
```c
static int license(FILE *f);
```
Prints the license information to the given file.
- `f`: `FILE *`, The output file descriptor
**Returns:**
`int`, Returns 0 upon completion.

#### `usage`
```c
static int usage(FILE *f);
```
Prints usage information for mkbitmap to the given file descriptor.
- `f`: `FILE *`, File descriptor to print to.
**Returns:**
`int`, Returns 0 upon completion.

#### `dopts`
```c
static void dopts(int ac, char *av[]);
```
Processes the command-line options.
- `ac`: `int`, Number of command-line arguments.
- `av`: `char **`, Array of command-line arguments.

#### `my_fopen_read`
```c
static FILE *my_fopen_read(const char *filename);
```
Opens a file for reading.
- `filename`: `const char *`, The path to the file
**Returns:**
`FILE *`, The file pointer, or stdin if filename is NULL or "-"

#### `my_fopen_write`
```c
static FILE *my_fopen_write(const char *filename);
```
Opens a file for writing.
- `filename`: `const char *`, The path to the file
**Returns:**
`FILE *`, The file pointer, or stdout if filename is NULL or "-"

#### `my_fclose`
```c
static void my_fclose(FILE *f, const char *filename);
```
Closes a file.
- `f`: `FILE *`, The file pointer to be closed
- `filename`: `const char *`, The file name - ignored if NULL or "-"

#### `make_outfilename`
```c
static char *make_outfilename(const char *infile, const char *ext);
```
Generates output filename based on input filename and extension.
- `infile`: `const char *`, The input filename.
- `ext`: `const char *`, The output extension.
**Returns:**
`char *`, The newly allocated output filename string or NULL on error.

#### `main`
```c
int main(int ac, char *av[]);
```
The entry point of the `mkbitmap` program, processing command-line options and performing bitmap conversions.
- `ac`: `int`, Number of command-line arguments.
- `av`: `char **`, Array of command-line arguments.
**Returns:**
`int`, Return status code


## File: potracelib_demo.c
```
This file contains a simple and self-contained demonstration of the potracelib API, showing how to create, fill, trace and output a bitmap, using the core functionalities.
```
### Includes
- `config.h` (conditional): Provides configuration defines.
- `stdio.h`: Standard input/output functions.
- `string.h`: For string manipulation functions.
- `errno.h`: For error number definitions.
- `stdlib.h`: For memory allocation functions.
- `potracelib.h`: Core Potrace library definitions.

### Macros
#### Bitmap Access Macros
- `BM_WORDSIZE`: The size in bytes for potrace_word
- `BM_WORDBITS`: The size in bits for potrace_word
- `BM_HIBIT`: A bitmask with only the hightest bit set in a potrace_word
- `bm_scanline`: Returns a pointer to the beginning of a scanline in the given bitmap
- `bm_index`: Returns a pointer to the potrace_word containing bit at given coordinates.
- `bm_mask`: Generates a mask to extract a single bit from a potrace_word
- `bm_range`: Checks if index is within bounds of given size
- `bm_safe`: Checks if given coordinates are within the bitmap
- `BM_USET`: Sets the specified bit without bound check
- `BM_UCLR`: Clears the specified bit without bound check
- `BM_UPUT`: Sets or clears specified bit based on provided value without bounds check
- `BM_PUT`: Sets or clears specified bit based on provided value and bounds checking

### Helper Functions
#### `bm_new`
```c
static potrace_bitmap_t *bm_new(int w, int h);
```
Creates and allocates a new bitmap structure.
- `w`: `int`, Width of bitmap
- `h`: `int`, Height of bitmap
**Returns:**
`potrace_bitmap_t *`, A pointer to new bitmap, NULL with errno on error.

#### `bm_free`
```c
static void bm_free(potrace_bitmap_t *bm);
```
Frees memory allocated for bitmap and all its data.
- `bm`: `potrace_bitmap_t *`, The bitmap to be freed.

### Main Function
#### `main`
```c
int main();
```
The main function of the demonstration program, showcasing use of the potracelib API, including creation of the bitmap, filling the bitmap, applying tracing parameters and outputting the traced curves to console as postscript data.
**Returns:**
`int`, 0 if program executed succesfully, 1 otherwise.