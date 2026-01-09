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

"""brake (LedRange) - turn on all pixels red..

This command implements a brake signel. It lights up the entire segment with
red LEDs and stays on until commanded off. The command has no parameters, it is
just:

    $brake

The `brake` command does not have any configuration settings.
"""

import asyncio
from cmdtemplate import CommandTemplate

class LedBrake(CommandTemplate):
    # pylint: disable=missing-class-docstring
    helpstr = "set brake signal, all segments full on"
    cfgstr = "start,length,brake-R,G,B,ambient-R,G,B"

    def __init__(self, strip: LedStrip, start_pixel: int=0, length: int=0,
                 color: int=0x040000, ambient: int=0) -> None:
        super().__init__(strip)
        self._color = color
        self._ambient = ambient
        if length == 0:
            self._start = 0
            self._stop = strip.numpixels
        else:
            self._start = start_pixel
            self._stop = start_pixel + length
            if self._stop > strip.numpixels:
                self._stop = strip.numpixels
        # stop is exclusive; start=0, stop=4 is pixels 0-3

    # 0 - config command
    # 1 - brake command
    # 2 - start pixel
    # 3 - length
    # 4 - R
    # 5 - G
    # 6 - B
    # 7 - ambient R
    # 8 - ambient G
    # 9 - ambient B
    #
    def config(self, cfglist):
        numpixels = self._strip.numpixels
        start = int(cfglist[2])
        length = int(cfglist[3])
        if start >= numpixels:
            start = numpixels - 1
        self._start = start
        self._stop = start + length
        if self._stop > numpixels:
            self._stop = numpixels
        r = int(cfglist[4]) & 0xFF
        g = int(cfglist[5]) & 0xFF
        b = int(cfglist[6]) & 0xFF
        self._color = (r << 16) + (g << 8) + b
        r = int(cfglist[7]) & 0xFF
        g = int(cfglist[8]) & 0xFF
        b = int(cfglist[9]) & 0xFF
        self._ambient = (r << 16) + (g << 8) + b

    async def run(self, parmlist):
        # make sure we have strip to write
        if self._strip is None:
            return

        # get the framebuffer
        framebuf = self._strip.buf
        color = self._color
        ambient = self._ambient

        # acquire LED strip resource lock
        await self._strip.acquire(self)

        # fill the entire framebuf with the primary color
        for pix in range(self._start, self._stop):
            framebuf[pix] = color
        self._strip.show()

        # even though brake is on and done, wait in a loop so we can get
        # explicit command to stop, and clear the display
        while not self._stoprequest:
            await asyncio.sleep_ms(100)

        # clean exit - clear, release the resource and return
        for pix in range(self._start, self._stop):
            framebuf[pix] = ambient
        self._strip.show()
        self._strip.release()
        self._stoprequest = False

class LedBrakeHard(CommandTemplate):
    # pylint: disable=missing-class-docstring
    helpstr = "set brake hard signal, rapid blink, then all segments on"
    cfgstr = "start,length,brake-R,G,B,ambient-R,G,B,blinks,delay"

    def __init__(self, strip: LedStrip, start_pixel: int=0, length: int=0,
                 color: int=0x040000, ambient: int=0,
                 blinks: int=10, delay: int=100) -> None:
        super().__init__(strip)
        self._color = color
        self._ambient = ambient
        if length == 0:
            self._start = 0
            self._stop = strip.numpixels
        else:
            self._start = start_pixel
            self._stop = start_pixel + length
            if self._stop > strip.numpixels:
                self._stop = strip.numpixels
        # stop is exclusive; start=0, stop=4 is pixels 0-3
        self._blinks = blinks
        self._delay = delay

    # 0 - config command
    # 1 - brake command
    # 2 - start pixel
    # 3 - length
    # 4 - R
    # 5 - G
    # 6 - B
    # 7 - ambient R
    # 8 - ambient G
    # 9 - ambient B
    # 10 - blinks
    # 11 - delay
    #
    def config(self, cfglist):
        numpixels = self._strip.numpixels
        start = int(cfglist[2])
        length = int(cfglist[3])
        if start >= numpixels:
            start = numpixels - 1
        self._start = start
        self._stop = start + length
        if self._stop > numpixels:
            self._stop = numpixels
        r = int(cfglist[4]) & 0xFF
        g = int(cfglist[5]) & 0xFF
        b = int(cfglist[6]) & 0xFF
        self._color = (r << 16) + (g << 8) + b
        r = int(cfglist[7]) & 0xFF
        g = int(cfglist[8]) & 0xFF
        b = int(cfglist[9]) & 0xFF
        self._ambient = (r << 16) + (g << 8) + b
        self._blinks = int(cfglist[10])
        self._delay = int(cfglist[11])

    async def run(self, parmlist):
        # make sure we have strip to write
        if self._strip is None:
            return

        # get the framebuffer
        framebuf = self._strip.buf
        start = self._start
        stop = self._stop
        color = self._color
        ambient = self._ambient
        delay = self._delay
        blinks = self._blinks

        # acquire LED strip resource lock
        await self._strip.acquire(self)

        # blink on and off
        for _ in range(blinks):
            # all off
            for pix in range(start, stop):
                framebuf[pix] = ambient
            self._strip.show()
            await asyncio.sleep_ms(delay)
            # all on
            for pix in range(start, stop):
                framebuf[pix] = color
            self._strip.show()
            await asyncio.sleep_ms(delay)

        # in exiting the loop, the LED is left on
        # even though brake is on and done, wait in a loop so we can get
        # explicit command to stop, and clear the display
        while not self._stoprequest:
            await asyncio.sleep_ms(delay)

        # clean exit - clear, release the resource and return
        for pix in range(start, stop):
            framebuf[pix] = ambient
        self._strip.show()
        self._strip.release()
        self._stoprequest = False
