# Container Image for Micropython Project

I created this custom container for use with this Micropython project. It is
meant to be used with CI tools. It includes all the tools and packages needed
to run tests, quality checks, and build documentation for the project.

**LICENSE:** [License for this container project](../LICENSE.md).

At the time of this writing, the image has yet been pushed to GHCR (still under
testing). I will update this README once it has been pushed.

## Included Tools and Packages

* git - used for release operations and docs
* make
* python3
* git-cliff - release notes
* micropython - unix port for running unit tests
* pre-built venv - all required python packages preloaded into a venv

## Usage

Makefile:

```
$ make help

Micropython Tools Container Image Maintenance
----------------------------------
login       - login to github registry (asks for github access token)
build       - build the python tools image
push        - push the image to github
run         - run container for local testing (PROJECT_ROOT)
images      - list local images
containers  - list local containers
```

# Maintenance

Here are common maintenance steps via Makefile. Podman is used internally.
There are a couple of environment variables used for identifying with Github.

* `ORGNAME` - the Github organization name where the image will be pushed
* `GITHUB_USERNAME` - login user name, needed to login and push

These may both be the same value depending on whether your project belongs to
an organziation separate from your own Github account. These values can be
provided on the command line when invoking the make tasks, or you can define
in your environment, or you can edit the Makefile and hardcode the values
there.

Look in the Makefile to see the exact commands, if you care:

### Build

    ORGNAME=myorgname make build

`ORGNAME` is a Github user name or organization name.

This will build the image using podman and store in your local podman
repository. If you are only building for local use, then ORGNAME does not
really matter, but it will be used in creating the image tag.

### Login

Using your github credentials:

    GITHUB_USERNAME=myusername make login

you will be prompted for the password, which is a Github personal access
token. You need to do this in order to push to the Github registry.

### Push

Push the image to Github so it can be used for workflow automation.

    ORGNAME=myorgname make push

`ORGNAME` is a Github user name or organization name. It should be the same you
used for `make build`. You should be logged in before using this step.

### CI Usage

In the Github workflow file, use this container:

    ghcr.io/ORGNAME/micropython-build:latest

### Running Locally

You can run the container locally (using podman) to test out all the make
targets:

    make run

You will be in a directory named `project` which is mapped to the top level
project directory. You should then be able to run local test and document
building tasks. You will not be able to run the tasks related to the hardware
target, like `make deploy`. These will not work. For example you `make test`
which will run the unit tests. They will execute using the container instead of
your local host tools. However it is still using your local filesystem and
output files will be written in your local project directory.

To quit out of the container, just `exit`.

### Image and Containers

As a convenience, `make images`, and `make containers` are tasks that show you
locally stored images and containers.
