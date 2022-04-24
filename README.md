# loan_app

![example workflow](https://github.com/vkmrishad/loan_app/actions/workflows/black.yaml/badge.svg)
![example workflow](https://github.com/vkmrishad/loan_app/actions/workflows/django-ci.yaml/badge.svg)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>


Install Poetry

    $ pip install poetry
    or
    $ pip3 install poetry

Activate or Create Env

    $ poetry shell

Install Packages from Poetry

    $ poetry install

NB: When using virtualenv, install from `$ pip install -r requirements.txt`.

## Runserver

    $ python manage.py runserver
    or
    $ ./manage.py runserver

Access server: http://127.0.0.1:8000

## Runserver using docker
Check this documentation to run with docker, https://docs.docker.com/samples/django/

## API Endpoints
Check Swagger/Redoc documantation after running server
#### Swagger: http://127.0.0.1:8000/api/
#### Redoc: http://127.0.0.1:8000/redoc/

## Test

    $ python manage.py test
    or
    $ ./manage.py test

## Version

* Python: 3.8+
* Postgres 12+ / Sqlite3
