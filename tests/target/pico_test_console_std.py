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
