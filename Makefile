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

# RSHELL LEGACY NOTES
# (using mpremote now instead of rshell so no longer applies)
# ABOUT RSHELL_PORT
# rshell does not recognize the Adafruit rp2040 board being used.
# so the port must be specified through the environment variable
# RSHELL_PORT. Be sure to set it to match your serial device connected
# to the Adafruit board.
# RSHELL NOTES
# initially circuitpython was used. rshell did not work well transferring
# files. there were permission problems and IO errors. The deploym target was
# added that just allows files to be copied to the mounted drive that is
# provided by circuitpython.
# However, rshell to work fine with micropython which is used at the time
# of this writing. And micropython does not automatically mount a drive to
# expose the filesystem.

APP_FILES=console_std.py cmdclasses.py cmdtemplate.py cmdif.py cmdparser.py ws2812_pio.py main.py ledmeter.py ledrange.py
SRC_DIR=ledstrip
BUILD_DIR=build

# micropython search path. needed for running unittest under upy
UPYPATH=~/.micropython/lib:$(shell pwd)/$(SRC_DIR)

all: help

include python-venv.mak

.PHONY: help
help: this_help venv_help

.PHONY: this_help
this_help:
	@echo ""
	@echo "-------------"
	@echo "Makefile help"
	@echo "-------------"
	@echo "All target operations use mpremote. It automatically discovers the"
	@echo "attached board and connects automatically, as long as there is only one."
	@echo ""
	@echo "boards      - list attached boards available to mpremote"
	@echo "deploy      - copy app files to target as py"
	@echo "deploy_mpy  - copy app files to target as mpy (requires mpy-cross)"
	@echo "repl        - enter repl of target using rshell"
	@echo "ls          - list files on target"
	@echo "reset       - reset the target"
	@echo "bootloader  - put device in bootloader mode (for upython updating)"
	@echo ""
	@echo "terminal    - open serial terminal using miniterm (SERPORT)"
	@echo "              Current SERPORT=$(SERPORT)"
	@echo ""
	@echo "test        - run host-based unit tests"
	@echo "lint        - run pylint where applicable"
	@echo "docstyle    - run pydocstyle"
	@echo "clean       - clean repo of all intermediate products"
	@echo ""
	@echo "testpico_ws2812 - run ws2812 driver test on attached pico"
	@echo "testpico_console- run a console IO test on the target"
	@echo ""

.PHONY: boards
boards: |venv
	venv/bin/mpremote devs

.PHONY: deploy
deploy: | venv
	for f in $(APP_FILES); do venv/bin/mpremote cp $(SRC_DIR)/$$f :$$f; done

$(BUILD_DIR):
	mkdir $@

# precompile to mpy files and deploy those
# assumes you have mpy-cross installed
.PHONY: deploy_mpy
deploy_mpy: $(APP_FILES) | venv $(BUILD_DIR)
	for f in $(APP_FILES);                                                  \
	do                                                                      \
	    mpy-cross $(SRC_DIR)/$$f -o $(BUILD_DIR)/$${f%.py}.mpy;                        \
	    venv/bin/mpremote cp $(BUILD_DIR)/$${f%.py}.mpy :                   \
	done

.PHONY: repl
repl: |venv
	venv/bin/mpremote repl

.PHONY: ls
ls: |venv
	venv/bin/mpremote ls

.PHONY: reset
reset: |venv
	venv/bin/mpremote reset

.PHONY: bootloader
bootloader: |venv
	venv/bin/mpremote bootloader

# make sure to set SERPORT to use terminal
.PHONY: terminal
terminal: venv
	venv/bin/python -m serial.tools.miniterm $(SERPORT) 115200

# WAS: uses python builtin unittest module, so does not require venv
# NOW: run tests using micropython to better match the target environment
# however unittest doesnt run the normal way so each test module has to
# be loaded individually
.PHONY: test
test:
	MICROPYPATH=$(UPYPATH) micropython tests/test_cmdparser.py
	MICROPYPATH=$(UPYPATH) micropython tests/test_cmdif.py
#	python3 -m unittest -v tests.test_cmdparser tests.test_cmdif

# run the target based test
.PHONY: testpico_ws2812
testpico_ws2812: |venv deploy
	venv/bin/mpremote run tests/pico_test_ws2812_pio.py

# This one must be run by hand on the target using a terminal. The reason is
# that the repl used for "run" is what we are testing.
# To run this after the copy below and the terminal is opened, do:
#     import test_pic_console_std
#
# and the test should run
#
.PHONY: testpico_console
testpico_console: |venv deploy
	venv/bin/mpremote cp tests/pico_test_console_std.py :
	@echo "In the REPL, 'import pico_test_console_std' and the test should run"
	venv/bin/mpremote repl

.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)

.PHONY: lint
lint: |venv
	@echo "TODO: $@ NOT IMPLEMENTED YET"

.PHONY: docstyle
docstyle: |venv
	@echo "TODO: $@ NOT IMPLEMENTED YET"
