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
call_cmd = ""

def reset_globals():
    global call_count
    global call_parms
    global call_fn
    global call_cmd
    call_count = 0
    call_parms = None
    call_fn = ""
    call_cmd = ""

# basic command, one-shot
class BasicCommand(CommandTemplate):
    helpstr = "basic command"

    def render(self, parmlist, framebuf):
        global call_count
        global call_parms
        global call_fn
        global call_cmd
        call_count += 1
        call_parms = parmlist
        call_fn = "render"
        call_cmd = "basic"
        return None

    def config(self, parmlist):
        global call_count
        global call_parms
        global call_fn
        global call_cmd
        call_count += 1
        call_parms = parmlist
        call_fn = "config"
        call_cmd = "basic"

# repeat command, runs each time run is called
class RepeatCommand(CommandTemplate):
    helpstr = "repeat command"

    def render(self, parmlist, framebuf):
        global call_count
        global call_parms
        global call_fn
        global call_cmd
        call_count += 1
        call_parms = parmlist
        call_fn = "render"
        call_cmd = "repeat"
        return 0    # indicate should be called repeatedly

    def config(self, parmlist):
        global call_count
        global call_parms
        global call_fn
        global call_cmd
        call_count += 1
        call_parms = parmlist
        call_fn = "config"
        call_cmd = "repeat"

class TestBasicAdd(unittest.TestCase):

    def setUp(self):
        reset_globals()
        self.ci = cmdif.CmdInterface()
        self.assertTrue(self.ci)
        # check internal state of cmdif
        self.assertIsNone(self.ci._cmdobj)
        self.assertIsNone(self.ci._cmdparms)
        self.assertEqual(0, self.ci._sched)

    # initially there are 3 commands populated
    def test_initial(self):
        self.assertEqual(3, len(self.ci._cmds))
        self.assertTrue("help" in self.ci._cmds)
        self.assertTrue("config" in self.ci._cmds)
        self.assertTrue("add" in self.ci._cmds)

    def test_add(self):
        newcmd = BasicCommand()
        self.ci.add_cmd("basic", newcmd)
        self.assertEqual(4, len(self.ci._cmds))
        self.assertTrue("basic" in self.ci._cmds)
        cmdobj = self.ci._cmds["basic"]
        self.assertEqual(newcmd, cmdobj)

class TestSetup(unittest.TestCase):

    def setUp(self):
        reset_globals()
        self.ci = cmdif.CmdInterface()
        self.assertTrue(self.ci)
        # check internal state of cmdif
        self.assertIsNone(self.ci._cmdobj)
        self.assertIsNone(self.ci._cmdparms)
        self.assertEqual(0, self.ci._sched)
        # add basic command so we can test operations on it
        self.newcmd = BasicCommand()
        self.ci.add_cmd("basic", self.newcmd)
        self.assertEqual(4, len(self.ci._cmds))
        self.assertTrue("basic" in self.ci._cmds)
        cmdobj = self.ci._cmds["basic"]
        self.assertEqual(self.newcmd, cmdobj)

    # verify valid command gets set up for execution
    def test_setup_good(self):
        newparms = ["basic", 1]
        self.ci.setup(newparms)
        self.assertEqual(self.newcmd, self.ci._cmdobj)
        self.assertEqual(newparms, self.ci._cmdparms)
        self.assertNotEqual(self.ci._sched, 0)

    # verify invalid command does not set up execution
    def test_setup_bad(self):
        newparms = ["foo", 1]
        self.ci.setup(newparms)
        self.assertIsNone(self.ci._cmdobj)
        self.assertIsNone(self.ci._cmdparms)
        self.assertEqual(0, self.ci._sched)

    # verify valid command gets set up for execution, followed by bad
    # command which undoes setup
    def test_setup_good_then_bad(self):
        newparms = ["basic", 1]
        self.ci.setup(newparms)
        self.assertEqual(self.newcmd, self.ci._cmdobj)
        self.assertEqual(newparms, self.ci._cmdparms)
        self.assertNotEqual(self.ci._sched, 0)
        newparms = ["foo", 1]
        self.ci.setup(newparms)
        self.assertIsNone(self.ci._cmdobj)

