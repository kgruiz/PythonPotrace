# potraceArgParser.py

import argparse
import math
import sys
from typing import List, Optional

# Assume these dependencies are implemented elsewhere
# from potracelib import potrace_param_default, potrace_trace
# from bitmap_io import bm_read, bm_free
# from progress_bar import progress_bar_vt100, progress_bar_simplified

VERSION = "1.16"  # Replace with actual version if needed
POTRACE = "potrace"

HAVE_ZLIB = True  # Assume zlib is available

DEFAULT_DIM_NAME = "px"  # Assume pixels as default for this Python implementation
DEFAULT_PAPERFORMAT = "a4"
DEFAULT_PAPERWIDTH = 595
DEFAULT_PAPERHEIGHT = 842
DEFAULT_DIM = 1.0  # Default unit multiplier (e.g., 72 for points if needed)

DIM_IN = 72.0
DIM_CM = 72.0 / 2.54
DIM_MM = 72.0 / 25.4
DIM_PT = 1.0

POTRACE_TURNPOLICY_BLACK = 0
POTRACE_TURNPOLICY_WHITE = 1
POTRACE_TURNPOLICY_LEFT = 2
POTRACE_TURNPOLICY_RIGHT = 3
POTRACE_TURNPOLICY_MINORITY = 4
POTRACE_TURNPOLICY_MAJORITY = 5
POTRACE_TURNPOLICY_RANDOM = 6


class PageFormat:
    def __init__(self, name: str, w: int, h: int):
        self.name = name
        self.w = w
        self.h = h


pageFormats = [
    PageFormat("a4", 595, 842),
    PageFormat("a3", 842, 1191),
    PageFormat("a5", 421, 595),
    PageFormat("b5", 516, 729),
    PageFormat("letter", 612, 792),
    PageFormat("legal", 612, 1008),
    PageFormat("tabloid", 792, 1224),
    PageFormat("statement", 396, 612),
    PageFormat("executive", 540, 720),
    PageFormat("folio", 612, 936),
    PageFormat("quarto", 610, 780),
    PageFormat("10x14", 720, 1008),
]


class TurnPolicy:
    def __init__(self, name: str, n: int):
        self.name = name
        self.n = n


turnPolicies = [
    TurnPolicy("black", POTRACE_TURNPOLICY_BLACK),
    TurnPolicy("white", POTRACE_TURNPOLICY_WHITE),
    TurnPolicy("left", POTRACE_TURNPOLICY_LEFT),
    TurnPolicy("right", POTRACE_TURNPOLICY_RIGHT),
    TurnPolicy("minority", POTRACE_TURNPOLICY_MINORITY),
    TurnPolicy("majority", POTRACE_TURNPOLICY_MAJORITY),
    TurnPolicy("random", POTRACE_TURNPOLICY_RANDOM),
]


class Backend:
    def __init__(
        self,
        name: str,
        ext: str,
        fixed: bool,
        pixel: bool,
        multi: bool,
        init_f,
        page_f,
        term_f,
        opticurve: bool,
    ):
        self.name = name
        self.ext = ext
        self.fixed = fixed
        self.pixel = pixel
        self.multi = multi
        self.init_f = init_f
        self.page_f = page_f
        self.term_f = term_f
        self.opticurve = opticurve


# Assume backend implementations are available
def page_svg(fout, plist, imginfo) -> None:
    print("Calling page_svg (mock)")
    pass


def InitPdf(fout) -> None:
    print("Calling InitPdf (mock)")
    pass


def PagePdf(fout, plist, imginfo) -> None:
    print("Calling PagePdf (mock)")
    pass


def PagePdfPage(fout, plist, imginfo) -> None:
    print("Calling PagePdfPage (mock)")
    pass


def TermPdf(fout) -> None:
    print("Calling TermPdf (mock)")
    pass


def PageEps(fout, plist, imginfo) -> None:
    print("Calling PageEps (mock)")
    pass


