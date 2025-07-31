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

"""cmdif - Command Interface Processor.

This module implements a command interface for receiving commands from a
console, processing, the command, and printing results. Commands are
implemented in a standardized way (see [CommandTemplate][ledstrip.cmdtemplate])
to make it "easy" to add additional commands, sort of like a plugin. A
command implementation has a run coroutine and can run once, or can loop with
periodic timing.

Most commands are added from their own modules, but there are some built-in
commands here that are used to support all commands:

* CmdHelp - provide a basic help function
* CmdConfig - provide a way to pass configuration to any command module
* CmdAdd - provide a way to add new command module to the list of commands
* CmdStop - stop a running command
* CmdFreeMem - display amount of free memory to console

This module relies on the presence of the [`console_std`][ledstrip.console_std]
module which provides an abstraction of read and write functions for a console.
This should allow this module to be used with different mechanisms of input and
output.
"""

import asyncio
from collections import OrderedDict
from console_std import console_init, console_writeln, console_write, console_read
import cmdparser
from  cmdtemplate import CommandTemplate
import gc

# TODO error handling for run/setup is not robust

class CmdFreeMem(CommandTemplate):
    """Display amount of free memory.

    This command class uses python gc functions to detemine the amounf of
    free memory. This can be used for diagnostic purposes to evaluate how
    much memory resource is being used by the program.
    """

    helpstr = "show free memory"

    async def run(self, parmlist: list[str]) -> None:
        """Print the amount of free memory."""
        gc.collect()
        freemem = gc.mem_free() # type: ignore[attr-defined]
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

    def __init__(self, cmddict: dict) -> None:
        """Create instance of help command."""
        super().__init__()
        self._dict = cmddict

    def cmdhelp(self) -> None:
        """Show basic help messages to the user."""
        console_writeln("\nCommands")
        console_writeln("--------")
        for cmdname, cmdobj in self._dict.items():
            cmdhelp = cmdobj.helpstr
            console_writeln(f"{cmdname:<8} : {cmdhelp}")
        console_writeln("")

    def cfghelp(self) -> None:
        """Show configuration help to the user."""
        console_writeln("\nConfigs")
        console_writeln("-------")
        for cmdname, cmdobj in self._dict.items():
            cfghelp = cmdobj.cfgstr
            console_writeln(f"{cmdname:<8} : {cfghelp}")
        console_writeln("")

    # this is called whenever parm[0]=='help'
    async def run(self, parmlist: list[str]) -> None:
        """Print command summary to the console."""
        # decide if this is a regular help, or a config help, and then
        # call the appropriate method to show the help to the user
        if len(parmlist) == 2 and parmlist[1] == "config":
            self.cfghelp()
        else:
            self.cmdhelp()

class CmdConfig(CommandTemplate):
    """Provide a configuration command, to configure other commands.

    Some commands have configuration options. This command class provides a
    standard way to set configuration options for a command.

    It is invoked as `config,<cmdname>,parm1,parm2,...`

    The parameters are passed through to the specified command's config handler
    if it has one. No checking is done on the actual parameters.
    """

    helpstr = "config,<cmdname>,parm1,parm2,..."

    def __init__(self, cmddict: dict) -> None:
        """Create instance of config command."""
        super().__init__()
        self._dict = cmddict

    # this is called when parm[0]=='config'
    # parm[1] should be the command to be conigured
    # parm[2] and greater are configuration parameters, which vary depending
    # on the command that is being configured
    async def run(self, parmlist: list[str]) -> None:
        """Update configurable parameters for specified command."""
        # check that there at least one parameter, and that the specified
        # command exists, and then pass to the command's config handler.
        if len(parmlist) >= 3:
            cmdname = parmlist[1]
            if cmdname in self._dict:
                cmdobj = self._dict[cmdname]
                cmdobj.config(parmlist)

class CmdStop(CommandTemplate):
    """Stop a previously running command.

    Because command "run" methods are coroutines, it is possible for them to
    run in a loop. This command provides a way to invoke the "stop" method
    to request that the run loop will exit.

    Normally, a new command willl stop the previous from running, and "stop"
    is not always necessary. But this allows a running pattern to be stopped
    and not replaced with anything else. (for example stop a turn signal)

    It is invoked as `stop,<cmdname>`
    """

    helpstr = "stop,<cmdname>"

    def __init__(self, cmddict: dict) -> None:
        """Create instance of stop command."""
        super().__init__()
        self._dict = cmddict

    # this is called when parm[0]=='stop'
    # parm[1] should be the command to be stop
    async def run(self, parmlist: list[str]) -> None:
        """Request specified command to stop itself."""
        # check that there at least one parameter, and that the specified
        # command exists, and then pass to the command's config handler.
        if len(parmlist) >= 2:
            cmdname = parmlist[1]
            if cmdname in self._dict:
                cmdobj = self._dict[cmdname]
                cmdobj.stop()

