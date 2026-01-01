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
    inherits from this class. If you are creating a new command or LED pattern,
    create a new class using this as a base class:

        from cmdtemplate import CommandTemplate
        ...

        class MyCommand(CommandTemplate):
            ...

    The new class should also be added to `cmdclasses.py` so that it will be
    made available to the command processor code.

    Derived classes must implement one required method `run()`. This method
    will be invoked as a coroutine task and so must be declared `async`.  There
    is an optional method, `config()` which is only needed if the new command
    has configuration attributes. Each of these is documented below.

    If the command is an LED pattern then at object creation you must also
    provide an existing [LedStrip][ledstrip.ledstrip] that the command pattern
    will use for display. If the command does not use any LED resources, then
    no other parameters are required.

    Usage:

    ``` py
    import ledstrip

    from cmdclasses import MyCommand
    # OR from cmdclasses import *

    # create an instance of LED strip (hardware resource)
    strip = ledstrip.LedStrip(0, 16, 100)

    # create instance of MyCommand
    mycommand = MyCommand(strip)
    ...
    ```
    """

    helpstr = "n/a"
    """Brief help string for the command.

    This will be shown by the help command. It should be pretty short.
    """

    cfgstr = "no configs"
    """Brief help for configuration parameters.

    This will be shown by the `$help,config` command. It should be very short
    list of the parameters and any description. If your command has no
    configuration parameters, you can just use this default.
    """

    # if LedStrip is not provided then the command should not try to render
    # any led strip output. this can be used for non-rendering commands like
    # help and diagnostics
    def __init__(self, strip: LedStrip=None) -> None:
        self._strip = strip
        self._stoprequest = False

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
                if len(cfglist) != 5: # optional sanity check
                    return
                # cfglist[0] is "config"
                # cfglist[1] is "mycommand" - the name of the command
                self.attr1 = int(cfglist[2])  # first parameter
                self.attr2 = int(cfglist[3])
                self.attr3 = int(cfglist[4])
                ...
                # possible other processing

        Nothing is returned and no errors are indicated.
        """
        pass

    # parmlist - list-like of strings with run-time parameters
    # parmlist[0] is command name
    # so command parms start with parmlist[1]
    #
    # This method will be run as a coroutine, If it is using the led strip, it
    # must take the resource lock at the start and release it at the end.
    # If it has a loop, it must have a yield within the loop. For loop commands
    # the loop must depend on `self._stoprequest` and exit (cleanly) if
    # stoprequest becomes `True`.
    # If must exit gracefully for all exit conditions including stoprequest or
    # on any error condition.
    #
    async def run(self, parmlist: list[str]) -> None:
        """Required method to carry out the command actions.

        This method is called whenever the command is invoked. Any parameters
        are passed in as a list. For example:

            $mycommand,parm1

        The method is passed a list of strings. The first entry is the command
        name which could be used for conditional behavior depending on the
        command name. The first parameter from the command line is the second
        item in the list.

        The `run` method should carry out any actions needed for the command.
        If the command is a one-shot, then just perform the statements in
        sequence and return. If the command runs in a loop, or does anything
        that takes a long time to complete, then it must have some kind of
        coroutine yield in the loop or long-running algorithm. The most common
        yield is a sleep, like this:

            await asyncio.sleep_ms(1)

        Using a 1 ms wait ensures that this coroutine will yield and let the
        rest of the system run. The delay can obviously be longer if the loop
        timing requires it. Most continuous running LED patterns will have a
        loop with some kind of timing. Note that `sleep_ms()` is available in
        micropython but not the standard python asyncio library. The "ms"
        version is useful in an embedded system and lets us avoid using a float
        to specify a delay time.

        If the command is an LED pattern it must use the `LedStrip` in
        `self._strip` to write to the pixel buffer. Get the buffer using the
        property `self._strip.buf`. The pixel buffer is an array of 32-bit
        integers that represents the color values of a pixel.  Assuming RGB,
        then the bits in the integer are arranged like this:

            [31:24] - not used
            [23:16] - red value
            [15:8] - green value
            [7:0] - blue value

        If the command is using an LED strip, then it must also acquire the
        LedStrip resource at the start, using `self.strip._acquire(), and
        release it at the end. If the command runs in a loop, then it must
        depend on the state of `self._stoprequest` and gracefully exit if
        stoprequest it True. No matter the reason for exiting, including any
        errors, the LED strip must be released if it was acquired earlier.

        Here is an example of a simple loop that writes some LEDs in a loop.

        Example:

        ``` py
        # this command blinks some LEDs on and off. It is passed a start and
        # ending pixel number
        #     $simpleled,start,stop
        async def run(self, parmlist: list[str]) -> None:
            # check for correct number of parms, and get parm values
            if len(parmlist) != 3:
                return
            start = int(parmlist[1])
            stop = int(parmlist[2])

            # since we use the LED strip, we must acquire access first
            # this will block until available
            await self._strip.acquire(self) # must pass self as parameter

            # get local variable for buffer, this will be faster in loops
            pixelbuf = self._strip.buf

            # we dont know the value in the pixel buf to start, so clear
            # the pixels we use.
            # normally since this is a loop it should yield but for this
            # example it just runs through
            for pix in range(start, stop):
                pixelbuf[pix] = 0

            # start the loop, depend on state of stoprequest
            while not self._stoprequest:
                # turn all the pixels on or off
                for pix in range(start, stop):
                    pixelbuf[pix] ^= 0x101010
                # display the pixel buffer
                self._strip.show()
                # we must always yield in the forever loop
                await asyncio.sleep_ms(200)

            # loop will exit if stoprequest becomes True
            # for our clean up we will clear the pixels we used and
            # clear the display. then release the ledstrip resource
            for pix in range(start, stop):
                pixelbuf[pix] = 0
            self._strip.show()
            self._strip.release
            #done
        ```
        """
        # body of the run function. if it does not use LED strip, then it
        # can perform its function and return.
        #
        # if the function is continuous running, like an ongoign blink pattern,
        # the it should monitor self._stoprequest and gracefully exit when this
        # is True
        #
        # if it has any long or non-terminating loops, then it should
        # yield with at least asyncio.sleep_ms(1). You cannot use 0 for the
        # wait because that will not yield
        #
        # If the function uses the LED strip for output, then it must acquire
        # the resource lock for the strip first, and release it at the end
        #
        # there must be no path where the function can exit without freeing
        # the resource lock

        # Example
        #
        # # get some local variable of stuff we need often
        # pixbuf = self._strip._buf
        #
        # # get the resource lock (will block)
        # self._strip.acquire(self)
        #
        # # some kind of run loop
        # while ...
        #     ... do stuff
        #     self._strip.show()
        #     asyncio.sleep_ms(...) # at least 1
        #     if self._stoprequest:
        #         ... whatever cleanup
        #         break
        #
        # self._strip.release()  ## IMPORTANT
        return

    def stop(self) -> None:
        """Request that a running command stop.

        This only sets the internal `stoprequest` flag. It is up to the logic
        in `run` to recognize the request and perform a graceful return.

        Usually there is no reason for a subclass to override this method.
        """
        self._stoprequest = True
