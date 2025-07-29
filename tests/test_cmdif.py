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

# TODO: figure out how to add test for the CmdAdd class.
# right now any classes that can be added must be imported into cmdif
# namespace. I dont know a simple way to get the test class importable into
# cmdif without having clutter we dont want for the production code.

# this is meant to be run using micropython and the mpy unittest module
# the test is called directly because unittest module does not work when
# invoked as a module. see the accompanying Makefile to see how the
# test is invoked.
#
# It might also work using regular python with regular unittest but I have
# not tested that.

# This unit test exercises the APIs and internal logic of the "cmdif"
# module. That module runs a command interface and dispatches commands

import unittest
import asyncio

from ledstrip import cmdif
from cmdtemplate import CommandTemplate
from ledstrip import ledstrip

# some globals used for tracking test states and events
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

    async def run(self, parmlist):
        global call_count
        global call_parms
        global call_fn
        global call_cmd
        call_count += 1
        call_parms = parmlist
        call_fn = "run"
        call_cmd = "basic"

    def config(self, parmlist):
        global call_count
        global call_parms
        global call_fn
        global call_cmd
        call_count += 1
        call_parms = parmlist
        call_fn = "config"
        call_cmd = "basic"

# long running command that loops until stopped
class LoopingCommand(CommandTemplate):
    helpstr = "looping command"

    def __init__(self):
        super().__init__()
        self.loop_counter = 0
        self.is_running = False

    async def run(self, parmlist):
        global call_count
        global call_parms
        global call_fn
        global call_cmd
        self.loop_counter = 0
        call_count += 1
        call_parms = parmlist
        call_fn = "run"
        call_cmd = "looping"
        while not self._stoprequest:
            self.is_running = True
            self.loop_counter += 1
            await asyncio.sleep(0.1)
        self.is_running = False

# command that uses a led strip (LedStrip class)
# use of led strip requires getting and releasing a resource lock
# this test class is used to verify this mechanism operation
class LedCommand(CommandTemplate):
    helpstr = "led resource command"

    def __init__(self, strip):
        super().__init__(strip)
        self.loop_counter = 0
        self.is_running = False

    # this run method acquires and frees the ledstrip resource lock in
    # the same way as would be needed by an LED pattern generator that
    # uses a pixel buffer and ws2812 strip driver
    async def run(self, parmlist):
        global call_count
        global call_parms
        global call_fn
        global call_cmd
        self.loop_counter = 0
        call_count += 1
        call_parms = parmlist
        call_fn = "run"
        call_cmd = "led"
        await self._strip.acquire(self)
        while not self._stoprequest:
            self.is_running = True
            self.loop_counter += 1
            await asyncio.sleep(0.1)
        self.is_running = False
        self._strip.release()

class TestBasicAdd(unittest.TestCase):

    def setUp(self):
        reset_globals()
        self.ci = cmdif.CmdInterface()
        self.assertTrue(self.ci)
        # get base number of built in commands
        self.numcmds = len(self.ci._cmds)

    # initially there are 3 commands populated
    def test_initial(self):
        self.assertEqual(self.numcmds, len(self.ci._cmds))
        self.assertTrue("help" in self.ci._cmds)
        self.assertTrue("config" in self.ci._cmds)
        self.assertTrue("add" in self.ci._cmds)

    def test_add(self):
        newcmd = BasicCommand()
        self.ci.add_cmd("basic", newcmd)
        self.assertEqual(self.numcmds+1, len(self.ci._cmds))
        self.assertTrue("basic" in self.ci._cmds)
        cmdobj = self.ci._cmds["basic"]
        self.assertEqual(newcmd, cmdobj)

