# Unused Fields Analysis - db/models.py

**Date:** 2026-01-15  
**Analysis Scope:** All fields in db/models.py models

## Summary

This document identifies fields that are defined in `db/models.py` but are not actively used in the application logic (templates, views, forms, signals, tests, or management commands).

## Methodology

Fields were searched across:
- ✅ Templates (*.html files)
- ✅ Views (db/views/*.py)
- ✅ Forms (db/forms.py)
- ✅ Admin (db/admin.py)
- ✅ Signals (db/signals.py)
- ✅ Tests (db/tests/*.py)
- ✅ Management commands (db/management/commands/*.py)
- ✅ Template tags (db/templatetags/*.py)

## Findings

### ❌ UNUSED FIELDS (Safe to Remove)

These fields are defined in models but never referenced in application logic:

#### Client Model
- **`email`** (EmailField) - Defined with default value "aclark@aclark.net" but never accessed anywhere in the codebase

#### Invoice Model
- **`gross`** (DecimalField) - Never assigned or used; the template uses a computed value from views, not this model field

#### Project Model
- **`total_hours`** (FloatField) - Only in model definition and migrations
- **`billable_hours`** (FloatField) - Only in model definition and migrations
- **`budget`** (DecimalField) - Only in model definition, migrations, and admin import configuration (but never actually used in logic)
- **`budget_spent`** (DecimalField) - Only in model definition, migrations, and admin import configuration
- **`budget_remaining`** (DecimalField) - Only in model definition and migrations
- **`total_costs`** (DecimalField) - Only in model definition, migrations, and admin import configuration
- **`team_costs`** (DecimalField) - Only in model definition, migrations, and admin import configuration
- **`cost`** (DecimalField) - Only in model definition and migrations
- **`expenses`** (DecimalField) - Only in model definition and migrations
- **`companies`** (ManyToManyField to Company) - Only in model definition and migrations, never used to associate companies with projects

### ✅ USED FIELDS (Keep)

These fields appear unused at first glance but are actually used:

#### Client Model
- **`address`** - Used in `db/templates/invoice.html:70` (displayed in invoice templates)
- **`company`** - Used in `db/views/client.py`, `db/views/project.py`, and `db/templates/invoice.html:43,45`

#### Company Model
- **`address`** - Used in `db/templates/invoice.html:45` and `db/management/commands/create_data.py:79`

#### Contact Model
- **`address`** - Used in `db/management/commands/create_data.py:111` (populated during data creation)

#### Invoice Model
- **`gross`** - ⚠️ **MISLEADING**: The template `statcards/revenue.html` displays `invoices.gross`, but this is actually a computed local variable from `db/views/dashboard.py:61-62` (sum of Invoice.amount), NOT the model field. The model field `Invoice.gross` is never used.
- **`net`** - Used in `db/signals.py:54,87,92` (computed), `db/templates/statcards/revenue.html`, and `db/views/dashboard.py`
- **`cost`** - Used in `db/signals.py:55,80,92` (computed), `db/views/dashboard.py`, and templates
- **`hours`** - Used in `db/signals.py:56,82-83,92` (computed), `db/views/base.py`, and `db/templates/invoice.html:135`
- **`reset`** - Used in `db/signals.py:58` to control invoice update logic
- **`currency`** - Used in `db/management/commands/create_data.py:156` and has a meaningful default

#### Project Model
- **`code`** - Used in `db/management/commands/create_data.py:138`
- **`amount`** - Used in `db/views/dashboard.py` (aggregated for dashboard stats)
- **`default_task`** - Used in `db/models.py:266-267` (Time model references it) and tested in `db/tests/test_time_default_task.py`

#### Task Model
- **`rate`** - Used in `db/signals.py:68`, `db/management/commands/create_data.py`, `db/templates/invoice.html:137`, and tests
- **`unit`** - Used in `db/management/commands/create_data.py:127` and validated in tests
- **`project`** - Used in `db/views/task.py` for relationship management

#### Time Model
- **`amount`** - Used extensively in `db/signals.py`, `db/views/invoice.py`, `db/templates/invoice.html:140`, and other templates
- **`cost`** - Used in `db/signals.py:60,64,80` and templates
- **`net`** - Used in `db/signals.py:61,69,72` and displayed in templates

## Recommendations

### High Priority (Safe to Remove)

1. **Remove Client.email** - This field has a default value but is never used anywhere in the application
2. **Remove Invoice.gross** - This field is never assigned or accessed; the template uses a computed value from dashboard view, not this model field
3. **Remove Project financial tracking fields**: `total_hours`, `billable_hours`, `budget`, `budget_spent`, `budget_remaining`, `total_costs`, `team_costs`, `cost`, `expenses`
   - These appear to be part of an incomplete or abandoned feature for project budget tracking
   - Removing them will simplify the Project model significantly
4. **Remove Project.companies** - This ManyToMany relationship is never used to associate companies with projects

### Medium Priority (Review First)

None - all suspicious fields have been verified as either used or unused.

### Migration Strategy

When removing these fields:
1. Create a data migration to ensure no data is lost (though unused fields likely have no meaningful data)
2. Remove the field from the model
3. Remove any imports/references in admin.py (especially in ImportExportModelAdmin resources)
4. Run `makemigrations` and `migrate`
5. Test thoroughly to ensure no hidden dependencies

## Impact Assessment

**Low Risk Removals:**
- Client.email
- Invoice.gross
- Project.companies
- Project.total_hours
- Project.billable_hours
- Project.budget
- Project.budget_spent
- Project.budget_remaining
- Project.total_costs
- Project.team_costs
- Project.cost
- Project.expenses

**Total Fields to Remove:** 12 fields across 3 models (Client: 1, Invoice: 1, Project: 10)

**Database Size Reduction:** Minimal (these are mostly small fields)
**Code Clarity:** Significant improvement - removes confusion about which fields are actually used
**Maintenance:** Easier - fewer fields to consider when making changes to models

## Notes

- All analysis is based on current codebase state as of 2026-01-15
- Migration files were excluded from the "usage" count since they just reflect model changes
- Admin import/export configurations were noted but don't constitute "usage" if the field is never populated or accessed in logic
