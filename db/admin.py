from django.contrib import admin
from .models import Company, Client, Project, Invoice, Time


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Company._meta.fields]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Client._meta.fields]
    list_filter = ["company"]
    search_fields = ["name", "email"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Project._meta.fields]
    list_filter = ["client"]
    search_fields = ["name", "description"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Invoice._meta.fields]
    list_filter = ["project"]
    search_fields = ["number"]


@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Time._meta.fields]
    list_filter = ["invoice", "date"]
    search_fields = ["description"]
