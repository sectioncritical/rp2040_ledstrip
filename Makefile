# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Licensed under AGPLv3
#
# Copyright (c) 2025 Joseph Kroesche
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

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

APP_FILES=console_std.py    \
          cmdclasses.py     \
          cmdtemplate.py    \
          cmdif.py          \
          cmdparser.py      \
          ws2812_pio.py     \
          main.py           \
          ledstrip.py       \
          ledrange.py       \
          ledrandom.py      \
          ledmeter.py       \
          ledturn.py        \
          ledbrake.py

BUILD_DIR=build

all: help

.PHONY: help
help:
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
	@echo "cleanpico   - delete app files from target"
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
	@echo "-------------"
	@echo "Documentation"
	@echo "-------------"
	@echo "docs-build  - build the documentation"
	@echo "docs-serve  - serve docs for local viewing"
	@echo "docs-clean  - clean docs related build products"
	@echo "gh-pages    - create gh-pages branch (no history)"
	@echo ""
	@echo "-------------"
	@echo "VENV management"
	@echo "-------------"
	@echo "venv        - create python virtual environment (automatic when needed)"
	@echo "cleanvenv   - clean the python venv"
	@echo "audit       - run python package checker (automatic when needed)"
	@echo "update      - update python package lock file"
	@echo ""

.PHONY: boards
boards:
	@uv run mpremote devs

.PHONY: deploy
deploy:
	@for f in $(APP_FILES); do uv run mpremote cp $$f :$$f; done

.PHONY: cleanpico
cleanpico:
	@for f in $(APP_FILES); do uv run mpremote rm :$$f; done

$(BUILD_DIR):
	mkdir $@

# precompile to mpy files and deploy those
# assumes you have mpy-cross installed
.PHONY: deploy_mpy
deploy_mpy: $(APP_FILES) | venv $(BUILD_DIR)
	for f in $(APP_FILES);                                                  \
	do                                                                      \
	    mpy-cross $$f -o $(BUILD_DIR)/$${f%.py}.mpy;             \
	    uv run mpremote cp $(BUILD_DIR)/$${f%.py}.mpy :                   \
	done

.PHONY: repl
repl:
	uv run mpremote repl

.PHONY: ls
ls:
	uv run mpremote ls

.PHONY: reset
reset:
	uv run mpremote reset

.PHONY: bootloader
bootloader:
	uv run mpremote bootloader

# make sure to set SERPORT to use terminal
.PHONY: terminal
terminal:
	uv run python -m serial.tools.miniterm $(SERPORT) 115200

# runs unit tests from the tests/ directory
# see that directory for more tests
.PHONY: test
test:
	@make -C tests test

.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)

.PHONY: lint
lint:
	uv run pylint --rcfile=pylintrc --enable-all-extensions ledstrip

.PHONY: docstyle
docstyle:
	uv run pydocstyle ledstrip

# DOCS RELATED TARGETS
.PHONY: docs-build
docs-build:
	uv run mkdocs build

.PHONY: docs-serve
docs-serve:
	uv run mkdocs serve

.PHONY: gh-pages
gh-pages:
	uv run ghp-import -n -o site

.PHONY: docs-clean
docs-clean:
	rm -rf site

.PHONY: issues
issues:
	@echo ""
	@git issue list -o "%T" -l "%i | %T| %D"

########################################
# PYTHON VIRTUAL ENVIRONMENT MAINTENANCE
########################################

.PHONY: venv
venv:
	uv sync --group dev
	uv run pip-audit

.PHONY: update
update:
	uv lock
	uv run pip-audit

.PHONY: cleanvenv
cleanvenv:
	rm -rf .venv

.PHONY: audit
audit:
	uv run pip-audit
