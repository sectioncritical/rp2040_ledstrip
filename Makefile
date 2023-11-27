# SPDX-License-Identifier: 0BSD
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
	@echo "deploy  - copy application files to target"
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

.PHONY: deploy
deploy: venv
	@echo "TODO: $@ NOT IMPLEMENTED YET"

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
