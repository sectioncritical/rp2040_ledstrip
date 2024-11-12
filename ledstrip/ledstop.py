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

"""stop - stop running pattern with optional clear."""

from cmdtemplate import CommandTemplate

class LedStop(CommandTemplate):
    """Stop the running pattern with option to clear display.

    This command will stop any running pattern. There is an optional parameter,
    which if '1', will also clear the diplay.

    *Examples*

        $stop
        $stop,0
        $stop,1
    """
    helpstr = "stop running pattern (stop,<clearflag>)"
    cfgstr = "no configs"

    def render(self, parmlist: list[str], framebuf: list[int]):
        clearflag = int(parmlist[1]) if len(parmlist) == 2 else 0
        if clearflag:
            for pix in range(len(framebuf)):
                framebuf[pix] = 0
        # returns None - does not run again
