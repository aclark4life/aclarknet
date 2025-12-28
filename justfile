# https://just.systems
# django-admin startproject aclarknet .
# django-admin startapp db
# python manage.py webpack_init --no-input
# ls -a | llm "Can you output a README.md based on what you see in this dir?"
# pre-commit install
# nvm install 14

default:
    echo 'Hello, world!'

# uv pip install
i:
    uv pip install -e '.[test]'

p:
    nvim pyproject.toml

r:
    nvim README.md

m:
    python manage.py migrate

mm:
    python manage.py makemigrations admin auth contenttypes wagtailcore taggit db account socialaccount cms

d:
    mongosh ${MONGODB_URI:-mongodb://localhost:27017} --eval 'db.getSiblingDB("aclarknet").dropDatabase()'

pc:
    pre-commit run --all-files

s:
    npm run watch &
    python manage.py runserver

su:
    export DJANGO_SUPERUSER_PASSWORD=admin && python manage.py createsuperuser --noinput --username=admin --email=admin@example.com

se:
    nvim aclarknet/settings.py

o:
    open http://localhost:8000/admin/

t:
    pytest db/tests/base.py

n:
    npm install

w:
    open http://localhost:8000/wagtail/
