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

# This file is a simple test driver for testing the ws2812_pio module. It is
# meant to be run on the rp2 target board that already has the ws2812_pio
# module installed.
#
# It will instantiate the module and perform a couple of simple operations to
# verify the module works.

import array
import time
import ws2812_pio as wspio

# Verify test by inspection:
# the first 3 LEDs should light in sequence R, G, B with half second between
# each. The cycle should repeat 10 times.

def run():
    print("running ws2812 test")
    print("you should see 3 LEDs blinking in sequence for about 15 seconds")
    ws = wspio.WS2812(smid=0, pin=16)
    pixels = array.array("I", [0 for _ in range(3)])
    colors = [0x003f00, 0x3f0000, 0x00003f]
    for _ in range(10):
        print("*", end="")
        for pix in range(3):
            pixels[pix] = colors[pix]
            pixels[pix-1] = 0
            ws.show(pixels)
            time.sleep_ms(500)
    for pix in range(3):
        pixels[pix] = 0
    ws.show(pixels)
    time.sleep_ms(100)
    ws.shutdown()
    print("\nTest exiting")

run()

