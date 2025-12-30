# GitHub Copilot Instructions for aclarknet

## Project Overview

This is a Django-based web application using Wagtail CMS with a modern frontend stack. The project combines Django's robust backend capabilities with Wagtail's powerful content management features, along with a React-based frontend built with Webpack.

## Tech Stack

### Backend
- **Django 6.0**: Main web framework
- **Wagtail**: CMS framework for content management
- **MongoDB**: Database backend using `django-mongodb-backend`
- **Django Allauth**: Authentication and social account management
- **Python 3.14**: Target Python version

### Frontend
- **React 19**: UI library
- **Webpack 5**: Module bundler
- **Tailwind CSS 4**: Utility-first CSS framework
- **Bootstrap 5**: CSS framework
- **Babel**: JavaScript transpiler
- **SASS**: CSS preprocessor

### Development Tools
- **Ruff**: Python linter and formatter (configured in pre-commit hooks)
- **ESLint**: JavaScript linter
- **Stylelint**: CSS linter
- **pytest**: Testing framework
- **pre-commit**: Git hooks for code quality
- **just**: Command runner (see `justfile` for available commands)

## Project Structure

```
aclarknet/          # Main Django project directory
├── settings/       # Split settings (base, dev, production)
├── templates/      # Project-wide templates
└── static/         # Project-wide static files

db/                 # Custom Django app for database models and views
cms/                # Content management system app
home/               # Home page and landing content
search/             # Search functionality
frontend/           # Frontend assets and webpack configuration
```

## Development Setup

### Installation
```bash
# Install Python dependencies with optional dev/test dependencies
uv pip install -e '.[dev,test]'

# Install Node.js dependencies
npm install

# Set up pre-commit hooks
pre-commit install
```

### Running the Application
```bash
# Run development server with webpack watch (from justfile)
just s  # Runs both 'npm run watch' and 'python manage.py runserver'

# Alternative: Run Django server only
python manage.py runserver

# Create superuser
just su  # Creates admin/admin@example.com with password 'admin'
```

### Database Management
```bash
# Run migrations
just m  # or: python manage.py migrate

# Make migrations (recreates all migrations)
just mm

# Drop MongoDB database
just d  # Uses MONGODB_URI or localhost:27017
```

## Code Style and Conventions

### Python
- Follow PEP 8 style guide
- Use Ruff for linting and formatting (configured in `.pre-commit-config.yaml`)
- Settings are split into `base.py`, `dev.py`, and `production.py`
- Default settings module: `aclarknet.settings.dev`
- Use type hints where appropriate

### JavaScript/React
- Follow ESLint configuration in `.eslintrc`
- Use modern ES6+ syntax
- React 19 with functional components preferred
- Use prop-types for type checking

### CSS
- Use Tailwind CSS utilities as the primary styling approach
- Follow Stylelint configuration in `.stylelintrc.json`
- SCSS files are supported via sass-loader

### Git Workflow
- Pre-commit hooks run automatically before commits
- Hooks check for trailing whitespace, EOF fixes, YAML validity, and run Ruff

## Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific test file
just t  # Runs pytest db/tests/base.py

# Using pytest
pytest
```

### Test Configuration
- Test framework: pytest with pytest-django
- Test settings: `DJANGO_SETTINGS_MODULE = "aclarknet.settings.dev"`
- Test locations: Each app has its own `tests.py` or `tests/` directory

## Build and Deployment

### Frontend Build
```bash
# Production build
npm run build  # Uses webpack.config.prod.js

# Development build with watch
npm run watch  # Uses webpack.config.watch.js

# Development server
npm run start  # Uses webpack.config.dev.js
```

### Static Files
- Static files are processed through Webpack
- Django collectstatic is configured for production
- Webpack assets manifest tracks built files

## Important Commands (from justfile)

- `just i`: Install all dependencies (prek + uv pip install)
- `just s`: Start development server with webpack watch
- `just m`: Run Django migrations
- `just mm`: Recreate all migrations from scratch
- `just d`: Drop MongoDB database
- `just pc`: Run pre-commit on all files
- `just t`: Run tests
- `just su`: Create superuser (admin/admin)
- `just o`: Open admin panel at http://localhost:8000/admin/
- `just w`: Open Wagtail admin at http://localhost:8000/wagtail/

## Key Dependencies to Be Aware Of

- **django-allauth**: Handles user authentication, registration, and social accounts
- **django-crispy-forms**: Enhanced form rendering
- **django-import-export**: Import/export functionality for admin
- **wagtail**: CMS framework - extensive functionality for content management
- **django-phonenumber-field**: Phone number validation and formatting
- **xhtml2pdf**, **html2docx**: Document generation capabilities

## Database

- Uses MongoDB instead of traditional SQL databases
- Connection via `django-mongodb-backend`
- Default connection: `mongodb://localhost:27017/aclarknet`
- Can be overridden with `MONGODB_URI` environment variable

## Admin Access

- Django Admin: http://localhost:8000/admin/
- Wagtail Admin: http://localhost:8000/wagtail/
- Default superuser: admin/admin (use `just su` to create)

## Custom App Configurations

The project uses custom app configurations in `aclarknet/apps.py` for Wagtail and Django core apps. This allows for customization of app behavior while maintaining Django's modular structure.

## When Making Changes

1. **Always run tests** after making changes to ensure nothing breaks
2. **Check pre-commit hooks** pass before committing
3. **Follow existing patterns** in the codebase for consistency
4. **Update migrations** after model changes using `just mm` or `python manage.py makemigrations`
5. **Rebuild frontend assets** if making JavaScript/CSS changes
6. **Consider both admin interfaces** when making changes to models (Django Admin and Wagtail)

## Environment Variables

- `DJANGO_SETTINGS_MODULE`: Settings module to use (defaults to `aclarknet.settings.dev`)
- `MONGODB_URI`: MongoDB connection string (defaults to `mongodb://localhost:27017`)
- `DJANGO_SUPERUSER_PASSWORD`: Used for automated superuser creation

## Notes for Copilot

- This project combines traditional Django development with CMS capabilities through Wagtail
- The frontend uses a hybrid approach: Wagtail templates with React components where needed
- MongoDB is used instead of PostgreSQL/MySQL, so ORM usage may differ slightly
- The `justfile` is the primary way developers interact with the project - reference it for common tasks
- Pre-commit hooks are mandatory - all code must pass Ruff linting/formatting before commit
