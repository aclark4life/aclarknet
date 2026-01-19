# Time Entry User Assignment Fix

## Problem
Users could create time entries but could not edit them. When editing a time entry, the user field was being set to `None`, which caused permission checks to fail.

## Root Cause
In `TimeUpdateView`, when a non-admin user submitted an update form:
1. The `user` field was not included in the form (by design, for security)
2. When the form was saved without a user field, Django set `user` to `None`
3. This broke the permission check: `self.request.user == time.user` (because `time.user` was now `None`)

## Solution
Modified `TimeUpdateView.form_valid()` in `db/views/time.py` to:
1. Check if the saved object has `user=None`
2. If so, retrieve the original object from the database
3. Restore the original user value before saving

```python
def form_valid(self, form):
    # Preserve the original user - the user field may not be in the form for non-admins
    obj = form.save(commit=False)
    # If user is not set (likely because it wasn't in the form), use the original value
    if obj.user is None:
        original_obj = self.get_object()
        obj.user = original_obj.user
    obj.save()
    self.object = obj
    return super().form_valid(form)
```

## Why This Works
- For regular users: The user field is not in the form, so it comes back as `None`. The fix restores it from the database.
- For admin users: The user field IS in the form, so it's never `None`. The fix doesn't interfere.
- Security: The user field remains hidden from regular users, preventing tampering.

## Test Coverage
Added 12 new tests covering:
- User can create and edit their own entries
- User field is preserved across multiple edits
- Users cannot edit other users' entries
- Admin users can edit any entry
- Multiple users can work independently

All 18 related tests pass.

## Files Changed
- `db/views/time.py`: Modified `TimeUpdateView.form_valid()`
- `db/tests/test_time_update_preserves_user.py`: New tests
- `db/tests/test_user_cannot_edit_own_time.py`: New tests
- `db/tests/test_admin_time_update.py`: New tests
- `db/tests/test_time_entry_workflow.py`: New tests
- `.gitignore`: Added frontend/build/ directory
