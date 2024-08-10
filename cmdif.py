
from collections import OrderedDict
from console_std import *
import cmdparser
from  cmdtemplate import CommandTemplate
from cmdclasses import *
import time

# TODO add error return from render
# or figure out error propagation chain exec->update->render
# so that $OK or $ERR is correct

class CmdHelp(CommandTemplate):
    helpstr = "show list of commands"

    def __init__(self, cmddict):
        super().__init__()
        self._dict = cmddict

    def cmdhelp(self):
        console_writeln("\nCommands")
        console_writeln("--------")
        for cmdname, cmdobj in self._dict.items():
            cmdhelp = cmdobj.helpstr
            console_writeln(f"{cmdname:<8}: {cmdhelp}")
        console_writeln("")

    def cfghelp(self):
        console_writeln("\nConfigs")
        console_writeln("-------")
        for cmdname, cmdobj in self._dict.items():
            cfghelp = cmdobj.cfgstr
            console_writeln(f"{cmdname:<8}: {cfghelp}")
        console_writeln("")

    def render(self, parmlist, framebuf):
        if len(parmlist) == 2 and parmlist[1] == "config":
            self.cfghelp()
        else:
            self.cmdhelp()
        return None

class CmdConfig(CommandTemplate):
    helpstr = "config,<cmdname>,parm1,parm2,..."

    def __init__(self, cmddict):
        super().__init__()
        self._dict = cmddict

    def render(self, parmlist, framebuf):
        if len(parmlist) >= 3:
            cmdname = parmlist[1]
            if cmdname in self._dict:
                cmdobj = self._dict[cmdname]
                cmdobj.config(parmlist)
        return None

# command class to allow adding other commands
class CmdAdd(CommandTemplate):
    helpstr = "Add new command (add,newmane,ClassName)"

    # provide the cmdinterface so it can add commands
    def __init__(self, cmdinterface):
        super().__init__()
        self._ci = cmdinterface

    # TODO add error handling to below

    def render(self, parmlist, framebuf):
        if len(parmlist) == 3:
            cmdname = parmlist[1]
            clsname = parmlist[2]
            cmdobj = globals()[clsname]()
            self._ci.add_cmd(cmdname, cmdobj)
        return None

class CmdInterface():
    def __init__(self, framebuf=None):
        self._cmds = OrderedDict()
        # dictionary format:
        # key - command name as string
        # value - CommandPattern object
        self._cmds["help"] = CmdHelp(self._cmds)
        self._cmds["config"] = CmdConfig(self._cmds)
        self._cmds["add"] = CmdAdd(self)

        # temporary additional commands
        self._cmds["range"] = LedRange()
        self._cmds["meter"] = LedMeter()
        self._cmds["2meter"] = DualMeter()
        self._cmds["paint"] = LedPaint()
        #

        self._cp = cmdparser.CmdParser()
        self._framebuf = framebuf
        self._cmdobj = None
        self._cmdparms = None
        self._sched = 0
        console_init()

    #
    # cmdname - string name of command
    # cmdobj - CommandPattern instance implementing a command
    def add_cmd(self, cmdname, cmdobj):
        self._cmds[cmdname] = cmdobj

    # setup a new command
    # given command line parameters input,
    # first item is command name and remaining are cmd args
    # determine if command exists and if so, set up for executing in a loop
    # send okay/err message to console depending on whether command exists
    #
    # param_list is command line parameters
    # param_list[0] is command name
    # remaining items in param_list are run time parms
    #
    # note: this will cancel any running command, even if incoming command
    # is invalid
    def setup(self, param_list):
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

    # executes current running command according to scheduled delay
    # if scheduled time has elapsed then call render, else do nothing
    #
    # return True if render was called, False otherwise
    # render being called implies the frame buffer was updated and so the
    # client should repaint. however some commands such as help dont alter
    # the frame buffer. these will still indicate True because render was
    # called
    def exec(self):
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
                elif delay < 0:
                    # command doesnt want repaint
                    # treat as None, but return false to not repaint
                    self._cmdobj = None  # dont run again
                    return False  # dont repaint
                else:
                    # schedule next run time
                    self._sched = time.ticks_add(now, delay)
                return True     # need to repaint

        # frame buffer was not updated so no need to repaint
        return False

    # processes incoming command line and runs scheduled commands
    # returns True if frame buffer was updated (caller should repaint)
    # this is not technically true for all commands such as help
    # any non-drawing commands will still indicate update needed
    def run(self):
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
