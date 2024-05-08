
from cmdtemplate import CommandTemplate

# 8-bit integer color interpolation
# numpixels - the number of pixels in the interpolated range
# pixel - the current pixel index
# gradient - tuple-like with start and end colors
#
# returns interpolated 8-bit color value
#
def interpolate_color(numpixels, pixel, gradient):
    totaldiff = gradient[1] - gradient[0]
    pctdiff = ((pixel * 1000) * totaldiff) // (numpixels * 1000)
    return gradient[0] + pctdiff

class LedMeter(CommandTemplate):
    helpstr = "meter,<pct 0-100>"
    cfgstr = "start,stop,r0,rN,g0,gN,b0,bN"

    def __init__(self):
        super().__init__()
        self._start = 0
        self._stop = 0
        self._rgradient = (0, 15)
        self._ggradient = (0, 15)
        self._bgradient = (0, 15)
        self._stride = 1
        self._numdots = 0

    #
    # cfglist is list of string parameters
    # 0 - config command
    # 1 - meter command
    # 2 - start pixel index
    # 3 - stop pixel index (inclusive)
    # pixel indexes can go in either direction
    # 4 - starting r (the r value at start pixel)
    # 5 - ending r   (the r value at stop pixel)
    # 6 - starting g (the r value at start pixel)
    # 7 - ending g   (the r value at stop pixel)
    # 8 - starting b (the r value at start pixel)
    # 9 - ending b   (the r value at stop pixel)
    #
    def config(self, cfglist):
        self._start = int(cfglist[2])
        self._stop = int(cfglist[3])
        self._rgradient = (int(cfglist[4]), int(cfglist[5]))
        self._ggradient = (int(cfglist[6]), int(cfglist[7]))
        self._bgradient = (int(cfglist[8]), int(cfglist[9]))
        self._stride = 1 if self._stop > self._start else -1
        self._numdots = abs(self._stop - self._start) + 1

    def render(self, parmlist, framebuf):
        pct = int(parmlist[1])
        litdots = ((self._numdots * pct) + 50) // 100
        for idx in range(litdots):
            red  = interpolate_color(self._numdots, idx, self._rgradient)
            green = interpolate_color(self._numdots, idx, self._ggradient)
            blue = interpolate_color(self._numdots, idx, self._bgradient)
            framebuf[self._start + (idx*self._stride)] = (green << 16) + (red << 8) + blue
        for idx in range(litdots, self._numdots):
            framebuf[self._start + (idx*self._stride)] = 0
        return None
