from django.urls import include, path

from .views import trigger_500
from .views.archive import archive


from .views.client import (
    ClientCopyView,
    ClientCreateView,
    ClientDeleteView,
    ClientDetailView,
    ClientListView,
    ClientUpdateView,
)
from .views.company import (
    CompanyCopyView,
    CompanyCreateView,
    CompanyDeleteView,
    CompanyDetailView,
    CompanyListView,
    CompanyUpdateView,
)
from .views.contact import (
    ContactCopyView,
    ContactCreateView,
    ContactDeleteView,
    ContactDetailView,
    ContactListView,
    ContactUpdateView,
)
from .views.dashboard import DashboardView
from .views.html import html_mode
from .views.invoice import (
    InvoiceCopyView,
    InvoiceCreateView,
    InvoiceDeleteView,
    InvoiceDetailView,
    InvoiceEmailDOCView,
    InvoiceEmailPDFView,
    InvoiceEmailTextView,
    InvoiceExportPDFView,
    InvoiceExportDOCView,
    InvoiceListView,
    InvoiceUpdateView,
)
from .views.lorem import FakeTextView
from .views.note import (
    NoteCopyView,
    NoteCreateView,
    NoteDeleteView,
    NoteDetailView,
    NoteEmailTextView,
    NoteListView,
    NoteListFullScreen,
    NoteUpdateView,
)
from .views.project import (
    ProjectCopyView,
    ProjectCreateView,
    ProjectDeleteView,
    ProjectDetailView,
    ProjectListView,
    ProjectUpdateView,
)
from .views.related import update_related_entries
from .views.report import (
    ReportCopyView,
    ReportCreateView,
    ReportDeleteView,
    ReportDetailView,
    ReportEmailTextView,
    ReportListView,
    ReportUpdateView,
)
from .views.search import SearchView
from .views.selected import update_selected_entries
from .views.task import (
    TaskCopyView,
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
)
from .views.time import (
    TimeCopyView,
    TimeCreateView,
    TimeDeleteView,
    TimeDetailView,
    TimeListView,
    TimeUpdateView,
)
from .views.user import (
    UserCopyView,
    UserCreateView,
    UserDeleteView,
    UserDetailView,
    UserListView,
    UserToContactView,
    UserUpdateView,
)

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
]

urlpatterns += [
    path("accounts/", include("allauth.socialaccount.providers.github.urls")),
]

urlpatterns += [
    path("search", SearchView.as_view(), name="search_index"),
]

urlpatterns += [
    path("company", CompanyListView.as_view(), name="company_index"),
    path("company", CompanyListView.as_view(), name="company_cancel"),
    path("company/create/", CompanyCreateView.as_view(), name="company_create"),
    path("company/<str:pk>/", CompanyDetailView.as_view(), name="company_view"),
    path("company/<str:pk>/update/", CompanyUpdateView.as_view(), name="company_edit"),
    path(
        "company/<str:pk>/delete/", CompanyDeleteView.as_view(), name="company_delete"
    ),
    path("company/<str:pk>/copy/", CompanyCopyView.as_view(), name="company_copy"),
]

urlpatterns += [
    path("time", TimeListView.as_view(), name="time_index"),
    path("time", TimeListView.as_view(), name="time_cancel"),
    path("time/create/", TimeCreateView.as_view(), name="time_create"),
    path("time/<str:pk>/", TimeDetailView.as_view(), name="time_view"),
    path("time/<str:pk>/update/", TimeUpdateView.as_view(), name="time_edit"),
    path("time/<str:pk>/delete/", TimeDeleteView.as_view(), name="time_delete"),
    path("time/<str:pk>/copy/", TimeCopyView.as_view(), name="time_copy"),
]

urlpatterns += [
    path("task", TaskListView.as_view(), name="task_index"),
    path("task", TaskListView.as_view(), name="task_cancel"),
    path("task/create/", TaskCreateView.as_view(), name="task_create"),
    path("task/<str:pk>/", TaskDetailView.as_view(), name="task_view"),
    path("task/<str:pk>/update/", TaskUpdateView.as_view(), name="task_edit"),
    path("task/<str:pk>/delete/", TaskDeleteView.as_view(), name="task_delete"),
    path("task/<str:pk>/copy/", TaskCopyView.as_view(), name="task_copy"),
]

urlpatterns += [
    path("report", ReportListView.as_view(), name="report_index"),
    path("report", ReportListView.as_view(), name="report_cancel"),
    path("report/create/", ReportCreateView.as_view(), name="report_create"),
    path("report/<str:pk>/", ReportDetailView.as_view(), name="report_view"),
    path("report/<str:pk>/update/", ReportUpdateView.as_view(), name="report_edit"),
    path("report/<str:pk>/delete/", ReportDeleteView.as_view(), name="report_delete"),
    path("report/<str:pk>/copy/", ReportCopyView.as_view(), name="report_copy"),
    path(
        "report/mail-text/<str:object_id>/",
        ReportEmailTextView.as_view(),
        name="report_email_text",
    ),
]

