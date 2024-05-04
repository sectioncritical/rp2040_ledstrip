
from cmdtemplate import CommandTemplate

class LedRange(CommandTemplate):
    helpstr = "set range to color <range,start,num,r,g,b>"

    def render(self, parmlist, framebuf):
        dot0 = int(parmlist[1])
        numdots = int(parmlist[2])
        red = int(parmlist[3])
        green = int(parmlist[4])
        blue = int(parmlist[5])
        color = green << 16
        color += red << 8
        color += blue
        for idx in range(numdots):
            framebuf[dot0+idx] = color
