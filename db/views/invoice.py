"""Invoice-related views."""

import io
import locale
from decimal import Decimal
from itertools import chain

from dateutil.relativedelta import relativedelta
from django.http import FileResponse
from django.shortcuts import get_object_or_404
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
    FakeDataMixin,
    ModelCopyMixin,
    RedirectToObjectViewMixin,
    SuperuserRequiredMixin,
)
from ..forms import InvoiceForm, TimeEntryFormSet
from ..models import Invoice, Project, Time

locale.setlocale(locale.LC_ALL, "")


class BaseInvoiceView(BaseView, SuperuserRequiredMixin):
    """Base view for Invoice model operations."""

    model = Invoice
    form_model = InvoiceForm
    form_class = InvoiceForm
    template_name = "edit.html"
    # Exclude description from title fields so it appears in card text with a label
    # This is especially important for related Time entries which have descriptions
    related_title_fields = ["name", "title", "subject"]


class InvoiceListView(BaseInvoiceView, ListView):
    template_name = "index.html"


class InvoiceCreateView(
    FakeDataMixin,
    BaseInvoiceView,
    RedirectToObjectViewMixin,
    CreateView,
):
    fake_data_function = "get_fake_invoice_data"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        # 1. Establish the base: First day of current month
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # 2. Calculate dates using relativedelta (handles year rollovers automatically)
        initial_data = {
            "start_date": start_of_month,
            "end_date": start_of_month + relativedelta(months=1, days=-1),
            "issue_date": start_of_month + relativedelta(months=1),
            "due_date": start_of_month + relativedelta(months=2),
            "name": context["form"].initial.get("name", ""),
        }

        # 3. Handle Project Logic
        project_id = self.request.GET.get("project_id")
        if project_id:
            # Use filter().first() to avoid DoesNotExist exceptions
            project = Project.objects.filter(pk=project_id).first()
            if project:
                initial_data.update(
                    {
                        "project": project,
                        "client": project.client,
                        "subject": f"{project} {now.strftime('%B %Y')}",
                    }
                )

        context["form"].initial = initial_data
        return context

    def form_valid(self, form):
        project_id = self.request.GET.get("project_id")
        if project_id:
            project = Project.objects.get(pk=project_id)
            form.instance.project = project
        return super().form_valid(form)


class InvoiceDetailView(BaseInvoiceView, DetailView):
    url_export_pdf = "invoice_export_pdf"
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
            lambda: {
                "hours": Decimal("0"),
                "amount": Decimal("0"),
                "cost": Decimal("0"),
                "rate": None,
            }
        )

        for time_entry in times:
            if time_entry.user:
                user_key = time_entry.user.username
                hours = time_entry.hours or Decimal("0")
                amount = time_entry.amount or Decimal("0")

                user_stats[user_key]["hours"] += hours
                user_stats[user_key]["amount"] += amount
                user_stats[user_key]["rate"] = time_entry.user.rate
                user_stats[user_key]["user"] = time_entry.user

                # Calculate cost (user rate * hours)
                if time_entry.user.rate:
                    user_stats[user_key]["cost"] += time_entry.user.rate * hours

        # Convert to list for template iteration
        user_calculations = []
        total_hours = Decimal("0")
        total_amount = Decimal("0")
        total_cost = Decimal("0")

        for username, stats in user_stats.items():
            cost = stats["cost"]
            amount = stats["amount"]
            difference = amount - cost

            # Calculate average task rate (amount / hours) after all entries are summed
            task_rate = None
            if stats["hours"] > 0:
                task_rate = stats["amount"] / stats["hours"]

            user_calculations.append(
                {
                    "user": stats["user"],
                    "username": username,
                    "hours": stats["hours"],
                    "user_rate": stats["rate"],
                    "task_rate": task_rate,
                    "cost": cost,
                    "amount": amount,
                    "difference": difference,
                }
            )
            total_hours += stats["hours"]
            total_amount += amount
            total_cost += cost

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
        context["calc_total_cost"] = total_cost
        context["calc_total_difference"] = total_amount - total_cost
        context["url_export_pdf"] = self.url_export_pdf

        return context


class InvoiceUpdateView(
    BaseInvoiceView,
    RedirectToObjectViewMixin,
    UpdateView,
):
    template_name = "invoice_edit.html"

    def get_time_formset(self):
        """Get the time entry formset for the invoice."""
        if self.request.POST:
            return TimeEntryFormSet(self.request.POST, instance=self.object)
        return TimeEntryFormSet(instance=self.object)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url_cancel"] = f"{self.model_name}_view"
        context["pk"] = self.kwargs["pk"]
        
        # Add the formset to the context
        if 'time_formset' not in kwargs:
            context['time_formset'] = self.get_time_formset()
        
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
        time_formset = self.get_time_formset()
        
        if time_formset.is_valid():
            self.object = form.save()
            time_formset.instance = self.object
            time_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(
                self.get_context_data(form=form, time_formset=time_formset)
            )




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
        invoice_number = obj.invoice_number
        self.template_name = "invoice.html"
        context = {}
        context["pdf"] = True
        context["object"] = obj
        context["times"] = obj.times.all().order_by("date")
        template = get_template(self.template_name)
        html_content = template.render(context)
        pdf_file = io.BytesIO()
        pisa.pisaDocument(io.BytesIO(html_content.encode("UTF-8")), pdf_file)
        pdf_file.seek(0)
        response = FileResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="{self.model_name}_{invoice_number}.pdf"'
        )

        return response
