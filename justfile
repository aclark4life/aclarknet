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

mm:
    python manage.py makemigrations admin auth contenttypes wagtailcore taggit db

d:
    mongosh ${MONGODB_URI:-mongodb://localhost:27017} --eval 'db.getSiblingDB("aclarknet").dropDatabase()'

pc:
    pre-commit run --all-files

s:
    python manage.py runserver

su:
    export DJANGO_SUPERUSER_PASSWORD=admin && python manage.py createsuperuser --noinput --username=admin --email=admin@example.com

se:
    vi aclarknet/settings.py

o:
    open http://localhost:8000/admin
