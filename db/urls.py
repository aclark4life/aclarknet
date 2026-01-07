from django.urls import include, path

from .views import trigger_500
from .views import archive
from .views import DashboardView
from .views import update_related_entries
from .views import SearchView
from .views import update_selected_entries


from .views import (
    ClientCopyView,
    ClientCreateView,
    ClientDeleteView,
    ClientDetailView,
    ClientListView,
    ClientUpdateView,
    CompanyCopyView,
    CompanyCreateView,
    CompanyDeleteView,
    CompanyDetailView,
    CompanyListView,
    CompanyUpdateView,
    ContactCopyView,
    ContactCreateView,
    ContactDeleteView,
    ContactDetailView,
    ContactListView,
    ContactUpdateView,
    InvoiceCopyView,
    InvoiceCreateView,
    InvoiceDeleteView,
    InvoiceDetailView,
    InvoiceEmailPDFView,
    InvoiceExportPDFView,
    InvoiceListView,
    InvoiceUpdateView,
    NoteCopyView,
    NoteCreateView,
    NoteDeleteView,
    NoteDetailView,
    NoteEmailTextView,
    NoteListView,
    NoteListFullScreen,
    NoteUpdateView,
    ProjectCopyView,
    ProjectCreateView,
    ProjectDeleteView,
    ProjectDetailView,
    ProjectListView,
    ProjectUpdateView,
    ReportCopyView,
    ReportCreateView,
    ReportDeleteView,
    ReportDetailView,
    ReportEmailTextView,
    ReportListView,
    ReportUpdateView,
    TaskCopyView,
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
    TimeCopyView,
    TimeCreateView,
    TimeDeleteView,
    TimeDetailView,
    TimeListView,
    TimeUpdateView,
    UserCopyView,
    UserCreateView,
    UserDeleteView,
    UserDetailView,
    UserListView,
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
    path("company/<path:pk>/", CompanyDetailView.as_view(), name="company_view"),
    path("company/<path:pk>/update/", CompanyUpdateView.as_view(), name="company_edit"),
    path(
        "company/<path:pk>/delete/", CompanyDeleteView.as_view(), name="company_delete"
    ),
    path("company/<path:pk>/copy/", CompanyCopyView.as_view(), name="company_copy"),
]

urlpatterns += [
    path("time", TimeListView.as_view(), name="time_index"),
    path("time", TimeListView.as_view(), name="time_cancel"),
    path("time/create/", TimeCreateView.as_view(), name="time_create"),
    path("time/<path:pk>/", TimeDetailView.as_view(), name="time_view"),
    path("time/<path:pk>/update/", TimeUpdateView.as_view(), name="time_edit"),
    path("time/<path:pk>/delete/", TimeDeleteView.as_view(), name="time_delete"),
    path("time/<path:pk>/copy/", TimeCopyView.as_view(), name="time_copy"),
]

urlpatterns += [
    path("task", TaskListView.as_view(), name="task_index"),
    path("task", TaskListView.as_view(), name="task_cancel"),
    path("task/create/", TaskCreateView.as_view(), name="task_create"),
    path("task/<path:pk>/", TaskDetailView.as_view(), name="task_view"),
    path("task/<path:pk>/update/", TaskUpdateView.as_view(), name="task_edit"),
    path("task/<path:pk>/delete/", TaskDeleteView.as_view(), name="task_delete"),
    path("task/<path:pk>/copy/", TaskCopyView.as_view(), name="task_copy"),
]

urlpatterns += [
    path("report", ReportListView.as_view(), name="report_index"),
    path("report", ReportListView.as_view(), name="report_cancel"),
    path("report/create/", ReportCreateView.as_view(), name="report_create"),
    path("report/<path:pk>/", ReportDetailView.as_view(), name="report_view"),
    path("report/<path:pk>/update/", ReportUpdateView.as_view(), name="report_edit"),
    path("report/<path:pk>/delete/", ReportDeleteView.as_view(), name="report_delete"),
    path("report/<path:pk>/copy/", ReportCopyView.as_view(), name="report_copy"),
    path(
        "report/mail-text/<path:object_id>/",
        ReportEmailTextView.as_view(),
        name="report_email_text",
    ),
]

