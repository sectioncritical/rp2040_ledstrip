
from time import sleep_us

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
    def render(self, parmlist, framebuf):
        pass

    #
    # parmlist - list-like of strings with run-time parameters
    # framebuf - implementation specific display device but usually
    #           a pixel array
    # returns True if it should be called again, False if one-shot
    #
    def update(self, parmlist=None, framebuf=None):
        self.render(parmlist, framebuf)
        if self._delay is None:
            return False
        if self._delay != 0:
            time.sleep_us(self._delay)
        return True

"""
class MeterPattern(LedPattern):
    def render(self, parms):
        pix = self._pix
        dot0 = self._dot0
        numdots = self._dots
        pct = int(parms[0])
        litdots = (numdots * pct) // 100
        for idx in range(litdots):
            # calculate percentage of red and green
            # for low idx it is mostly red and idx gets bigger
            # the red decreases and the green increases
            red = (64 * (numdots - idx)) // numdots
            green = (64 * idx) // numdots
            pix[dot0 + idx] = (green << 16) + (red << 8)
        for idx in range(litdots, numdots):
            pixels[dot0 + idx] = 0
"""
