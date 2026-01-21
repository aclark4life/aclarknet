# aclarknet Documentation

This directory contains the Sphinx documentation for the aclarknet project.

## Building the Documentation

### Prerequisites

Install the required dependencies:

```bash
pip install -e '.[dev]'
```

This will install:
- `sphinx` - Documentation generator
- `furo` - Modern Sphinx theme
- `myst-parser` - Markdown support for Sphinx

### Building HTML Documentation

```bash
cd docs
make html
```

The built documentation will be available in `docs/_build/html/`.

To view it, open `docs/_build/html/index.html` in your browser.

### Cleaning Build Files

```bash
cd docs
make clean
```

## Documentation Structure

The documentation is organized into the following sections:

### Deployment
- `deployment_guide.md` - Comprehensive deployment guide with detailed instructions
- `deployment_quickstart.md` - Quick reference for deployment tasks

### Database
- `db_views.md` - Documentation for the database views module
- `invoice_time_formset.md` - Invoice time entry formset feature

### Frontend
- `frontend.md` - Frontend overview and setup
- `frontend_application.md` - Frontend application details
- `frontend_components.md` - Frontend components documentation

## Adding New Documentation

1. Create a new `.md` file in the `docs/` directory
2. Add the file (without the `.md` extension) to the appropriate section in `index.rst`
3. Build the documentation to verify your changes

Example:

```rst
.. toctree::
   :maxdepth: 2
   :caption: My Section:

   my_new_doc
```

## Configuration

The Sphinx configuration is in `conf.py`. Key settings:

- **Theme**: Furo (modern, responsive theme)
- **Markdown Support**: MyST parser with extensions for:
  - Colon fence
  - Definition lists
  - Substitution
  - Task lists

## Additional Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [MyST Parser Documentation](https://myst-parser.readthedocs.io/)
- [Furo Theme Documentation](https://pradyunsg.me/furo/)
