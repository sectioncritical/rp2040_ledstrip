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

# This test driver is meant to run on the pico. It will import the console_std
# module. It uses the write and read function to interact with the user.
#
# To test this on a micropython board this file and the console_std (module
# under test) should be copied to the board. Then use the REPL to import this
# file and the test will run. There should be a make target to take care of
# all this so check the project Makefile.

import time
from console_std import *

console_init()
console_write("This should have no line ending ...")
console_writeln("This should have a line ending")
console_writeln("This should be on its own line")

instr = ""

console_writeln("Type in 123 followed by enter")
console_writeln("Dots will be printed to the console while it is waiting for")
console_writeln("your input to prove it is non-blocking")
console_writeln("You should see the 1 2 3 characters echoed as you type them")

while(True):
    inchars = console_read()
    if inchars:
        console_write(inchars)
        instr += inchars
        if inchars[0] == '\r' or inchars[0] == '\n':
            break
    console_write(".")
    time.sleep_ms(500)

console_writeln("Number of character received: " + str(len(instr)))

if instr[0:3] == "123":
    console_writeln("OK Expected characters were found")
    console_writeln("Line terminator character was: " + str(ord(instr[3])))
else:
    console_writeln("ERROR unexpected input: " + instr)

while(True):
    inchars = console_read()
    if inchars:
        console_writeln("Also received character: " + str(ord(inchar[0])))
    else:
        break

console_writeln("Test ended")
