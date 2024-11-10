#
# SPDX-License-Identifier: 0BSD
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

class CommandTemplate():
    """
    CommandTemplate for implementing commands.

    This is a base class that is used for all commands. Any command (pattern)
    inherits from this class. If you are creating a new command or pattern, create
    a new class using this as a base class:

        from cmdtemplate import CommandTemplate
        ...

        class MyCommand(CommandTemplate):
            ...

    The new command class must implement one required method `render()`. There is
    an optional method, `config()` which is only needed if the new command has
    configuration attributes. Each of these is documented below.

    The new class should also be added to `cmdclasses.py` so that it will be made
    available to the command processor code.
    """

    helpstr = "n/a"
    """Brief help string for the command.

    This will be shown by the help command. It should be pretty short.
    """

    cfgstr = "no configs"
    """Brief help for configuration parameters.

    This will be shown by the `$help,config` command. It should be very short
    list of the parameters and any description.
    """

    #
    def __init__(self):
        self._delay = None

    #
    # cfglist - list-like of strings with config values
    # cfglist[0] is "config" and cfglist[1] is command name
    # so config parameters start with cfglist[2]
    #
    def config(self, cfglist: list[str]) -> None:
        """Optional method for configuring the command.

        This method is used if the command has any configurable attributes. If
        the command has nothing to configure, then this does not need to be
        implemented by the subclass.

        This method will be called when the config command is issued for a
        specific command. For example, if the command has three configurable
        attributes, the config command might look like:

            $config,mycommand,parm1,parm2,parm3

        The method is always passed the attributes as a list of strings. The
        first two items in the list are "config" command itself, and the name
        of the command being configured ("mycommand" in the above example).

        The command class and the command name are related but separate. It is
        possible to have two different named commands that have the same
        underlying command class. In this case, the implementation of `config`
        could have conditional behavior depending on the name of the command.

        All the parameters are passed as strings, but they are almost certainly
        integers, so they need to be converted when they are stored, using
        `int(v)`.

        *Example Implementation*

            def config(self, cfglist):
                # cfglist[0] is "config"
                # cfglist[1] is "mycommand" - the name of the command
                self.attr1 = int(cfglist[2])  # first parameter
                self.attr2 = int(cfglist[3])
                self.attr3 = int(cfglist[4])
                ...
                # possible other processing

        Nothing is returned.
        """
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
        """Required method to carry out the command actions.

        This method is called whenever the command is invoked. Any parameters
        are passed in as a list. For example:

            $mycommand,parm1

        The method is passed a list of strings. The first entry is the command
        name which could be used for conditional behavior depending on the
        command name. The first parameter from the command line is the second
        item in the list.

        A pixel array named `framebuf` is passed to the method. This is an
        array of 32-bit integers that represents the color values of a pixel.
        Assuming RGB, then the bits in the integer are arranged like this:

            [31:24] - not used
            [23:16] - red value
            [15:8] - green value
            [7:0] - blue value

        The `render` method should carry out any actions that are required to
        execute the command. For example if it an LED pattern, then the method
        should calculate how each LED should be lit and store the pixel values
        in the `framebuf` array. `render` needs to calculate the pixel value
        for any pixels it changes, and set the R, G, and B fields to the
        calculated values.

        The `render` method is called using a simple scheduling process. This
        allows for repeating or progressing patterns (a chase for example) to
        be continually recalculated and redrawn.

        `render` can return three different ways:

        * None - this is a one-shot command, does not need to run again
        * 0 - call back immediately - for continuous updating at maximum rate
        * N (where N is int>0) - N is a delay in microseconds, render will be
          called back after that amount of time

        Upon return from `render()`, the LED strip will be updated using the
        pixel values in `framebuf`.

        *Example One-Shot Command*

        ``` py
        # command named "ledset" to turn on a single pixel
        # "$ledset,pixnum,r,g,b"
        #
        def render(self, parmlist, framebuf):
            # parmlist[0] is "ledset"
            # should probably check for valid pixnum (not shown)
            pixnum = int(parmlist[1])
            # get color parameters as integers
            red = int(parmlist[2])
            grn = int(parmlist[3])
            blu = int(parmlist[4])
            # calculate the pixel value for the given color parameters
            color = (red << 16) + (grn << 8) + blu
            # set the specified pixel in the frame buffer
            framebuf[pixnum] = color

            # this one does not need to be repeated, so return None
            return None
        ```

        *Example Periodic Command*

        ``` py

        # the class needs its own variables to track state
        def __init__():
            super().__init__()  # get the superclass
            self._delay = 10000  # 10 ms, overrides default of None
            self._pixnum = 0
            self._pixmax = 100   # could be configurable

        # command named "ledrun" to cause a single pixel to "run" down the strip
        # the lit LED will run from pixel 0 to some limit and then repeat
        # in this example the limit is hard coded, but it could be a
        # configurable attribute
        # "$ledrun,r,g,b"
        #
        def render(self, parmlist, framebuf):
            # parmlist[0] is "ledrun"
            # get color parameters as integers
            red = int(parmlist[1])
            grn = int(parmlist[2])
            blu = int(parmlist[3])
            # calculate the pixel value for the given color parameters
            color = (red << 16) + (grn << 8) + blu

            # clear the last pixel that was lit
            framebuf[self._pixnum] = 0

            # advance the pixel, and set the color
            self._pixnum += 1
            if self._pixnum > self._pixmax:
                self._pixnum = 0  # reset to beginning

            framebuf[self._pixnum] = color  # turn on new pixel

            # repeat after a fixed delay (run periodically)
            return self._delay
        ```





        """
        return None
