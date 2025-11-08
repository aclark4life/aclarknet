from django.contrib import admin, messages
from django.db.models import Sum, F, ExpressionWrapper, FloatField
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, path
from django.utils.html import format_html
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .models import Company, Client, Employee, Project, Invoice, Time, Task


# ─────────────────────────────────────────────
# Inlines
# ─────────────────────────────────────────────


class TimeInline(admin.TabularInline):
    model = Time
    extra = 1
    fields = ["view_link", "date", "task", "hours", "cost"]
    readonly_fields = ["cost", "view_link"]

    def view_link(self, obj):
        if obj.pk:
            url = reverse("admin:db_time_change", args=[obj.pk])
            return format_html(
                '<a href="{}" class="inline-related" title="View selected time">'
                '<img width=24 height=24 src="/static/admin/img/icon-viewlink.svg" alt="View"></a>',
                url,
            )
        return "-"

    view_link.short_description = "View"


class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 1
    fields = ["view_link", "number", "date", "amount"]
    readonly_fields = ["view_link"]

    def view_link(self, obj):
        if obj.pk:
            url = reverse("admin:db_invoice_change", args=[obj.pk])
            return format_html(
                '<a href="{}" class="inline-related" title="View selected invoice">'
                '<img width=24 height=24 src="/static/admin/img/icon-viewlink.svg" alt="View"></a>',
                url,
            )
        return "-"

    view_link.short_description = "View"


class ClientInline(admin.TabularInline):
    model = Client
    extra = 1
    fields = ["view_link", "name", "email", "phone"]
    readonly_fields = ["view_link"]

    def view_link(self, obj):
        if obj.pk:
            url = reverse("admin:db_client_change", args=[obj.pk])
            return format_html(
                '<a href="{}" class="inline-related" title="View selected client">'
                '<img width=24 height=24 src="/static/admin/img/icon-viewlink.svg" alt="View"></a>',
                url,
            )
        return "-"

    view_link.short_description = "View"


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1
    fields = ["view_link", "name", "start_date", "end_date"]
    readonly_fields = ["view_link"]

    def view_link(self, obj):
        if obj.pk:
            url = reverse("admin:db_project_change", args=[obj.pk])
            return format_html(
                '<a href="{}" class="inline-related" title="View selected project">'
                '<img width=24 height=24 src="/static/admin/img/icon-viewlink.svg" alt="View"></a>',
                url,
            )
        return "-"

    view_link.short_description = "View"


# ─────────────────────────────────────────────
# Admins
# ─────────────────────────────────────────────


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Company._meta.fields]
    inlines = [ClientInline]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Client._meta.fields]
    list_filter = ["company"]
    search_fields = ["name", "email"]
    inlines = [ProjectInline]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Project._meta.fields]
    list_filter = ["client"]
    search_fields = ["name", "description"]
    inlines = [InvoiceInline]


# ─────────────────────────────────────────────
# Invoice admin with PDF export button
# ─────────────────────────────────────────────


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Invoice._meta.fields] + [
        "total_time",
        "total_amount",
    ]
    list_filter = ["project"]
    search_fields = ["number"]
    inlines = [TimeInline]
    actions = ["export_as_pdf"]
    change_form_template = "admin/db/invoice/change_form.html"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            total_time_sum=Sum("times__hours"),
            total_amount_sum=Sum(
                ExpressionWrapper(
                    F("times__hours") * F("times__task__hourly_rate"),
                    output_field=FloatField(),
                )
            ),
        )
        return qs

    @admin.display(ordering="total_time_sum", description="Total Time (hours)")
    def total_time(self, obj):
        return obj.total_time_sum or 0

    @admin.display(ordering="total_amount_sum", description="Total Amount ($)")
    def total_amount(self, obj):
        return obj.total_amount_sum or 0

    # ── Action for multiple selection ──────────────────────────────
    def export_as_pdf(self, request, queryset):
        """Export selected invoices as a single PDF."""
        return self._generate_pdf(queryset)

    export_as_pdf.short_description = "Export selected invoices as PDF"

    # ── Custom button on change view ──────────────────────────────
    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        invoice = self.get_object(request, object_id)
        if invoice:
            pdf_url = reverse("admin:db_invoice_export_pdf", args=[invoice.pk])
            extra_context["extra_buttons"] = format_html(
                '<a class="button" href="{}" '
                'style="margin-left:10px;background:#5b80b2;color:white;padding:6px 10px;'
                'border-radius:4px;text-decoration:none;">🧾 Export PDF</a>',
                pdf_url,
            )
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    # ── Custom URL for button ──────────────────────────────
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/export-pdf/",
                self.admin_site.admin_view(self.export_single_pdf),
                name="db_invoice_export_pdf",
            ),
        ]
        return custom_urls + urls

    def export_single_pdf(self, request, object_id):
        """Handle the Export PDF button for a single invoice."""
        invoice = self.get_object(request, object_id)
        if not invoice:
            messages.error(request, "Invoice not found.")
            return HttpResponseRedirect(reverse("admin:db_invoice_changelist"))
        return self._generate_pdf([invoice])

    # ── Shared PDF generation logic ──────────────────────────────
    def _generate_pdf(self, invoices):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - 50

        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y, "Invoice Export")
        y -= 30

        for invoice in invoices:
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y, f"Invoice #{invoice.number}")
            y -= 20

            p.setFont("Helvetica", 12)
            project_name = invoice.project.name if invoice.project else "No Project"
            p.drawString(50, y, f"Project: {project_name}")
            y -= 15
            p.drawString(50, y, f"Date: {invoice.date}")
            y -= 15

            total_amount = sum(
                (time.hours * (time.task.hourly_rate if time.task else 0))
                for time in invoice.times.all()
            )
            p.drawString(50, y, f"Amount: ${total_amount:.2f}")
            y -= 15

            p.setFont("Helvetica-Oblique", 12)
            p.drawString(50, y, "Time Entries:")
            y -= 20

            for time_entry in invoice.times.all():
                task = time_entry.task.name if time_entry.task else "No Task"
                cost = time_entry.hours * (
                    time_entry.task.hourly_rate if time_entry.task else 0
                )
                p.setFont("Helvetica", 11)
                p.drawString(
                    70,
                    y,
                    f"{time_entry.date} | {task} | {time_entry.hours}h | ${cost:.2f}",
                )
                y -= 15
                if y < 100:
                    p.showPage()
                    y = height - 50

            y -= 30
            if y < 100:
                p.showPage()
                y = height - 50

        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type="application/pdf")
        filename = (
            "invoices.pdf" if len(invoices) > 1 else f"invoice_{invoices[0].number}.pdf"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


# ─────────────────────────────────────────────
# Remaining Admins
# ─────────────────────────────────────────────


@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Time._meta.fields]
    list_filter = ["invoice", "task", "date"]
    search_fields = ["description", "task__name"]
    readonly_fields = ["cost"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["name", "hourly_rate", "description"]
    search_fields = ["name"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Employee._meta.fields]
    search_fields = ["first_name", "last_name", "email"]
