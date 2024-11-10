#
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
    helpstr = "set range to color <range,start,num,r,g,b>"

    def render(self, parmlist, framebuf):
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
        return None     # no further calls needed
