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

"""console_std - Console IO implementation using stdin/stdout.

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
def console_init() -> None:
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
