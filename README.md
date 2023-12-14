Car LED Strip Controller
========================

This project is for controlling LED strips intended for use on a car. It
expects to run on a Raspberry Pico RP2040 board, using CircuitPython. The
prototyping hardware is the
[Adafruit RP2040 Kee Boar](https://www.adafruit.com/product/5302) (no that is
not a typo). The LED strips are WS2812 compatible strip such as
[these from Adafruit](https://www.adafruit.com/product/2970).

The controller code accepts commands via a hardware serial port and implements
a set of patterns that might be useful for a car.

License
-------
This project uses the
[Zero-Clause BSD License](https://opensource.org/license/0bsd/). See the
[LICENSE file](LICENSE.md) for actual license text. Basically, you can do
whatever you want with this project but I am not responsible for anything.

Documents
---------
Some preliminary documentation can be found in the [`docs`](docs/) directory.

TODO
----
This README should be filled out with docs, usage, etc sections.
