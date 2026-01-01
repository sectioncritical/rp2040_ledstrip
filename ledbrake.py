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
