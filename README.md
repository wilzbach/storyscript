
[![PyPi](https://img.shields.io/pypi/v/storyscript.svg?maxAge=600&style=for-the-badge)](https://pypi.python.org/pypi/storyscript)
[![CircleCI](https://img.shields.io/circleci/project/github/storyscript/storyscript/master.svg?style=for-the-badge)](https://circleci.com/gh/storyscript/storyscript)
[![Codecov](https://img.shields.io/codecov/c/github/storyscript/storyscript.svg?style=for-the-badge)](https://codecov.io/github/storyscript/storyscript)
[![Docs](https://img.shields.io/badge/docs-online-brightgreen.svg?style=for-the-badge)](https://docs.asyncy.com/storyscript)
[![Devdocs](https://img.shields.io/badge/devdocs-online-brightgreen.svg?style=for-the-badge)](https://storyscript.readthedocs.io)


<div align="center">
<img src="https://user-images.githubusercontent.com/2041757/44708914-9c66a380-aaa8-11e8-8e53-502c17ab5be3.png" width="275">
</div>

## 👋 Meet Storyscript
The [DSL](https://en.wikipedia.org/wiki/Domain-specific_language) for **Application Storytelling**.
Develop rapidly, deploy natively to the cloud and focus on what matters most: business-logic.
Designed with :heart: by [@Asyncy](https://asyncy.com) on a mission to bring application development to the next level.

```coffee
# Applications are stories of data.
when http server listen path: '/' as request     # Serverless
    result = anyMicroservice action key: value   # Written in any language wrapped in Docker or RKT
    result = anyFunction(key: value)             # Lambda, OpenFaaS, KNative or Storyscript
    items = 'string' split by: ','               # Mutations == No middleware
    data = OpenAPI get users: users              # OpenAPI & AsyncAPI for legacy system support
    sent = machinebox/textbox process input:data # Free/Paid Serivces
    if sent.positive                             # Conditions
        foreach list as item                     # Turing complete
            # ...
    request write content: 'Hello World!'

# Next launch on the Asyncy Platform
$ asyncy deploy  # Zero-devop deployments into Kubernetes
```

💯Open Source for a delicious application development. :sparkles::cake::sparkles:

> 🚀Choose: hosted **Asyncy Cloud** or `helm install asyncy` for on-premises deployments.

## Current status

Storyscript is at an alpha stage and is part of the [Asyncy](https://asyncy.com)
project. If you want to learn more about Asyncy, and how to use Storyscript
with Asyncy, you can visit the [asyncy documentation](https://docs.asyncy.com)

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
