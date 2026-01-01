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
