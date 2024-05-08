
from cmdtemplate import CommandTemplate
from ledmeter import LedMeter

class DualMeter(CommandTemplate):
    helpstr = "meter2,pct,pct (0-100)"
    cfgstr = "start,stop,r0,rN,g0,gN,b0,bN,start,stop,r0,rN,g0,gN,b0,bN"

    def __init__(self):
        super().__init__()
        self._m1 = LedMeter()
        self._m2 = LedMeter()

    #
    # cfglist is list of string parameters
    # 0 - config command
    # 1 - meter command
    # 2 - start pixel index
    # 3 - stop pixel index (inclusive)
    # pixel indexes can go in either direction
    # 4 - starting r (the r value at start pixel)
    # 5 - ending r   (the r value at stop pixel)
    # 6 - starting g (the r value at start pixel)
    # 7 - ending g   (the r value at stop pixel)
    # 8 - starting b (the r value at start pixel)
    # 9 - ending b   (the r value at stop pixel)
    # 10-17 start,stop,... for second meter
    #
    def config(self, cfglist):
        # for the first meter we can just pass the command line as-is
        self._m1.config(cfglist)
        # for the second meter we need to take a slice of cfglist so the
        # parms are lined up right
        # starting at index 8 ensures the start parameter is in the 3rd
        # slot which is what config is expecting
        self._m2.config(cfglist[8:])

    def render(self, parmlist, framebuf):
        self._m1.render(parmlist, framebuf)
        self._m2.render(parmlist[1:], framebuf)
        return None
