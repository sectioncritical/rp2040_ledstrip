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

"""range (LedRange) - set range of pixels to a color.

This command is used to set a range of one or more pixels to a fixed color. The
format is:

    $range,<start-pixel>,<num-pixels>,<color1>,<color2>,<color3>

* start-pixel - the starting pixel number (0-origin) of the range
* num-pixels  - the number of pixels to include in the range
* color1/2/3  - the value of each of the three color fields, 0-255

The color format is usually RGB or GRB. You can experiment setting each in turn
to see how they are mapped with your hardware.

The main purpose of this command is for prototyping and debugging. Once a
pattern is defined, it should be implemented as a new command class in this
code.

*Example*

Set pixels 10-19 to blue at half intensity:

    $range,10,10,0,0,128

The `range` command does not have any configuration settings.
"""

from cmdtemplate import CommandTemplate

class LedRange(CommandTemplate):
    # pylint: disable=missing-class-docstring
    helpstr = "set range to color <range,start,num,r,g,b>"

    async def run(self, parmlist):
        # make sure we have strip to write
        if self._strip is None:
            return

        # get the framebuffer
        framebuf = self._strip.buf

        # acquire LED strip resource lock
        await self._strip.acquire(self)

        # write the pattern to the buffer
        dot0 = int(parmlist[1])
        numdots = int(parmlist[2])
        red = int(parmlist[3])
        green = int(parmlist[4])
        blue = int(parmlist[5])
        color = green << 16
        color += red << 8
        color += blue
        for idx in range(numdots):
            framebuf[dot0+idx] = color

        # write the pattern out
        self._strip.show()

        # release the resource and return
        self._strip.release()
