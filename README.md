[![PyPi](https://img.shields.io/pypi/v/storyscript.svg?maxAge=600&style=for-the-badge)](https://pypi.python.org/pypi/storyscript)
[![CircleCI](https://img.shields.io/circleci/project/github/storyscript/storyscript/master.svg?style=for-the-badge)](https://circleci.com/gh/storyscript/storyscript)
[![Codecov](https://img.shields.io/codecov/c/github/storyscript/storyscript.svg?style=for-the-badge)](https://codecov.io/github/storyscript/storyscript)
[![Docs](https://img.shields.io/badge/docs-online-brightgreen.svg?style=for-the-badge)](https://docs.storyscript.io)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v1.4%20adopted-ff69b4.svg?style=for-the-badge)](https://github.com/storyscript/.github/blob/master/CODE_OF_CONDUCT.md)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)


<div>
    <p align="center"><img src="https://user-images.githubusercontent.com/2041757/68865115-19c70580-06a7-11ea-955a-1c769960b366.png" width="450"></p>
    <h3 align="center">Magical coding notebook for tomorrow's developer.</h3>
    <p align="center">Storyscript is code, editor, infrastructure and community all-in-one.<br>Fully open source and on a mission to make coding for everyone.</p>
     <p align="center"><img src="https://user-images.githubusercontent.com/2041757/70599795-5cb8c200-1bee-11ea-89a5-dc52e2e708d2.png" width="650"></p>
</div>

<h3 align="center">Learn more at <a href="https://storyscript.io">https://storyscript.io</a></h3>


<hr>
<blockquote align="center">Developer Documentation</blockquote>
<hr>

## Installation

Storyscript can be installed with [pip](https://pip.pypa.io):

```sh
pip install storyscript
```

## Usage

Write a simple story:

```sh
echo 'my-service message text:"hello world!"' > hello.story
```

Compile a story to JSON:

```sh
storyscript compile -j hello.story
```

## Development documentation

[Development docs](https://storyscript.readthedocs.io) are provided for those
who wish to contribute to the project or want to understand how to execute
compiled stories.

Install [pre-commit](https://pre-commit.com/#install) and set up a git hook:

```bash
pip install --user pre-commit
pre-commit install
```

This will ensure that every commit is formatted according to [`black`](https://github.com/psf/black).

## Contributing

If you want to contribute to Storyscript, you can join the community at
[our slack](https://asyncy.click/slack) where we discuss features and future
plans.

You can find open issues on [github](https://github.com/storyscript/storyscript/issues),
along with [contribution guidelines](https://github.com/storyscript/storyscript/blob/master/CONTRIBUTING.md)
for happy coding.
There are [simple issues](https://github.com/storyscript/storyscript/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22)
for new contributors and
[issues that need help](https://github.com/storyscript/storyscript/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22)

### Contributors

The list of contributors is available [here](https://github.com/storyscript/storyscript/contributors)

## Issues

* For problems directly related to the CLI: [Add an issue on GitHub.](https://github.com/storyscript/cli/issues/new)
* To share feedback and suggestions: [We appreciate your ideas and honesty!](https://asyncy.click/feedback)
* For other issues: [Submit a support ticket.](mailto:support@storyscript.io)
