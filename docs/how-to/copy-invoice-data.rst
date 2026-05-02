Copy Invoice Data for Emails
============================

This guide explains how to use the copy buttons in the invoice view to
quickly paste formatted invoice data into emails or other communications.

Overview
--------

The invoice view includes per-row copy buttons that format data as
plain text suitable for pasting into emails. Each row in the totals
accordion has a copy button that captures that row's label and value.

Using the Copy Buttons
----------------------

1. Open an invoice and expand the **Total** accordion (open by default
   at the top of the invoice view).

2. Each data row (e.g., Hours, Rate, Amount) has a **copy icon** on the
   right side.

3. Click the copy button for any row to copy it to your clipboard in
   the format::

      Label: Value

4. Paste directly into an email, Slack message, or any plain-text field.

Copying Multiple Rows
---------------------

To copy a summary block for an email:

1. Click the copy button on each row you want to include.
2. Paste each into your email in sequence.

The output is deliberately minimal and plain — no HTML, no extra
formatting — so it pastes cleanly into any email client.

Example Output
--------------

After clicking copy on a row, the clipboard will contain something like::

   Hours: 12.5
   Rate: $150.00
   Amount: $1,875.00

Notes
-----

- Copy buttons are visible in the web view only — they do not appear in
  PDF exports.
- If the clipboard API is unavailable (e.g., non-HTTPS or older browser),
  the button may not function. Use a modern browser over HTTPS.
