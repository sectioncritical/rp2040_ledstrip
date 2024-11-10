Using the LED Controller Firmware
=================================

*Prerequisites*

* [hardware is set up](hardware.md)
* [LED controller firmware is installed](installing.md)

The LED controller firmware ("firmware") is running on the Raspberry Pico
board. It uses a simple serial protocol to accept commands and sends responses.
[The serial protocol](protocol.md) is carried over USB serial port emulation
and is connected to a host computer that sends the commands and processes the
responses.

**TODO:** put simple block diagram here

The firmware is intended to be commanded by a higher level controller. For
example, in a vehicle a Raspberry Pi may be connected to several LED
controllers and send commands to all of them to coordinate patterns across
multiple LED strips. However, the simple command protocol is also human
readable, so it is possible to type commands on a serial terminal

Protocol
--------
See the [protocol](protocol.md) documentation for full details of the serial
protocol. But in brief, it is meant to be usable by human or another program.
The commands and responses all use ASCII characters with delimiters.

**Command**

    $<cmdname>[,<parm1>[,...]]\n

* '$' - start of command
* cmdname - the name of the command (no spaces)
* parm1 - first parameter, if the command requires parameters
* ... - additional required parameters, if any
* '\n' - newline character marks the end of the command

**Response**

The response is simply either `$OK\n` or `$ERROR\n` (where '\n' is newline
character). There is no additional information about the nature of an error.

Using the Terminal
------------------
You can use any serial terminal emulator on your host computer. This project
Makefile has a built-in task for using a terminal, and uses the
[pyserial miniterm utility](https://pyserial.readthedocs.io/en/latest/tools.html#module-serial.tools.miniterm).

The following instructions assume you are using the Makefile method.

First you must set an environment variable `SERPORT` to the serial device of
the connected board. If you use `make boards` you should see a listing that
includes your board and the serial device name. As an example:

    export SERPORT=/dev/cu.usbmodem1424201

Once that is set, you can type `make terminal` and it will start a terminal
session connected to your Pico board. From here you can now type commands. Try
the following to start:

    $help

This should show you a brief help message such as the following:

    $OK

    Commands
    --------
    help    : show list of commands
    config  : config,<cmdname>,parm1,parm2,...
    add     : Add new command (add,newname,ClassName)
    range   : set range to color <range,start,num,r,g,b>
    meter   : meter,<pct 0-100>

If that works then you are propertly connected to the Pico board and the
LED controller firmware is running and responding.

Example
-------
The `range` command is a simple one-shot command that sets one or more LEDs to
a fixed color. It looks like this:

    $range,<start-pixel>,<pixel-count>,<color1>,<color2>,<color3>

The color order depends on your LED strip. They are usually RGB or GRB. The
value for each color is intensity for 0-255. Be aware that not all LED strips
have full 8-bits of intensity setting. Assuming RGB for this example, the
following will set pixels 10 through 19 to green at half intensity:

    $range,10,10,0,127,0

See [Pattern Commands](implemented-patterns.md) for a list of all existing
pattern commands. The [Protocol](protocol.md) document lists other non-pattern
commands.
