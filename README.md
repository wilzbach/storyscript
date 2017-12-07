  # StoryScript

> Write code in English.

[![Travis CI](https://secure.travis-ci.org/asyncy/storyscript.svg?branch=master)](http://travis-ci.org/asyncy/storyscript)
[![Codecov](https://codecov.io/gh/asyncy/storyscript/branch/master/graphs/badge.svg)](https://codecov.io/github/asyncy/storyscript)


# Overview

StoryScript is a language for orchestrating micro-services in a algorithmic program.

#### **Why StoryScript?**
Traditional programming languages have many abstractions, syntax and dependency management that is unnecessary when writing high-level algorithms.

#### **Why a language and not a UI?**
- Code is portable, able to be easily shared and showcased.
- Version controllable and change transparent.
- Not vendor-specific. Code is can be adapted to other applications.
- Quickly read and understand without navigation or 3rd party permissions.

---
Read our [Documentation](https://github.com/asyncy/storyscript/blob/master/DOCS.md) on the syntax.
---

# Goals

1. Lint and syntax check StoryScript files.
1. Translate the StoryScript into a machine readable logical tree.
1. Suggestion and autocomplete algorithm logic.


# Installation

```
pip install storyscript
```


# Usage

To be determined.


# Issues

For problems directly related to the CLI, [add an issue on GitHub](https://github.com/asyncy/storyscript/issues/new).

For other issues, [submit a support ticket](#)

[Contributors](https://github.com/heroku/storyscript/contributors)


# Developing

### Setup

```sh
# create virtual env
virtualenv venv
# install dependencies
. venv/bin/activate; pip install -r requirements.txt -r tests/requirements.txt
```

### Run test suite

```sh
./tests/test
```
