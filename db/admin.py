from django.contrib import admin
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Company, Client, Project, Invoice, Time, Task


# Inline for Time in Invoice
class TimeInline(admin.TabularInline):
    model = Time
    extra = 1
    fields = ["date", "task", "hours", "description", "cost", "user"]
    readonly_fields = ["cost"]  # cost is calculated
    show_change_link = False


# Inline for Invoice in Project
class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 1
    fields = ["number", "date", "amount"]
    show_change_link = True
    # Nested inlines not supported natively


# Inline for Project in Client
class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1
    fields = ["name", "description", "start_date", "end_date"]
    show_change_link = True


# Inline for Client in Company
class ClientInline(admin.TabularInline):
    model = Client
    extra = 1
    fields = ["name", "email", "phone", "address"]
    show_change_link = True


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


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Invoice._meta.fields] + [
        "total_time",
        "total_amount",
    ]
    list_filter = ["project"]
    search_fields = ["number"]
    inlines = [TimeInline]
    actions = ["export_as_pdf"]  # ✅ new action

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            total_time_sum=Sum("times__hours"),
            total_amount_sum=Sum(
                ExpressionWrapper(
                    F("times__hours") * F("times__task__hourly_rate"),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
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

    # ✅ NEW: PDF Export Action
    def export_as_pdf(self, request, queryset):
        """Export selected invoices as a single PDF."""
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        y = height - 50
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y, "Invoice Export")
        y -= 30

        for invoice in queryset:
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y, f"Invoice #{invoice.number}")
            y -= 20

            p.setFont("Helvetica", 12)
            project_name = invoice.project.name if invoice.project else "No Project"
            p.drawString(50, y, f"Project: {project_name}")
            y -= 15
            p.drawString(50, y, f"Date: {invoice.date}")
            y -= 15

            # ✅ Compute total dynamically
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
                if y < 100:  # new page when space runs out
                    p.showPage()
                    y = height - 50

            y -= 30
            if y < 100:
                p.showPage()
                y = height - 50

        p.save()
        buffer.seek(0)

        response = HttpResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="invoices.pdf"'
        return response

    export_as_pdf.short_description = "Export selected invoices as PDF"


@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = ["invoice", "task", "date", "hours", "description", "cost", "user"]
    list_filter = ["invoice", "task", "date"]
    search_fields = ["description", "task__name"]
    readonly_fields = ["cost"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["name", "hourly_rate", "description"]
    search_fields = ["name"]
