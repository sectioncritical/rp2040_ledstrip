
class CommandTemplate():
    #
    # brief help string for the command
    #
    helpstr = "n/a"
    cfgstr = "no configs"

    #
    def __init__(self):
        self._delay = None

    #
    # cfglist - list-like of strings with config values
    # cfglist[0] is "config" and cfglist[1] is command name
    # so config parameters start with cfglist[2]
    #
    def config(self, cfglist):
        pass

    #
    # parmlist - list-like of strings with run-time parameters
    # parmlist[0] is command name
    # so command parms start with parmlist[1]
    # framebuf - implementation specific display device but usually
    #           a pixel array
    #
    # returns: None - no further calls needed
    #          0 - call again immediately to run pattern
    #          >0 - microseconds to delay before calling again
    def render(self, parmlist, framebuf):
        return None
