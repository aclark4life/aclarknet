# Foreign Key Design Review: DB Models

## Executive Summary

This document provides a comprehensive code review of the foreign key relationships in the DB app models, focusing on the design pattern: **Company → Client → Project → Invoice → Time**, with **Task** as a supporting model for rate management.

**Overall Assessment:** The current FK design is **well-structured and follows Django best practices**. The child-to-parent FK pattern is correctly implemented throughout the hierarchy.

---

## 1. Fundamental FK Design Principle

### The Rule: **Child Should Have FK to Parent**

In Django ORM and relational database design, **the child (many-side) should have the foreign key pointing to the parent (one-side)**.

**Why?**
- Database normalization: One FK field in the child table vs. many potential references in parent
- Query efficiency: `SELECT * FROM child WHERE parent_id = X` is indexed and fast
- Data integrity: CASCADE/SET_NULL on child deletion is cleaner
- Django ORM patterns: `parent.child_set.all()` or `parent.children.all()` (with related_name)

**Anti-pattern:** Parent having FK to child creates a 1-to-1 forced relationship and breaks the one-to-many model.

---

## 2. Current Model Hierarchy Analysis

### 2.1 Company → Client Relationship (One-to-Many)

**Current Implementation:**
```python
class Client(BaseModel):
    company = models.ForeignKey(
        "Company", blank=True, null=True, on_delete=models.SET_NULL
    )
```

**Assessment:** ✅ **CORRECT**

**Reasoning:**
- **Parent:** Company (one company)
- **Child:** Client (many clients per company)
- **Design:** Client has FK to Company ✓
- **Query pattern:** `company.client_set.all()` retrieves all clients for a company
- **Business logic:** A company can have multiple clients, but a client belongs to one company at a time
- **Nullability:** `null=True` allows standalone clients (freelancer scenario)
- **Deletion behavior:** `SET_NULL` preserves client data when company is deleted

**Recommendation:** Add explicit `related_name`:
```python
company = models.ForeignKey(
    "Company", 
    blank=True, 
    null=True, 
    on_delete=models.SET_NULL,
    related_name="clients"  # Instead of company.client_set
)
```

---

### 2.2 Client → Project Relationship (One-to-Many)

**Current Implementation:**
```python
class Project(BaseModel):
    client = models.ForeignKey(
        Client, blank=True, null=True, on_delete=models.SET_NULL
    )
```

**Assessment:** ✅ **CORRECT**

**Reasoning:**
- **Parent:** Client (one client)
- **Child:** Project (many projects per client)
- **Design:** Project has FK to Client ✓
- **Query pattern:** `client.project_set.all()` retrieves all projects for a client
- **Business logic:** A client can have multiple projects, but a project belongs to one client
- **Nullability:** `null=True` allows internal projects without a client
- **Deletion behavior:** `SET_NULL` preserves project data when client is deleted

**Recommendation:** Add explicit `related_name`:
```python
client = models.ForeignKey(
    Client, 
    blank=True, 
    null=True, 
    on_delete=models.SET_NULL,
    related_name="projects"
)
```

---

### 2.3 Project → Invoice Relationship (One-to-Many)

**Current Implementation:**
```python
class Invoice(BaseModel):
    project = models.ForeignKey(
        "Project", blank=True, null=True, on_delete=models.SET_NULL
    )
```

**Assessment:** ✅ **CORRECT**

**Reasoning:**
- **Parent:** Project (one project)
- **Child:** Invoice (many invoices per project)
- **Design:** Invoice has FK to Project ✓
- **Query pattern:** `project.invoice_set.all()` retrieves all invoices for a project
- **Business logic:** A project can have multiple invoices (monthly billing, milestones), but an invoice is for one project
- **Nullability:** `null=True` allows miscellaneous invoices not tied to a specific project
- **Deletion behavior:** `SET_NULL` preserves invoice data when project is deleted

**Recommendation:** Add explicit `related_name`:
```python
project = models.ForeignKey(
    "Project", 
    blank=True, 
    null=True, 
    on_delete=models.SET_NULL,
    related_name="invoices"
)
```

