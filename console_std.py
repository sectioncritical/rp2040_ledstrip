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

"""
console_std - Console IO implementation using stdin/stdout.

This module implements the following functions for console IO using sys.stdin
and sys.stdin. Select polling is used for non-blocking input.

- console_init
- console_write
- console_writeln
- console_read

If you import this module using ``from console_std import *`` then you can
get these function names directly into the namespace and will not need to
use the module.fn notation.
"""

import select
import sys

console_poll = None

# initialize whatever we are using for serial comms
def console_init():
    """Initialize serial IO console.

    This should be called once at the start of the application. It performs
    any initialization needed for this implementation of a serial console.
    """
    global console_poll
    console_poll = select.poll()
    console_poll.register(sys.stdin, select.POLLIN)

def console_write(printstr: str) -> None:
    """Write a string to the console.

    Tha string parameter is written to the console without interpretation or
    adding any line terminators.

    :param printstr: the string to be printed to the console
    """
    sys.stdout.write(printstr)

# write a line to serial console with CRLF termination
def console_writeln(printstr: str) -> None:
    """Write a string to the console with line terminator.

    This performs the same function as ``console_write`` except that it also
    add a line ending.

    :param printstr: the string to be printed to the console
    """
    console_write(printstr)
    console_write("\r\n")

def console_read() -> str:
    """Read available characters from the console input.

    Returns a string with any characters that were read from the console input,
    or ``None`` if there was nothing available.

    :return: string of one or more characters, or None.
    """
    if console_poll.poll(0):
        input = sys.stdin.read(1)
        return input
    return None
