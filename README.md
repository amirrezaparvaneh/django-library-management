# Django Library Management

A library management web application built with Django.

Repository: `https://github.com/amirrezaparvaneh/django-library-management`

## Features

Full book management (create, edit, delete, search, and price/date/category filtering), bulk deletion of current results, user registration/login/logout, categories, and private per-user favorites.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

For production, configure `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, and `DJANGO_ALLOWED_HOSTS`.

## Database Design

The visual Entity-Relationship Diagram of the library management system:

![Library ER Diagram](docs/er-diagram.svg)

The editable diagram is available at `docs/er-diagram.drawio`, with its text description in `docs/er-diagram.md`.
