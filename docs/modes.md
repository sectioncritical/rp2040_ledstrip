# LED Mode Commands

This is some preliminary documentation about how the commands work and the
description of different blink modes. A lot of things are TBD, especially the
arrangement of the LED strips in the vehicle.

## Command Protocol

Commands are carried over a serial interface using async protocol 115200,N,8,1.
There is a simple command and acknowledge format. The LED controller is
intended to be commanded by another computer such as a Raspberry Pi so the
protocol should be machine friendly. However it is extremely convenient for a
human to be able to exercise the controller using a serial terminal. To help
with machine processing, the format uses framing characters. But all the
commands and acknowledgements are ASCII strings and so can be typed and read
by a human at a terminal.

### Packet Framing

A "packet" starts with a '$' character and is terminated by a newline '\n'. To
be tolerant of CR/LF confusion with different systems and terminals, the
implementation will be tolerant of a terminating character(s) of CR, LF, CRLF,
or LFCR. In the description below `LF` or `\n` is used to mean the terminating
character.

### Command Format

A command follows this format:

    $cmdname,1234,...\n

The first parameter is always a command name. Parameters are comma separated
with no spaces. Additional parameters after the command name are determined by
the type of command.

Everything should generally be lower case, but the implementation is
case-insensitive.

### Response Format

The controller will always provide a response. The client should always wait
for a response before sending another command. The responses are:

    $ok\n
    $err\n

To keep things simple, these are the only responses. If there is an error there
is no additional diagnostic info unless provided by a debug build.

## Commands

The LED controller is always in a `mode`. The mode is changed by a command. The
following table shows the currently defined modes.

**NOTE:** at the time of this writing it is not known exactly how the LED
strips are arranged in the vehicle, nor how many there are or how many separate
controllers are used. The list below is best estimate at this time of how the
modes will be defined.

| Mode      | Parameters    | Description                                               |
|-----------|---------------|-----------------------------------------------------------|
|off        |none           |all off                                                    |
|reverse    |blink rate     |all blink white solid or at settable rate                  |
|brake      |none           |all red                                                    |
|brakehard  |none           |all red rapid blink 3 times then solid                     |
|run        |rate,reverse   |chase pattern with variable speed and color, reversible    |
|turn       |none(see note) |red snake in one direction                                 |
|dazzle     |pattern        |demo patterns for display, random or selectable            |

Notes:

* we may want a day/night mode difference. TBD if this will be commanded per
  mode, or separate modes for day and night
* turn mode will depend on whether there is a separate string per side, or if
  it is a single string across the back. If a single string then a left/right
  parameter will be needed
* brake and brake hard could be combined with a "hard" parameter
* this concept assumes that the different LED strings are separated by
  function. If a string is used as a combined function, for example a single
  strip across the back used for braking and turn signals, then some more
  complexity will need to be introduced to the command set to allow addressing
  or multiple functions at once
* dazzle may be one command with selection parameter, or we may just define
  each dazzle type as a separate command
