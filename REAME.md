# Django Tutoring Project

Django Tutoring Project is a simple website where teachers can sign up and create courses while students can sign up and buy the courses.
The project also contains a blog and a event/ticket buying system.

## Features

-   Enroll for Course(s)
-   Buy event tickets
-   Blog

## Installation

```sh
$ git clone https://github.com/evanceodoyo/django_tutoring_project.git
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Create a new PostgreSQL database

```sh
 $ psql postgres
 $ CREATE DATABASE databasename$
 $ \connect databasename
```

Set the environment variables in settings.py
Make migrations

```sh
$ python manage.py makemigrations
$ python manage.py migrate
```

Create a superuser

```sh
$ python manage.py createsuperuser
```

Start the development server

```sh
$ python manage.py runserver
```
