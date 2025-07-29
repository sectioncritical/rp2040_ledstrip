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
#

# This Makefile is used for testing of the rp2040_ledstrip module. It depends
# on the existence of the venv in the parent directory.
#
# There are 3 kinds of tests:
#
# * unit - traditional unit tests that run on host under micropython(unix)
# * target - tests that execute on the target board
# * host - tests that run on the host and talk to the target firmware

SRC_DIR=..:../ledstrip

# micropython search path. needed for running unittest under upy
UPYPATH=.frozen:/usr/lib/micropython:~/.micropython/lib:$(shell pwd)/$(SRC_DIR)

all: help

.PHONY: help
help: this_help

.PHONY: this_help
this_help:
	@echo ""
	@echo "-------------"
	@echo "Makefile help"
	@echo "-------------"
	@echo ""
	@echo "* uses parent level venv when needed"
	@echo "* uses parent level deploy when needed"
	@echo ""
	@echo "boards      - prints list of attached boards"
	@echo "ls          - lists files on target pico"
	@echo "reset       - resets target board"
	@echo "deploy      - copies source files to target board"
	@echo "repl        - invoke REPL on target"
	@echo ""
	@echo "Unit Tests (runs only on host)"
	@echo "------------------------------"
	@echo "test        - traditional unit tests, but using micropython on host"
	@echo ""
	@echo "Pico Tests (runs on attached pico)"
	@echo "----------------------------------"
	@echo "picotest    - run all pico board tests"
	@echo "picotest_ws2812  - run the ws2812 driver test"
	@echo "picotest_console - run the console driver test"
	@echo ""
	@echo "Host Tests (runs on host, talks to attached board)"
	@echo "--------------------------------------------------"
	@echo "hosttest_basic   - run basic test of firmware"
	@echo "hosttest_random  - run random pattern test"
	@echo ""

.PHONY: boards
boards:
	@make -C .. boards

.PHONY: ls
ls:
	@make -C .. ls

.PHONY: reset
reset:
	@make -C .. reset

.PHONY: deploy
deploy:
	@make -C .. deploy

.PHONY: repl
repl:
	@make -C .. repl

# uses host-based micropython to run traditional python unit tests
# micropython is used to better represent the actual target
# these are probably also runnable from parent directory using python
# unittest like:
#	python3 -m unittest -v tests.test_cmdparser tests.test_cmdif
.PHONY: test
test:
	MICROPYPATH=$(UPYPATH) micropython test_cmdparser.py
	MICROPYPATH=$(UPYPATH) micropython test_cmdif.py
	MICROPYPATH=$(UPYPATH) micropython test_ledstrip.py

# run target based tests
.PHONY: picotest
picotest:
	@echo ""
	@echo "About to run ws2812 driver test on pico target"
	@echo ""
	@echo "Press enter to continue: "
	@read foobar
	@make picotest_ws2812
	@echo ""
	@echo "About to run console test on pico target"
	@echo ""
	@echo "Press enter to continue: "
	@read foobar
	@make picotest_console
#	../venv/bin/mpremote run target/pico_test_console_std.py

# run the target based test
.PHONY: picotest_ws2812
picotest_ws2812:
	../venv/bin/mpremote run target/pico_test_ws2812_pio.py

# This one must be run by hand on the target using a terminal. The reason is
# that the repl used for "run" is what we are testing.
# To run this after the copy below and the terminal is opened, do:
#     import test_pic_console_std
#
# and the test should run
#
# NOTES: this test does not always start the REPL, i think because the
# main ledstrip program is running in its loop. there is an issue open for
# this. so you may or may not be able to type the "import" statement and
# get this test to run
.PHONY: picotest_console
picotest_console:
	@echo ""
	@echo "THIS TEST HAS SOME ISSUES - SEE COMMENTS IN MAKEFILE"
	@echo ""
	../venv/bin/mpremote cp target/pico_test_console_std.py :
	@echo ""
	@echo "This test must be run by hand."
	@echo "In the REPL, 'import pico_test_console_std' and the test should run"
	@echo ""
	@echo "At the end of the test, type ctrl-x to get back to the shell."
	@echo ""
	../venv/bin/mpremote repl

.PHONY: cleanpico
cleanpico:
	../venv/bin/mpremote rm :pico_test_console_std.py

.PHONY: hosttest_basic
hosttest_basic:
	@echo ""
	@echo "Shows a multicolored static pattern across LED strip"
	@echo "Then continuously blinks lower pixels"
	@echo ""
	@echo "Type ctrl-c to stop the test"
	@echo ""
	@echo "Press return to continue ..."
	@read foobar
	../venv/bin/python host/testit.py

.PHONY: hosttest_random
hosttest_random:
	@echo ""
	@echo "Shows a random flashing pattern across LED strip"
	@echo ""
	@echo "Type ctrl-c to stop the test"
	@echo ""
	@echo "Press return to continue ..."
	@read foobar
	../venv/bin/python host/underhoodLights.py
