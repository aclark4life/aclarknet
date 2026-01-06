from crispy_forms.layout import Div, Field
from crispy_forms.helper import FormHelper
from django.contrib.auth import get_user_model
from django import forms
from django.utils import timezone
from .models import Client, Company, Contact, Invoice, Note, Project, Report, Task, Time


User = get_user_model()


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = (
            # "publish",
            # "link",
            "name",
            "description",
            "address",
            "url",
            # "company",
            # "tags",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            # Div(Field("publish"), css_class="col-sm-3"),
            # Div(Field("link"), css_class="col-sm-3"),
            Div(
                Field("name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(Field("url", css_class="form-control"), css_class="col-sm-6"),
            Div(
                Field("description", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            Div(
                Field("address", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            # Div(Field("company", css_class="form-control"), css_class="col-sm-12"),
            # Div(Field("tags", css_class="form-control"), css_class="col-sm-12"),
            css_class="row",
        )


class CompanyForm(forms.ModelForm):
    client_set = forms.ModelMultipleChoiceField(
        queryset=Client.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
        required=False,
        label="Clients",
    )

    class Meta:
        model = Company
        fields = ("name", "url", "description", "client_set")

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
                Field("description", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            Div(Field("client_set", css_class="vh-100"), css_class="col-sm-12"),
            css_class="row",
        )

        if self.instance.pk:
            self.fields["client_set"].initial = self.instance.client_set.all()


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = (
            "first_name",
            "last_name",
            "name",
            "email",
            # "client",
            "url",
            "number",
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
            # Div(Field("client", css_class="form-control"), css_class="col-sm-12"),
            css_class="row",
        )


class InvoiceForm(forms.ModelForm):
    """
    Issue Date, Last Payment Date, Invoice ID, PO Number, Client, Subject,
    Invoice Amount, Paid Amount, Balance, Subtotal, Discount, Tax, Tax2,
    Currency, Currency Symbol, Document Type
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            # Div(Field("contacts", css_class="form-control"), css_class="col-sm-12"),
            Div(
                Field("subject", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(Field("user", css_class="form-control"), css_class="col-sm-6"),
            # Div(Field("company", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("start_date", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("end_date", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("issue_date", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("due_date", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("client", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("project", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("task", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("po_number", css_class="form-control"), css_class="col-sm-6"),
            # Div(Field("paid_amount", css_class="form-control"), css_class="col-sm-6"),
            css_class="row mx-1",
        )

        # Get the choices for the field
        choices = self.fields["client"].choices
        sorted_choices = sorted(choices, key=lambda choice: choice[1])
        self.fields["client"].choices = sorted_choices

        # Get the choices for the field
        choices = self.fields["contacts"].choices
        sorted_choices = sorted(choices, key=lambda choice: choice[1])
        self.fields["contacts"].choices = sorted_choices

        self.fields["company"].empty_label = None

    class Meta:
        model = Invoice
        fields = (
            "contacts",
            "user",
            "project",
            "task",
            "subject",
            "client",
            "company",
            "issue_date",
            "start_date",
            "end_date",
            "due_date",
            "po_number",
            "paid_amount",
        )
        widgets = {
            "ein": forms.widgets.NumberInput(),
            "po_number": forms.widgets.NumberInput(),
            "sa_number": forms.widgets.NumberInput(),
        }

    issue_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        initial=timezone.now,
    )

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        initial=timezone.now,
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        initial=timezone.now,
    )

    due_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        initial=timezone.now,
    )

    contacts = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.filter(archived=False),
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
        required=False,
    )


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ("text", "title")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(
                Field("title", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            Div(
                Field("text", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            # Div(Field("notes", css_class="form-control"), css_class="col-sm-12"),
            css_class="row",
        )


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            "name",
            "description",
            "client",
            "task",
            "start_date",
            "end_date",
            # "team",
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
            Div(Field("task", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("start_date", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("end_date", css_class="form-control"), css_class="col-sm-6"),
            Div(
                Field("description", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            # Div(Field("team", css_class="form-control"), css_class="col-sm-12"),
            # Div(Field("client", css_class="form-control"), css_class="col-sm-12"),
            css_class="row",
        )
        # choices = self.fields["team"].choices
        # sorted_choices = sorted(choices, key=lambda choice: choice[1])
        # self.fields["team"].choices = sorted_choices


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = (
            "name",
            "date",
            "hours",
            "amount",
            "cost",
            "net",
            "clients",
            "invoices",
            "projects",
            "tasks",
            "contacts",
            "user",
            "company",
            # "team",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(
                Field("name", css_class="form-control bg-transparent border"),
                css_class="col-sm-4",
            ),
            Div(Field("date", css_class="form-control"), css_class="col-sm-4"),
            Div(Field("hours", css_class="form-control"), css_class="col-sm-4"),
            Div(Field("amount", css_class="form-control"), css_class="col-sm-4"),
            css_class="row",
        )

    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "col-2"}),
        required=False,
        initial=timezone.now,
    )

    contacts = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.filter(archived=False),
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
        required=False,
    )


class AdminReportForm(ReportForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = self.helper.layout
        layout.append(
            Div(Field("net", css_class="form-control"), css_class="col-sm-4"),
        )
        layout.append(
            Div(Field("cost", css_class="form-control"), css_class="col-sm-4")
        )
        layout.append(
            Div(Field("clients", css_class="form-control"), css_class="col-sm-6"),
        )
        layout.append(
            Div(Field("projects", css_class="form-control"), css_class="col-sm-6"),
        )
        layout.append(
            Div(Field("tasks", css_class="form-control"), css_class="col-sm-6"),
        )
        layout.append(
            Div(Field("invoices", css_class="form-control"), css_class="col-sm-6"),
        )
        layout.append(
            Div(Field("user", css_class="form-control"), css_class="col-sm-6"),
        )
        layout.append(
            Div(Field("company", css_class="form-control"), css_class="col-sm-6"),
        )
        layout.append(
            Div(
                Field("team", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
        )
        layout.append(
            Div(
                Field("contacts", css_class="form-control"),
                css_class="col-sm-6",
            ),
        )
        choices = self.fields["contacts"].choices
        sorted_choices = sorted(choices, key=lambda choice: choice[1])
        self.fields["contacts"].choices = sorted_choices
        choices = self.fields["user"].choices
        sorted_choices = sorted(choices, key=lambda choice: choice[1])
        self.fields["user"].choices = sorted_choices


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("name", "rate", "unit")

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
            Div(Field("rate", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("unit", css_class="form-control"), css_class="col-sm-6"),
            css_class="row",
        )


class TimeForm(forms.ModelForm):
    """ """

    class Meta:
        model = Time
        fields = [
            # "user",
            "date",
            "hours",
            "description",
            # "client",
            # "project",
            # "task",
            # "invoice",
            # "amount",
            # "net",
            # "cost",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(Field("date", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("hours", css_class="form-control"), css_class="col-sm-6"),
            # Div(Field("user", css_class="form-control"), css_class="col-sm-4"),
            # Div(Field("invoice", css_class="form-control"), css_class="col-sm-4"),
            # Div(Field("project", css_class="form-control"), css_class="col-sm-4"),
            Div(
                Field("description", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            css_class="row",
        )

    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        initial=timezone.now,
    )


class AdminTimeForm(TimeForm):
    """ """

    hours = forms.FloatField(
        required=False,
        initial=1.0,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Retrieve the existing layout object
        # layout = self.helper.layout

        # Make modifications to the layout object
        # layout.append(
        #     Div(Field("task", css_class="form-control"), css_class="col-sm-4")
        # )
        # layout.append(
        #     Div(Field("project", css_class="form-control"), css_class="col-sm-4")
        # )
        # layout.append(
        #     Div(Field("client", css_class="form-control"), css_class="col-sm-4")
        # )
        # layout.append(
        #     Div(Field("amount", css_class="form-control"), css_class="col-sm-4")
        # )
        # layout.append(
        #     Div(Field("cost", css_class="form-control"), css_class="col-sm-4")
        # )
        # layout.append(Div(Field("net", css_class="form-control"), css_class="col-sm-4"))

        # Sort choices for user field
        # choices = self.fields["user"].choices
        # sorted_choices = sorted(choices, key=lambda choice: choice[1])
        # self.fields["user"].choices = sorted_choices


class UserForm(forms.ModelForm):
    rate = forms.FloatField(required=False)
    mail = forms.BooleanField(required=False)
    address = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 4, "cols": 40})
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "rate",
            "mail",
            "address",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = getattr(self.instance, "profile", None)
        if profile:
            self.fields["rate"].initial = profile.rate
            self.fields["mail"].initial = profile.mail
            self.fields["address"].initial = profile.address

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(Field("is_active"), css_class="col-sm-3"),
            Div(Field("mail", css_class=""), css_class="col-sm-9"),
            Div(
                Field("username", css_class="form-control bg-transparent border"),
                css_class="col-sm-4",
            ),
            Div(Field("email", css_class="form-control"), css_class="col-sm-4"),
            Div(Field("rate", css_class="form-control"), css_class="col-sm-4"),
            Div(
                Field("first_name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(
                Field("last_name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(
                Field("address", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            css_class="row",
        )

    def save(self, commit=True):
        user = super().save(commit=commit)
        profile = getattr(user, "profile", None)
        if profile:
            profile.rate = self.cleaned_data["rate"]
            profile.address = self.cleaned_data["address"]
            profile.mail = self.cleaned_data["mail"]
        if commit:
            user.save()
        if profile and commit:
            profile.save()
        return user
