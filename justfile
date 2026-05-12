# https://just.systems
# django-admin startproject aclarknet .
# django-admin startapp db
# python manage.py webpack_init --no-input
# ls -a | llm "Can you output a README.md based on what you see in this dir?"
# pre-commit install
# nvm install 14

default:
    echo 'Hello, world!'

# Install dependencies (Python, Node, and pre-commit)
install:
    uv pip install -e '.[dev,test]'
    npm install
    prek install

alias i := install

# Edit pyproject.toml
edit-pyproject:
    nvim pyproject.toml

alias p := edit-pyproject

# Edit README.md
edit-readme:
    nvim README.md

alias r := edit-readme

# Run Django migrations
migrate:
    python manage.py migrate

alias m := migrate

# Make and run migrations (drops database first)
make-migrations: drop-database
    # rm -rvf aclarknet/migrations/
    # rm -rvf cms/migrations/
    # rm -rvf db/migrations/
    # rm -rvf home/migrations/
    # rm -rvf siteuser/migrations/
    python manage.py makemigrations admin auth contenttypes siteuser wagtailcore taggit db account socialaccount cms wagtailadmin wagtaildocs wagtailimages wagtailembeds wagtailforms wagtailredirects wagtailsearch home wagtailusers blog
    python manage.py migrate

alias mm := make-migrations

# Drop MongoDB database
drop-database:
    mongosh ${MONGODB_URI:-mongodb://localhost:27017} --eval 'db.getSiblingDB("aclarknet").dropDatabase()'

alias d := drop-database

# Run pre-commit on all files
pre-commit:
    prek --all-files

alias pc := pre-commit

# Run development server with webpack watch
server:
    npm run watch &
    python manage.py runserver

alias s := server

# Create Django superuser (admin/admin)
create-superuser:
    export DJANGO_SUPERUSER_PASSWORD=admin && python manage.py createsuperuser --noinput --username=admin

alias su := create-superuser

# Edit Django settings
edit-settings:
    nvim aclarknet/settings/base.py

alias se := edit-settings

# Open Django admin dashboard in browser
open-dashboard:
    open http://localhost:8000/dashboard/

alias o := open-dashboard

# Run tests
test:
    pytest db/tests/

alias t := test

# Install npm packages
npm-install:
    npm install

alias n := npm-install

# Open Wagtail admin in browser
open-wagtail:
    open http://localhost:8000/wagtail/

alias w := open-wagtail

# Build Docker image and create ECR repository
build-docker:
    docker build -t aclarknet .
    aws ecr create-repository --repository-name aclarknet

alias b := build-docker

# Create initial data
create-data:
    python manage.py create_data

alias cd := create-data

# Build Sphinx documentation
docs:
    cd docs && make html

# Clean and rebuild Sphinx documentation
docs-clean:
    cd docs && make clean && make html

# Deploy to production server (initial deployment)
deploy-initial:
    #!/usr/bin/env bash
    echo "Running initial deployment to /srv/aclarknet..."
    sudo deployment/deploy.sh --initial

alias di := deploy-initial

# Deploy to production server (update deployment)
deploy:
    #!/usr/bin/env bash
    echo "Deploying updates to /srv/aclarknet..."
    sudo deployment/deploy.sh

alias dp := deploy

# Deploy to production server remotely via SSH
deploy-remote:
    ssh aclark.net "cd /srv/aclarknet && sudo deployment/deploy.sh"

alias dpr := deploy-remote

# Check production service status
deploy-status:
    sudo systemctl status aclarknet.service

alias ds := deploy-status

# View production logs
deploy-logs:
    sudo journalctl -u aclarknet.service -n 50

alias dl := deploy-logs

# Restart production service
deploy-restart:
    sudo systemctl reload aclarknet.service
    sudo systemctl restart aclarknet.service
    sudo systemctl restart thelounge.service
    sudo systemctl reload nginx.service
    sudo systemctl restart nginx.service

alias dr := deploy-restart

# Build production static files
build-prod:
    npm run build
    python manage.py collectstatic --noinput

alias bp := build-prod

# Import blog entries from data/blog_entries.csv (use --update to overwrite existing)
import-blog:
    python manage.py import_entries --csv data/blog_entries.csv

alias ib := import-blog

# Import blog entries with --update flag (overwrites existing entries)
import-blog-update:
    python manage.py import_entries --csv data/blog_entries.csv --update

alias ibu := import-blog-update

# Regenerate data/blog_entries.csv from cloned blog repos (requires repos cloned in /tmp/blog-import/)
generate-blog-csv:
    python manage.py blog_to_csv --repo-path /tmp/blog-import/blog-2017 --source blog-2017 --output /tmp/blog-import/csvs/blog-2017.csv
    python manage.py blog_to_csv --repo-path /tmp/blog-import/blog-2020 --source blog-2020 --output /tmp/blog-import/csvs/blog-2020.csv
    python manage.py blog_to_csv --repo-path /tmp/blog-import/pelican-blog --source pelican-blog --output /tmp/blog-import/csvs/pelican-blog.csv
    python manage.py blog_to_csv --repo-path /tmp/blog-import/blog --source blog --output /tmp/blog-import/csvs/blog.csv
    python manage.py blog_to_csv --merge /tmp/blog-import/csvs/blog-2017.csv /tmp/blog-import/csvs/blog-2020.csv /tmp/blog-import/csvs/pelican-blog.csv /tmp/blog-import/csvs/blog.csv --output data/blog_entries.csv

alias gbc := generate-blog-csv

# Import blog entries from data/posts/*.rst files (upserts on pub_date + slug)
import-rst-posts:
    python manage.py import_rst_posts

alias irp := import-rst-posts

# Push local changes and reimport blog posts on production
deploy-posts:
    git push
    ssh aclark.net "cd /srv/aclarknet && sudo git pull && sudo DJANGO_SETTINGS_MODULE=aclarknet.settings.production .venv/bin/python manage.py import_rst_posts && sudo systemctl restart aclarknet"

alias dposts := deploy-posts

# Clone blog source repos to /tmp/blog-import/ for CSV regeneration
clone-blog-repos:
    gh repo clone aclark4life/blog /tmp/blog-import/blog || true
    gh repo clone aclark4life/blog-2017 /tmp/blog-import/blog-2017 || true
    gh repo clone aclark4life/blog-2020 /tmp/blog-import/blog-2020 || true
    gh repo clone aclark4life/pelican-blog /tmp/blog-import/pelican-blog || true

alias cbr := clone-blog-repos
