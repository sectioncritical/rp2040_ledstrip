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
#
# TODO:
# - add proper doc comments
# - automation: linting, doc gen, style
# - verify and tweak output timing
# - structured ways to access pixel data
#
# This module implements a driver for WS2812-based LED strips. It uses the
# RP2040 hardware PIO module to bit-bang the protocol.
#
"""Provides a WS2812 LED driver for an RP2040 (Pico) microcontroller.

Utilizes the PIO hardware, and DMA to perform transfers from the pixel buffer
to the PIO output FIFO.
"""

# ruff: noqa: F821

import array
import rp2
from machine import Pin

# Timing for the ws2812 serial protocol. We use 3 time segments. It is high
# during the T1, then high or low during T2 depending on the bit value, then
# low during T3. The cycle time is chosen to be 64 ns, which gives the
# following values for each segment.
#
# T1 - 384 ns, 6 cycles
# T2 - 320 ns, 5 cycles
# T3 - 512 ns, 8 cycles

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW, out_init=rp2.PIO.OUT_LOW,
             fifo_join=rp2.PIO.JOIN_TX)
def ws2812_shifter() -> None:
    """Shift 24-bit LED values to a GPIO per the WS2812 protocol.

    *This is not a callable function.*

    **The following describes module internals and is not part of the API.**

    This is an RP2040 PIO state machine program to shift 24-bit values per the
    WS2812 protocol. Pixel values are represented as 24-bit values, 8-bits each
    of RGB (order changes depending on the specific LED used). Bits are encoded
    with a varying pulse width - a wider pulse for a 1 and a shorter pulse for
    a 0. There is always a high period and a low period.

    32-bits are pulled from the PIO TX FIFO. This is the pixel value that was
    written to the FIFO by the application. The lower 24-bits contain the pixel
    data. First the top 8 bits are discarded. Then the remaining 24-bits are
    considered one at a time.

    First the output is driven high for a fixed period of time. This is the
    high time regardless whether the bit is 1 or 0. Then the output is driven
    low or high depending on the bit value, for a fixed amount of time. This is
    the variable section. Finally, the output is driven low for a fixed amount
    of time. This is the low time for both high and low bit values.

    Once all 24-bits are shofted out, the cycle repeats and the next word is
    read from the FIFO. If there are no more data in the FIFO, then the state
    machine blocks with the output in a low state. This ensures the latching
    period occurs at the end of a set of pixels.
    """
    pull(block)                 # wait for next pixel value
    out(x, 8)                   # throw away upper 8 bits
    label("more_bits")
    set(pins, 1).delay(5)       # fixed high time
    out(pins, 1).delay(4)       # output set according to bit value
    set(pins, 0).delay(6)       # fixed low time
    jmp(not_osre, "more_bits")  # repeat until all 24 bits are shifted
    wrap()                      # back to top for next pixel value

class WS2812:
    """PIO drive for WS2812-based LED strips.

    Provides a class that uses the Raspberry Pico RP20204 PIO to implement a
    serial driver for WS2812-like LED strips. The LED pixel data is kept in an
    array that is passed to a function that copies the data to the PIO state
    machine where it is shifted out on a GPIO in the proper format.

    Recommended usage::

        # use state machine 0, and IO pin 16
        ws2812 = WS2812(smid=0, pin=16)
        ...
        # create 3 pixel array of red, green, blue
        pixels = array.array("I", [0x00FF00, 0xFF0000, 0x0000FF])
        # write the pixel data to the LED strip
        ws2812.show(pixels)
        ...

    :param smid: state machine number to use for PIO
    :param pin: GPIO pin number to use for WS2812 signal
    """

    def __init__(self, smid: int, pin: int) -> None:
        """Class constructor for WS2812."""
        # debug pin, if needed
        #self.debug_pin = Pin(23, Pin.OUT)
        #self.debug_pin.low()

        # create the state machine
        self._ws_pin = Pin(pin, Pin.OUT)
        # 64 ns, divider is 8
        self._sm = rp2.StateMachine(smid, ws2812_shifter, freq=15625000,
                          set_base=self._ws_pin, out_base=self._ws_pin)
        self._sm.active(1)

        # set up dma for state machine
        # code snippets from: https://docs.micropython.org/en/latest/library/rp2.DMA.html
        self._dma = rp2.DMA()
        pio_num = 0 if smid < 4 else 1
        dreq_idx = (pio_num << 3) + smid
        self.dmactrl = self._dma.pack_ctrl(size=2, inc_write=False, treq_sel=dreq_idx)

    def __str__(self) -> str:
        return f"ws2812: {self._sm}, {self._ws_pin}"

    def shutdown(self) -> None:
        """Halt the state machine.

        This will stop the state machine from running. Once this method is
        called, the object can no longer be used.
        """
        self._sm.active(0)

    def show(self, pixarray: array.array) -> None:
        """Send pixel data to ws2812 GPIO pin.

        Copies an array of pixel data to the WS2812 PIO driver. The pixel data
        is formatted as an iterable of 32-bit integers. The pixel data is 3
        colors, each 8-bits, in the lower 24 bits. The upper 8 bits are
        ignored. The ordering of RGB depends on the specific LEDs used so there
        is not a universal setting. However GRB is common.

        If the ordering is GRB:
        - ``0xFF0000`` is green
        - ``0x00FF00`` is red
        - ``0x0000FF`` is blue

        It is best to allocate an array or list for your pixel data at the
        beginning of the program and modify the contents, as opposed to
        creating a new list each time you want to write pixel data.

        You can use a regular python list, but micropython also provides an
        ``array`` type that is a C-like array and that may be more efficient.
        """
        #self.debug_pin.high()

        sm = self._sm
        xfer_count = len(pixarray)
        self._dma.config(read=pixarray, write=sm, count=xfer_count,
                         ctrl=self.dmactrl, trigger=True)
        while self._dma.active():
            pass

        #self.debug_pin.low()
