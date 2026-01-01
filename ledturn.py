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

"""turn - turn signal pattern."""

import asyncio
from ledstrip import LedStrip
from cmdtemplate import CommandTemplate

class LedTurn(CommandTemplate):
    helpstr = "turn signal chaser"
    cfgstr = "start,stop,r,g,b,delay_ms"

    def __init__(self, strip: LedStrip, start=0, stop=30, red=64, grn=0, blu=0, delay=0):
        super().__init__(strip)
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
    # 7 - delay in milliseconds
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

    # this is basically a chase
    async def run(self, parmlist) -> None:
        # check valid LED strip available and acquire lock
        if self._strip is None:
            return
        framebuf = self._strip.buf
        await self._strip.acquire(self)
        # at this point we have locked access to LED strip

        while not self._stoprequest:
            # compute next pixel to be updated
            pixcolor = self._color if self._on else 0
            framebuf[self._pix] = pixcolor
            self._pix += self._stride
            if (((self._stride == 1) and (self._pix > self._stop))
               or ((self._stride == -1) and (self._pix < self._stop))):
                self._on = not self._on
                self._pix = self._start

            # update the display
            self._strip.show()
            # yield for the update delay time
            await asyncio.sleep_ms(self._delay)

        # clean exit - clear display and release lock
        self._strip.clear()
        self._strip.release()
        self._stoprequest = False
