RP2040 LED Strip Controller
===========================

**This is work-in-progress and early development. Don't count on anything
working or the docs being up to date.**

This project is located at <https://github.com/sectioncritical/rp2040_ledstrip>.

Project documentation is located at <https://sectioncritical.github.io/rp2040_ledstrip/>/

This project is an LED strip pattern generator/controller for use with an
[Raspberry Pico RP2040](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#pico-1-family).
It was originally intended for use on a car, but it could be used in other
situations.

The project uses MicroPython with the [Adafruit Feather RP2040 Scorpio Board](
https://www.adafruit.com/product/5650). It should also work directly with other
RP2040-based boards with little or no changes. One advantage of the Scorpio
board is that is has level shifters on the board to drive the LED logic signal
with 5V. It was designed to be a driver for LEDs or LED strips. The LED strips
are WS2812 compatible strip such as [these from Adafruit](https://www.adafruit.com/product/2970).

The controller code accepts commands via USB serial port and implements a set
of patterns that might be useful for a car. Right now, one Pico drives one LED
strip, although I endeavor to add multi-string capability. I will probably do
that whenever the car project requires it. Up to now we are using one Pico per
LED string.

Why did I write new code to drive a WS2812 when there already exists libraries
such as Adafruit? I found that those existing libraries used floating point to
adjust pixel values and I could not get the patterns I wanted to make to run
very fast. The other libraries are highly abstracted which makes them easy to
use, but also less performant. The driver and pattern generation of this
only uses integer math. The RP2040 does not have hardware floating point
support.

We decided to use MicroPython instead of Adafruit's CircuitPython for reasons.

License
-------
This project uses the [Zero-Clause BSD License](https://opensource.org/license/0bsd/).
See the [LICENSE file](LICENSE.md) for actual license text. Basically, you can
do whatever you want with this project but I am not responsible for anything.

Issue Tracking
--------------
For this project I am using [git issue](https://github.com/dspinellis/git-issue).
This is a portable way to track issues that is not dependent on Github, plus
it is a command line tool.

In case you want to see the issue repo, you must have git-issue installed. Once
you have that you can:

    git issue clone https://github.com/sectioncritical/issue-car_ledstrip.git

It should clone the issues repo and then you can use `git issue` commands to
view and interact with issues.