---

### 2.4 Invoice → Time Relationship (One-to-Many)

**Current Implementation:**
```python
class Time(BaseModel):
    invoice = models.ForeignKey(
        Invoice,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="times",  # ✅ Already has related_name
    )
```

**Assessment:** ✅ **CORRECT AND WELL-DESIGNED**

**Reasoning:**
- **Parent:** Invoice (one invoice)
- **Child:** Time (many time entries per invoice)
- **Design:** Time has FK to Invoice ✓
- **Query pattern:** `invoice.times.all()` retrieves all time entries for an invoice
- **Business logic:** An invoice contains multiple time entries, but a time entry is billed on one invoice
- **Related name:** Already properly configured as `times`
- **Nullability:** `null=True` allows unbilled time entries
- **Deletion behavior:** `SET_NULL` preserves time tracking data when invoice is deleted

**Evidence in Code:**
```python
# In db/views/invoice.py:118
times = invoice.times.all().order_by("-id")

# In db/signals.py:60
times = Time.objects.filter(invoice=instance)
```

---

### 2.5 Project → Time Relationship (Optional One-to-Many)

**Current Implementation:**
```python
class Time(BaseModel):
    project = models.ForeignKey(
        Project,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
```

**Assessment:** ✅ **CORRECT**

**Reasoning:**
- **Parent:** Project (one project)
- **Child:** Time (many time entries per project)
- **Design:** Time has FK to Project ✓
- **Query pattern:** `project.time_set.all()` retrieves all time entries for a project
- **Business logic:** Time entries track work on a project, even before invoicing
- **Nullability:** `null=True` allows time tracking without a project
- **Deletion behavior:** `SET_NULL` preserves time data when project is deleted

**Recommendation:** Add explicit `related_name`:
```python
project = models.ForeignKey(
    Project,
    blank=True,
    null=True,
    on_delete=models.SET_NULL,
    related_name="time_entries"
)
```

---

## 3. Task Model Integration

### 3.1 Task → Project Relationship (Optional Many-to-One)

**Current Implementation:**
```python
class Task(BaseModel):
    project = models.ForeignKey(
        "Project",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Project this task belongs to (optional)",
    )
    rate = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
```

**Assessment:** ✅ **CORRECT AND WELL-DESIGNED**

**Reasoning:**
- **Parent:** Project (one project)
- **Child:** Task (many tasks per project)
- **Design:** Task has FK to Project ✓
- **Query pattern:** `project.tasks.all()` retrieves all tasks for a project
- **Business logic:** Tasks can be project-specific (with different rates) or global/reusable
- **Related name:** Properly configured as `tasks`
- **Nullability:** `null=True` allows global tasks reusable across projects
- **Purpose:** Task defines the **billing rate** for time entries

**Key Feature:**
```python
class Project(BaseModel):
    default_task = models.ForeignKey(
        "Task",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="project_defaults",
        help_text="Default task for this project's time entries",
    )
```
This allows projects to have a default billing rate via a default task.

---

### 3.2 Time → Task Relationship (Many-to-One)

**Current Implementation:**
```python
class Time(BaseModel):
    task = models.ForeignKey(
        Task,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
```

**Assessment:** ✅ **CORRECT AND CRITICAL FOR INVOICE CALCULATION**

**Reasoning:**
- **Parent:** Task (one task)
- **Child:** Time (many time entries per task)
- **Design:** Time has FK to Task ✓
- **Query pattern:** `task.time_set.all()` retrieves all time entries for a task
- **Business logic:** Time entries need a task to determine the billing rate
- **Automatic assignment:** Time entries automatically get a task via `Time.save()` method

**Critical Code Logic:**
```python
class Time(BaseModel):
    def save(self, *args, **kwargs):
        # Priority: project default > explicit task > global default
        if self.project and self.project.default_task:
            self.task = self.project.default_task
        elif self.task_id:
            pass  # Keep the explicit task
        else:
            self.task = Task.get_default_task()
        super().save(*args, **kwargs)
```

