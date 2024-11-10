# LED Controller Command Protocol

**This is WIP and nnot necessarily up to date or completely accurate**

This page explains the command protocol used for the LED Controller. The
protocol itself is mostly hardware independent, but is intended to be carried
over a seerial port. The serial port could be USB serial, or a physical
hardware serial port. At the time of this writing, USB serial is used.

## Goals

The protocol is intended to be both machine and human usable. In "production"
it is expected to controlled from another machine such as Raspberry Pi. For
development, it is convenient for a person to be able to type commands on a
terminal and see the resulting behavior.

To support human-usability, all data is ASCII characters which can be displayed
or typed on a terminal.

To support machine-usability, it uses fixed start and stop characters, and a
delimiter between all fields. This makes it easier to parse.

## Command Protocol

Commands are carried over a serial interface between the host (commanding) and
the target board. This a simple command and acknowledge format. The LED
controller is intended to be commanded by another computer such as a Raspberry
Pi so the protocol is machine friendly. However it is extremely convenient for a
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

**NOTE:** at this time due to a bug, commands must be lower case

### Response Format

The controller will always provide a response. The client should always wait
for a response before sending another command. The responses are:

    $OK\n
    $ERR\n

To keep things simple, these are the only responses. If there is an error there
is no additional diagnostic info unless provided by a debug build.

## Utility Commands

There are some built-in commands, separate from LED pattern commands. For
LED patterns see [Implemented Patterns](implemented-patterns.md).

In any command examples below, the '\n' terminator is not shown, but implied.

### Help

There is a built in help command for human users. It shows a brief line of
help for each implemented command.

    $help

Some commands have configuration parameters. Those commands have brief config
help:

    $help,config

## Config

Some commands have configuration options. A configuration command follows this
pattern:

    $config,<cmdname>,<parm1>,...

Following the config command is the name of the command to configure, followed
by one or more comma-separated parameters.

There will always be at least one parameter because it doesn't make sense to
configure something with zero parameters. If a command is not configurable and
the `config` command invokes it, an error will be returned.

## Add

Internally, all commands are implemented from a class template, kind of like a
plugin. See [adding new commands](add-new-patterns.md) for more details.

The add command lets you add as a new command, any command classes that are
implemented in the code. One way this could be useful is the ability to add a
second instance of an existing command that might be configured differently.
For example, maybe there is a chase pattern command that moves in one direction
over a subset of the string. You could add that same class as a second command
and then use the `config` command to configure a chase over a different subset
of the LED strip and maybe in the opposite direction.

Another way the add command could be useful is in allowing a single set of
firmware with all pattern command classes implement in the code, but only a
subset added at runtime for a specific application. Perhaps on a vehicle there
is one LED strip that is used for brake lights and a custom braking pattern.
And a second strip that is used for turn signals. The same firmware containing
all the possible patterns could be deployed to all the controller boards, and
then each board customized at runtime with the specific commands needed for
each board.

Anyway, maybe its useful, maybe not, but the `add` command looks like this:

    $add,<new-cmd-name>,<class-name>

"new-cmd-name" is a new name for the new command (cannot be an existing command
name). The class name is the source code class name of an existing class.

For example, suppose there is an existing command called `leftchase` and it
uses a class called `LedChase`. Assuming this command is configurable, you
could add a new "rightchase" command like this:

    $add,rightchase,LedChase

Followed by a config:

    $config,rightchase,parm1,etc,...
