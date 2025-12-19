
import asyncio
import cmdif
from console_std import console_writeln
from cmdclasses import *
from  cmdtemplate import CommandTemplate
import ledstrip

# TODO: figure out how to make a "customization" module or plugin that can
# be used for each RGB pico to customize it for its unique patterns while
# reusing all the other code

# TODO move this to its own file
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
wing_strip = ledstrip.LedStrip(0, 16, 145)
#strip1 = ledstrip.LedStrip(1, 19, 144)

# create the command interface. all commands will be added to the ci
ci = cmdif.CmdInterface()

# create and add all the patterns used by this LED strip controller
stripcmd = CmdStrips([wing_strip])  # list of all strips
ci.add_cmd("strips", stripcmd)
range = LedRange(wing_strip)
ci.add_cmd("range", range)
#range1 = LedRange(strip1)
#ci.add_cmd("range1", range1)
random = LedRandom(wing_strip)
ci.add_cmd("random", random)
#randomog = LedRandomOG(strip1)
#ci.add_cmd("randomog", randomog)
leftturn = LedTurn(strip=wing_strip, start=30, stop=0)
ci.add_cmd("left", leftturn)
rightturn = LedTurn(strip=wing_strip, start=144-30, stop=144)
ci.add_cmd("right", rightturn)
meter = LedMeter(wing_strip)
ci.add_cmd("meter", meter)
brake = LedBrake(wing_strip)
ci.add_cmd("brake", brake)
brakehard = LedBrakeHard(wing_strip)
ci.add_cmd("brakehard", brakehard)

# start up command interface loop as main coroutine loop
# it will dispatch commands as coroutine tasks
#
asyncio.run(ci.run())

# getting here means the main run loop exited, which is not usual
print("RGB LED strip program exited")