class TestExecBasic(unittest.TestCase):

    def setUp(self):
        reset_globals()
        self.ci = cmdif.CmdInterface()
        self.assertTrue(self.ci)
        # check internal state of cmdif
        self.assertIsNone(self.ci._cmdobj)
        self.assertIsNone(self.ci._cmdparms)
        self.assertEqual(self.ci._sched, 0)
        # add basic command so we can test operations on it
        self.newcmd = BasicCommand()
        self.ci.add_cmd("basic", self.newcmd)
        self.assertEqual(len(self.ci._cmds), 4)
        self.assertTrue("basic" in self.ci._cmds)
        cmdobj = self.ci._cmds["basic"]
        self.assertEqual(self.newcmd, cmdobj)

    # no command is set up so nothing should happen
    def test_exec_nocmd(self):
        ret = self.ci.exec()
        self.assertFalse(ret)
        self.assertEqual(call_count, 0)
        self.assertIsNone(call_parms)
        self.assertEqual(call_fn, "")
        self.assertEqual(call_cmd, "")

    # basic is setup, then should exec one time
    def test_exec_basic(self):
        newparms = ["basic", 2]
        self.ci.setup(newparms)
        ret = self.ci.exec()
        # stuff should have happened
        self.assertTrue(ret)    # need to repaint
        # render was called
        self.assertEqual(call_count, 1)
        self.assertEqual(newparms, call_parms)
        self.assertEqual(call_fn, "render")
        self.assertEqual(call_cmd, "basic")
        # cmdobj was reset to not run again
        self.assertIsNone(self.ci._cmdobj)

        # call it again verify nothing else happened
        ret = self.ci.exec()
        self.assertFalse(ret)
        # callback data is unchanged from previous
        self.assertEqual(call_count, 1)
        self.assertEqual(newparms, call_parms)
        self.assertEqual(call_fn, "render")
        self.assertEqual(call_cmd, "basic")

class TestExecRepeat(unittest.TestCase):

    def setUp(self):
        reset_globals()
        self.ci = cmdif.CmdInterface()
        self.assertTrue(self.ci)
        # check internal state of cmdif
        self.assertIsNone(self.ci._cmdobj)
        self.assertIsNone(self.ci._cmdparms)
        self.assertEqual(self.ci._sched, 0)
        # add basic command so we can test operations on it
        self.newcmd = RepeatCommand()
        self.ci.add_cmd("repeat", self.newcmd)
        self.assertEqual(len(self.ci._cmds), 4)
        self.assertTrue("repeat" in self.ci._cmds)
        cmdobj = self.ci._cmds["repeat"]
        self.assertEqual(self.newcmd, cmdobj)

    # no command is set up so nothing should happen
    def test_exec_nocmd(self):
        ret = self.ci.exec()
        self.assertFalse(ret)
        self.assertEqual(call_count, 0)
        self.assertIsNone(call_parms)
        self.assertEqual(call_fn, "")
        self.assertEqual(call_cmd, "")

    # repeat is setup, then should exec mulitple times
    def test_exec_repeat(self):
        newparms = ["repeat", 3]
        self.ci.setup(newparms)
        ret = self.ci.exec()
        # stuff should have happened
        self.assertTrue(ret)    # need to repaint
        # render was called
        self.assertEqual(call_count, 1)
        self.assertEqual(newparms, call_parms)
        self.assertEqual(call_fn, "render")
        self.assertEqual(call_cmd, "repeat")
        # cmdobj is still valid
        self.assertIsNotNone(self.ci._cmdobj)

        # call it again verify runs again
        ret = self.ci.exec()
        self.assertTrue(ret)
        # callback data is unchanged but call count is bumped
        self.assertEqual(call_count, 2)
        self.assertEqual(newparms, call_parms)
        self.assertEqual(call_fn, "render")
        self.assertEqual(call_cmd, "repeat")

        # call it 10 more times
        for _ in range(10):
            ret = self.ci.exec()
            self.assertTrue(ret)
        self.assertEqual(call_count, 12)
        self.assertEqual(newparms, call_parms)
        self.assertEqual(call_fn, "render")
        self.assertEqual(call_cmd, "repeat")

class TestConfig(unittest.TestCase):

    def setUp(self):
        reset_globals()
        self.ci = cmdif.CmdInterface()
        self.assertTrue(self.ci)
        # check internal state of cmdif
        self.assertIsNone(self.ci._cmdobj)
        self.assertIsNone(self.ci._cmdparms)
        self.assertEqual(self.ci._sched, 0)
        # add basic command so we can test operations on it
        self.newcmd = BasicCommand()
        self.ci.add_cmd("basic", self.newcmd)
        self.assertEqual(len(self.ci._cmds), 4)
        self.assertTrue("basic" in self.ci._cmds)
        cmdobj = self.ci._cmds["basic"]
        self.assertEqual(self.newcmd, cmdobj)

    # setup config for basic command, then exec and verify config happened
    def test_config(self):
        newparms = ["config", "basic", 4, 5]
        self.ci.setup(newparms)
        # this should cause config for basic command to be called
        ret = self.ci.exec()
        # config doesnt actually need repaint, but render is called so
        # the return indication is True
        self.assertTrue(ret)
        # config was called
        self.assertEqual(call_count, 1)
        self.assertEqual(newparms, call_parms)
        self.assertEqual(call_fn, "config")
        self.assertEqual(call_cmd, "basic")
        # cmdobj was reset to not run again
        self.assertIsNone(self.ci._cmdobj)

if __name__ == "__main__":
    unittest.main()
