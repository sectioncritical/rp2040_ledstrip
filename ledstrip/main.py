
import asyncio
import cmdif
from console_std import console_writeln
from cmdclasses import *
from  cmdtemplate import CommandTemplate
import ledstrip

# TODO: figure out how to make a "customization" module or plugin that can
# be used for each RGB pico to customize it for its unique patterns while
# reusing all the other code

# provide a command to query the list of LED strips in the system
class CmdStrips(CommandTemplate):
    """Display table of LED strips..

    This command prints a simple table of the instantiated `ledstrip` classes
    for diagnostic purposes.
    """
    helpstr = "show LED strip resources"

    def __init__(self, ledstrips: list[ledstrip.LedStrip]) -> None:
        super().__init__(strip=None)
        self._strips = ledstrips

    async def run(self, parmlist: list[str]) -> None:
        for idx, strip in enumerate(self._strips):
            console_writeln(f"{idx}: {str(strip)}")

# create the led strip instances
strip0 = ledstrip.LedStrip(0, 16, 144)
strip1 = ledstrip.LedStrip(1, 19, 144)

# create the command interface. all commands will be added to the ci
ci = cmdif.CmdInterface()

# create and add all the patterns used by this LED strip controller
stripcmd = CmdStrips([strip0, strip1])
ci.add_cmd("strips", stripcmd)
range0 = LedRange(strip0)
ci.add_cmd("range0", range0)
range1 = LedRange(strip1)
ci.add_cmd("range1", range1)
random = LedRandom(strip0)
ci.add_cmd("random", random)
randomog = LedRandomOG(strip1)
ci.add_cmd("randomog", randomog)
leftturn = LedTurn(strip=strip0, start=0, stop=30)
ci.add_cmd("left", leftturn)
rightturn = LedTurn(strip=strip1, start=0, stop=30)
ci.add_cmd("right", rightturn)
meter = LedMeter(strip0)
ci.add_cmd("meter", meter)

# start up command interface loop as main coroutine loop
# it will dispatch commands as coroutine tasks
#
asyncio.run(ci.run())

# getting here means the main run loop exited, which is not usual
print("RGB LED strip program exited")
