# loan_app
API for Mini Aspire

![example workflow](https://github.com/vkmrishad/loan_app/actions/workflows/black.yaml/badge.svg)
![example workflow](https://github.com/vkmrishad/loan_app/actions/workflows/django-ci.yaml/badge.svg)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

## Clone

    git clone https://github.com/vkmrishad/loan_app.git
    or
    git clone git@github.com:vkmrishad/loan_app.git

## Environment and Package Management
Install Poetry

    $ pip install poetry
    or
    $ pip3 install poetry

Activate or Create Env

    $ poetry shell

Install Packages from Poetry

    $ poetry install

NB: When using virtualenv, install from `$ pip install -r requirements.txt`.
For environment variables follow `sample.env`

## Runserver

    $ python manage.py runserver
    or
    $ ./manage.py runserver

Access server: http://127.0.0.1:8000
Access Admin: http://127.0.0.1:8000/admin/

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

## SuperUser
Create superuser to test admin feature

    $ python manage.py createsuperuser
    or
    $ ./manage.py createsuperuser

## Version

* Python: 3.8+
* Postgres 12+ / Sqlite3
