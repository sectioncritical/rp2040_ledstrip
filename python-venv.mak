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

venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || python3 -m venv venv
	venv/bin/python -m pip install -U pip setuptools wheel
	venv/bin/python -m pip install -U pip-audit
	venv/bin/python -m pip install --no-deps -r $<
	touch $@
	-venv/bin/pip-audit

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
	rm -rf venv
	python3 -m venv venv
	venv/bin/python -m pip install -U pip setuptools wheel
	venv/bin/python -m pip install -Ur requirements.in
	venv/bin/python -m pip freeze > requirements.txt

.PHONY: cleanvenv
cleanvenv:
	rm -rf venv

.PHONY: audit
audit: venv
	venv/bin/pip-audit

# NOTES about nodeenv
# in case npm packages are needed for a project they should be installed in a
# sandbox within the venv. This can be done with the following steps.
#
# nodeenv needs to be installed, either through requirements file or line
# during creation of venv
#     venv/bin/python -m pip install nodeenv (versioned?)
#
# install node (versioned?)
#     venv/bin/nodeenv -p
#
# install some package (-g is correct, it will go into venv)
#     . venv/bin/activate; npm install -g <some_package>
#
# npm security, versioning, and package pinning not covered here but should be
# considered.