def InitPs(fout) -> None:
    print("Calling InitPs (mock)")
    pass


def PagePs(fout, plist, imginfo) -> None:
    print("Calling PagePs (mock)")
    pass


def TermPs(fout) -> None:
    print("Calling TermPs (mock)")
    pass


def PageDxf(fout, plist, imginfo) -> None:
    print("Calling PageDxf (mock)")
    pass


def PageGeoJson(fout, plist, imginfo) -> None:
    print("Calling PageGeoJson (mock)")
    pass


def PagePgm(fout, plist, imginfo) -> None:
    print("Calling PagePgm (mock)")
    pass


def PageGimp(fout, plist, imginfo) -> None:
    print("Calling PageGimp (mock)")
    pass


def PageXfig(fout, plist, imginfo) -> None:
    print("Calling PageXfig (mock)")
    pass


backendListGlobal = [
    Backend("svg", ".svg", False, False, False, None, page_svg, None, True),
    Backend("pdf", ".pdf", False, False, True, InitPdf, PagePdf, TermPdf, True),
    Backend("pdfpage", ".pdf", True, False, True, InitPdf, PagePdfPage, TermPdf, True),
    Backend("eps", ".eps", False, False, False, None, PageEps, None, True),
    Backend("postscript", ".ps", True, False, True, InitPs, PagePs, TermPs, True),
    Backend("ps", ".ps", True, False, True, InitPs, PagePs, TermPs, True),
    Backend("dxf", ".dxf", False, True, False, None, PageDxf, None, True),
    Backend("geojson", ".json", False, True, False, None, PageGeoJson, None, True),
    Backend("pgm", ".pgm", False, True, True, None, PagePgm, None, True),
    Backend("gimppath", ".svg", False, True, False, None, PageGimp, None, True),
    Backend("xfig", ".fig", True, False, False, None, PageXfig, None, False),
]


class Info:
    def __init__(self):
        self.backend: Optional[Backend] = None
        self.debug: int = 0
        self.widthD: Dim = Dim(float("inf"))
        self.heightD: Dim = Dim(float("inf"))
        self.rx: float = float("inf")
        self.ry: float = float("inf")
        self.sx: float = float("inf")
        self.sy: float = float("inf")
        self.stretch: float = 1.0
        self.lmarD: Dim = Dim(float("inf"))
        self.rmarD: Dim = Dim(float("inf"))
        self.tmarD: Dim = Dim(float("inf"))
        self.bmarD: Dim = Dim(float("inf"))
        self.angle: float = 0.0
        self.paperWidth: int = DEFAULT_PAPERWIDTH
        self.paperHeight: int = DEFAULT_PAPERHEIGHT
        self.tight: bool = False
        self.unit: float = 10.0
        self.compress: int = 1
        self.psLevel: int = 2
        self.color: int = 0x000000
        self.gamma: float = 2.2
        self.param = None  # Assuming potrace_param_default() returns an object
        self.longCoding: bool = False
        self.outFile: Optional[str] = None
        self.blackLevel: float = 0.5
        self.invert: bool = False
        self.opaque: bool = False
        self.grouping: int = 1
        self.fillColor: int = 0xFFFFFF
        self.progress: bool = False
        self.progressBar = None  # Assuming DEFAULT_PROGRESS_BAR is accessible
        self.infiles: List[str] = []
        self.infileCount: int = 0
        self.someInfiles: bool = False


info = Info()


class Dim:
    def __init__(self, x: float = 0.0, d: float = 0.0):
        self.x = x
        self.d = d


def BackendLookup(name: str, bp: List[Optional[Backend]]) -> int:
    matches = 0
    bMatch = None

    for b in backendListGlobal:
        if b.name.lower() == name.lower():
            bp[0] = b
            return 0
        elif b.name.lower().startswith(name.lower()):
            matches += 1
            bMatch = b

    if matches == 1:
        bp[0] = bMatch
        return 0
    elif matches > 1:
        return 2
    else:
        return 1


