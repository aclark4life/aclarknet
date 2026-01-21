# Sphinx Documentation

This directory contains the Sphinx documentation for the aclarknet project.

## Building the Documentation

### Using Make

```bash
cd sphinx_docs
make html
```

### Using justfile

```bash
just docs
```

## Viewing the Documentation

After building, open `_build/html/index.html` in your web browser.

## Adding New Documentation

1. Add your markdown or reStructuredText files to this directory
2. Update `index.rst` to include your new file in the toctree
3. Rebuild the documentation

## Theme

The documentation uses the [Furo](https://github.com/pradyunsg/furo) theme, which provides a clean, modern look.

## Markdown Support

This documentation supports both reStructuredText (.rst) and Markdown (.md) files through the myst-parser extension.
