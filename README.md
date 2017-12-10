# StoryScript

![StoryScript logo](https://s3.amazonaws.com/asnycy/storyscript.png)

> A language for orchestrating microservices in an algorithmic program.

[![Travis CI](https://secure.travis-ci.org/asyncy/storyscript.svg?branch=master)](http://travis-ci.org/asyncy/storyscript) [![Codecov](https://codecov.io/gh/asyncy/storyscript/branch/master/graphs/badge.svg)](https://codecov.io/github/asyncy/storyscript) [![Pypi](https://img.shields.io/pypi/v/storyscript.svg)](https://pypi.python.org/pypi?%3Aaction=pkg_edit&name=storyscript) [![BCH compliance](https://bettercodehub.com/edge/badge/asyncy/storyscript?branch=master)](https://bettercodehub.com/results/asyncy/storyscript)

## The story behind StoryScript.

The **inspiration** behind StoryScript began with feedback from business owners who were looking for high-level marketing automation. After receiving many creative stories there was a common thread that became abundantly clear: **logic operations** (`if/then`, `for each`, and `while`) and **microservices** (email, SMS, and social media posts).

> How can you write an executable algorithm that a nontechnical person can understand?

Stories began taking shape into systematic algorithms with a defined structure. StoryScript emerged as **a language to programmatically orchestrate a series of events**.

> Why a new language and not NodeJS (or another language?

The architecture behind OOP programming languages focus on executing functions not high-level event orchestration. Stories have asynchronous operations that traditional languages are not equipped to execute.

> How to execute a StoryScript?

Programs written in StoryScript are compiled into event logic trees which computers can follow in the defined logical progression. This concept increases readability, transparency, scalability while reducing technical debt, debugging time, and dev-ops system management. [Asyncy](https://asyncy.com) ~was built~ is being built as the platform to executing StoryScripts.


> Why a language and not a UI?

Code is portable, sharable, version controlled, non-vendor specific, transparent and predictable.

## Writing a story in StoryScript.

Read our [syntax documentation here](https://github.com/asyncy/storyscript/blob/master/DOCS.md).


# Issues

For problems directly related to the CLI, [add an issue on GitHub](https://github.com/asyncy/storyscript/issues/new).

For other issues, [submit a support ticket](mailto:help@storyscripts.org)

[Contributors](https://github.com/asyncy/storyscript/contributors)


# Contribute

There are a variety of ways you can contribute to StoryScript.

1. Review our [issues](https://github.com/asyncy/storyscript/issues) and check the labels for
  - [`good first issue`](https://github.com/asyncy/storyscript/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22) a nice issue to get your feet wet.
  - [`help wanted`](https://github.com/asyncy/storyscript/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22) are issues that we are looking for feedback on.
1. Join our [Slack community](https://join.slack.com/t/asyncy/shared_invite/enQtMjgxODI2NzEyMjc5LWJiZDg1YzFkYzVhZmVlYTk2MGRmYjcxNzYwMmU4NWYwYTZkZDhlMzkwNTIxOGQ1ZjVjZGJhZDgxNzhmMjZkODA) to discuss plans and ideas.

### Goals

The goals of this package are:

1. Compile StoryScripts into a `json` formatted event logical tree.
1. Lint and syntax check StoryScript files.


### Installation

```
pip install storyscript
```


### Usage

```
storyscript -f path/to/my_first_story.story
```

### Developing

```sh
# create virtual env
virtualenv venv
# install dependencies
. venv/bin/activate; pip install -r requirements.txt -r tests/requirements.txt
# run test suite
./tests/test
```

Please follow our [contribution guidelines](https://github.com/asyncy/storyscript/blob/master/CONTRIBUTING.md).
