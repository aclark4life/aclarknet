"""Views package for the db app.

This package organizes views into logical modules for better maintainability.
"""

# Base classes and error handlers
from .base import (
    AuthenticatedRequiredMixin,
    BaseView,
    FilterByUserMixin,
    ModelCopyMixin,
    RedirectToObjectViewMixin,
    SuperuserRequiredMixin,
    custom_403,
    custom_404,
    custom_500,
    trigger_500,
)

# Client views
from .client import (
    ClientCopyView,
    ClientCreateView,
    ClientDeleteView,
    ClientDetailView,
    ClientListView,
    ClientUpdateView,
)

# Company views
from .company import (
    CompanyCopyView,
    CompanyCreateView,
    CompanyDeleteView,
    CompanyDetailView,
    CompanyListView,
    CompanyUpdateView,
)

# Contact views
from .contact import (
    ContactCopyView,
    ContactCreateView,
    ContactDeleteView,
    ContactDetailView,
    ContactListView,
    ContactUpdateView,
)

# Dashboard and utility views
from .dashboard import (
    DashboardView,
    display_mode,
    lounge,
)

# Invoice views
from .invoice import (
    InvoiceCopyView,
    InvoiceCreateView,
    InvoiceDeleteView,
    InvoiceDetailView,
    InvoiceExportPDFView,
    InvoiceListView,
    InvoiceUpdateView,
)

# Note views
from .note import (
    NoteAddToObjectView,
    NoteCopyView,
    NoteCreateView,
    NoteDeleteView,
    NoteDetailView,
    NoteListFullScreen,
    NoteListView,
    NoteUpdateView,
)

# Project views
from .project import (
    ProjectCopyView,
    ProjectCreateView,
    ProjectDeleteView,
    ProjectDetailView,
    ProjectListView,
    ProjectUpdateView,
)

# Search views
from .search import SearchView

# Task views
from .task import (
    TaskCopyView,
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
)

# Time views
from .time import (
    TimeCopyView,
    TimeCreateView,
    TimeDeleteView,
    TimeDetailView,
    TimeListView,
    TimeUpdateView,
)

# Utility functions
from .utils import (
    update_related_entries,
    update_selected_entries,
)

__all__ = [
    # Base classes
    "AuthenticatedRequiredMixin",
    "BaseView",
    "FilterByUserMixin",
    "ModelCopyMixin",
    "RedirectToObjectViewMixin",
    "SuperuserRequiredMixin",
    "custom_403",
    "custom_404",
    "custom_500",
    "trigger_500",
    # Client views
    "ClientCopyView",
    "ClientCreateView",
    "ClientDeleteView",
    "ClientDetailView",
    "ClientListView",
    "ClientUpdateView",
    # Company views
    "CompanyCopyView",
    "CompanyCreateView",
    "CompanyDeleteView",
    "CompanyDetailView",
    "CompanyListView",
    "CompanyUpdateView",
    # Contact views
    "ContactCopyView",
    "ContactCreateView",
    "ContactDeleteView",
    "ContactDetailView",
    "ContactListView",
    "ContactUpdateView",
    # Dashboard views
    "DashboardView",
    "display_mode",
    "html_mode",
    "lounge",
    "save_positions",
    # Invoice views
    "InvoiceCopyView",
    "InvoiceCreateView",
    "InvoiceDeleteView",
    "InvoiceDetailView",
    "InvoiceExportPDFView",
    "InvoiceListView",
    "InvoiceUpdateView",
    # Note views
    "NoteAddToObjectView",
    "NoteCopyView",
    "NoteCreateView",
    "NoteDeleteView",
    "NoteDetailView",
    "NoteListFullScreen",
    "NoteListView",
    "NoteUpdateView",
    # Project views
    "ProjectCopyView",
    "ProjectCreateView",
    "ProjectDeleteView",
    "ProjectDetailView",
    "ProjectListView",
    "ProjectUpdateView",
    # Report views
    "ReportCopyView",
    "ReportCreateView",
    "ReportDeleteView",
    "ReportDetailView",
    "ReportListView",
    "ReportUpdateView",
    # Search views
    "SearchView",
    # Task views
    "TaskCopyView",
    "TaskCreateView",
    "TaskDeleteView",
    "TaskDetailView",
    "TaskListView",
    "TaskUpdateView",
    # Time views
    "TimeCopyView",
    "TimeCreateView",
    "TimeDeleteView",
    "TimeDetailView",
    "TimeListView",
    "TimeUpdateView",
    # User views
    "UserCopyView",
    "UserCreateView",
    "UserDeleteView",
    "UserDetailView",
    "UserListView",
    "UserUpdateView",
    # Utility functions
    "update_related_entries",
    "update_selected_entries",
]
