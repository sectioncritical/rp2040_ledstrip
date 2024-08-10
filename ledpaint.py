
from cmdtemplate import CommandTemplate

class LedPaint(CommandTemplate):
    helpstr = "repaint the display"

    def render(self, parmlist, framebuf):
        # None will cause it to not rerun command, and to redraw
        return None
