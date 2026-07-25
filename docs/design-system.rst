Design System Reference
========================

This document describes the visual conventions used across aclarknet's
dashboard and public-facing templates.

Color Palette
-------------

Colors are defined as CSS custom properties in the base template and
design preview page:

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Variable
     - Value
     - Usage
   * - ``--brand``
     - ``#1997c6``
     - Primary brand blue; links, icons, highlights
   * - ``--dark``
     - ``#0f2b3d``
     - Dark navy; headings, nav background, footer
   * - ``--light``
     - ``#f8f9fa``
     - Off-white; section backgrounds, card backgrounds

Bootstrap utility classes are preferred over custom colors wherever
possible (``text-muted``, ``bg-light``, ``border``, etc.).

Buttons
-------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Class
     - Usage
   * - ``btn-primary``
     - Primary actions (save, submit, confirm)
   * - ``btn-outline-primary``
     - Secondary actions (edit, view, cancel)
   * - ``btn-outline-danger``
     - Destructive actions (delete, remove)
   * - ``btn-sm``
     - Inline table/card actions

Avoid custom button variants. The ``btn-outline-dashboard`` and
``btn-outline-secondary`` classes were removed during the design
unification pass.

Typography
----------

- **Font**: Inter (loaded via Google Fonts)
- **Headings**: ``fw-bold``, Bootstrap heading scale (``h1``–``h5``)
- **Body**: default Bootstrap sizing (1rem / 16px)
- **Small/meta text**: ``small`` or ``text-muted``
- **Section eyebrows**: ``section-eyebrow`` class — small caps, tracked,
  muted color above section headings

Spacing
-------

- Section padding: ``py-5`` (3rem top/bottom)
- Card inner padding: ``p-4``
- List/grid gaps: ``g-3`` or ``g-4``
- Inline element margin: ``mb-3`` or ``my-3``

Avoid ad-hoc ``mt-5 mb-3`` combinations; prefer symmetric ``my-3``.

Cards
-----

Standard card pattern::

   <div class="p-4 rounded-3 h-100" style="border:1px solid #e9ecef;">
     ...
   </div>

Use ``h-100`` inside ``row g-4`` grids to equalise card heights.
Hover effects use a subtle ``box-shadow`` transition, not background
color changes.

Tables
------

- Use ``table table-hover`` for interactive rows.
- Date/action cells use ``display:flex`` with ``height:100%`` so the
  entire cell is clickable, not just the text.
- Links within table cells: dark text (``text-dark``) with a gray hover,
  matching the table-hover row style, to avoid jarring color jumps.

Icons
-----

Font Awesome 6 (Free) is used throughout. Preferred style is
``fa-solid`` for UI actions and ``fa-brands`` for technology logos.

Common icon usage:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Icon
     - Usage
   * - ``fa-copy``
     - Copy to clipboard buttons
   * - ``fa-external-link``
     - Open in new tab links
   * - ``fa-robot``
     - GitHub Copilot / AI
   * - ``fa-brain``
     - Claude AI
   * - ``fa-microchip``
     - OpenAI

PDF / Web Distinction
---------------------

Interactive elements (copy buttons, external links, action icons) are
wrapped in ``{% if not pdf %}`` blocks so they are excluded from PDF
exports. Static, print-safe content (amounts, labels, dates) renders
in both contexts.