#
# removed CmdAdd class for now because it is not used and nuisance to
# maintain, plus it uses code space. If it is needed again, perhaps move to
# main where it has access to the list of ledstrips, which will be needed
# if CmdAdd is re-supported
#
# command class to allow adding other commands
#class CmdAdd(CommandTemplate):
#    """Provide a command that allows adding new commands.
#
#    Any command classes that are implemented and listed in
#    [`cmdclasses.py`][ledstrip.cmdclasses] can be added to the command list.
#    This allows for the existence of many kinds of commands (mostly LED
#    patterns) when only some will be used for a particular installation. Common
#    firmware can be installed on multiple controllers, and the `add` command in
#    combination with the `config` command allows a particular controller to be
#    configured at run time from the console command line.
#    """
#    helpstr = "Add new command (add,newname,ClassName)"
#
#    # provide the cmdinterface so it can add commands
#    def __init__(self, cmdinterface: CmdInterface) -> None:
#        super().__init__()
#        self._ci = cmdinterface
#
#    # TODO add error handling to below
#
#    # this is called when parm[0]=='add'
#    # parm[1] should be the name of the command (how it will be invoked)
#    # parm[2] is the Class name that implements the command (from cmdclasses.py)
#    async def run(self, parmlist: list[str]) -> None:
#        if len(parmlist) == 3:
#            cmdname = parmlist[1]
#            clsname = parmlist[2]
#            cmdobj = globals()[clsname]()
#            self._ci.add_cmd(cmdname, cmdobj)

class CmdInterface:
    """Provides methods for processing command line input."""

    def __init__(self) -> None:
        """Instantiate the command interface (one per system)."""
        self._cmds: OrderedDict = OrderedDict()
        # dictionary format:
        # key - command name as string
        # value - CommandPattern object
        self._cmds["help"] = CmdHelp(self._cmds)
        self._cmds["config"] = CmdConfig(self._cmds)
        #self._cmds["add"] = CmdAdd(self)
        self._cmds["stop"] = CmdStop(self._cmds)
        self._cmds["freemem"] = CmdFreeMem()

        # temporary additional commands
        #self._cmds["meter"] = LedMeter()
        #

        # used for testing to allow run loop to exit
        self._exit = False

        self._cp = cmdparser.CmdParser()
        console_init()

    def add_cmd(self, cmdname: str, cmdobj: CommandTemplate) -> None:
        """Add a new command of the specified class to the command list.

        :param cmdname: name of the new command, must be unique from other
            command names
        :param cmdobj: a [CommandTemplate][ledstrip.cmdtemplate] subclass
            implementing the new command
        """
        self._cmds[cmdname] = cmdobj

    def setup(self, param_list: list[str]) -> CommandTemplate:
        """Start running a new command.

        This is called by the command loop whenever a complete command line is
        received. It uses the input parameter list to determine if the named
        command exists. If so it dispatches the command as a coroutine through
        its `run()` method.

        It sends `$OK` or `$ERR` to the serial console as a reply. If a valid
        command is dispatched, the CommandTemplate object will be returned.
        If the command is not valid then `None` is returned.

        :param param_list: string list of all the command line parameters,
            including the command name which is the first item.
        :return: the [CommandTemplate][ledstrip.cmdtemplate] subclass that
            implements the command, or `None`
        """
        if param_list[0] in self._cmds:
            # if new command is valid, schedule it to run immediately
            cmdobj = self._cmds[param_list[0]]
            asyncio.create_task(cmdobj.run(param_list)) # noqa: RUF006
            console_writeln("$OK")
            return cmdobj
        elif param_list[0] == "exit":
            self._exit = True
        else:
            # if command is not valid, send error message to console
            console_writeln("$ERR")
            return None

    async def run(self) -> None:
        """Command line processing and run loop.

        This method is called from the top level program after it has completed
        initializations. This method should be called as the coroutine main
        event loop using `asycio.run()`. Once it starts this loop runs forever
        unless stopped by setting the attribute `_exit`, which is only done in
        a testing context.

        The run loop processes incoming data from the command line, calls the
        parser, and dispatches commands when a complete command line is
        received.

        Command errors are silently ignored.
        """
        # TODO: consider error handling from call to setup

        # loop forever, with a yield
        while not self._exit:
            # yield
            await asyncio.sleep_ms(1)  # type: ignore[attr-defined]
            # process any new incoming characters
            incoming = console_read()
            if incoming:
                console_write(incoming)     # echo to console
                cmdargs = self._cp.process_input(incoming)

                # if there is a complete new command line, then setup new command
                if cmdargs:
                    self.setup(cmdargs)
