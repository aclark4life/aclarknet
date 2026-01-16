"""Invoice-related views."""

import io
import locale
from decimal import Decimal
from itertools import chain

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

try:
    from xhtml2pdf import pisa
except ModuleNotFoundError:
    pisa = None

from .base import (
    BaseView,
    FakeDataMixin,
    ModelCopyMixin,
    RedirectToObjectViewMixin,
    SuperuserRequiredMixin,
)
from ..forms import InvoiceForm
from ..models import Invoice, Project, Time

locale.setlocale(locale.LC_ALL, "")


class BaseInvoiceView(BaseView, SuperuserRequiredMixin):
    """Base view for Invoice model operations."""

    model = Invoice
    form_model = InvoiceForm
    form_class = InvoiceForm
    template_name = "edit.html"


class InvoiceListView(BaseInvoiceView, ListView):
    template_name = "index.html"


class InvoiceCreateView(
    FakeDataMixin,
    BaseInvoiceView,
    RedirectToObjectViewMixin,
    CreateView,
):
    fake_data_function = "get_fake_invoice_data"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     project_id = self.request.GET.get("project_id")
    #     now = timezone.now()
    #     year = now.year
    #     month = now.month
    #     start_date = timezone.datetime(year, month, 1)
    #     end_date = (
    #         timezone.datetime(year, month, 1) + timezone.timedelta(days=32)
    #     ).replace(day=1) - timezone.timedelta(days=1)
    #     month = now.month + 2
    #     if month > 12:
    #         year += 1
    #         month -= 12
    #     due_date = timezone.datetime(year, month, 1)
    #     month = now.month + 1
    #     if month > 12:
    #         year += 1
    #         month -= 12
    #     if month == 12:
    #         year += 1
    #         month = 1
    #     issue_date = timezone.datetime(year, month, 1)
    #     context["form"].initial = {
    #         "start_date": start_date,
    #         "end_date": end_date,
    #         "issue_date": issue_date,
    #         "due_date": due_date,
    #     }
    #     if project_id:
    #         project = Project.objects.get(pk=project_id)
    #         client = project.client
    #         subject = f"{project} {now.strftime('%B %Y')}"
    #         context["form"].initial.update(
    #             {
    #                 "subject": subject,
    #                 "client": client,
    #                 "project": project,
    #             }
    #         )
    #     return context

    def form_valid(self, form):
        project_id = self.request.GET.get("project_id")
        if project_id:
            project = Project.objects.get(pk=project_id)
            form.instance.project = project
        return super().form_valid(form)


class InvoiceDetailView(BaseInvoiceView, DetailView):
    url_export_doc = "invoice_export_doc"
    url_export_pdf = "invoice_export_pdf"
    url_email_doc = "invoice_email_doc"
    url_email_pdf = "invoice_email_pdf"
    url_email_text = "invoice_email_text"
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        invoice = self.get_object()
        times = invoice.times.all().order_by("-id")
        project = invoice.project
        queryset_related = [q for q in [times] if q.exists()]
        if project:
            queryset_related.append([project])
            client = invoice.project.client
            if client:
                queryset_related.append([client])
                # Add company through client if exists
                if client.company:
                    queryset_related.append([client.company])
        queryset_related = list(chain(*queryset_related))
        self._queryset_related = queryset_related
        self.has_related = True

        # Calculate user-based statistics
        from collections import defaultdict

        user_stats = defaultdict(
            lambda: {"hours": Decimal("0"), "amount": Decimal("0"), "rate": None}
        )

        for time_entry in times:
            if time_entry.user:
                user_key = time_entry.user.username
                user_stats[user_key]["hours"] += time_entry.hours or Decimal("0")
                user_stats[user_key]["amount"] += time_entry.amount or Decimal("0")
                user_stats[user_key]["rate"] = time_entry.user.rate
                user_stats[user_key]["user"] = time_entry.user

        # Convert to list for template iteration
        user_calculations = []
        total_hours = Decimal("0")
        total_amount = Decimal("0")

        for username, stats in user_stats.items():
            user_calculations.append(
                {
                    "user": stats["user"],
                    "username": username,
                    "hours": stats["hours"],
                    "rate": stats["rate"],
                    "amount": stats["amount"],
                }
            )
            total_hours += stats["hours"]
            total_amount += stats["amount"]

        # Sort by username for consistent display
        user_calculations.sort(key=lambda x: x["username"])

        # Define extra field values with formatted currency
        # Use safe formatting with None checks
        # self.field_values_extra = [
        #     (
        #         "Total",
        #         locale.currency(invoice.amount, grouping=True)
        #         if invoice.amount is not None
        #         else "N/A",
        #     ),
        #     (
        #         "Cost",
        #         locale.currency(invoice.cost, grouping=True)
        #         if invoice.cost is not None
        #         else "N/A",
        #     ),
        #     (
        #         "Net",
        #         locale.currency(invoice.net, grouping=True)
        #         if invoice.net is not None
        #         else "N/A",
        #     ),
        #     ("Hours", invoice.hours if invoice.hours is not None else "N/A"),
        # ]

        context = super().get_context_data(**kwargs)
        context["is_detail_view"] = True

        context["times"] = times
        context["user_calculations"] = user_calculations
        context["calc_total_hours"] = total_hours
        context["calc_total_amount"] = total_amount
        context["url_export_doc"] = self.url_export_doc
        context["url_export_pdf"] = self.url_export_pdf
        context["url_email_doc"] = self.url_email_doc
        context["url_email_pdf"] = self.url_email_pdf
        context["url_email_text"] = self.url_email_text

        return context


