# https://just.systems
# django-admin startproject aclarknet .
# django-admin startapp db
# python manage.py webpack_init --no-input
# ls -a | llm "Can you output a README.md based on what you see in this dir?"
# pre-commit install

default:
    echo 'Hello, world!'

i:
    uv pip install -e .

p:
    vi pyproject.toml

r:
    vi README.md

m:
    python manage.py migrate
