from django.contrib import admin
from .models import Company, Project


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Company._meta.fields]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Project._meta.fields]