class InvoiceUpdateView(
    BaseInvoiceView,
    RedirectToObjectViewMixin,
    UpdateView,
):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url_cancel"] = f"{self.model_name}_view"
        context["pk"] = self.kwargs["pk"]
        return context

    def get_initial(self):
        initial = super().get_initial()
        times = Time.objects.filter(invoice=self.object)
        initial_times = [time.id for time in times]
        initial["times"] = initial_times
        return initial

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def form_valid(self, form):
        return super().form_valid(form)


class InvoiceDeleteView(BaseInvoiceView, DeleteView):
    template_name = "delete.html"
    success_url = reverse_lazy("invoice_index")

    def get_queryset(self):
        return Invoice.objects.all()


class InvoiceCopyView(
    BaseInvoiceView,
    ModelCopyMixin,
    RedirectToObjectViewMixin,
    CreateView,
):
    pass


class InvoiceExportPDFView(BaseInvoiceView, View):
    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["object_id"]
        obj = get_object_or_404(self.model, id=object_id)
        self.template_name = "table/invoice.html"
        context = {}
        context["pdf"] = True
        context["object"] = obj
        context["times"] = obj.times.all().order_by("date")
        template = get_template(self.template_name)
        html_content = template.render(context)
        pdf_file = io.BytesIO()
        pisa.CreatePDF(io.BytesIO(html_content.encode("UTF-8")), pdf_file)
        pdf_file.seek(0)
        response = FileResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="{self.model_name}_{object_id}.pdf"'
        )

        return response


class InvoiceEmailPDFView(BaseInvoiceView, View):
    model = Invoice
    template_name = None

    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["object_id"]
        obj = get_object_or_404(self.model, id=object_id)
        self.template_name = "table/invoice.html"
        context = {}
        context["pdf"] = True
        context["object"] = obj
        context["times"] = obj.times.all().order_by("date")
        template = get_template(self.template_name)
        html_content = template.render(context)
        pdf_file = io.BytesIO()
        pisa.CreatePDF(io.BytesIO(html_content.encode("UTF-8")), pdf_file)
        pdf_file.seek(0)
        subject = obj.subject
        email = EmailMessage(
            subject=subject,
            body="Please find attached, thank you!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.DEFAULT_FROM_EMAIL],
        )
        email.attach(
            f"{subject.replace(' ', '_')}.pdf",
            pdf_file.getvalue(),
            "application/pdf",
        )
        email.send()
        messages.success(
            request, f"Email sent successfully to: {settings.DEFAULT_FROM_EMAIL}"
        )
        return redirect(obj)
