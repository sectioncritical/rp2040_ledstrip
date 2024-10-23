Car LED Strip Controller
========================

**This is work-in-progress and early development. Don't count on anything
working or the docs being up to date.**

This project is for controlling LED strips intended for use on a car. It
expects to run on a Raspberry Pico RP2040 board, using MicroPython. The
prototyping hardware is the
[Adafruit Feather RP2040 Scorpio](https://www.adafruit.com/product/5650). The
LED strips are WS2812 compatible strip such as [these from Adafruit](
https://www.adafruit.com/product/2970).

The Scorpio board is designed to be a driver for LEDs or LED strips.

We decided to use MicroPython instead of Adafruit's CircuitPython for reasons.

The controller code accepts commands via USB serial port and implements a set
of patterns that might be useful for a car.

License
-------
This project uses the
[Zero-Clause BSD License](https://opensource.org/license/0bsd/). See the
[LICENSE file](LICENSE.md) for actual license text. Basically, you can do
whatever you want with this project but I am not responsible for anything.

Issue Tracking
--------------
See further down.

Documents
---------
Some preliminary documentation can be found in the [`docs`](docs/) directory.

Makefile
--------
A makefile is used as a helper for common tasks. You can try:

    make help

to see all the available tasks.

Virtual Environment
-------------------
All of the tasks for this project use the python virtual environment (venv) for
installing all dependencies and python based tools. The Makefile can create and
maintain the `venv` and the venv is used for all tasks.

For all of the remaining discussion below, it is assumed that the venv is
installed and activated or that the Makefile is used to perform the tasks.

Assumption: your system has `python3` on the executable path.

Installing the virtual environment is not necessary as a separate step. It will
be done automatically the first time you `make` something that needs it. But if
you want to manage it separately you can do the following:

* `make venv` - installs the virtual environment
* `make cleanvenv` - removes the virtual environment

If you want to use the venv outside of the Makefile, you can activate it from
the command prompt:

    . venv/bin/activate

If you use `make cleanvenv`, be sure to `deactivate` first. Usually it is not
necessary to clean the venv.

Talking to Target Board
-----------------------
There is a Makefile with targets for most common tasks. It uses [mpremote](
https://docs.micropython.org/en/latest/reference/mpremote.html) to talk to the
target. Mpremote will be installed automatically if you use the Makefile to
manage the venv.

You can make sure that `mpremote` is working by using the target:

    make boards

You should see a list of serial ports and the Scorpio board should be listed.
Here is how it shows up on my mac:

    /dev/cu.usbmodem1424201 df625857831b4436 239a:80f2 MicroPython Board in FS mode

Some other things you can do:

* `make reset` - resets the target - do this after updating the main program
* `make ls` - list all the files on the target

Installing the LED program
--------------------------
To install the LED program, all the necessary python files need to be copied to
the target board. Do this with:

    make deploy

After that you should do a `make reset` and then the target should be ready to
go.

There is a `make repl` task which should let you enter the *REPL* on the target
board. However, if the LED program is installed and working, then the REPL
cannot be entered. The program and the REPL use the same USB serial connection
so there is no way to "exit" the main program and enter the REPL. You can
delete a file on the target board such as `main.py` and then the LED program
will not run. I dont have a make task for this but you can use
`mpremote rm main.py` from the command line (with the activated venv).

Using the Terminal
------------------
You can type commands to the LED program using the terminal. First you have to
set the environment variable `SERPORT` to be the serial port device. From the
"boards" example above, my board is device `/dev/cu.usbmodem1424201`. Depending
on your shell, set the variable something like this:

    export SERPORT=/dev/cu.usbmodem1424201

After that you can `make terminal` and you are now talking to the LED program
running on the target board. Try typing the following in the termina:

    $help

Hit return, and you should see some help text listed.

Installing MicroPython
----------------------
In case you need to install/update MicroPython on the target, here are some
brief instructions:

* get firmware from here: <https://micropython.org/download/ADAFRUIT_FEATHER_RP2040/>.
  That link is for the Adafruit Feather RP2040 board which is very similar to
  the Scorpio board. At the time of this writing there was not a separate
  firmware released for the Scorpio board.
* Rename the downloaded firmware file to `firmware.uf2`.
* put the target board into bootloader mode: `make bootloader`. This should
  cause the target to mount as a volume to your host. On a Mac it appears as
  a subdirectory under `/Volumes`, but on another OS it may appear differently.
* Identify the path to the mounted volume and copy `firmware.uf2` there.
* The target should immediately reboot and the mounted volume will disappear.
* Within a few seconds the target should now be running the new version of
  MicroPython.

Issue Tracking
--------------
For this issue I am using [git issue](https://github.com/dspinellis/git-issue).
This is a portable way to track issues that is not dependent on Github, plus
it is a command line tool.

In case you want to see the issue repo, you must have git-issue installed. Once
you have that you can:

    git issue clone https://github.com/sectioncritical/issue-car_ledstrip.git

It should clone the issues repo and then you can use `git issue` commands to
view and interact with issues.
