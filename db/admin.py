from django import forms
from django.contrib import admin
from .models import Company, Project
from django_mongodb_backend.forms import EmbeddedModelArrayField


class CompanyAdminForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = "__all__"
        widgets = {
            "website": forms.URLInput(attrs={"size": 60}),
        }

    projects = EmbeddedModelArrayField(
        Project,
        prefix="project",
        extra_forms=1,
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    # Automatically include all model fields in the list display

    form = CompanyAdminForm
    list_display = [field.name for field in Company._meta.fields]
