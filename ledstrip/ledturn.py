# SPDX-License-Identifier: 0BSD
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""turn - turn signal pattern."""

from cmdtemplate import CommandTemplate

class LedTurn(CommandTemplate):
    helpstr = "turn signal chaser"
    cfgstr = "start,stop,r,g,b,delay_us"

    def __init__(self, start=0, stop=30, red=64, grn=0, blu=0, delay=10000):
        super().__init__()
        # configurables
        self._start = int(start)
        self._stop = int(stop)
        self._delay = int(delay)
        self._color = ((int(red) << 16) + (int(grn) << 8) + int(blu))

        #  internal state
        self._stride = 1 if self._stop >= self._start else -1
        self._pix = self._start
        self._on = True

    # 0 - "config"
    # 1 - "<turn>" (name may be custom)
    # 2 - start pixel number
    # 3 - stop pixel number (exclusive)
    # 4 - red color (0-255) ## assumes RGB order
    # 5 - green color (0-255)
    # 6 - blue color (0-255)
    # 7 - delay in microseconds
    def config(self, cfglist):
        self._start = int(cfglist[2])
        self._stop = int(cfglist[3])
        self._color = ((int(cfglist[4]) << 16)
                    + (int(cfglist[5]) << 8)
                    + int(cfglist[6]))
        self._delay = int(cfglist[7])
        self._stride = 1 if self._stop >= self._start else -1
        self._pix = self._start
        self._on = True

    def render(self, parmlist, framebuf):
        pixcolor = self._color if self._on else 0
        framebuf[self._pix] = pixcolor
        self._pix += self._stride
        if (((self._stride == 1) and (self._pix > self._stop))
           or ((self._stride == -1) and (self._pix < self._stop))):
            self._on = not self._on
            self._pix = self._start
        return self._delay

