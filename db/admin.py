from decimal import Decimal

from django.contrib import admin
from import_export import fields, widgets
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource as ImportExportModelResource

from .models import (
    Client,
    Company,
    Contact,
    Invoice,
    Note,
    Project,
    Task,
    Time,
)


class BooleanWidget(widgets.Widget):
    def clean(self, value):
        """
        Return eval string value
        """
        if value == "Yes":
            return True
        else:
            return False


class DecimalWidget(widgets.Widget):
    def clean(self, value):
        """
        Return eval string value
        """
        if value:
            return Decimal(value.replace(",", ""))
        else:
            return Decimal(0)


class ClientResource(ImportExportModelResource):
    class Meta:
        model = Client

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):
        if dataset.headers:
            dataset.headers = [
                str(header).lower().strip() for header in dataset.headers
            ]

        if "id" not in dataset.headers:
            dataset.headers.append("id")


@admin.register(Client)
class ClientAdmin(ImportExportModelAdmin):
    resource_class = ClientResource


@admin.register(Company)
class CompanyAdmin(ImportExportModelAdmin):
    pass


class ContactResource(ImportExportModelResource):
    client = fields.Field(
        column_name="client",
        attribute="client",
        widget=widgets.ForeignKeyWidget(Client, "name"),
    )

    class Meta:
        model = Contact

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):
        if dataset.headers:
            dataset.headers = [
                str(header).lower().strip() for header in dataset.headers
            ]

        if "id" not in dataset.headers:
            dataset.headers.append("id")


@admin.register(Contact)
class ContactAdmin(ImportExportModelAdmin):
    resource_class = ContactResource


class InvoiceResource(ImportExportModelResource):
    client = fields.Field(
        column_name="client",
        attribute="client",
        widget=widgets.ForeignKeyWidget(Client, "name"),
    )
    amount = fields.Field(
        column_name="amount", attribute="amount", widget=DecimalWidget()
    )
    paid_amount = fields.Field(
        column_name="paid_amount", attribute="paid_amount", widget=DecimalWidget()
    )
    balance = fields.Field(
        column_name="balance", attribute="balance", widget=DecimalWidget()
    )
    document_id = fields.Field(
        column_name="invoice_id", attribute="document_id", widget=DecimalWidget()
    )

    class Meta:
        model = Invoice

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):
        if dataset.headers:
            dataset.headers = [
                str(header).lower().strip() for header in dataset.headers
            ]

        if "id" not in dataset.headers:
            dataset.headers.append("id")


@admin.register(Invoice)
class InvoiceAdmin(ImportExportModelAdmin):
    resource_class = InvoiceResource


@admin.register(Note)
class NoteAdmin(ImportExportModelAdmin):
    pass


class ProjectResource(ImportExportModelResource):
    client = fields.Field(
        column_name="client",
        attribute="client",
        widget=widgets.ForeignKeyWidget(Client, "name"),
    )

    class Meta:
        model = Project

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):
        if dataset.headers:
            dataset.headers = [
                str(header).lower().strip() for header in dataset.headers
            ]

        if "id" not in dataset.headers:
            dataset.headers.append("id")


@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    resource_class = ProjectResource


class TaskResource(ImportExportModelResource):
    class Meta:
        model = Task

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):
        if dataset.headers:
            dataset.headers = [
                str(header).lower().strip() for header in dataset.headers
            ]

        if "id" not in dataset.headers:
            dataset.headers.append("id")


@admin.register(Task)
class TaskAdmin(ImportExportModelAdmin):
    resource_class = TaskResource
    list_display = ["name", "project", "rate", "unit"]
    list_filter = ["project"]
    search_fields = ["name", "project__name"]


class TimeResource(ImportExportModelResource):
    billable = fields.Field(
        column_name="billable", attribute="billable", widget=BooleanWidget()
    )
    client = fields.Field(
        column_name="client",
        attribute="client",
        widget=widgets.ForeignKeyWidget(Client, "name"),
    )
    invoiced = fields.Field(
        column_name="invoiced", attribute="invoiced", widget=BooleanWidget()
    )
    project = fields.Field(
        column_name="project",
        attribute="project",
        widget=widgets.ForeignKeyWidget(Project, "name"),
    )
    task = fields.Field(
        column_name="task",
        attribute="task",
        widget=widgets.ForeignKeyWidget(Task, "name"),
    )

    class Meta:
        model = Time

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):
        if dataset.headers:
            dataset.headers = [
                str(header).lower().strip() for header in dataset.headers
            ]

        if "id" not in dataset.headers:
            dataset.headers.append("id")


@admin.register(Time)
class TimeAdmin(ImportExportModelAdmin):
    resource_class = TimeResource
