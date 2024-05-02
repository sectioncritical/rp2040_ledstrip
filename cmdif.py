
from collections import OrderedDict
from console_std import *
import cmdparser
from  cmdtemplate import CommandTemplate
from cmdclasses import *

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

class CmdInterface():
    def __init__(self, framebuf=None):
        self._cmds = OrderedDict()
        # dictionary format:
        # key - command name as string
        # value - CommandPattern object
        self._cmds["help"] = CmdHelp(self._cmds)
        self._cmds["config"] = CmdConfig(self._cmds)
        self._cmds["add"] = CmdAdd(self)
        self._cp = cmdparser.CmdParser()
        self._framebuf = framebuf
        console_init()

    #
    # cmdname - string name of command
    # cmdobj - CommandPattern instance implementing a command
    def add_cmd(self, cmdname, cmdobj):
        self._cmds[cmdname] = cmdobj

    # param_list is 0 or more command line parameters
    # param_list[0] is interpreted as the command name
    # remaining items in list, if any, are run-time parameters
    def exec(self, param_list):
        if param_list[0] in self._cmds:
            cmdobj = self._cmds[param_list[0]]
            cmdobj.update(param_list, self._framebuf)
            console_writeln("$OK")
        else:
            console_writeln("$ERR")

    def run(self):
        incoming = console_read()
        if incoming:
            console_write(incoming)     # echo to console
            cmdargs = self._cp.process_input(incoming)
            if cmdargs:
                self.exec(cmdargs)
