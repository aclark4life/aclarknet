# https://just.systems

default:
    echo 'Hello, world!'

[group('django')]
django-open:
    open http://localhost:8000
alias o := django-open

[group('django')]
django-serve:
    python manage.py runserver

[group('django')]
django-migrate:
    python manage.py migrate
alias m := django-migrate

[group('django')]
django-su:
    export DJANGO_SUPERUSER_PASSWORD=admin && python manage.py createsuperuser --noinput --username admin --email aclark@aclark.net
alias su := django-su

[group('npm')]
npm-install:
    cd frontend && npm install

[group('npm')]
npm-serve:
    cd frontend && npm run watch &

[group('python')]
pip-install:
    python -m pip install --upgrade pip
    python -m pip install -e .
alias i := pip-install

serve: npm-install npm-serve django-serve

alias s := serve
