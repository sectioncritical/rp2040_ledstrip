TLDR - Just Tell Me How to Use it Stop Explaining Things
========================================================

After reading all the docs I wrote, I realize it is a lot of information. Here
I attempt to give you the steps in the simplest way possible, but there may
still be some stuff you have to understand.

Set up your computer
--------------------

All of my instructions assume you are using a "Unix-y" environment and you
type commands in a terminal window. This means you have:

* git (if you want to clone the project)
* python3
* GNU Make
* bash-compatible shell

There may be some other dependency that I didn't list here.

If you are using Mac or Linux you are probably fine although you may need to
use the package manager to install something (like GNU Make if you don't have
it).

If you are using Windows, you will need a compatible environment such as
[Cygwin](https://en.wikipedia.org/wiki/Cygwin) or 
[WSL](https://en.wikipedia.org/wiki/Windows_Subsystem_for_Linux).

Get the hardware and set it up
------------------------------

Get an [Adafruit Scorpio Board](https://www.adafruit.com/product/5650) and plug
it into your host/development computer. This will be good enough to install the
LED Controller firmware. But if you want to connect LEDs and see some blinky
lights, then you will have to read and understand the [Hardware](hardware.md)
section.

Get the project code
--------------------

If you don't want to use git,
[download a zip from GitHub](https://github.com/sectioncritical/rp2040_ledstrip/archive/refs/heads/main.zip).

If you want to use git, you can clone it:

    git clone https://github.com/sectioncritical/rp2040_ledstrip.git

Use command line
----------------

At this point you should be typing in a terminal window, and in the directory
named `rp2040_ledstrip`. There should be a file named `Makefile` there.

Install MicroPython
-------------------

This only needs to be done once. If your board does not already have
MicroPython, then you will need to
[install MicroPython](installing.md#installing-micropython)

Check board communication
-------------------------

**NOTE:** the very first time you do this step, you will see bunch of messages
go by as the python environment is set up. This will only happen the first
time.

Type `make boards` and you should see a list of attached boards, one of which
should be your Scorpio board:

*Example*

    ❯ make boards
    /dev/cu.BLTH None 0000:0000 None None
    /dev/cu.Bluetooth-Incoming-Port None 0000:0000 None None
    /dev/cu.usbmodem1424201 df625857831b4436 239a:80f2 MicroPython Board in FS mode

Install the program onto the Scorpio
------------------------------------

`make deploy` will copy the files to the board.

*Example*

    ❯ make deploy
    cp ledstrip/console_std.py :console_std.py
    cp ledstrip/cmdclasses.py :cmdclasses.py
    cp ledstrip/cmdtemplate.py :cmdtemplate.py
    cp ledstrip/cmdif.py :cmdif.py
    cp ledstrip/cmdparser.py :cmdparser.py
    cp ledstrip/ws2812_pio.py :ws2812_pio.py
    cp ledstrip/main.py :main.py
    cp ledstrip/ledmeter.py :ledmeter.py
    cp ledstrip/ledrange.py :ledrange.py

Then `make reset` to restart the board.

Start serial terminal to Scorpio
--------------------------------

From the list of boards you did earlier, set the SERPORT environment variable
to the device name of your board.

*Example*

    export SERPORT=/dev/cu.usbmodem1424201

Then `make terminal` and you should be talking to the Scorpio board.

    ❯ make terminal
    venv/bin/python -m serial.tools.miniterm /dev/cu.usbmodem1424201 115200
    --- Miniterm on /dev/cu.usbmodem1424201  115200,8,N,1 ---
    --- Quit: Ctrl+] | Menu: Ctrl+T | Help: Ctrl+T followed by Ctrl+H ---

Send commands
-------------

Type `$help` and hit return. You should see something like this:

*Example*

    $help
    $OK

    Commands
    --------
    help    : show list of commands
    config  : config,<cmdname>,parm1,parm2,...
    add     : Add new command (add,newname,ClassName)
    range   : set range to color <range,start,num,r,g,b>
    meter   : meter,<pct 0-100>

The exact list of commands may be different.
If you have an LED strip correctly attached and powered, you can light up some
pixels as a test:

    $range,0,10,0,0,15

This should light the first 10 pixels as blue.