urlpatterns += [
    path("project", ProjectListView.as_view(), name="project_index"),
    path("project", ProjectListView.as_view(), name="project_cancel"),
    path("project/create/", ProjectCreateView.as_view(), name="project_create"),
    path("project/<str:pk>/", ProjectDetailView.as_view(), name="project_view"),
    path("project/<str:pk>/update/", ProjectUpdateView.as_view(), name="project_edit"),
    path(
        "project/<str:pk>/delete/", ProjectDeleteView.as_view(), name="project_delete"
    ),
    path("project/<str:pk>/copy/", ProjectCopyView.as_view(), name="project_copy"),
]

urlpatterns += [
    path("user", UserListView.as_view(), name="user_index"),
    path("user", UserListView.as_view(), name="user_cancel"),
    path("user/create/", UserCreateView.as_view(), name="user_create"),
    path("user/<str:pk>/", UserDetailView.as_view(), name="user_view"),
    path("user/<str:pk>/update/", UserUpdateView.as_view(), name="user_edit"),
    path("user/<str:pk>/delete/", UserDeleteView.as_view(), name="user_delete"),
    path("user/<str:pk>/copy/", UserCopyView.as_view(), name="user_copy"),
]

urlpatterns += [
    path("contact", ContactListView.as_view(), name="contact_index"),
    path("contact", ContactListView.as_view(), name="contact_cancel"),
    path("contact/create/", ContactCreateView.as_view(), name="contact_create"),
    path("contact/<str:pk>/", ContactDetailView.as_view(), name="contact_view"),
    path("contact/<str:pk>/update/", ContactUpdateView.as_view(), name="contact_edit"),
    path(
        "contact/<str:pk>/delete/", ContactDeleteView.as_view(), name="contact_delete"
    ),
    path("contact/<str:pk>/copy/", ContactCopyView.as_view(), name="contact_copy"),
]

urlpatterns += [
    path("note", NoteListView.as_view(), name="note_index"),
    path("note", NoteListView.as_view(), name="note_cancel"),
    path("note/fullscreen", NoteListFullScreen.as_view(), name="note-fullscreen"),
    path("note/create/", NoteCreateView.as_view(), name="note_create"),
    path("note/<str:pk>/", NoteDetailView.as_view(), name="note_view"),
    path("note/<str:pk>/update/", NoteUpdateView.as_view(), name="note_edit"),
    path("note/<str:pk>/delete/", NoteDeleteView.as_view(), name="note_delete"),
    path("note/<str:pk>/copy/", NoteCopyView.as_view(), name="note_copy"),
    path(
        "note/mail-text/<str:object_id>/",
        NoteEmailTextView.as_view(),
        name="note_email_text",
    ),
]

urlpatterns += [
    path("client", ClientListView.as_view(), name="client_index"),
    path("client", ClientListView.as_view(), name="client_cancel"),
    path("client/create/", ClientCreateView.as_view(), name="client_create"),
    path("client/<str:pk>/", ClientDetailView.as_view(), name="client_view"),
    path("client/<str:pk>/update/", ClientUpdateView.as_view(), name="client_edit"),
    path("client/<str:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),
    path("client/<str:pk>/copy/", ClientCopyView.as_view(), name="client_copy"),
]

urlpatterns += [
    path("invoice/", InvoiceListView.as_view(), name="invoice_index"),
    path("invoice/", InvoiceListView.as_view(), name="invoice_cancel"),
    path("invoice/create/", InvoiceCreateView.as_view(), name="invoice_create"),
    path("invoice/<str:pk>/", InvoiceDetailView.as_view(), name="invoice_view"),
    path("invoice/<str:pk>/update/", InvoiceUpdateView.as_view(), name="invoice_edit"),
    path(
        "invoice/<str:pk>/delete/", InvoiceDeleteView.as_view(), name="invoice_delete"
    ),
    path("invoice/<str:pk>/copy/", InvoiceCopyView.as_view(), name="invoice_copy"),
    path(
        "invoice/export-doc/<str:object_id>/",
        InvoiceExportDOCView.as_view(),
        name="invoice_export_doc",
    ),
    path(
        "invoice/export-pdf/<str:object_id>/",
        InvoiceExportPDFView.as_view(),
        name="invoice_export_pdf",
    ),
    path(
        "invoice/mail-doc/<str:object_id>/",
        InvoiceEmailDOCView.as_view(),
        name="invoice_email_doc",
    ),
    path(
        "invoice/mail-pdf/<str:object_id>/",
        InvoiceEmailPDFView.as_view(),
        name="invoice_email_pdf",
    ),
    path(
        "invoice/mail-text/<str:object_id>/",
        InvoiceEmailTextView.as_view(),
        name="invoice_email_text",
    ),
]

urlpatterns += [
    path("update-selected/", update_selected_entries, name="update-selected"),
]

urlpatterns += [
    path("update-related/", update_related_entries, name="update-related"),
]

urlpatterns += [
    path("fake-text/", FakeTextView.as_view(), name="fake_text"),
]

urlpatterns += [
    path("search/", SearchView.as_view(), name="search"),
]

urlpatterns += [
    path("convert/<str:user_id>/", UserToContactView.as_view(), name="user_to_contact"),
]

urlpatterns += [path("archive/", archive, name="archive")]
# urlpatterns += [path("chess-board/", ChessBoardView.as_view(), name="chess-board")]
urlpatterns += [path("html-mode/", html_mode, name="html-mode")]
urlpatterns += [path("trigger_500/", trigger_500, name="trigger_500")]

handler403 = "db.views.custom_403"
handler404 = "db.views.custom_404"
handler500 = "db.views.custom_500"