**Invoice Calculation:**
```python
# In db/signals.py:77-78
time.amount = time.task.rate * time.hours
time.net = time.amount - time.cost
```

**Recommendation:** Add explicit `related_name`:
```python
task = models.ForeignKey(
    Task,
    blank=True,
    null=True,
    on_delete=models.SET_NULL,
    related_name="time_entries"
)
```

---

## 4. Invoice Generation Workflow

### How It Works:

1. **Time Entry Creation:**
   - User creates `Time` entry with `project`, `hours`, and optionally `task`
   - `Time.save()` auto-assigns task based on priority:
     - If project has `default_task` → use it
     - Else if task explicitly set → keep it  
     - Else → use global default task (`Task.get_default_task()`)

2. **Invoice Creation:**
   - User creates `Invoice` for a `Project`
   - Time entries are associated with the invoice: `time.invoice = invoice_instance`

3. **Invoice Calculation (via signals):**
   - When Invoice is saved, `update_invoice` signal calculates totals:
     ```python
     time.amount = time.task.rate * time.hours  # Task provides the rate
     time.cost = time.user.profile.rate * time.hours  # User's cost rate
     time.net = time.amount - time.cost  # Profit
     ```
   - Invoice totals are sum of all associated time entries:
     ```python
     invoice.amount = sum(time.amount for time in times)
     invoice.cost = sum(time.cost for time in times)
     invoice.hours = sum(time.hours for time in times)
     invoice.net = invoice.amount - invoice.cost
     ```

4. **Critical Dependencies:**
   - ✅ `Time.task` must exist → provides billing rate
   - ✅ `Time.invoice` links time to invoice
   - ✅ `Time.project` (optional) provides context
   - ✅ `Task.rate` determines revenue per hour

---

## 5. Where Task Fits in the Hierarchy

### Question: Where does Task fit?

**Answer:** Task is a **supporting/reference model** that exists **parallel to the hierarchy** rather than within it.

```
Company → Client → Project → Invoice → Time
                      ↓                   ↑
                   Task ←-----------------┘
                   (rate table)
```

**Design Rationale:**
1. **Tasks are reusable:** A task like "Development" or "Consulting" can apply to many projects
2. **Tasks define rates:** Each task has a `rate` field that determines billing
3. **Flexible association:** 
   - Tasks can be project-specific (`Task.project = project`)
   - Tasks can be global (`Task.project = None`)
4. **Time entries use tasks:** `Time.task` determines the billing rate for that time entry
5. **Projects can have default tasks:** `Project.default_task` auto-assigns to time entries

**This design is optimal because:**
- ✅ Supports project-specific rates (different projects, different rates for same task type)
- ✅ Supports global task templates
- ✅ Separates "what work was done" (task) from "what time was spent" (time entry)
- ✅ Makes rate changes easy (update task rate, all future time entries use new rate)

---

## 6. Recommendations for Improvements

### 6.1 Add Related Names (LOW PRIORITY)

**Current State:** Some FKs lack `related_name`, relying on default `_set` suffix.

**Recommendation:** Add explicit `related_name` for better code readability:

```python
# In Client model
company = models.ForeignKey(
    "Company", 
    blank=True, 
    null=True, 
    on_delete=models.SET_NULL,
    related_name="clients"  # Instead of company.client_set
)

# In Project model
client = models.ForeignKey(
    Client, 
    blank=True, 
    null=True, 
    on_delete=models.SET_NULL,
    related_name="projects"  # Instead of client.project_set
)

# In Invoice model
project = models.ForeignKey(
    "Project", 
    blank=True, 
    null=True, 
    on_delete=models.SET_NULL,
    related_name="invoices"  # Instead of project.invoice_set
)

# In Time model
project = models.ForeignKey(
    Project,
    blank=True,
    null=True,
    on_delete=models.SET_NULL,
    related_name="time_entries"  # Instead of project.time_set
)

task = models.ForeignKey(
    Task,
    blank=True,
    null=True,
    on_delete=models.SET_NULL,
    related_name="time_entries"  # Instead of task.time_set
)
```

