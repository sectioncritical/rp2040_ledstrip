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

# ABOUT RSHELL_PORT
# rshell does not recognize the Adafruit rp2040 board being used.
# so the port must be specified through the environment variable
# RSHELL_PORT. Be sure to set it to match your serial device connected
# to the Adafruit board.

all: help

.PHONY: help
help:
	@echo ""
	@echo "Makefile help"
	@echo "-------------"
	@echo ""
	@echo "Make sure RSHELL_PORT is set in your environment"
	@echo "Current value ($(RSHELL_PORT))"
	@echo ""
	@echo "deploy  - copy application files to target (rshell)"
	@echo "deploym - copy app files to target using mac file system"
	@echo ""
	@echo "terminal- open serial terminal using miniterm (SERPORT)"
	@echo "Current SERPORT=$(SERPORT)"
	@echo ""
	@echo "test    - run host-based unit tests"
	@echo "lint    - run pylint where applicable (not implemented)"
	@echo "docstyle- run pydocstyle (not implemented)"
	@echo "clean   - clean repo of all intermediate products"
	@echo ""
	@echo "ports   - list ports that rshell knows about"
	@echo "rshell  - invoke rshell to target (not repl)"
	@echo "repl    - enter repl of target using rshell"
	@echo "ls      - list files on target"
	@echo ""
	@echo "venv        - create python virtual env (automatic when needed)"
	@echo "cleanvenv   - clean the python venv"
	@echo "safety      - run python package checked (automatic when needed)"
	@echo ""

# uses python builtin unittest module, so does not require venv
.PHONY: test
test:
	python3 -m unittest -v tests.test_cmdparser

.PHONY: clean
clean:

# i would like to use rshell to deploy because it will not rely on mounted
# drive to host filesystem. However I have not been able to get rshell to
# copy file TO the target, although it can copy from. I spent some time
# searching on the error message and also looking at the rshell source but
# giving up for now so i can make progress.
.PHONY: deploy
deploy: #venv
	@echo "deply via rshell does not work right now, sorry :-("
#	venv/bin/rshell cp code.py /pyboard
#	venv/bin/rshell cp cmdparser.py /pyboard

# deploy on a mac using file system copy
# assumes target board is mounted to a certain location
.PHONY: deploym
deploym:
	cp boot.py /Volumes/CIRCUITPY/.
	cp code.py /Volumes/CIRCUITPY/.
	cp cmdparser.py /Volumes/CIRCUITPY/.

# make sure to set SERPORT to use terminal
.PHONY: terminal
terminal: venv
	venv/bin/python -m serial.tools.miniterm $(SERPORT) 115200

.PHONY: lint
lint: venv
	@echo "TODO: $@ NOT IMPLEMENTED YET"

.PHONY: docstyle
docstyle: venv
	@echo "TODO: $@ NOT IMPLEMENTED YET"

.PHONY: ls
ls: venv
	venv/bin/rshell ls -al /pyboard

.PHONY: ports
ports: venv
	venv/bin/rshell --list

.PHONY: rshell
rshell: venv
	venv/bin/rshell

.PHONY: repl
repl: venv
	venv/bin/rshell repl

venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || python3 -m venv venv
	venv/bin/python -m pip install -U pip setuptools wheel
	venv/bin/python -m pip install -Ur $<
	venv/bin/python -m pip install -U safety
	touch $@
	venv/bin/safety check

.PHONY: cleanvenv
cleanvenv:
	rm -rf venv

.PHONY: safety
safety: venv
	venv/bin/safety check
