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

"""
cmdif - Command Interface Processor.

This module implements a command interface for receiving commands from a
console, processing, the command, and printing results. Commands are
implemented in a standardized way (see [CommandTemplate][ledstrip.cmdtemplate])
to make it "easy" to add additional commands, sort of like a plugin. Any
command implementation can schedule itself to run once, repeatedly, or with
periodic timing.

Most commands are added from their own modules, but there are some built-in
commands here that are used to support all commands:

* CmdHelp - provide a basic help function
* CmdConfig - provide a way to pass configuration to any command module
* CmdAdd - provide a way to add new command module to the list of commands

This module relies on the presence of the [`console_std`][ledstrip.console_std]
module which provides an abstraction of read and write functions for a console.
This should allow this module to be used with different mechanisms of input and
output.
"""

from collections import OrderedDict
from console_std import *
import cmdparser
from  cmdtemplate import CommandTemplate
from cmdclasses import *
import time
import gc

# TODO add error return from render
# or figure out error propagation chain exec->update->render
# so that $OK or $ERR is correct

class CmdFreeMem(CommandTemplate):
    helpstr = "show free memory"
    def render(self, parmlist, framebuf):
        gc.collect()
        freemem = gc.mem_free()
        console_writeln(f"free mem: {freemem}")

class CmdHelp(CommandTemplate):
    """Provide a basic help command.

    This command class provides two commands to show help to the user. It uses
    strings that are part of the CommandTemplate as the help message.

    The two commands are:

    * `help` - show simple help message for every installed command
    * `help,config` - show configuration options for a command, if any

    The help is automatic for each command as long as the implementation
    provides a help string.
    """
    helpstr = "show list of commands"

    def __init__(self, cmddict):
        super().__init__()
        self._dict = cmddict

    def cmdhelp(self):
        """Show basic help messages to the user."""
        console_writeln("\nCommands")
        console_writeln("--------")
        for cmdname, cmdobj in self._dict.items():
            cmdhelp = cmdobj.helpstr
            console_writeln(f"{cmdname:<8} : {cmdhelp}")
        console_writeln("")

    def cfghelp(self):
        """Show configuration help to the user."""
        console_writeln("\nConfigs")
        console_writeln("-------")
        for cmdname, cmdobj in self._dict.items():
            cfghelp = cmdobj.cfgstr
            console_writeln(f"{cmdname:<8} : {cfghelp}")
        console_writeln("")

    # this is called whenever parm[0]=='help'
    def render(self, parmlist, framebuf):
        # decide if this is a regular help, or a config help, and then
        # call the appropriate method to show the help to the user
        if len(parmlist) == 2 and parmlist[1] == "config":
            self.cfghelp()
        else:
            self.cmdhelp()
        return None

class CmdConfig(CommandTemplate):
    """Provide a configuration command, to configure other commands.

    Some commands have configuration options. This command class provides a
    standard way to set configuration options for a command.

    It is invoked as `config,<cmdname>,parm1,parm2,...`

    The parameters are passed through to the specified command's config handler
    if it has one. No checking is done on the actual parameters.
    """
    helpstr = "config,<cmdname>,parm1,parm2,..."

    def __init__(self, cmddict):
        super().__init__()
        self._dict = cmddict

    # this is called when parm[0]=='config'
    # parm[1] should be the command to be conigured
    # parm[2] and greater are configuration parameters, which vary depending
    # on the command that is being configured
    def render(self, parmlist, framebuf):
        # check that there at least one parameter, and that the specified
        # command exists, and then pass to the command's config handler.
        if len(parmlist) >= 3:
            cmdname = parmlist[1]
            if cmdname in self._dict:
                cmdobj = self._dict[cmdname]
                cmdobj.config(parmlist)
        return None

# command class to allow adding other commands
class CmdAdd(CommandTemplate):
    """Provide a command that allows adding new commands.

    Any command classes that are implemented and listed in
    [`cmdclasses.py`][ledstrip.cmdclasses] can be added to the command list.
    This allows for the existence of many kinds of commands (mostly LED
    patterns) when only some will be used for a particular installation. Common
    firmware can be installed on multiple controllers, and the `add` command in
    combination with the `config` command allows a particular controller to be
    configured at run time from the console command line.
    """
    helpstr = "Add new command (add,newname,ClassName)"

    # provide the cmdinterface so it can add commands
    def __init__(self, cmdinterface):
        super().__init__()
        self._ci = cmdinterface

    # TODO add error handling to below

    # this is called when parm[0]=='add'
    # parm[1] should be the name of the command (how it will be invoked)
    # parm[2] is the Class name that implements the command (from cmdclasses.py)
    def render(self, parmlist, framebuf):
        if len(parmlist) == 3:
            cmdname = parmlist[1]
            clsname = parmlist[2]
            cmdobj = globals()[clsname]()
            self._ci.add_cmd(cmdname, cmdobj)
        return None