# the following tests all call "cmdif.setup" to decode and dispatch commands
# that are being tested. Normally setup is called from the main event loop
# which runs as a coroutine, and all commands are dispatched using
# asyncio.run(). therefore setup should be called from each test case as a
# coroutine. That is the reason for async methods below and asyncio.run()
# calls.
#
class TestRun(unittest.TestCase):

    def setUp(self):
        reset_globals()
        self.ci = cmdif.CmdInterface()
        self.assertTrue(self.ci)
        # add basic command so we can test operations on it
        self.basic_cmd = BasicCommand()
        self.ci.add_cmd("basic", self.basic_cmd)
        self.assertTrue("basic" in self.ci._cmds)
        cmdobj = self.ci._cmds["basic"]
        self.assertEqual(self.basic_cmd, cmdobj)
        # add looping command so we can test operations on it
        self.loop_cmd = LoopingCommand()
        self.ci.add_cmd("looping", self.loop_cmd)
        self.assertTrue("looping" in self.ci._cmds)
        cmdobj = self.ci._cmds["looping"]
        self.assertEqual(self.loop_cmd, cmdobj)
        # create an LED strip resource to be used with following commands
        self.strip = ledstrip.LedStrip(0, 16, 100);
        # led LED resource using command to test lock acquire/release
        self.led_cmd = LedCommand(self.strip)
        self.ci.add_cmd("led", self.led_cmd)
        self.assertTrue("led" in self.ci._cmds)
        cmdobj = self.ci._cmds["led"]
        self.assertEqual(self.led_cmd, cmdobj)
        # another command instance that uses resource lock
        self.led2_cmd = LedCommand(self.strip)
        self.ci.add_cmd("led2", self.led2_cmd)
        self.assertTrue("led2" in self.ci._cmds)
        cmdobj = self.ci._cmds["led2"]
        self.assertEqual(self.led2_cmd, cmdobj)

    # verify valid command runs
    async def async_test_setup_good(self):
        newparms = ["basic", 1]
        ret = self.ci.setup(newparms) # should run command as coro
        self.assertEqual(ret, self.basic_cmd)    # verify no error on dispatch
        self.assertEqual(call_count, 0) # verify has not run yet, before yield
        await asyncio.sleep(0.1)  # yield, allow coro to run
        # verify the command was run
        self.assertEqual(call_count, 1)
        self.assertEqual(newparms, call_parms)
        self.assertEqual(call_fn, "run")
        self.assertEqual(call_cmd, "basic")

    def test_setup_good(self):
        asyncio.run(self.async_test_setup_good())

    # verify invalid command does not run and returns error
    async def async_test_setup_bad(self):
        newparms = ["foo", 1]
        ret = self.ci.setup(newparms)
        self.assertIsNone(ret) # error in command
        await asyncio.sleep(0.1)
        # verify no command was run
        self.assertEqual(call_count, 0)
        self.assertIsNone(call_parms)
        self.assertEqual(call_fn, "")
        self.assertEqual(call_cmd, "")

    def test_setup_bad(self):
        asyncio.run(self.async_test_setup_bad())
    
    # run looping command and verify it keeps running until stop
    async def async_test_looping(self):
        newparms = ["looping", 1]
        # cmdobj is the instance of the command we invoked
        # can use it to access internals for test purposes
        cmdobj = self.ci.setup(newparms)
        self.assertEqual(cmdobj, self.loop_cmd)    # verify no error on dispatch
        # command should be running as a coro, but we have to yield
        # allow it to run for 1 second then check some things
        self.assertEqual(call_count, 0)
        await asyncio.sleep(0.2) # needs to be longer than delay in "run"
        # check normal call entry point stuff
        self.assertEqual(call_count, 1)
        self.assertEqual(newparms, call_parms)
        self.assertEqual(call_fn, "run")
        self.assertEqual(call_cmd, "looping")
        # now check that looper is running. count should increase
        self.assertTrue(cmdobj.is_running)
        self.assertTrue(cmdobj.loop_counter > 0)
        # save the loop counter  to check it again
        saved_loop_counter = cmdobj.loop_counter
        # let it run some more
        await asyncio.sleep(0.5)
        # check it is still running
        self.assertTrue(cmdobj.is_running)
        self.assertTrue(cmdobj.loop_counter > saved_loop_counter)
        # send stop command, wait a moment, then verify it stopped
        newparms = ["stop", "looping"]
        ret = self.ci.setup(newparms)
        self.assertTrue(ret)
        await asyncio.sleep(0.3)
        self.assertFalse(cmdobj.is_running)
        saved_loop_counter = cmdobj.loop_counter
        await asyncio.sleep(0.2)
        self.assertEqual(saved_loop_counter, cmdobj.loop_counter)

    def test_looping(self):
        asyncio.run(self.async_test_looping())

    # test "led" command which uses ledstrip resources
    # this test validates the resource lock/release mechanism
    # we already verify a command loop can be stopped in the above test,
    # so this is about the handling of the ledstrip resource lock
    async def async_test_led(self):
        # run command and verify it is running
        newparms = ["led", 1]
        cmdobj = self.ci.setup(newparms)
        self.assertEqual(cmdobj, self.led_cmd)
        # command should be running as a coro, but we have to yield
        # allow it to run for a few ticks then check some things
        self.assertEqual(call_count, 0)
        await asyncio.sleep(0.2) # needs to be longer than delay in "run"
        # check normal call entry point stuff
        self.assertEqual(call_count, 1)
        self.assertEqual(newparms, call_parms)
        self.assertEqual(call_fn, "run")
        self.assertEqual(call_cmd, "led")
        self.assertTrue(cmdobj.is_running)
        # verify the resource lock on ledstrip
        self.assertTrue(self.strip.locked())
        self.assertEqual(self.strip._user, self.led_cmd)

        # run a second command
        reset_globals()
        newparms = ["led2", 2]
        cmdobj2 = self.ci.setup(newparms)
        self.assertEqual(cmdobj2, self.led2_cmd)
        # at this point new command is scheduled but not running
        # verify first task is still running
        self.assertTrue(cmdobj.is_running)
        # and new one is not
        self.assertFalse(cmdobj2.is_running)
        # yielding here should cause the first task to stop and
        # new one to start
        await asyncio.sleep(0.2)
        # check normal call entry point stuff
        self.assertEqual(call_count, 1)
        self.assertEqual(newparms, call_parms)
        self.assertEqual(call_fn, "run")
        self.assertEqual(call_cmd, "led")
        self.assertFalse(cmdobj.is_running)
        self.assertTrue(cmdobj2.is_running)
        # verify the resource lock on ledstrip, new command should own the lock
        self.assertTrue(self.strip.locked())
        self.assertEqual(self.strip._user, self.led2_cmd)

    def test_led(self):
        asyncio.run(self.async_test_led())

class TestConfig(unittest.TestCase):

    def setUp(self):
        reset_globals()
        self.ci = cmdif.CmdInterface()
        self.assertTrue(self.ci)
        # add basic command so we can test operations on it
        self.newcmd = BasicCommand()
        self.ci.add_cmd("basic", self.newcmd)
        self.assertTrue("basic" in self.ci._cmds)
        cmdobj = self.ci._cmds["basic"]
        self.assertEqual(self.newcmd, cmdobj)

    # setup config for basic command, then exec and verify config happened
    async def async_test_config(self):
        newparms = ["config", "basic", 4, 5]
        ret = self.ci.setup(newparms)
        self.assertTrue(ret)
        # this should cause config for basic command to be called
        await asyncio.sleep(0.1)
        # config was called
        self.assertEqual(call_count, 1)
        self.assertEqual(newparms, call_parms)
        self.assertEqual(call_fn, "config")
        self.assertEqual(call_cmd, "basic")

    def test_config(self):
        asyncio.run(self.async_test_config())

if __name__ == "__main__":
    unittest.main()