urlpatterns += [
    path("project", ProjectListView.as_view(), name="project_index"),
    path("project", ProjectListView.as_view(), name="project_cancel"),
    path("project/create/", ProjectCreateView.as_view(), name="project_create"),
    path("project/<path:pk>/", ProjectDetailView.as_view(), name="project_view"),
    path("project/<path:pk>/update/", ProjectUpdateView.as_view(), name="project_edit"),
    path(
        "project/<path:pk>/delete/", ProjectDeleteView.as_view(), name="project_delete"
    ),
    path("project/<path:pk>/copy/", ProjectCopyView.as_view(), name="project_copy"),
]

urlpatterns += [
    path("user", UserListView.as_view(), name="user_index"),
    path("user", UserListView.as_view(), name="user_cancel"),
    path("user/create/", UserCreateView.as_view(), name="user_create"),
    path("user/<path:pk>/", UserDetailView.as_view(), name="user_view"),
    path("user/<path:pk>/update/", UserUpdateView.as_view(), name="user_edit"),
    path("user/<path:pk>/delete/", UserDeleteView.as_view(), name="user_delete"),
    path("user/<path:pk>/copy/", UserCopyView.as_view(), name="user_copy"),
]

urlpatterns += [
    path("contact", ContactListView.as_view(), name="contact_index"),
    path("contact", ContactListView.as_view(), name="contact_cancel"),
    path("contact/create/", ContactCreateView.as_view(), name="contact_create"),
    path("contact/<path:pk>/", ContactDetailView.as_view(), name="contact_view"),
    path("contact/<path:pk>/update/", ContactUpdateView.as_view(), name="contact_edit"),
    path(
        "contact/<path:pk>/delete/", ContactDeleteView.as_view(), name="contact_delete"
    ),
    path("contact/<path:pk>/copy/", ContactCopyView.as_view(), name="contact_copy"),
]

urlpatterns += [
    path("note", NoteListView.as_view(), name="note_index"),
    path("note", NoteListView.as_view(), name="note_cancel"),
    path("note/fullscreen", NoteListFullScreen.as_view(), name="note-fullscreen"),
    path("note/create/", NoteCreateView.as_view(), name="note_create"),
    path("note/<path:pk>/", NoteDetailView.as_view(), name="note_view"),
    path("note/<path:pk>/update/", NoteUpdateView.as_view(), name="note_edit"),
    path("note/<path:pk>/delete/", NoteDeleteView.as_view(), name="note_delete"),
    path("note/<path:pk>/copy/", NoteCopyView.as_view(), name="note_copy"),
    path(
        "note/mail-text/<path:object_id>/",
        NoteEmailTextView.as_view(),
        name="note_email_text",
    ),
]

urlpatterns += [
    path("client", ClientListView.as_view(), name="client_index"),
    path("client", ClientListView.as_view(), name="client_cancel"),
    path("client/create/", ClientCreateView.as_view(), name="client_create"),
    path("client/<path:pk>/", ClientDetailView.as_view(), name="client_view"),
    path("client/<path:pk>/update/", ClientUpdateView.as_view(), name="client_edit"),
    path("client/<path:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),
    path("client/<path:pk>/copy/", ClientCopyView.as_view(), name="client_copy"),
]

urlpatterns += [
    path("invoice/", InvoiceListView.as_view(), name="invoice_index"),
    path("invoice/", InvoiceListView.as_view(), name="invoice_cancel"),
    path("invoice/create/", InvoiceCreateView.as_view(), name="invoice_create"),
    path("invoice/<path:pk>/", InvoiceDetailView.as_view(), name="invoice_view"),
    path("invoice/<path:pk>/update/", InvoiceUpdateView.as_view(), name="invoice_edit"),
    path(
        "invoice/<path:pk>/delete/", InvoiceDeleteView.as_view(), name="invoice_delete"
    ),
    path("invoice/<path:pk>/copy/", InvoiceCopyView.as_view(), name="invoice_copy"),
    path(
        "invoice/export-pdf/<path:object_id>",
        InvoiceExportPDFView.as_view(),
        name="invoice_export_pdf",
    ),
    path(
        "invoice/mail-pdf/<path:object_id>/",
        InvoiceEmailPDFView.as_view(),
        name="invoice_email_pdf",
    ),
]

urlpatterns += [
    path("update-selected/", update_selected_entries, name="update-selected"),
]

urlpatterns += [
    path("update-related/", update_related_entries, name="update-related"),
]

urlpatterns += [
    path("search/", SearchView.as_view(), name="search"),
]

urlpatterns += [path("archive/", archive, name="archive")]
urlpatterns += [path("trigger_500/", trigger_500, name="trigger_500")]

handler403 = "db.views.custom_403"
handler404 = "db.views.custom_404"
handler500 = "db.views.custom_500"
