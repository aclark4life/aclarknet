# Invoice Form Submission Fix

## Problem
Users were unable to create or update invoices. The form submission would fail silently without redirecting to the invoice detail view.

## Root Cause Analysis

### Previous PRs Attempted to Fix Symptoms
The last 3 PRs (#80, #81, #82) attempted to fix "redirect issues" by manipulating the `form_valid()` method:
- PR #80: Removed manual `form.save()` calls
- PR #81: Added explicit `self.object = form.save()` calls back
- PR #82: Removed explicit save calls again

None of these addressed the actual problem.

### The Real Issue
The `InvoiceForm` declared `start_date` and `end_date` fields in its `Meta.fields`:

```python
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = (
            "project",
            "name",
            "issue_date",
            "start_date",    # ❌ Field doesn't exist on Invoice model!
            "end_date",      # ❌ Field doesn't exist on Invoice model!
            "due_date",
            "paid_amount",
        )
```

But the `Invoice` model didn't have these fields! When Django's `ModelForm.save()` tried to save the form data, it would fail because it couldn't find these fields on the model instance.

### Evidence Supporting This Conclusion

1. **Form Layout**: The form explicitly includes these fields in its layout (lines 128-129)
2. **Form Fields**: The form defines `start_date` and `end_date` as DateField widgets (lines 154-164)
3. **Template Usage**: The invoice template (line 82) expects these fields to exist:
   ```html
   <div>{{ object.start_date }}&mdash;{{ object.end_date }}</div>
   ```
4. **Commented Code**: The InvoiceCreateView had commented-out code that calculated these dates (lines 65-68, 82-86)

## Solution

### Changes Made

1. **Added missing fields to Invoice model** (`db/models.py`):
   ```python
   class Invoice(BaseModel):
       issue_date = models.DateField("Issue Date", default=timezone.now)
       start_date = models.DateField("Start Date", blank=True, null=True)  # NEW
       end_date = models.DateField("End Date", blank=True, null=True)      # NEW
       due_date = models.DateField("Due", blank=True, null=True)
   ```

2. **Created migration** (`db/migrations/0002_add_invoice_date_fields.py`):
   - Adds `start_date` field to Invoice model
   - Adds `end_date` field to Invoice model
   - Both fields are nullable to support existing invoices

3. **No view changes needed**: The existing `InvoiceCreateView.form_valid()` is correct:
   ```python
   def form_valid(self, form):
       project_id = self.request.GET.get("project_id")
       if project_id:
           project = Project.objects.get(pk=project_id)
           form.instance.project = project
       return super().form_valid(form)  # This now works!
   ```

### Why This Fix Works

The Django `ModelFormMixin.form_valid()` method does this:
1. Calls `self.object = form.save()` 
2. Calls `return HttpResponseRedirect(self.get_success_url())`

With the missing fields, step 1 would fail silently or raise an error. Now that the model has all the fields the form expects, the save succeeds and the redirect works.

## Testing

Created integration tests in `db/tests/test_invoice_date_fields.py`:
- Tests that Invoice model has `start_date` and `end_date` fields
- Tests that these fields can be null (for backwards compatibility)
- Tests that all InvoiceForm fields exist on the Invoice model

## Migration Required

Run migrations to apply the database schema changes:
```bash
python manage.py migrate
```

## Summary

The issue was **not** with the redirect logic or `form_valid()` method. The problem was that the form was trying to save fields that didn't exist on the model. The previous PRs were treating symptoms (redirect failures) rather than the cause (missing model fields).

This is a minimal, surgical fix that adds only the two missing fields needed for the form to work correctly.
