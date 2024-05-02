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

# Unit tests for the cmdif.py command interface.
#
# To run:
#     python -m unittest -v test_cmdif.py
#
# I recommend using a venv although this test and cmdif do not require
# any installed packages.

# Update for micropython testing. The above does not work if running unit
# tests with micropython. See the Makefile to see how the test is set up.

# TODO: figure out how to add test for the CmdAdd class.
# right now any classes that can be added must be imported into cmdif
# namespace. I dont know a simple way to get the test class importable into
# cmdif without having clutter we dont want for the production code.

import unittest
import cmdif
from cmdtemplate import CommandTemplate

call_count = 0
call_parms = None
call_fn = ""

class FooCommand(CommandTemplate):
    helpstr = "foo command"

    def render(self, parmlist, framebuf):
        global call_count
        global call_parms
        global call_fn
        call_count += 1
        call_parms = parmlist
        call_fn = "render"

    def config(self, parmlist):
        global call_count
        global call_parms
        global call_fn
        call_count += 1
        call_parms = parmlist
        call_fn = "config"

class TestAddMethod(unittest.TestCase):

    def setUp(self):
        global call_count
        global call_parms
        global call_fn
        self.ci = cmdif.CmdInterface()
        self.assertTrue(self.ci)
        call_count = 0
        call_parms = None
        call_fn = ""
        self.assertIsNone(call_parms)
        self.assertEqual(0, call_count)
        self.assertEqual("", call_fn)

    # initially there are 3 commands populated
    def test_initial(self):
        self.assertEqual(3, len(self.ci._cmds))
        self.assertTrue("help" in self.ci._cmds)
        self.assertTrue("config" in self.ci._cmds)

    def test_add(self):
        foocmd = FooCommand()
        self.ci.add_cmd("foo", foocmd)
        self.assertEqual(4, len(self.ci._cmds))
        self.assertTrue("foo" in self.ci._cmds)
        cmdobj = self.ci._cmds["foo"]
        self.assertEqual(foocmd, cmdobj)

    def test_exec(self):
        foocmd = FooCommand()
        self.ci.add_cmd("foo", foocmd)
        fooparms = ["foo", 1]
        self.ci.exec(fooparms)
        self.assertEqual(fooparms, call_parms)
        self.assertEqual(1, call_count)
        self.assertEqual("render", call_fn)

    def test_exec_bad(self):
        foocmd = FooCommand()
        self.ci.add_cmd("foo", foocmd)
        fooparms = ["bar", 2]
        self.ci.exec(fooparms)
        self.assertIsNone(call_parms)
        self.assertEqual(0, call_count)

    def test_config(self):
        foocmd = FooCommand()
        self.ci.add_cmd("foo", foocmd)
        fooparms = ["config", "foo", 3]
        self.ci.exec(fooparms)
        self.assertEqual(fooparms, call_parms)
        self.assertEqual(1, call_count)
        self.assertEqual("config", call_fn)

if __name__ == "__main__":
    unittest.main()