class CmdInterface():
    """Provides methods for processing command line input."""
    def __init__(self, framebuf=None):
        self._cmds = OrderedDict()
        # dictionary format:
        # key - command name as string
        # value - CommandPattern object
        self._cmds["help"] = CmdHelp(self._cmds)
        self._cmds["config"] = CmdConfig(self._cmds)
        self._cmds["add"] = CmdAdd(self)
        self._cmds["freemem"] = CmdFreeMem()

        # temporary additional commands
        self._cmds["range"] = LedRange()
        self._cmds["meter"] = LedMeter()
        self._cmds["randomog"] = LedRandomOG()
        self._cmds["random"] = LedRandom()
        self._cmds["stop"] = LedStop()
        #

        self._cp = cmdparser.CmdParser()
        self._framebuf = framebuf
        self._cmdobj = None
        self._cmdparms = None
        self._sched = 0
        console_init()

    def add_cmd(self, cmdname: str, cmdobj: CommandTemplate) -> None:
        """Adds a new command of the specified class to the command list.

        :param cmdname: name of the new command, must be unique from other
            command names
        :param cmdobj: a [CommandTemplate][ledstrip.cmdtemplate] subclass
            implementing the new command
        """
        self._cmds[cmdname] = cmdobj

    def setup(self, param_list: list[str]) -> None:
        """Setup to start running a new command.

        This is called by the command loop whenever a complete command line is
        received. It uses the input parameter list to determine if the named
        command exists. If so it sets up for executing in the exec loop.

        It send `$OK` or `$ERR` to the serial console as a reply. Any currently
        running command will be canceled, even if the new command is invalid.

        :param param_list: string list of all the command line parameters,
            including the command name which is the first item.
        """
        if param_list[0] in self._cmds:
            # if new command is valid, schedule it to run immediately
            self._cmdobj = self._cmds[param_list[0]]
            self._cmdparms = param_list
            self._sched = time.ticks_us()
            console_writeln("$OK")
        else:
            # if command is not valid, cancel anything in progress and
            # indicate error to console
            self._cmdobj = None
            console_writeln("$ERR")

    def exec(self) -> bool:
        """Execute currently scheduled command.

        This method is called repeatedly from the run loop. It checks to see
        if any command is scheduled to run, and if so calls the `render()`
        method for that command. The return value determines how the command
        is rescheduled. The return value is:

        * None - do not run again
        * int(0) - run again immediately
        * int(N) > 0 - run after N ticks have elapsed, in microseconds

        The return value is `True` if the command was run, or `False` if not.

        **NOTES:** if render() was called, the `True` return will cause the
        LED strip to be repainted, even if the frame buffer was not updated.
        Some commands do not even affect the LED status. In the future consider
        a way for render() itself to indicate if a repaint is needed.
        """
        # check for scheduled command
        if self._cmdobj:
            # get the current time and compare to scheduled time
            now = time.ticks_us()
            if time.ticks_diff(now, self._sched) >= 0:
                # time has elapsed so run the command
                delay = self._cmdobj.render(self._cmdparms, self._framebuf)
                # process the return from the command ...
                if delay is None:
                    self._cmdobj = None  # doesnt need to run again
                elif delay == 0:
                    self._sched = now    # run again immediately
                else:
                    # schedule next run time
                    self._sched = time.ticks_add(now, delay)
                return True     # need to repaint

        # frame buffer was not updated so no need to repaint
        return False

    def run(self) -> bool:
        """Command line processing and run loop.

        This method is called repeatedly from the top level run loop. It
        processes incoming data from the command line, calls the parser, and
        dispatches commands when a complete command line is received.

        It returns whatever `exec()` returns, which is used as a repaint signal
        at the top level.
        """
        # process any new incoming characters
        incoming = console_read()
        if incoming:
            console_write(incoming)     # echo to console
            cmdargs = self._cp.process_input(incoming)

            # if there is a complete new command line, then setup new command
            if cmdargs:
                self.setup(cmdargs)

        # run existing scheduled command
        return self.exec()
