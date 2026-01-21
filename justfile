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
    uv pip install -e '.[dev,test]'
    npm install
    prek install

p:
    nvim pyproject.toml

r:
    nvim README.md

m:
    python manage.py migrate

mm: d
    rm -rvf aclarknet/migrations/
    rm -rvf cms/migrations/
    rm -rvf db/migrations/
    rm -rvf home/migrations/
    rm -rvf siteuser/migrations/
    python manage.py makemigrations admin auth contenttypes siteuser wagtailcore taggit db account socialaccount cms wagtailadmin wagtaildocs wagtailimages wagtailembeds wagtailforms wagtailredirects wagtailsearch home wagtailusers
    python manage.py migrate

d:
    mongosh ${MONGODB_URI:-mongodb://localhost:27017} --eval 'db.getSiblingDB("aclarknet").dropDatabase()'

pc:
    prek --all-files

s:
    npm run watch &
    python manage.py runserver

su:
    export DJANGO_SUPERUSER_PASSWORD=admin && python manage.py createsuperuser --noinput --username=admin

se:
    nvim aclarknet/settings/base.py

o:
    open http://localhost:8000/dashboard/

t:
    pytest db/tests/

n:
    npm install

w:
    open http://localhost:8000/wagtail/

b:
    docker build -t aclarknet .
    aws ecr create-repository --repository-name aclarknet

cd:
    python manage.py create_data

# Build Sphinx documentation
docs:
    cd docs && make html

# Clean and rebuild Sphinx documentation
docs-clean:
    cd docs && make clean && make html
