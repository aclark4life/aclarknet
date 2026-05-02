Invoice Dashboard Design
========================

This document explains the design decisions behind the invoice view,
accordion layout, time entry links, and PDF/web rendering distinctions.

Accordion Layout
----------------

The invoice view uses Bootstrap accordions to group related information.
The current layout is:

1. **Total** (top, open by default) — summary figures: hours, rate,
   amount. Placed first so the most important numbers are immediately
   visible without scrolling.
2. **Invoice** (below, closed by default) — line items and time entries.
   Collapsed on load to reduce visual noise; expand when reviewing detail.

The Detail accordion was removed from the invoice view — its content was
either redundant or better represented in the Total summary.

Time Entry Links
----------------

Each time entry row in the Invoice accordion includes a clickable date
link. Clicking the date opens the corresponding time entry edit form in a
new tab, making it easy to correct entries without losing your place in
the invoice.

The link is styled as a subtle icon (``fa-external-link``) rather than
a plain URL to keep the table visually clean.

PDF / Web Rendering
-------------------

Time entry links are intentionally hidden from PDF exports. The template
uses a conditional block::

   {% if not pdf %}
     <a href="..." target="_blank">...</a>
   {% endif %}

This keeps PDFs clean for client delivery while retaining interactive
links in the browser view. The same pattern is used for copy buttons and
other interactive elements that have no meaning in a static document.

Copy Buttons
------------

Each row in the Total accordion includes a copy button (clipboard icon)
that copies the row's label and value as plain text. This is designed
for quickly pasting invoice summaries into emails without reformatting.

See :doc:`../how-to/copy-invoice-data` for usage instructions.

Design Unification
------------------

The dashboard templates underwent a design unification pass to ensure
consistency across views:

- **Buttons** — standardised on ``btn-outline-primary`` and
  ``btn-primary``; project-specific variants (``btn-outline-dashboard``)
  were removed.
- **Colors** — a single neutral palette is used across all dashboard
  views, consistent with the Stripe payment page.
- **Spacing** — card and section spacing normalised to ``my-3`` /
  ``mb-3`` throughout.
- **Hover effects** — table row hover and card hover use the same subtle
  background shift for visual consistency.
