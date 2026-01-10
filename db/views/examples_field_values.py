"""
Demonstration of field_values refactoring usage patterns.

This file shows concrete examples of how to use the new field_values
customization features in different scenarios.
"""

from django.views.generic import DetailView

from db.views.base import BaseView
from db.forms import ClientForm, InvoiceForm, ProjectForm
from db.models import Client, Invoice, Project


# Example 1: Default behavior - show all fields
# =============================================
class ClientDetailViewSimple(BaseView, DetailView):
    """
    Shows all fields from ClientForm by default.
    
    Before: Would only show fields if user.is_superuser
    After: Shows all fields for any authenticated user
    """

    model = Client
    form_class = ClientForm
    template_name = "view.html"
    # No customization needed - all fields shown automatically


# Example 2: Include only specific fields
# ========================================
class ClientDetailViewMinimal(BaseView, DetailView):
    """
    Shows only essential client information.
    
    Use case: Public-facing view or simplified display
    """

    model = Client
    form_class = ClientForm
    template_name = "view.html"

    # Only show these fields
    field_values_include = ["name", "url"]


# Example 3: Exclude sensitive fields
# ====================================
class ClientDetailViewSecure(BaseView, DetailView):
    """
    Shows all fields except sensitive ones.
    
    Use case: When you want most fields but need to hide some
    """

    model = Client
    form_class = ClientForm
    template_name = "view.html"

    # Hide sensitive or internal fields
    field_values_exclude = ["internal_notes", "billing_info"]


# Example 4: Add extra computed fields
# =====================================
class ProjectDetailViewEnhanced(BaseView, DetailView):
    """
    Shows form fields plus computed statistics.
    
    Use case: Display additional calculated or formatted values
    """

    model = Project
    form_class = ProjectForm
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        project = self.get_object()

        # Add computed fields
        self.field_values_extra = [
            ("Total Invoices", project.invoice_set.count()),
            ("Total Hours", sum(t.hours or 0 for t in project.time_set.all())),
            ("Status", "Active" if project.active else "Inactive"),
        ]

        return super().get_context_data(**kwargs)


# Example 5: Complex customization
# =================================
class InvoiceDetailViewCustom(BaseView, DetailView):
    """
    Combines include filter with extra formatted fields.
    
    Use case: Highly customized view with specific fields and calculations
    """

    model = Invoice
    form_class = InvoiceForm
    template_name = "view.html"

    # Only show these core fields
    field_values_include = ["subject", "issue_date", "due_date", "project"]

    def get_context_data(self, **kwargs):
        import locale

        invoice = self.get_object()

        # Add formatted financial fields
        self.field_values_extra = [
            (
                "Total Amount",
                locale.currency(invoice.amount, grouping=True)
                if invoice.amount
                else "N/A",
            ),
            (
                "Cost",
                locale.currency(invoice.cost, grouping=True)
                if invoice.cost
                else "N/A",
            ),
            (
                "Net Profit",
                locale.currency(invoice.net, grouping=True) if invoice.net else "N/A",
            ),
            ("Hours Billed", f"{invoice.hours:.2f}" if invoice.hours else "N/A"),
            ("Payment Status", "Paid" if invoice.paid_amount else "Unpaid"),
        ]

        return super().get_context_data(**kwargs)


# Example 6: Conditional field display
# =====================================
class ClientDetailViewConditional(BaseView, DetailView):
    """
    Dynamically adjusts which fields to show based on conditions.
    
    Use case: Different fields for different user types or states
    """

    model = Client
    form_class = ClientForm
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        client = self.get_object()

        # Show more fields for active clients
        if client.active:
            self.field_values_include = ["name", "url", "description", "email"]
        else:
            self.field_values_include = ["name", "url"]

        # Add status indicator
        self.field_values_extra = [
            ("Status", "Active" if client.active else "Inactive"),
            ("Projects", client.project_set.count()),
        ]

        return super().get_context_data(**kwargs)


# Example 7: Migration from old pattern
# ======================================

# OLD WAY (before refactoring):
class InvoiceDetailViewOld(BaseView, DetailView):
    """Old pattern - DON'T USE THIS."""

    model = Invoice
    form_class = InvoiceForm
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        import locale

        # Old: Call super first, then manually append
        context = super().get_context_data(**kwargs)

        # Old: Manual manipulation of context after creation
        context["field_values"].append(
            ("Total", locale.currency(self.object.amount, grouping=True))
        )
        context["field_values"].append(
            ("Cost", locale.currency(self.object.cost, grouping=True))
        )

        return context


# NEW WAY (after refactoring):
class InvoiceDetailViewNew(BaseView, DetailView):
    """New pattern - USE THIS."""

    model = Invoice
    form_class = InvoiceForm
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        import locale

        invoice = self.get_object()

        # New: Set field_values_extra BEFORE calling super
        self.field_values_extra = [
            (
                "Total",
                locale.currency(invoice.amount, grouping=True)
                if invoice.amount
                else "N/A",
            ),
            (
                "Cost",
                locale.currency(invoice.cost, grouping=True)
                if invoice.cost
                else "N/A",
            ),
        ]

        # New: Call super last
        return super().get_context_data(**kwargs)


# Example 8: Performance consideration
# =====================================
class ClientDetailViewOptimized(BaseView, DetailView):
    """
    Performance optimized - only compute extra fields once.
    
    Use case: Expensive calculations or database queries
    """

    model = Client
    form_class = ClientForm
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        client = self.get_object()

        # Expensive queries done once and cached
        total_invoices = client.project_set.aggregate(
            total=models.Sum("invoice__amount")
        )["total"]

        self.field_values_extra = [
            ("Total Revenue", f"${total_invoices:,.2f}" if total_invoices else "$0.00"),
            ("Projects", client.project_set.count()),
        ]

        return super().get_context_data(**kwargs)
