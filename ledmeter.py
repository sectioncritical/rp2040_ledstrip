# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Licensed under AGPLv3
#
# Copyright (c) 2025 Joseph Kroesche
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""meter (LedMeter) - show a level meter over a range of pixels, with gradient.

This command is used to show a "level meter" or "progress meter" over a range
of pixels in the LED strip. The command has a "percent" parameter which lights
up the corresponding number of pixels over a defined range. There can also be
a color gradient. For example all green at the low end and progressively
getting redder as the value increases.

The command format is:

    $meter,<percent>

where `percent` is 0-100.

Prior to using, the `meter` command must be configured to specify the pixels
that are part of the meter display, and the color gradient to use. The config
command has the following format:

    $config,meter,<start-pxel>,<stop-pixel>,<r0>,<rN>,<g0>,<gN>,<b0>,<bN>

* start-pixel - the beginning pixel of the meter display
* stop-pixel - the ending pixel of the meter display, inclusive
* r0 - the beginning value for "red"
* rN - the ending value for "red"
* g0/gN - begin/end value for "green"
* b0/bN - begin/end value for "blue"

**NOTES:**

* The colors listed above assume RGB format. Swap values if your order is GRB.
* The start pixel and stop pixel can be in either increasing or decreasing order
* the config only need to be done once for a given powered session. If the
  controller board is repowered or reset, the config command must be sent again

*Example*

A meter function is defined to go from pixel 0 to pixel 19 (20 pixels), in the
increasing direction. It should be fully red at the low end, and fully green
at the full end. The colors in mid-scale will be interpolated between the two
ends.

    $config,meter,0,19,255,0,0,255,0,0

To set the meter display to 50%, half the pixels (10) will be lit ranging from
red at the lowest end to yellow-ish in the middle:

    $meter,50

There is one meter command built-in, named `meter`. Additional meter instances
can be added using the `add` command.

    $add,meter2,LedMeter

Will create a second meter function, named `meter2`. It can be configured for
a different set of pixels and different gradient so you can have two different
meter displays on a single LED strip.
"""

from cmdtemplate import CommandTemplate
from ledstrip import LedStrip

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

    def __init__(self, strip: LedStrip) -> None:
        super().__init__(strip)
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

    # this is a one-shot display so it does not loop and does not wait
    async def run(self, parmlist) -> None:
        # check valid LED strip available and acquire lock
        if self._strip is None:
            return
        framebuf = self._strip.buf
        await self._strip.acquire(self)
        # at this point we have locked access to LED strip

        pct = int(parmlist[1])
        litdots = ((self._numdots * pct) + 50) // 100
        for idx in range(litdots):
            red  = interpolate_color(self._numdots, idx, self._rgradient)
            green = interpolate_color(self._numdots, idx, self._ggradient)
            blue = interpolate_color(self._numdots, idx, self._bgradient)
            framebuf[self._start + (idx*self._stride)] = (green << 16) + (red << 8) + blue
        for idx in range(litdots, self._numdots):
            framebuf[self._start + (idx*self._stride)] = 0

        # update the display
        self._strip.show()

        # clean exit
        self._strip.release()
