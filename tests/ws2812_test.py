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
# This file implements a stub for the "ws2812_pio" module. The real module
# uses rp2040 hardware which is not present in a standalone micropython test
# environment. This fake module is provided so that other modules dependent
# on ws2812_pio and be tested.

# TODO: possible future improvements
# - instrument this module to be able to verify calls from depending modules
#   are correct

class WS2812():

    def __init__(self, smid: int, pin: int) -> None:
        pass

    def shutdown(self):
        pass

    def show(self, pixarray):
        pass