**Impact:** 
- More readable code: `company.clients.all()` vs `company.client_set.all()`
- Would require migration and updating view code

---

### 6.2 Consider PROTECT for Task Deletion (MEDIUM PRIORITY)

**Current State:**
```python
class Time(BaseModel):
    task = models.ForeignKey(
        Task,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,  # Sets to NULL when task deleted
    )
```

**Issue:** If a task is deleted, time entries lose their rate information, breaking invoice calculations.

**Recommendation:** Consider using `on_delete=models.PROTECT`:
```python
task = models.ForeignKey(
    Task,
    blank=True,
    null=True,
    on_delete=models.PROTECT,  # Prevent deletion of tasks with time entries
    related_name="time_entries"
)
```

**Trade-off:** This prevents accidental deletion but makes cleanup harder. The current `SET_NULL` approach is acceptable since `Time.save()` will reassign a default task.

---

### 6.3 Add Database Indexes (LOW PRIORITY)

**Note:** Django automatically creates indexes on ForeignKey fields, but explicit `db_index=True` ensures consistency.

---

## 7. Design Pattern Validation

### ✅ All FK relationships follow the correct pattern:

| Relationship | Parent | Child | FK Location | Status |
|--------------|--------|-------|-------------|--------|
| Company → Client | Company | Client | Client.company | ✅ Correct |
| Client → Project | Client | Project | Project.client | ✅ Correct |
| Project → Invoice | Project | Invoice | Invoice.project | ✅ Correct |
| Invoice → Time | Invoice | Time | Time.invoice | ✅ Correct |
| Project → Time | Project | Time | Time.project | ✅ Correct |
| Task → Project | Project | Task | Task.project | ✅ Correct |
| Task → Time | Task | Time | Time.task | ✅ Correct |

---

## 8. Summary

### Current FK Design: ✅ **EXCELLENT**

**Strengths:**
1. ✅ All FK relationships follow the correct child-to-parent pattern
2. ✅ Proper use of `null=True` for optional relationships
3. ✅ Proper use of `SET_NULL` to preserve data integrity on deletion
4. ✅ Task model correctly designed as a rate table
5. ✅ Invoice calculation logic properly uses FKs to traverse relationships
6. ✅ Related names used where most critical (`times`, `tasks`)

**Minor Improvements (Non-Critical):**
1. Add explicit `related_name` to all FKs for code readability
2. Consider `PROTECT` for Task deletion to prevent orphaned rates (or keep current `SET_NULL`)
3. Document the workflow for creating invoices with task rates

**Conclusion:**
The current foreign key design is **sound and follows Django best practices**. No structural changes are required. The hierarchy Company → Client → Project → Invoice → Time with Task as a rate table is optimal for the invoicing workflow.

---

## 9. Answer to Original Question

### "Should the parent or the child have the FK for each of these models?"

**Answer:** ✅ **The child should have the FK** (and your current design already does this correctly)

**Current Implementation (All Correct):**
- ✅ Client has FK to Company (child → parent)
- ✅ Project has FK to Client (child → parent)
- ✅ Invoice has FK to Project (child → parent)
- ✅ Time has FK to Invoice (child → parent)
- ✅ Time has FK to Task (child → parent)
- ✅ Task has FK to Project (child → parent, optional)

### "How should Task fit in?"

**Answer:** Task is a **rate table** that sits parallel to the hierarchy:
- Tasks can be project-specific or global (reusable)
- Time entries reference tasks to get billing rates
- Projects can have default tasks
- This design allows flexible billing: same task type, different rates per project

### "The goal is to create invoices with time entries associated with a task rate."

**Answer:** ✅ **This is already working correctly**:
1. Time entries are created with a task (auto-assigned if not specified)
2. Task has a `rate` field
3. When invoice is saved, signal calculates: `time.amount = time.task.rate * time.hours`
4. Invoice totals are sum of all time entry amounts

**No changes needed** - the current FK design fully supports this workflow.
