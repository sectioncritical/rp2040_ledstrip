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

    async def run(self, parmlist):
        # make sure we have strip to write
        if self._strip is None:
            return

        # get the framebuffer
        framebuf = self._strip.buf

        # acquire LED strip resource lock
        await self._strip.acquire(self)

        # fill the entire framebuf with red
        for pix in range(len(framebuf)):
            framebuf[pix] = 0x040000   # GRB

        # even though brake is on and done, wait in a loop so we can get
        # explicit command to stop, and clear the display
        while not self._stoprequest:

            # write the pattern out
            self._strip.show()

            await asyncio.sleep_ms(100)

        # clean exit - clear, release the resource and return
        self._strip.clear()
        self._strip.release()
        self._stoprequest = False

class LedBrakeHard(CommandTemplate):
    # pylint: disable=missing-class-docstring
    helpstr = "set brake hard signal, rapid blink, then all segments on"

    async def run(self, parmlist):
        # make sure we have strip to write
        if self._strip is None:
            return

        # get the framebuffer
        framebuf = self._strip.buf

        # acquire LED strip resource lock
        await self._strip.acquire(self)

        # blink on and off
        for _ in range(10):
            # all off
            self._strip.clear()
            await asyncio.sleep_ms(100)
            # all on
            for pix in range(len(framebuf)):
                framebuf[pix] = 0x040000   # GRB
            self._strip.show()
            await asyncio.sleep_ms(100)

        # in exiting the loop, the LED is left on
        # even though brake is on and done, wait in a loop so we can get
        # explicit command to stop, and clear the display
        while not self._stoprequest:
            await asyncio.sleep_ms(100)

        # clean exit - clear, release the resource and return
        self._strip.clear()
        self._strip.release()
        self._stoprequest = False
