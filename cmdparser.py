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

# TODO:
# - add proper doc comments
# - automation: linting, doc gen, style
# - consider if it needs to be more memory efficient. it creates and destroys
#   bytearrays

# This module implements a simple command line processor. It is meant to be
# able to accept 1 or more bytes at a time, as they arrive from a serial port
# for example. Once a proper start and stop framing characters are seen, it
# returns all the arguments as a list of strings.
#
# It is intended to be used from a main loop that is checking for serial or
# other command input. As bytes are recieved they are passed to this parser
# and once a properly formatted command is received it returns the args to
# the main loop caller. The client then decides what to do with the args. This
# module does not interpret the contents of any incoming commands. It just
# validates the format and breaks into list of args.
#
# The format is:
# - command starts with '$', anything else is ignored until start character
#   is seen
# - there can be one or more args, which are ascii characters, each separated
#   by a comma with no spaces
# - the command terminates with a newline \n. It can also tolerate a \r
#   or combinations of \r\n or \n\r just to accomodate whatever various serial
#   terminal programs do when you hit enter.
# - everything is interpreted as ascii, if you pass a unicode character you
#   will probably get garbage out
# - it does not echo anything, that is up to client if needed
# - everything outside of $...\n is ignored
#
# A note about efficiency: it creates bytearrays during the process which are
# then eventually freed. If it causes a memory usage or gc problem then it
# can be revisited to see how to reuse a single allocated array instead of
# creating new ones on the fly.
#
# The client is meant to only call process_input() and not the other methods
# in this class.
#
# Usage:
#
# import cmdparser
#
# cp = cmdparser.CmdParser()
#
# while (processing main loop):
#     ...
#     if incoming_bytes_are_available():
#         incoming = get_the_incoming_bytes()
#         cmdargs = cp.process_input(incoming)
#         # if not None, then there is new args
#         if cmdargs:
#             numargs = len(cmdargs)
#             process_command(cmdargs)
#             ...
#     ...
#
class CmdParser():
    def __init__(self):
        self._buf = None

    # INTERNAL METHOD
    # break apart the command line and return args as strings
    # cmdline is bytes-like
    # should be string beginning with '$' and ending with '\n'
    # contents should be comma separated list of args, no spaces
    # expects only ascii input
    # any alpha will be converted to lower case
    # returns args as list of strings (one or more)
    # or an empty list which means there was an error
    def parse_cmd(self, cmdline):
        # check the line start and end terminators first
        startch = cmdline[0]
        stopch = cmdline[-1]

        # if input is properly framed
        if startch == ord('$') and stopch == ord('\n'):

            # convert it to string and lower case
            cmdstr = cmdline.decode("ascii").lower()
            cmdstr = cmdstr[1:-1]  # remove terminators
            cmdargs = cmdstr.split(',')
            # return the parsed input args
            return cmdargs

        return []  # bad start/stop chars, return error

    # INTERNAL METHOD
    # inbuf is bytes-like one or more characters
    # returns None or bytearray buffer containing properly framed command
    # this method is separated from process_input() to make it easier to test
    def assemble_cmd(self, inbuf):
        # process all incoming characters
        for ch in inbuf:
            # if it is a $ that is start of a command
            if ch == ord('$'):
                self._buf = bytearray([ch])
            # only process anything else if there is already an ongoing input
            # IOW ignore anything that comes in not preceeded with a $
            elif self._buf:
                # if line terminator comes in then attempt to parse the
                # command line, return result to caller
                if ch == ord('\n') or ch == ord('\r'):
                    self._buf.append(ord('\n'))
                    ret = self._buf
                    self._buf = None  # reset the input buffer
                    return ret
                # any other character just store it
                else:
                    self._buf.append(ch)
        return None

    # PUBLIC METHOD
    # inbuf is bytes-like one or more characters
    # returns None or list of command line components as strings
    # empty list means there was an error
    def process_input(self, inbuf):
        buf = self.assemble_cmd(inbuf)
        if buf:
            return self.parse_cmd(buf)
        return None
