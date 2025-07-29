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

# This Makefile provides tasks common to python projects, specifically for
# the management of virtual environment (venv). It is meant to be included in
# the main project Makefile

# this file assumes it is located in top level project directory.
# it uses the top level directory named to determine the project name
# that is used for naming the venv.

# VENV definition stuff

# the below computes a location for VENV that is outside the project directory.
# I decided to put the venv outside the project directory for reasons.
# If you want the venv to be in a specific location, just define VENV in a
# make or environent variable. Make sure it is an absolute and not relative
# path.
# For example: VENV=$(pwd)/venv
#
# The default behavior is this Makefile devises a cached location to keep the
# venv.

ifndef VENV

# directory of this makefile. we need to know that because part of the venv
# name is a hash of the path. we need a consistent location for the path
# in case this file is included from Makefiles in other directories
PROJDIR:=$(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PROJNAME:=$(shell basename $(PROJDIR))

# if VENV is defined in the environment or command line then that is used
# as the path for the venv. It should be a full path.
# ex: VENV=$(pwd)/venv
#
# otherwise (default behavior) a location will be used that is in a cache
# directory outside of the project directory

# determine location where VENV is stored
ifndef XDG_CACHE_HOME
VENV_CACHE:=$(HOME)/.cache/venvs
else
VENV_CACHE:=$(XDG_CACHE_HOME)/venvs
endif

VENV:=$(VENV_CACHE)/$(PROJNAME)-$(shell echo $$PROJDIR|shasum|cut -c1-6)
endif

########

.PHONY: venv_help
venv_help:
	@echo ""
	@echo "--------------------------------------"
	@echo "Python Virtual Environment Help (venv)"
	@echo "--------------------------------------"
	@echo "venv        - create python virtual env (automatic when needed)"
	@echo "cleanvenv   - clean the python venv"
	@echo "audit       - run python package checker (automatic when needed)"
	@echo "requirements- create or update the requirements.txt file"
	@echo ""
	@echo "Manual activation:"
	@echo ". $(VENV)/bin/activate"
	@echo ""

.PHONY: venv
venv: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	mkdir -p $(VENV_CACHE)
	test -d $(VENV) || python3 -m venv $(VENV)
	$(VENV)/bin/python -m pip install -U pip setuptools wheel
	$(VENV)/bin/python -m pip install -U pip-audit
	$(VENV)/bin/python -m pip install --no-deps -r $<
	touch $@
	-$(VENV)/bin/pip-audit

# this target generates a requirements.txt with pinned versions, from a
# requirements.in file. The .in file should just list the desired modules.
# This target is just run in order to update the modules and versions. Normally
# the venv (activate) target creates the venv using the requirements.txt so
# that the same module versions are always used.
# The intention is that both requirements.in and requirements.txt are version
# controlled with the .txt file being updated infrequently.
#
.PHONY: requirements
requirements:
	rm -rf $(VENV)
	python3 -m venv $(VENV)
	$(VENV)/bin/python -m pip install -U pip setuptools wheel
	$(VENV)/bin/python -m pip install -Ur requirements.in
	$(VENV)/bin/python -m pip freeze > requirements.txt

.PHONY: cleanvenv
cleanvenv:
	rm -rf $(VENV)

.PHONY: audit
audit: venv
	$(VENV)/bin/pip-audit

# NOTES about nodeenv
# in case npm packages are needed for a project they should be installed in a
# sandbox within the venv. This can be done with the following steps.
#
# nodeenv needs to be installed, either through requirements file or line
# during creation of venv
#     $(VENV)/bin/python -m pip install nodeenv (versioned?)
#
# install node (versioned?)
#     $(VENV)/bin/nodeenv -p
#
# install some package (-g is correct, it will go into venv)
#     . $(VENV)/bin/activate; npm install -g <some_package>
#
# npm security, versioning, and package pinning not covered here but should be
# considered.
