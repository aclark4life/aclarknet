# https://just.systems
# django-admin startproject aclarknet .
# django-admin startapp db
# python manage.py webpack_init -h

default:
    echo 'Hello, world!'

i:
    uv pip install -e .

p:
    vi pyproject.toml
