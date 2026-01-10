"""Invoice-related views."""

import io
import locale
from itertools import chain

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import get_template
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
from xhtml2pdf import pisa

from .base import (
    BaseView,
    ModelCopyMixin,
    RedirectToObjectViewMixin,
    SuperuserRequiredMixin,
)
from ..forms import InvoiceForm
from ..models import Company, Invoice, Project, Time


class BaseInvoiceView(BaseView, SuperuserRequiredMixin):
    """Base view for Invoice model operations."""

    model = Invoice
    form_model = InvoiceForm
    form_class = InvoiceForm
    template_name = "edit.html"


class InvoiceListView(BaseInvoiceView, ListView):
    template_name = "index.html"


class InvoiceCreateView(
    BaseInvoiceView,
    RedirectToObjectViewMixin,
    CreateView,
):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.request.GET.get("project_id")
        now = timezone.now()
        year = now.year
        month = now.month
        start_date = timezone.datetime(year, month, 1)
        end_date = (
            timezone.datetime(year, month, 1) + timezone.timedelta(days=32)
        ).replace(day=1) - timezone.timedelta(days=1)
        month = now.month + 2
        if month > 12:
            year += 1
            month -= 12
        due_date = timezone.datetime(year, month, 1)
        month = now.month + 1
        if month > 12:
            year += 1
            month -= 12
        if month == 12:
            year += 1
            month = 1
        issue_date = timezone.datetime(year, month, 1)
        context["form"].initial = {
            "start_date": start_date,
            "end_date": end_date,
            "issue_date": issue_date,
            "due_date": due_date,
        }
        if project_id:
            project = Project.objects.get(pk=project_id)
            client = project.client
            task = project.task
            company = Company.objects.first()
            subject = f"{project} {now.strftime('%B %Y')}"
            context["form"].initial.update(
                {
                    "subject": subject,
                    "client": client,
                    "project": project,
                    "company": company,
                    "task": task,
                }
            )
        return context

    def form_valid(self, form):
        self.object = form.save()
        project_id = self.request.GET.get("project_id")
        if project_id:
            project = Project.objects.get(pk=project_id)
            self.object.project = project
            self.object.save()
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
        contacts = invoice.contacts.all()
        notes = invoice.notes.all()
        times = invoice.times.all().order_by("-id")
        project = invoice.project
        client = invoice.client
        task = invoice.task
        queryset_related = [q for q in [notes, times, contacts] if q.exists()]
        if project:
            queryset_related.append([project])
        if client:
            queryset_related.append([client])
        if task:
            queryset_related.append([task])
        queryset_related = list(chain(*queryset_related))
        queryset_related = sorted(queryset_related, key=self.get_archived)
        self._queryset_related = queryset_related
        self.has_related = True
        self.has_preview = True
        context = super().get_context_data(**kwargs)
        context["is_detail_view"] = True

        context["times"] = times
        context["notes"] = notes
        context["url_export_doc"] = self.url_export_doc
        context["url_export_pdf"] = self.url_export_pdf
        context["url_email_doc"] = self.url_email_doc
        context["url_email_pdf"] = self.url_email_pdf
        context["url_email_text"] = self.url_email_text
        context["field_values"].append(
            ("Total", locale.currency(self.object.amount, grouping=True))
        )
        context["field_values"].append(
            ("Cost", locale.currency(self.object.cost, grouping=True))
        )
        context["field_values"].append(
            ("Net", locale.currency(self.object.net, grouping=True))
        )
        context["field_values"].append(("Hours", self.object.hours))
        context["field_values"].append(("Company", self.object.company))
        contacts = self.object.contacts.all()
        context["field_values"].append(("Contacts", ""))
        if contacts:
            for contact in contacts:
                context["field_values"].append(("↳", contact))

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
        self.object = form.save()
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
        contact_emails = [
            contact.email for contact in obj.contacts.all() if contact.email is not None
        ]
        if contact_emails:
            for contact_email in contact_emails:
                email = EmailMessage(
                    subject=subject,
                    body="Please find attached, thank you!",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[contact_email],
                )
                email.attach(
                    f"{subject.replace(' ', '_')}.pdf",
                    pdf_file.getvalue(),
                    "application/pdf",
                )
                email.send()
                messages.success(
                    request, f"Email sent successfully to: {contact_email}"
                )
        else:
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
