Development Environment
=======================

Tool Prerequisites
------------------

This project was mainly developed using MacOS and that is how it is tested. I
also used it on a Raspberry Pi running Raspbian, in-system, to install the
firmware on a target Pico. I believe you could use Linux-based or Windows OS
as well for development.

### Python 3

Assumes `python3` is on the system path. It is used to create a virtual
environment and the python is invoked through the venv after that. Check it
with:

    python3 --version

Should return `3.something`.

You should also have python3 `venv` and `pip3` which may be included with your
python3 installation, or may require a separate package installation. You can
check with:

    python3 -m pip --version    # shows a version number
    python3 -m venv -h          # shows help

If for some reason you will not use the venv, you can see all the packages used
by this project in the two requirements files:

* requirements.in - a list of all top level packages for the project
* requirements.txt - a list of all packages including dependencies, with pinned
  versions

### mpremote

This is a python tool that is used to communicate with a Pico board that is
running MicroPython. It is normally installed automatically as part of the
Python virtual environment (see below). But if you are not using the venv you
may have to install this separately.

### GNU Make

A Makefile is used to help automate tasks. If you don't want to use make you
can look in the Makefile and see the specific commands and just type those out.
You can check for make with:

    make --version
    GNU Make 3.81               # typical response
    ...

### Bash-compatible shell

Some of the Makefile targets have some simple bash-style scripts. If you don't
have a bash-like shell environment, then you can alter the Makefile to be
compatible with your shell, or don't use the Makefile.

### MicroPython

Some of the unit tests use [MicroPython](https://micropython.org) running on
the development system. For this to work you must have MicroPython installed on
your system path. It is not needed if you are not using any unit tests.

MicroPython is also used on the RP2040 Pico but that is separate from running
MicroPython on your development system.

You will need to use your OS package management system to install MicroPython.
For example, MacPorts or apt.

There is a related tool called `mpy-cross`. This allows for precompiling to
bytecode before installing on the Pico. To use this feature you will also need
`mpy-cross` installed on your system. This is not well tested by me and is
probably not needed. It may save memory space on the target but since I am
still in development with many ongoing changes, I have not used mpy-cross much
other than as a curiousity.

Python Virtual Environment
--------------------------
All of the tasks for this project use the python virtual environment (venv) for
installing all dependencies and python based tools. The Makefile can create and
maintain the `venv` and the venv is used for all tasks.

If you are not using the Makefile, you can create the virtual environment
(venv) with:

    python3 -m venv venv

And then there are more steps to activate it and install the dependencies. Take
a look at the steps in the Makefile if you want to do this manually.

For all of the remaining discussion below, it is assumed that the venv is
installed and activated or that the Makefile is used to perform the tasks.

Assumption: your system has `python3` on the executable path.

Installing the virtual environment is not necessary as a separate step. It will
be done automatically the first time you `make` something that needs it. But if
you want to manage it separately you can do the following:

* `make venv` - installs the virtual environment
* `make cleanvenv` - removes the virtual environment

If you want to use the venv outside of the Makefile, you can activate it from
the command prompt:

    . venv/bin/activate

If you use `make cleanvenv`, be sure to `deactivate` first. Usually it is not
necessary to clean the venv.

### Package Version Pinning

When the *venv* is created, it uses the `requirements.txt` file which contains
version numbers for all packages. This means that the same versions are always
installed.

If you want to add a new package, it should be added in `requirements.in` which
is all the "requested" packages for the project. Then update `requirements.txt`
using:

    make requirements

This will updates all the packages to the latest and generate a new
`requirements.txt` with the latest versions. Use `git diff requirements.txt`
to see all the version changes. You can revert any version changes you don't
want.

The purpose of this system is to make sure that package versions are always
specified and changed in a deliberate and controlled way.

### Package Auditing

I use [`pip-audit`](https://github.com/pypa/pip-audit) to scan all packages
whenever the *venv* is set up. It will run automatically.

Makefile
--------
A Makefile is used to automate common tasks, so that most things you want to
do can be accomplished with `make <something>`.

You can see the available make targets with `make help`. At the time of this
writing, here is the current list of available targets:

    -------------
    Makefile help
    -------------
    All target operations use mpremote. It automatically discovers the
    attached board and connects automatically, as long as there is only one.

    boards      - list attached boards available to mpremote
    deploy      - copy app files to target as py
    deploy_mpy  - copy app files to target as mpy (requires mpy-cross)
    repl        - enter repl of target using rshell
    ls          - list files on target
    reset       - reset the target
    bootloader  - put device in bootloader mode (for upython updating)

    terminal    - open serial terminal using miniterm (SERPORT)
                  Current SERPORT=/dev/cu.usbmodem1424201

    test        - run host-based unit tests
    lint        - run pylint where applicable
    docstyle    - run pydocstyle
    clean       - clean repo of all intermediate products

    testpico_ws2812 - run ws2812 driver test on attached pico
    testpico_console- run a console IO test on the target

    -------------
    Documentation
    -------------
    docs-build  - build the documentation
    docs-serve  - serve docs for local viewing
    docs-clean  - clean docs related build products
    gh-pages    - create gh-pages branch (no history)

    --------------------------------------
    Python Virtual Environment Help (venv)
    --------------------------------------
    venv        - create python virtual env (automatic when needed)
    cleanvenv   - clean the python venv
    audit       - run python package checker (automatic when needed)
    requirements- create or update the requirements.txt file
