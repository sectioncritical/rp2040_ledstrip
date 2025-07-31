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

"""random - random pattern commands."""

import asyncio
from random import randint, randrange, choice as randchoice
from cmdtemplate import CommandTemplate
from ledstrip import LedStrip

# TODO for random operations do we need to set the seed? for example, could
# seed with current time when command is executed

class LedRandomOG(CommandTemplate):
    """Random pattern based on Bill's pattern 2.

    This command lights one or more LEDs in the string at random locations and
    with random colors. It is based on Bill's original pattern 2 code. This
    command has no configuration and no parameters. It is just invoked by
    itself:

        $randomog
    """
    helpstr = "bill's original pattern2"
    cfgstr = "no configs"

    def __init__(self, strip: LedStrip) -> None:
        super().__init__(strip)

    # def config(self, cfglist):

    async def run (self, parmlist: list[str]) -> None:
        # this is a rewriting of Bill's underhoodLights algorithm for
        # pattern 2. The code looks different but the outcome should be the
        # same or simimlar.
        # TODO rewrite as lookup table or similar

        # check valid LED strip available and acquire lock
        if self._strip is None:
            return
        framebuf = self._strip.buf
        await self._strip.acquire(self)
        # at this point we have locked access to LED strip

        while not self._stoprequest:
            # determine random elements
            colorChooser = randint(0, 100)
            startPixel = randint(0, 410)
            numPixels = randint(1, 5)
            grn = randint(20, 255) << 16
            red = randint(20, 255) << 8
            blu = randint(20, 255)

            # select which colors to apply
            if colorChooser < 30:
                color = 0
            elif colorChooser < 35:  # green
                color = grn
            elif colorChooser < 40:  # red
                color = red
            elif colorChooser < 45:  # blue
                color = blu
            elif colorChooser < 50:  # red/green
                color = grn + red
            elif colorChooser < 55:  # green/blue
                color = grn + blu
            elif colorChooser < 60:  # red/blue
                color = red + blu
            elif colorChooser < 70:  # more green
                color = grn
            else:
                color = grn + red + blu

            # set the pixels in the frame buffer
            for pix in range(startPixel, startPixel+numPixels+1):
                framebuf[pix] = color
            self._strip.show()

            # rerun every 100 ms
            await asyncio.sleep_ms(100)

        # clean exit - clear display and release lock
        self._strip.clear()
        self._strip.release()
        self._stoprequest = False

class LedRandom(CommandTemplate):
    """Configurable random pattern generator.

    This command generates a pattern similar to *randomog*. But it has
    configurable options. Originally, random colors were used for each pixel.
    But that ends up with most pixels have all 3 of RGB turned on which ends up
    just making mostly pastels. This pattern generates random colors for each
    channel, but then randomly chooses only one or two of those channels to
    mix together (there is also a chance of all 3 channels but it is low
    probability). This results in much brighter colors and more bright reds,
    greens, and blues. It just looks more colorful.

    At some period, a random spot on the LED strip is selected, and a random
    number of sequential pixels are lit, with a random color as described
    above. There is also some probability that pixels are set to dark.

    The command itself takes no parameters:

        $random

    But it has a configuration:

        $config,random,<dark-threshold>,<max-intensity>,<num-pixels>,<delayus>

    * dark-threshold - a random value from 0-255 is compared to the dark
      threshold. If it is below the threshold then the color will be dark (off).
      For example, to make there be a 50% chance of dark pixels, use a value of
      128.
    * max-intensity - this is a mask that limits the value of a color channel.
      It is ANDed with the random color. It should probably be a power of 2,
      minus 1, or you will get strange results. For example, 127, 63, 31, etc.
      If you select 127 (the default) then that will force the upper bit to
      always be off, which limits the max intensity for any channel to 127.
      The reason for doing this is to reduce the overall power consumed by the
      LED strip. If you want max intensity without any limit, then set this
      value to 255.
    * num-pixels - this should 1 or more. It is the maximum number of
      consecutive pixels that will be lit up. The algorithm uses a random
      number between 1 and this value. The default is 5.
    * delayms - the repeat period in milliseconds. The lower the number, the
      faster the pattern updates. The default is 100 which is 100
      milliseconds.
    """
    helpstr = "show random colors"
    cfgstr = "dark-threshold(0-255),max-intensity(0-255),num-pixels,delay_us"

    chooser = [0x0000FF, 0x00FF00, 0x00FFFF,            # noqa: RUF012
               0xFF0000, 0xFF00FF, 0xFFFF00, 0xFFFFFF]

    def __init__(self, strip: LedStrip) -> None:
        super().__init__(strip)
        self._dark_threshold = 77  # 30% chance of dark
        self._max_intensity = 0x7F7F7F
        self._max_pixels = 5
        self._delay = 100 # 100 ms

    # cfglist[0] - "config"
    # cfglist[1] - "random"
    # cfglist[2] - dark threshold (0-255)
    # cfglist[3] - max intensity (0-255)
    # cfglist[4] - max number of pixels to light
    # cfglist[5] - periodic delay in microseconds
    def config(self, cfglist: list[str]) -> None:
        # do bare minimum error checking
        if len(cfglist) == 6:
            self._dark_threshold = int(cfglist[2]) & 0xff
            intens = int(cfglist[3]) & 0xFF
            self._max_intensity = (intens << 16) + (intens << 8) + intens
            self._max_pixels = int(cfglist[4])
            self._delay = int(cfglist[5])

    async def run(self, parmlist: list[str]) -> None:
        # check valid LED strip available and acquire lock
        if self._strip is None:
            return
        framebuf = self._strip.buf
        await self._strip.acquire(self)
        # at this point we have locked access to LED strip

        while not self._stoprequest:
            # get a random color value (all 3 colors)
            color = randrange(0x7FFFFFFF)
            # use upper 8 bits as probability of dark
            dark = color >> 24
            if dark < self._dark_threshold:
                # below dark threshold so set color to 0 (off)
                color = 0
            else:
                # use the lower 3 bytes for the pixel value
                # apply the color chooser, then the intensity cap
                color = color & randchoice(self.chooser)
                color = color & self._max_intensity  # cap the intensity

            # determine number of pixels to light
            numpixels = randint(1, self._max_pixels)

            # determine starting pixel
            startpix = randrange(len(framebuf) - numpixels)

            # set the affected pixels
            for pix in range(numpixels):
                framebuf[startpix+pix] = color
            self._strip.show()

            # return the rerun period
            await asyncio.sleep_ms(self._delay)

        # clean exit - clear display and release lock
        self._strip.clear()
        self._strip.release()
        self._stoprequest = False
