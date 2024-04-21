
from collections import OrderedDict
from console_std import *
import cmdparser

class CmdInterface():
    def __init__(self):
        self._cmds = OrderedDict()
        # dictionary format:
        # key - command name as string
        # value - tuple:
        # 0 - function to execute the command
        # 1 - help string for the command
        # 2 - list of 0 or more config items specific for the command
        #     (can be empty)
        self._cmds["help"] = (self.cmd_help, "show list of commands", [])
        self._cp = None

    # command format
    # param_list - list of all command line parameters, including command name
    # config_list - list of optional config items needed by the command
    def cmd_help(self, param_list, config_list):
        console_writeln("\nCommands")
        console_writeln("--------")
        for key, value in self._cmds.items():
            console_writeln(f"{key:<8}: {value[1]}")
        console_writeln("")
        return None

    def add_cmd(self, cmdname, cmdfn, cmdhelp, cmdcfg):
        self._cmds[cmdname] = (cmdfn, cmdhelp, cmdcfg)

    # param_list is 0 or more command line parameters
    # param_list[0] is interpreted as the command name
    def exec(self, param_list):
        if param_list[0] in self._cmds:
            cmdentry = self._cmds[param_list[0]]
            cmdfn = cmdentry[0]
            cfg_list = cmdentry[2]
            cmdfn(param_list, cfg_list)
            console_writeln("$OK")
        else:
            console_writeln("$ERR")

    def run(self):
        if not self._cp:
            self._cp = cmdparser.CmdParser()
        console_init()
        while True:
            incoming = console_read()
            if incoming:
                console_write(incoming)     # echo to console
                cmdargs = self._cp.process_input(incoming)
                if cmdargs:
                    self.exec(cmdargs)
