Hardware Description
====================

**Incomplete and WIP**

**TODO add board/prototyping photo and block diagrams or schematics**

The hardware is an RP2040 board such as the Adafruit Scorpio board. The
control board is set up with MicroPython and is connected to the host via the
build-in USB connector. The board is powered by 5V via USB.

The USB connection provides both an interface for maintaining and updating the
firmware, as well as a virtual serial port for commanding. The board is
configured and updated from the host using `mpremote`. This lets you install
python files, view and delete files and some other board management tasks.

When the firmware is installed (see the installation help), when the boards
starts or is reset, it runs the ledstrip control firmware which takes over the
virtual serial port. Now you connect using a terminal (if a human) or opening
the serial device from your program and sending and receiving commands.

Using the `mpremote` tool from a host computer can regain control of the serial
interface for the above-mentioned maintenance tasks.

See the protocol documentation for information about how to use the command
interface.

The LED string should be WS2812 compatible LEDs. It should work with 5V or 12V
and the string should have its own power supply. Usually the data signal is 5V
so the hardware should have a level shifter on the LED data signal (such as the
Scorpio board), or you can just try with the 3.3V GPIO which sometimes works
okay but not always.

At the time of this writing we have driven at least 400 LEDs in a string.

The LED string will have power and ground for the power supply. The power
supply ground is shared with the logic ground of the controller board. A ground
wire from the LED string should be connected to a ground pin on the controller
board. Sometimes the LED strip has a "data ground" which you can use but
internally it is the same as the power supply ground. The LED strip data signal
should be connected to a GPIO output of the controller board. The specific
GPIO pin is specified in the firmware. The Scorpio board has 8 GPIOs that are
suitable for this and have 5V level shifters.