def BackendList(fout, j: int, linelen: int) -> int:
    for i, b in enumerate(backendListGlobal):
        if j + len(b.name) > linelen:
            fout.write("\n")
            j = 0
        j += fout.write(b.name)
        if i < len(backendListGlobal) - 1:
            j += fout.write(", ")
    return j


def LicenseInfo(f) -> None:
    f.write(
        "This program is free software; you can redistribute it and/or modify\n"
        "it under the terms of the GNU General Public License as published by\n"
        "the Free Software Foundation; either version 2 of the License, or\n"
        "(at your option) any later version.\n"
        "\n"
        "This program is distributed in the hope that it will be useful,\n"
        "but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
        "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the\n"
        "GNU General Public License for more details.\n"
        "\n"
        "You should have received a copy of the GNU General Public License\n"
        "along with this program; if not, write to the Free Software Foundation\n"
        "Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.\n"
    )


def ShowDefaults(f) -> None:
    f.write(f"Default unit: {DEFAULT_DIM_NAME}\n")
    f.write(f"Default page size: {DEFAULT_PAPERFORMAT}\n")


def UsageInfo(f) -> None:
    f.write(f"Usage: {POTRACE} [options] [filename...]\n")
    f.write("General options:\n")
    f.write(" -h, --help                 - print this help message and exit\n")
    f.write(" -v, --version              - print version info and exit\n")
    f.write(" -l, --license              - print license info and exit\n")
    f.write("File selection:\n")
    f.write(" <filename>                 - an input file\n")
    f.write(" -o, --output <filename>    - write all output to this file\n")
    f.write(
        " --                         - end of options; 0 or more input filenames follow\n"
    )
    f.write("Backend selection:\n")
    f.write(" -b, --backend <name>       - select backend by name\n")
    f.write(" -b svg, -s, --svg          - SVG backend (scalable vector graphics)\n")
    f.write(" -b pdf                     - PDF backend (portable document format)\n")
    f.write(" -b pdfpage                 - fixed page-size PDF backend\n")
    f.write(
        " -b eps, -e, --eps          - EPS backend (encapsulated PostScript) (default)\n"
    )
    f.write(" -b ps, -p, --postscript    - PostScript backend\n")
    f.write(" -b pgm, -g, --pgm          - PGM backend (portable greymap)\n")
    f.write(" -b dxf                     - DXF backend (drawing interchange format)\n")
    f.write(" -b geojson                 - GeoJSON backend\n")
    f.write(" -b gimppath                - Gimppath backend (GNU Gimp)\n")
    f.write(" -b xfig                    - XFig backend\n")
    f.write("Algorithm options:\n")
    f.write(
        " -z, --turnpolicy <policy>  - how to resolve ambiguities in path decomposition\n"
    )
    f.write(
        " -t, --turdsize <n>         - suppress speckles of up to this size (default 2)\n"
    )
    f.write(" -a, --alphamax <n>         - corner threshold parameter (default 1)\n")
    f.write(" -n, --longcurve            - turn off curve optimization\n")
    f.write(
        " -O, --opttolerance <n>     - curve optimization tolerance (default 0.2)\n"
    )
    f.write(
        " -u, --unit <n>             - quantize output to 1/unit pixels (default 10)\n"
    )
    f.write(
        " -d, --debug <n>            - produce debugging output of type n (n=1,2,3)\n"
    )
    f.write("Scaling and placement options:\n")
    f.write(" -P, --pagesize <format>    - page size (default is a4)\n")
    f.write(" -W, --width <dim>          - width of output image\n")
    f.write(" -H, --height <dim>         - height of output image\n")
    f.write(
        " -r, --resolution <n>[x<n>] - resolution (in dpi) (dimension-based backends)\n"
    )
    f.write(" -x, --scale <n>[x<n>]      - scaling factor (pixel-based backends)\n")
    f.write(" -S, --stretch <n>          - yresolution/xresolution\n")
    f.write(" -A, --rotate <angle>       - rotate counterclockwise by angle\n")
    f.write(" -M, --margin <dim>         - margin\n")
    f.write(" -L, --leftmargin <dim>     - left margin\n")
    f.write(" -R, --rightmargin <dim>    - right margin\n")
    f.write(" -T, --topmargin <dim>      - top margin\n")
    f.write(" -B, --bottommargin <dim>   - bottom margin\n")
    f.write(" --tight                    - remove whitespace around the input image\n")
    f.write("Color options, supported by some backends:\n")
    f.write(" -C, --color #rrggbb        - set foreground color (default black)\n")
    f.write(" --fillcolor #rrggbb        - set fill color (default transparent)\n")
    f.write(" --opaque                   - make white shapes opaque\n")
    f.write("SVG options:\n")
    f.write(" --group                    - group related paths together\n")
    f.write(" --flat                     - whole image as a single path\n")
    f.write("Postscript/EPS/PDF options:\n")
    f.write(" -c, --cleartext            - do not compress the output\n")
    f.write(
        " -2, --level2               - use postscript level 2 compression (default)\n"
    )
    if HAVE_ZLIB:
        f.write(" -3, --level3               - use postscript level 3 compression\n")
    f.write(" -q, --longcoding           - do not optimize for file size\n")
    f.write("PGM options:\n")
    f.write(
        " -G, --gamma <n>            - gamma value for anti-aliasing (default 2.2)\n"
    )
    f.write("Frontend options:\n")
    f.write(
        " -k, --blacklevel <n>       - black/white cutoff in input file (default 0.5)\n"
    )
    f.write(" -i, --invert               - invert bitmap\n")
    f.write("Progress bar options:\n")
    f.write(" --progress                 - show progress bar\n")
    f.write(" --tty <mode>               - progress bar rendering: vt100 or dumb\n")
    f.write("\n")
    f.write("Dimensions can have optional units, e.g. 6.5in, 15cm, 100pt.\n")
    f.write(
        f"Default is {DEFAULT_DIM_NAME} (or pixels for pgm, dxf, and gimppath backends).\n"
    )
    f.write("Possible input file formats are: pnm (pbm, pgm, ppm), bmp.\n")
    j = f.write("Backends are: ")
    BackendList(f, j, 78)
    f.write(".\n")


