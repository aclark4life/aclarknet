"""Report-related views."""

import decimal
from itertools import chain

from django.db.models import F, Sum
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from .base import BaseView, SuperuserRequiredMixin
from ..forms import ReportForm
from ..models import Client, Company, Invoice, Report, Time


def get_queryset_related(self):
    """Get related querysets for a report."""
    report = self.get_object()
    company = report.company
    notes = report.notes.all()
    clients = report.clients.all()
    invoices = report.invoices.all()
    projects = report.projects.all()
    reports = report.reports.all()
    queryset_related = [
        q for q in [clients, invoices, notes, projects, reports] if q.exists()
    ]
    return company, projects, invoices, report, queryset_related


class BaseReportView(BaseView, SuperuserRequiredMixin):
    """Base view for Report model operations."""

    model = Report
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = ReportForm
    form_class = ReportForm
    template_name = "edit.html"
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"

    url_export_pdf = "report_export_pdf"
    url_email_pdf = "report_email_pdf"
    url_email_text = "report_email_text"

    def get_context_data(self, **kwargs):
        """Add export and email URLs to context."""
        context = super().get_context_data(**kwargs)
        context["url_export_pdf"] = self.url_export_pdf
        context["url_email_pdf"] = self.url_email_pdf
        context["url_email_text"] = self.url_email_text
        return context


class ReportDetailView(BaseReportView, DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        company, projects, invoices, report, queryset_related = get_queryset_related(
            self
        )

        context["invoices"] = invoices

        if company:
            queryset_related.insert(0, [company])

        queryset_related = list(chain(*queryset_related))

        for project in projects:
            for team_member in project.team.all():
                if team_member and team_member not in queryset_related:
                    queryset_related.append(team_member)

        for invoice in invoices:
            for time_entry in invoice.times.all():
                if time_entry:
                    queryset_related.append(time_entry)

        self._queryset_related = queryset_related
        self.has_related = True

        context["is_detail_view"] = True
        return context

    template_name = "view.html"


class CreateOrUpdateReportView(BaseReportView):
    update = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        last_month = now - timezone.timedelta(days=now.day)
        last_month = last_month.strftime("%B")

        if not self.update:
            context["form"].initial = {
                "name": f"{last_month} {now.year}",
            }

        clients = Client.objects.filter(archived=False)
        invoices = Invoice.objects.filter(archived=False)
        companies = Company.objects.filter(archived=False)

        projects = [invoice.project for invoice in invoices if invoice.project]
        tasks = [project.task for project in projects]

        report_hours = invoices.aggregate(hours=Sum("hours"))["hours"]
        report_amount = invoices.aggregate(amount=Sum(F("amount")))["amount"]
        report_cost = invoices.aggregate(cost=Sum(F("cost")))["cost"]
        report_net = invoices.aggregate(net=Sum(F("net")))["net"]

        team = {}
        for project in projects:
            team[project.name] = {}
            task = project.task

            gross, cost, net, rate = 0, 0, 0, 0

            for member in project.team.all():
                times = Time.objects.filter(
                    user=member, project=project, archived=False
                )

                approved = times.filter(invoice__isnull=False).aggregate(
                    total=Sum(F("hours"))
                )
                approved = approved["total"] or 0
                approved = decimal.Decimal(approved)

                if task:
                    gross = approved * task.rate

                profile = member.profile

                if profile:
                    rate = member.profile.rate
                    if rate:
                        cost = approved * member.profile.rate
                    if gross and cost:
                        net = gross - cost

                team[project.name][member.username] = {}
                team[project.name][member.username]["rate"] = str(rate)
                team[project.name][member.username]["hours"] = str(approved)
                team[project.name][member.username]["gross"] = str(gross)
                team[project.name][member.username]["cost"] = str(cost)
                team[project.name][member.username]["net"] = str(net)

            context["form"].initial.update(
                {
                    "clients": clients,
                    "projects": projects,
                    "tasks": tasks,
                    "invoices": invoices,
                    "hours": f"{report_hours or 0:.2f}",
                    "amount": f"{report_amount or 0:.2f}",
                    "cost": f"{report_cost or 0:.2f}",
                    "net": f"{report_net or 0:.2f}",
                    "user": self.request.user,
                    "company": companies.first(),
                    "team": team,
                }
            )

        return context


class ReportListView(BaseReportView, ListView):
    template_name = "index.html"


class ReportCreateView(CreateOrUpdateReportView, CreateView):
    success_url = reverse_lazy("report_view")

    def get_form(self, form_class=None):
        companies = Company.objects.filter(archived=False)
        form = super().get_form(form_class)
        form.fields["company"].queryset = companies
        return form

    def get_success_url(self):
        return reverse_lazy("report_view", args=[self.object.pk])


class ReportUpdateView(CreateOrUpdateReportView, UpdateView):
    update = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs["pk"]
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("report_view", args=[self.object.pk])


class ReportDeleteView(BaseReportView, DeleteView):
    template_name = "delete.html"
    success_url = reverse_lazy("report_index")

    def get_queryset(self):
        return Report.objects.all()


class ReportCopyView(BaseReportView, CreateView):
    success_url = reverse_lazy("report_index")

    def get_queryset(self):
        return Report.objects.all()

    def get_initial(self):
        original_report = Report.objects.get(pk=self.kwargs["pk"])
        return {
            "name": original_report.name,
        }

    def form_valid(self, form):
        new_report = form.save(commit=False)
        new_report.pk = None
        new_report.save()
        return super().form_valid(form)


# Placeholder for ReportEmailTextView - not in original views.py
class ReportEmailTextView(BaseReportView, View):
    """Placeholder for email text functionality."""

    def get(self, request, *args, **kwargs):
        # Implementation similar to NoteEmailTextView could be added here
        pass
