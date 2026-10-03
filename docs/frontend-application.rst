Frontend Application
====================

Webpack scans ``src/application`` for ``.js`` files and includes them as
entry points.

For ``application/app.js``, import it in a template like this:

::

   {% javascript_pack 'app' attrs='charset="UTF-8"' %}

In most cases, you do not need another file in this directory.
