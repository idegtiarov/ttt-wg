# Tic Tac Toe

[![Maintainability](https://api.codeclimate.com/v1/badges/4e167b0f5d284864f81e/maintainability)](https://codeclimate.com/github/idegtiarov/ttt-wg/maintainability)


## About

It is a simple tic-tac-toe game.

## Getting started

### Deployment

Deployment is based on the `Docker` containers. There is the config file
`docker-compose.yml` for the local dev deployment.

Docker and Docker Compose are required to be installed before start
the deploying.

#### Installation steps

Clone the project.

Local deployment can be started by the docker-compose up command in the
console:

    docker-compose up

  Note: Development server available on `localhost:8007`. Multi-player mode
  could be tested by open link in different browsers or creating a tunnel with
  the help of tools like [ngrok](https://ngrok.com/).

##### Optional parameters

Player are waiting for the opponent for the certain time which is configured by
the parameter `TTT_WAIT_TIME` in the `config.settings.local` file. By default it is
set to 5 seconds.


### Running tests

* to run tests locally:
    install the `tox` by `pip install tox` and run command:

        > tox

 `tox` runs flake8 linter tests and pytest environment, each of them could be
 started separately by the commands:

        > tox -e flake8
        > tox -e pytest

 Note: To run `pytest` tests block docker containers with redis and database
 should be started.
