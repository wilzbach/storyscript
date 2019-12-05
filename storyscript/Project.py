# -*- coding: utf-8 -*-
import io
import os


class Project:
    """
    Creates a new Storyscript project with an example story and a readme.
    """

    @staticmethod
    def readme(name):
        readme = (
            "# {}\n\n{} is a Storyscript app\n\n## Storyscript\n\n"
            "You can compile Storyscript with `storyscript compile -j`"
            "\n\nExtras:\n - Get in touch with other Storyscripters at "
            "our [slack](https://asyncy.click/slack)\n - Check out the"
            "docs for [Storyscript on Asyncy]"
            "(https://docs.asyncy.com/storyscript)"
        ).format(name, name)
        with io.open("{}/README.md".format(name), "w") as f:
            f.write(readme)

    @staticmethod
    def app(name):
        story = (
            "# Here's a simple http server\nhttp server\n\t"
            "when server listen method:'get' "
            "path:'/'\n\t\tclient write content: 'Hello Storyscript!'"
        )
        with io.open("{}/src/{}.story".format(name, name), "w") as f:
            f.write(story)

    @classmethod
    def new(cls, name):
        if os.path.exists("{}/src".format(name)) is False:
            os.makedirs("{}/src".format(name))
        cls.readme(name)
        cls.app(name)
