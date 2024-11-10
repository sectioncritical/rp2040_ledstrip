Intalling Firmware Onto a Pico
==============================

I refer to this software package, `rp2040_ledstrip`, as [firmware](
https://en.wikipedia.org/wiki/Firmware). It means the software that is copied
to the Pico and runs on the Pico.

Everything described here assumes you have [the development environment](venv.md).

If MicroPython is not installed on your target board, [see below](#installing-micropython).

Check for connected board
-------------------------

    make boards

Should return a list of one or more boards, one of which should be your Pico
board. Mine looks like this:

    /dev/cu.BLTH None 0000:0000 None None
    /dev/cu.Bluetooth-Incoming-Port None 0000:0000 None None
    /dev/cu.usbmodem1424201 df625857831b4436 239a:80f2 MicroPython Board in FS mode

Install the LED Firmware
------------------------

    make deploy

Copies all the necessary files to the target board. In case the file is already
present you may see some "Up to date" messages. Here is an example:

    cp ledstrip/console_std.py :console_std.py
    Up to date: console_std.py
    cp ledstrip/cmdclasses.py :cmdclasses.py
    Up to date: cmdclasses.py
    cp ledstrip/cmdtemplate.py :cmdtemplate.py
    Up to date: cmdtemplate.py
    cp ledstrip/cmdif.py :cmdif.py
    cp ledstrip/cmdparser.py :cmdparser.py  
    Up to date: cmdparser.py
    cp ledstrip/ws2812_pio.py :ws2812_pio.py
    Up to date: ws2812_pio.py
    cp ledstrip/main.py :main.py
    Up to date: main.py
    cp ledstrip/ledmeter.py :ledmeter.py
    Up to date: ledmeter.py
    cp ledstrip/ledrange.py :ledrange.py
    Up to date: ledrange.py

Once this step is done, I recommend you reset the target board with:

    make reset

After that you should be able to [use the firmware](using.md).

Troubleshooting
---------------

Make sure the board shows up in the list from `make boards`. You can try
unplugging and re-plugging the board, sometimes that helps if there is a
communication problem.

Installing MicroPython
----------------------
I don't have this automated at this time. In case you need to install/update
MicroPython on the target, here are some brief instructions:

* get MicroPython "firmware" from here: <https://micropython.org/download/ADAFRUIT_FEATHER_RP2040/>.
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

**NOTE:** the use of the word "firmware" in this section is referring to the
MicroPython binary that gets installed on the target board. Everywhere else in
this documentation, "firmware" means the LED controller software.
