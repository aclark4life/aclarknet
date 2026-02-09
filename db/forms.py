from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field
from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone

from .models import Client, Company, Contact, Invoice, Note, Project, Task, Time


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = (
            "name",
            "company",
            "address",
            "description",
            "url",
            "featured",
            "category",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(
                Field("name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(Field("url", css_class="form-control"), css_class="col-sm-6"),
            Div(
                Field("address", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            Div(
                Field("description", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            Div(Field("featured", css_class="form-check-input"), css_class="col-sm-4"),
            Div(Field("category", css_class="form-control"), css_class="col-sm-4"),
            Div(Field("company", css_class="form-control"), css_class="col-sm-4"),
            css_class="row",
        )


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = (
            "name",
            "address",
            "description",
            "url",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(
                Field("name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(Field("url", css_class="form-control"), css_class="col-sm-6"),
            Div(
                Field("address", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            Div(
                Field("description", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            css_class="row",
        )


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = (
            "first_name",
            "last_name",
            "name",
            "email",
            "number",
            "client",
            "address",
            "description",
            "url",
        )
        labels = {
            "name": "Full name",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(
                Field("first_name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(
                Field("last_name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(
                Field("name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(Field("email", css_class="form-control"), css_class="col-sm-6"),
            Div(
                Field("number", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(
                Field("url", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            css_class="row",
        )


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = (
            "invoice_number",
            "name",
            "project",
            "issue_date",
            "start_date",
            "end_date",
            "due_date",
            "amount",
            "paid_amount",
            "balance",
            "net",
            "cost",
            "hours",
            "currency",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make balance read-only since it's calculated from amount - paid_amount
        if "balance" in self.fields:
            self.fields["balance"].disabled = True
        # Make invoice_number read-only since it's auto-generated
        if "invoice_number" in self.fields:
            self.fields["invoice_number"].disabled = True
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = (
            "name",
            "description",
            "user",
            "content_type",
            "object_id",
            "is_testimonial",
            "is_featured",
        )
        widgets = {
            "content_type": forms.HiddenInput(),
            "object_id": forms.HiddenInput(),
            "user": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(
                Field("name", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            Div(
                Field("description", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            Div(
                Field("is_testimonial"),
                css_class="col-sm-6",
            ),
            Div(
                Field("is_featured"),
                css_class="col-sm-6",
            ),
            css_class="row",
        )


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            "name",
            "client",
            "description",
            "start_date",
            "end_date",
            "amount",
            "default_task",
        )
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.fields["client"].empty_label = "Select a client"
        self.fields[
            "client"
        ].queryset = Client.objects.all()  # Fetch all clients for the dropdown
        self.helper.layout = Div(
            Div(
                Field("name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(Field("start_date", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("end_date", css_class="form-control"), css_class="col-sm-6"),
            Div(
                Field("description", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            css_class="row",
        )


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            "name",
            "project",
            "rate",
            "unit",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(
                Field("name", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            Div(Field("project", css_class="form-control"), css_class="col-sm-12"),
            Div(Field("rate", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("unit", css_class="form-control"), css_class="col-sm-6"),
            css_class="row",
        )


class TimeForm(forms.ModelForm):
    """ """

    class Meta:
        model = Time
        fields = [
            "project",
            "task",
            "user",
            "invoice",
            "date",
            "hours",
            "description",
        ]
        widgets = {
            "user": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        # Extract user from kwargs (if provided)
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # For admin users, make the user field visible (not hidden)
        # For non-admin users, keep it hidden and remove admin-only fields
        if user and user.is_superuser:
            # Make user field visible for admins by replacing the HiddenInput widget
            # with a Select widget. The ModelChoiceField already has the queryset set up.
            from django.contrib.auth import get_user_model

            User = get_user_model()
            # Replace the widget while preserving the field's queryset
            self.fields["user"].widget = forms.Select()
            self.fields["user"].queryset = User.objects.all().order_by("username")
        else:
            # Remove invoice, task, name, and project fields for non-admin users
            self.fields.pop("invoice", None)
            self.fields.pop("task", None)
            self.fields.pop("name", None)
            self.fields.pop("project", None)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False

        # Build layout conditionally based on available fields
        layout_fields = [
            Div(Field("date", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("hours", css_class="form-control"), css_class="col-sm-6"),
        ]

        # Only add admin-only fields if they exist (i.e., for admins)
        if "name" in self.fields:
            layout_fields.append(
                Div(Field("name", css_class="form-control"), css_class="col-sm-6")
            )
        if "user" in self.fields and user and user.is_superuser:
            layout_fields.append(
                Div(Field("user", css_class="form-control"), css_class="col-sm-6")
            )
        if "project" in self.fields:
            layout_fields.append(
                Div(Field("project", css_class="form-control"), css_class="col-sm-6")
            )
        if "invoice" in self.fields:
            layout_fields.append(
                Div(Field("invoice", css_class="form-control"), css_class="col-sm-6")
            )
        if "task" in self.fields:
            layout_fields.append(
                Div(Field("task", css_class="form-control"), css_class="col-sm-6")
            )

        layout_fields.append(
            Div(
                Field("description", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            )
        )

        self.helper.layout = Div(*layout_fields, css_class="row")

    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        initial=timezone.now,
    )


class TimeEntryForm(forms.ModelForm):
    """Simplified form for Time entries in the invoice formset."""

    class Meta:
        model = Time
        fields = ["date", "hours", "description", "project", "task", "user"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "hours": forms.NumberInput(attrs={"class": "form-control", "step": "0.25"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "project": forms.Select(attrs={"class": "form-control"}),
            "task": forms.Select(attrs={"class": "form-control"}),
            "user": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].initial = timezone.now
        self.fields["description"].required = False
        self.fields["project"].required = False
        self.fields["task"].required = False
        self.fields["user"].required = False


# Create the inline formset for Time entries on Invoice
TimeEntryFormSet = inlineformset_factory(
    Invoice,
    Time,
    form=TimeEntryForm,
    extra=0,  # Number of empty forms to display
    can_delete=True,
    fields=["date", "hours", "description", "project", "task", "user"],
)
