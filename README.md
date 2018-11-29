![storyscript-logo](https://user-images.githubusercontent.com/2041757/44708914-9c66a380-aaa8-11e8-8e53-502c17ab5be3.png)

[![PyPi](https://img.shields.io/pypi/v/storyscript.svg?maxAge=600&style=for-the-badge)](https://pypi.python.org/pypi/storyscript)
[![CircleCI](https://img.shields.io/circleci/project/github/storyscript/storyscript/master.svg?style=for-the-badge)](https://circleci.com/gh/storyscript/storyscript)
[![Codecov](https://img.shields.io/codecov/c/github/storyscript/storyscript.svg?style=for-the-badge)](https://codecov.io/github/storyscript/storyscript)
[![Docs](https://img.shields.io/badge/docs-online-brightgreen.svg?style=for-the-badge)](https://docs.asyncy.com/storyscript)
[![Devdocs](https://img.shields.io/badge/devdocs-online-brightgreen.svg?style=for-the-badge)](https://storyscript.readthedocs.io)


# Storyscript

StoryScript is an high-level language that can be used to orchestrate
microservices in an algorithmic way. Unlike a traditional language, StoryScript
describes operations against or with services:

```coffee
today = date now
invoices = database get items:"invoices" where:"month={{today.month}}"
if today.day == 1
  send invoices
```

You can launch a scalable web application with a five-liner:

```coffee
stream http-server as request
  query = parse-request request:request
  data = database get query:query
  html = erb template:'/assets/template.erb' data:data
  request.write input:html
```

These stories are compiled into event trees and run by a platform that
implements StoryScript execution, like [Asyncy](https://github.com/Asyncy)

## Current status

StoryScript is at an alpha stage and is part of the [Asyncy](https://asyncy.com)
project. If you want to learn more about Asyncy, and how to use StoryScript
with Asyncy, you can visit the [asyncy documentation](https://docs.asyncy.com)

At the moment, Asyncy is the only platform that can execute StoryScript, however
due the open source nature of the project, there might be more platforms that
support StoryScript in the future.

## Getting started

Create a Python 3.6 virtualenv:

```sh
virtualenv --python=python3.6 folder
```

Activate it:

```sh
cd folder
source bin/activate
```

Install with pip:

```sh
pip install storyscript
```

Write a simple story:

```sh
echo "alpine echo text:'hello world!'" > hello.story
```

Compile a story to JSON:

```sh
storyscript parse -j hello.story
```

## Development documentation

[Development docs](https://storyscript.readthedocs.io) are provided for those
who wish to contribute to the project or want to understand how to execute
compiled stories.

## Contributing

If you want to contribute to Storyscript, you can join the community at
[our slack](https://asyncy.click/slack) where we discuss features and future
plans.

You can find open issues on [github](https://github.com/asyncy/storyscript/issues),
along with [contribution guidelines](https://github.com/asyncy/storyscript/blob/master/CONTRIBUTING.md)
for happy coding.
There are [simple issues](https://github.com/asyncy/storyscript/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22)
for new contributors and
[issues that need help](https://github.com/asyncy/storyscript/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22)

### Contributors

The list of contributors is available [here](https://github.com/asyncy/storyscript/contributors)

## Issues

For problems directly related to the CLI, [add an issue on GitHub](https://github.com/asyncy/storyscript/issues/new)
For other issues, [submit a support ticket](mailto:help@storyscripts.org)
