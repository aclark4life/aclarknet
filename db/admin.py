from django.contrib import admin
from .models import Company, Client, Project, Invoice, Time, Task


# Inline for Time in Invoice
class TimeInline(admin.TabularInline):
    model = Time
    extra = 1
    fields = ["date", "task", "hours", "description", "cost"]
    readonly_fields = ["cost"]  # cost is calculated
    show_change_link = False


# Inline for Invoice in Project
class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 1
    fields = ["number", "date", "amount"]
    show_change_link = True
    # Nested inlines not supported natively


# Inline for Project in Client
class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1
    fields = ["name", "description", "start_date", "end_date"]
    show_change_link = True


# Inline for Client in Company
class ClientInline(admin.TabularInline):
    model = Client
    extra = 1
    fields = ["name", "email", "phone", "address"]
    show_change_link = True


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Company._meta.fields]
    inlines = [ClientInline]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Client._meta.fields]
    list_filter = ["company"]
    search_fields = ["name", "email"]
    inlines = [ProjectInline]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Project._meta.fields]
    list_filter = ["client"]
    search_fields = ["name", "description"]
    inlines = [InvoiceInline]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Invoice._meta.fields]
    list_filter = ["project"]
    search_fields = ["number"]
    inlines = [TimeInline]


@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = ["invoice", "task", "date", "hours", "description", "cost"]
    list_filter = ["invoice", "task", "date"]
    search_fields = ["description", "task__name"]
    readonly_fields = ["cost"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["name", "hourly_rate", "description"]
    search_fields = ["name"]
