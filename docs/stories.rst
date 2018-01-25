Understanding Stories
======================
In the previous example we did something cryptic on the second line::

    alpine echo "hello world"


This works because Storyscript supports a list of commands that can be used
to perform actions.

*alpine* is a generic Alpine Linux container that can perform shell commands, like
*echo "hello world"*

In most cases you will choose a command specific to the action you want to make
and provide the action. For example, to tweet::

    twitter tweet "I have been created with Storyscript!"

Services
########
Services currently available:

* alpine (generic command)

Asyncy will have a public marketplace for developer to build any service
imaginable as a command in Asyncy. Here are just a few concepts:

* Execute code, such as `python`, `node`, `ruby`, etc.
* Connect to any database.
* Interact with all social media providers.
* Communicate with any API endpoint.

Asyncy is a platform for even more complex and unique commands, such as:

* A cron scheduler
* A Slack chat bot
* A dev-ops CI/CD pipeline
* IOT monitoring and interaction
* Full scale backend applications
* Front-end web servers
* Using API by AcuWeather (for example) to forecast weather
* Interact with the entire Wolfram Alpha platform