def ParseDimension(s: str) -> Dim:
    s = s.strip()
    res = Dim()
    try:
        res.x = float(s[:-2])
        unit = s[-2:].lower()
        if unit == "in":
            res.d = DIM_IN
        elif unit == "cm":
            res.d = DIM_CM
        elif unit == "mm":
            res.d = DIM_MM
        elif unit == "pt":
            res.d = DIM_PT
        else:
            res.x = float(s)  # No unit
    except (ValueError, IndexError):
        try:
            res.x = float(s)
        except ValueError:
            pass  # Keep default 0.0

    return res


def ParseDimensions(s: str) -> tuple[Dim, Dim]:
    parts = s.split("x")
    if len(parts) == 2:
        dx = ParseDimension(parts[0])
        dy = ParseDimension(parts[1])
        if dx.d and not dy.d:
            dy.d = dx.d
        elif not dx.d and dy.d:
            dx.d = dy.d
        return dx, dy
    else:
        dx = ParseDimension(s)
        return dx, Dim()


def DoubleOfDim(d: Dim, default: float) -> float:
    return d.x * d.d if d.d else d.x * default


def ParseColor(s: str) -> int:
    if s.startswith("#") and len(s) == 7:
        try:
            return int(s[1:], 16)
        except ValueError:
            return -1
    return -1


