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

# class to represent an attached LED strip which has its own PIO and pixel
# buffer

import array
import asyncio

from cmdtemplate import CommandTemplate

try:
    import ws2812_pio as wspio
except ImportError:
    from tests import ws2812_test as wspio


class LedStrip:
    """Attached LED strip which has its own PIO and pixel buffer.

    Provides a class to represent an LED strip and its resources. There should
    be one instance of this class for each physical LED strip attached to the
    controller. Memory will be allocated for a pixel buffer.

    The pixel buffer is an array of 32-bit integers that represents the color
    values of a pixel.  Assuming RGB, then the bits in the integer are arranged
    like this:

        [31:24] - not used
        [23:16] - red value
        [15:8]  - green value
        [7:0]   - blue value

    A client should always use [acquire] to gain access to the buffer and PIO
    resources before writing to the buffer. The method [release] should be
    called when the client no longer needs access to the LED strip.

    :param smid: state machine number to use for PIO
    :param pin: GPIO pin number for the ws2812 signal
    :param numpixels: number of pixels in the string
    """

    def __init__(self, smid: int, pin: int, numpixels: int) -> None:
        self._buf = array.array("I", [0 for _ in range(numpixels * 3)])
        self._numpixels = numpixels
        self._pio = wspio.WS2812(smid, pin)
        self._lock = asyncio.Lock()
        self._user = None

    def __str__(self) -> str:
        return f"sm: {self._pio}, lock: {self._lock.locked()}, user: {self._user}"

    @property
    def buf(self) -> array.array:
        """Get the pixel buffer array."""
        return self._buf

    async def acquire(self, newuser: CommandTemplate) -> None:
        """Acquire resource lock for the strip.

        If the resource is already in use by another client, it requests the
        previous client to stop and then awaits for the lock to released, and
        then acquires the lock.

        :param newuser: client that is taking control of the LED strip
        """
        if self._user:
            self._user.stop()
        await self._lock.acquire()
        self._user = newuser

    def release(self) -> None:
        """Release the lock and clear the current user."""
        self._lock.release()
        self._user = None

    def locked(self) -> bool:
        """Return True if the lock is currently held."""
        return self._lock.locked()

    def clear(self) -> None:
        """Clear the LED strip by setting all pixels to 0 (off), and then
        updating the display."""
        for pix in range(len(self._buf)):
            self._buf[pix] = 0
        self.show()

    def fill(self) -> None:
        """Fill the LED strip with dim white (0x101010)."""
        for pix in range(len(self._buf)):
            self._buf[pix] = 0x101010
        self.show()

    def show(self) -> None:
        """Repaint the strip with the current buffer contents."""
        self._pio.show(self._buf)
