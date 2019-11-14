[![PyPi](https://img.shields.io/pypi/v/storyscript.svg?maxAge=600&style=for-the-badge)](https://pypi.python.org/pypi/storyscript)
[![CircleCI](https://img.shields.io/circleci/project/github/storyscript/storyscript/master.svg?style=for-the-badge)](https://circleci.com/gh/storyscript/storyscript)
[![Codecov](https://img.shields.io/codecov/c/github/storyscript/storyscript.svg?style=for-the-badge)](https://codecov.io/github/storyscript/storyscript)
[![Docs](https://img.shields.io/badge/docs-online-brightgreen.svg?style=for-the-badge)](https://docs.storyscript.io)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v1.4%20adopted-ff69b4.svg?style=for-the-badge)](https://github.com/storyscript/.github/blob/master/CODE_OF_CONDUCT.md)


<div>
    <p align="center"><img src="https://user-images.githubusercontent.com/2041757/68865115-19c70580-06a7-11ea-955a-1c769960b366.png" width="450"></p>
    <h3 align="center">Code that connects without plumbing.</h3>
    <p align="center">The <b>open source</b> cloud-native programming language that<br>connects containers, “serverless” functions and APIs seamlessly<br>for building powerful mini-apps and workflows.</p>
     <p align="center"><img src="https://user-images.githubusercontent.com/2041757/68863667-aa501680-06a4-11ea-9200-47fbdac7f769.png" width="650"></p>
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