def DoOptions() -> None:
    global info
    parser = argparse.ArgumentParser(add_help=False)

    # General options
    parser.add_argument(
        "-h", "--help", action="store_true", help="print this help message and exit"
    )
    parser.add_argument(
        "-v", "--version", action="store_true", help="print version info and exit"
    )
    parser.add_argument(
        "-l", "--license", action="store_true", help="print license info and exit"
    )

    # File selection
    parser.add_argument("filenames", nargs="*", help="input filenames")
    parser.add_argument("-o", "--output", help="write all output to this file")
    parser.add_argument(
        "--", dest="end_of_options", action="store_true", help=argparse.SUPPRESS
    )  # Placeholder

    # Backend selection
    group_backend = parser.add_mutually_exclusive_group()
    group_backend.add_argument("-b", "--backend", help="select backend by name")
    group_backend.add_argument("-s", "--svg", action="store_true", help="SVG backend")
    group_backend.add_argument(
        "-e", "--eps", action="store_true", help="EPS backend (default)"
    )
    group_backend.add_argument(
        "-p", "--postscript", action="store_true", help="PostScript backend"
    )
    group_backend.add_argument("-g", "--pgm", action="store_true", help="PGM backend")

    # Algorithm options
    parser.add_argument(
        "-z", "--turnpolicy", help="how to resolve ambiguities in path decomposition"
    )
    parser.add_argument(
        "-t",
        "--turdsize",
        type=int,
        help="suppress speckles of up to this size (default 2)",
    )
    parser.add_argument(
        "-a", "--alphamax", type=float, help="corner threshold parameter (default 1)"
    )
    parser.add_argument(
        "-n", "--longcurve", action="store_true", help="turn off curve optimization"
    )
    parser.add_argument(
        "-O",
        "--opttolerance",
        type=float,
        help="curve optimization tolerance (default 0.2)",
    )
    parser.add_argument(
        "-u", "--unit", type=float, help="quantize output to 1/unit pixels (default 10)"
    )
    parser.add_argument(
        "-d", "--debug", type=int, help="produce debugging output of type n (n=1,2,3)"
    )

    # Scaling and placement options
    parser.add_argument(
        "-P", "--pagesize", help=f"page size (default is {DEFAULT_PAPERFORMAT})"
    )
    parser.add_argument("-W", "--width", help="width of output image")
    parser.add_argument("-H", "--height", help="height of output image")
    parser.add_argument(
        "-r", "--resolution", help="resolution (in dpi) (dimension-based backends)"
    )
    parser.add_argument("-x", "--scale", help="scaling factor (pixel-based backends)")
    parser.add_argument("-S", "--stretch", type=float, help="yresolution/xresolution")
    parser.add_argument(
        "-A", "--rotate", type=float, help="rotate counterclockwise by angle"
    )
    parser.add_argument("-M", "--margin", help="margin")
    parser.add_argument("-L", "--leftmargin", help="left margin")
    parser.add_argument("-R", "--rightmargin", help="right margin")
    parser.add_argument("-T", "--topmargin", help="top margin")
    parser.add_argument("-B", "--bottommargin", help="bottom margin")
    parser.add_argument(
        "--tight", action="store_true", help="remove whitespace around the input image"
    )

    # Color options
    parser.add_argument("-C", "--color", help="set foreground color (default black)")
    parser.add_argument("--fillcolor", help="set fill color (default transparent)")
    parser.add_argument(
        "--opaque", action="store_true", help="make white shapes opaque"
    )

    # SVG options
    parser.add_argument(
        "--group", action="store_true", help="group related paths together"
    )
    parser.add_argument(
        "--flat", action="store_true", help="whole image as a single path"
    )

    # Postscript/EPS/PDF options
    group_ps = parser.add_mutually_exclusive_group()
    group_ps.add_argument(
        "-c", "--cleartext", action="store_true", help="do not compress the output"
    )
    group_ps.add_argument(
        "-2",
        "--level2",
        action="store_true",
        help="use postscript level 2 compression (default)",
    )
    if HAVE_ZLIB:
        group_ps.add_argument(
            "-3",
            "--level3",
            action="store_true",
            help="use postscript level 3 compression",
        )
    parser.add_argument(
        "-q", "--longcoding", action="store_true", help="do not optimize for file size"
    )

    # PGM options
    parser.add_argument(
        "-G", "--gamma", type=float, help="gamma value for anti-aliasing (default 2.2)"
    )

    # Frontend options
    parser.add_argument(
        "-k",
        "--blacklevel",
        type=float,
        help="black/white cutoff in input file (default 0.5)",
    )
    parser.add_argument("-i", "--invert", action="store_true", help="invert bitmap")

    # Progress bar options
    parser.add_argument("--progress", action="store_true", help="show progress bar")
    parser.add_argument("--tty", help="progress bar rendering: vt100 or dumb")

    args = parser.parse_args()

    # Set defaults
    BackendLookup("eps", [info.backend])
    info.param = None  # Assuming potrace_param_default() is called later if needed
    info.progressBar = None  # Assuming DEFAULT_PROGRESS_BAR is used later if needed

    if args.help:
        UsageInfo(sys.stdout)
        sys.exit(0)

    if args.version:
        sys.stdout.write(f"{POTRACE} {VERSION}\n")
        # sys.stdout.write(f"Library version: {potrace_version()}\n") # Assuming potrace_version exists
        ShowDefaults(sys.stdout)
        sys.exit(0)

    if args.license:
        sys.stdout.write(f"{POTRACE} {VERSION}\n\n")
        LicenseInfo(sys.stdout)
        sys.exit(0)

    if args.backend:
        r = BackendLookup(args.backend, [info.backend])
        if r == 1:
            sys.stderr.write(f"{POTRACE}: unrecognized backend -- {args.backend}\n")
            sys.stderr.write("Use one of: ")
            BackendList(sys.stderr, 0, 70)
            sys.stderr.write(".\n")
            sys.exit(1)
        elif r == 2:
            sys.stderr.write(f"{POTRACE}: ambiguous backend -- {args.backend}\n")
            sys.stderr.write("Use one of: ")
            BackendList(sys.stderr, 0, 70)
            sys.stderr.write(".\n")
            sys.exit(1)
    elif args.svg:
        BackendLookup("svg", [info.backend])
    elif args.eps:
        BackendLookup("eps", [info.backend])
    elif args.postscript:
        BackendLookup("postscript", [info.backend])
    elif args.pgm:
        BackendLookup("pgm", [info.backend])

    if args.output:
        info.outFile = args.output

    info.infiles = [f for f in args.filenames if f != "--"]
    info.infileCount = len(info.infiles)
    info.someInfiles = bool(info.infileCount)
    if args.end_of_options:
        info.someInfiles = True

    if args.width:
        info.widthD = ParseDimension(args.width)
    if args.height:
        info.heightD = ParseDimension(args.height)

    if args.resolution:
        dimx, dimy = ParseDimensions(args.resolution)
        if dimx.d == 0 and dimy.d == 0 and dimx.x != 0.0 and dimy.x != 0.0:
            info.rx = dimx.x
            info.ry = dimy.x
        elif dimx.d == 0 and dimx.x != 0.0 and dimy.x == 0.0:
            info.rx = info.ry = dimx.x
        else:
            sys.stderr.write(f"{POTRACE}: invalid resolution -- {args.resolution}\n")
            sys.exit(1)

    if args.scale:
        dimx, dimy = ParseDimensions(args.scale)
        if dimx.d == 0 and dimy.d == 0:
            info.sx = dimx.x
            info.sy = dimy.x
        elif dimx.d == 0 and dimy.x == 0.0:
            info.sx = info.sy = dimx.x
        else:
            sys.stderr.write(f"{POTRACE}: invalid scaling factor -- {args.scale}\n")
            sys.exit(1)

    if args.stretch is not None:
        info.stretch = args.stretch
    if args.margin:
        dim = ParseDimension(args.margin)
        info.lmarD = info.rmarD = info.tmarD = info.bmarD = dim
    if args.leftmargin:
        info.lmarD = ParseDimension(args.leftmargin)
    if args.rightmargin:
        info.rmarD = ParseDimension(args.rightmargin)
    if args.topmargin:
        info.tmarD = ParseDimension(args.topmargin)
    if args.bottommargin:
        info.bmarD = ParseDimension(args.bottommargin)
    if args.tight:
        info.tight = True
    if args.rotate is not None:
        info.angle = args.rotate
        if info.angle <= -180 or info.angle > 180:
            info.angle -= 360 * math.ceil(info.angle / 360 - 0.5)

    if args.pagesize:
        found = False
        for pf in pageFormats:
            if pf.name.lower() == args.pagesize.lower():
                info.paperWidth = pf.w
                info.paperHeight = pf.h
                found = True
                break
        if not found:
            dimx, dimy = ParseDimensions(args.pagesize)
            if dimx.x != 0 and dimy.x != 0:
                info.paperWidth = int(round(DoubleOfDim(dimx, DEFAULT_DIM)))
                info.paperHeight = int(round(DoubleOfDim(dimy, DEFAULT_DIM)))
            else:
                sys.stderr.write(
                    f"{POTRACE}: unrecognized page format -- {args.pagesize}\n"
                )
                sys.stderr.write("Use one of: ")
                page_names = [pf.name for pf in pageFormats]
                sys.stderr.write(", ".join(page_names))
                sys.stderr.write(", or specify <dim>x<dim>.\n")
                sys.exit(1)

    if args.turnpolicy:
        found = False
        for tp in turnPolicies:
            if tp.name.lower() == args.turnpolicy.lower():
                # info.param.turnpolicy = tp.n  # Assuming param is initialized later
                found = True
                break
        if not found:
            sys.stderr.write(
                f"{POTRACE}: unrecognized turnpolicy -- {args.turnpolicy}\n"
            )
            sys.stderr.write("Use one of: ")
            turn_names = [tp.name for tp in turnPolicies]
            sys.stderr.write(", ".join(turn_names))
            sys.stderr.write(".\n")
            sys.exit(1)

    if args.turdsize is not None:
        pass  # info.param.turdsize = args.turdsize
    if args.unit is not None:
        info.unit = args.unit
    if args.cleartext:
        info.psLevel = 2
        info.compress = 0
    elif args.level2:
        info.psLevel = 2
        info.compress = 1
    elif args.level3 and HAVE_ZLIB:
        info.psLevel = 3
        info.compress = 1
    elif args.level3 and not HAVE_ZLIB:
        sys.stderr.write(f"{POTRACE}: option -3 not supported, using -2 instead.\n")
        info.psLevel = 2
        info.compress = 1
    if args.longcoding:
        info.longCoding = True
    if args.alphamax is not None:
        pass  # info.param.alphamax = args.alphamax
    if args.opttolerance is not None:
        pass  # info.param.opttolerance = args.opttolerance
    if args.debug is not None:
        info.debug = args.debug
    if args.color:
        info.color = ParseColor(args.color)
        if info.color == -1:
            sys.stderr.write(f"{POTRACE}: invalid color -- {args.color}\n")
            sys.exit(1)
    if args.fillcolor:
        info.fillColor = ParseColor(args.fillcolor)
        if info.fillColor == -1:
            sys.stderr.write(f"{POTRACE}: invalid color -- {args.fillcolor}\n")
            sys.exit(1)
        info.opaque = True
    if args.opaque:
        info.opaque = True
    if args.group:
        info.grouping = 2
    if args.flat:
        info.grouping = 0
    if args.gamma is not None:
        info.gamma = args.gamma
    if args.blacklevel is not None:
        info.blackLevel = args.blacklevel
    if args.invert:
        info.invert = True
    if args.progress:
        info.progress = True
    if args.tty:
        if args.tty == "dumb":
            pass  # info.progressBar = progress_bar_simplified
        elif args.tty == "vt100":
            pass  # info.progressBar = progress_bar_vt100
        else:
            sys.stderr.write(
                f"{POTRACE}: invalid tty mode -- {args.tty}. Try --help for more info\n"
            )
            sys.exit(1)
