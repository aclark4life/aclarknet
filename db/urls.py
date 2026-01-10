from bson import ObjectId
from django.urls import include, path, register_converter

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
    DashboardView,
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
    SearchView,
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
    archive,
    trigger_500,
    update_related_entries,
    update_selected_entries,
)


# Via timgraham
class ObjectIdConverter:
    regex = "[a-fA-F0-9]{24}"

    def to_python(self, value):
        return ObjectId(value)

    def to_url(self, value):
        return str(value)


register_converter(ObjectIdConverter, "object_id")

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
    path("company/<object_id:pk>/", CompanyDetailView.as_view(), name="company_view"),
    path(
        "company/<object_id:pk>/update/",
        CompanyUpdateView.as_view(),
        name="company_edit",
    ),
    path(
        "company/<object_id:pk>/delete/",
        CompanyDeleteView.as_view(),
        name="company_delete",
    ),
    path(
        "company/<object_id:pk>/copy/", CompanyCopyView.as_view(), name="company_copy"
    ),
]

urlpatterns += [
    path("time", TimeListView.as_view(), name="time_index"),
    path("time", TimeListView.as_view(), name="time_cancel"),
    path("time/create/", TimeCreateView.as_view(), name="time_create"),
    path("time/<object_id:pk>/", TimeDetailView.as_view(), name="time_view"),
    path("time/<object_id:pk>/update/", TimeUpdateView.as_view(), name="time_edit"),
    path("time/<object_id:pk>/delete/", TimeDeleteView.as_view(), name="time_delete"),
    path("time/<object_id:pk>/copy/", TimeCopyView.as_view(), name="time_copy"),
]

urlpatterns += [
    path("task", TaskListView.as_view(), name="task_index"),
    path("task", TaskListView.as_view(), name="task_cancel"),
    path("task/create/", TaskCreateView.as_view(), name="task_create"),
    path("task/<object_id:pk>/", TaskDetailView.as_view(), name="task_view"),
    path("task/<object_id:pk>/update/", TaskUpdateView.as_view(), name="task_edit"),
    path("task/<object_id:pk>/delete/", TaskDeleteView.as_view(), name="task_delete"),
    path("task/<object_id:pk>/copy/", TaskCopyView.as_view(), name="task_copy"),
]

urlpatterns += [
    path("report", ReportListView.as_view(), name="report_index"),
    path("report", ReportListView.as_view(), name="report_cancel"),
    path("report/create/", ReportCreateView.as_view(), name="report_create"),
    path("report/<object_id:pk>/", ReportDetailView.as_view(), name="report_view"),
    path(
        "report/<object_id:pk>/update/", ReportUpdateView.as_view(), name="report_edit"
    ),
    path(
        "report/<object_id:pk>/delete/",
        ReportDeleteView.as_view(),
        name="report_delete",
    ),
    path("report/<object_id:pk>/copy/", ReportCopyView.as_view(), name="report_copy"),
    path(
        "report/mail-text/<object_id:object_id>/",
        ReportEmailTextView.as_view(),
        name="report_email_text",
    ),
]

urlpatterns += [
    path("project", ProjectListView.as_view(), name="project_index"),
    path("project", ProjectListView.as_view(), name="project_cancel"),
    path("project/create/", ProjectCreateView.as_view(), name="project_create"),
    path("project/<object_id:pk>/", ProjectDetailView.as_view(), name="project_view"),
    path(
        "project/<object_id:pk>/update/",
        ProjectUpdateView.as_view(),
        name="project_edit",
    ),
    path(
        "project/<object_id:pk>/delete/",
        ProjectDeleteView.as_view(),
        name="project_delete",
    ),
    path(
        "project/<object_id:pk>/copy/", ProjectCopyView.as_view(), name="project_copy"
    ),
]

urlpatterns += [
    path("user", UserListView.as_view(), name="user_index"),
    path("user", UserListView.as_view(), name="user_cancel"),
    path("user/create/", UserCreateView.as_view(), name="user_create"),
    path("user/<object_id:pk>/", UserDetailView.as_view(), name="user_view"),
    path("user/<object_id:pk>/update/", UserUpdateView.as_view(), name="user_edit"),
    path("user/<object_id:pk>/delete/", UserDeleteView.as_view(), name="user_delete"),
    path("user/<object_id:pk>/copy/", UserCopyView.as_view(), name="user_copy"),
]

urlpatterns += [
    path("contact", ContactListView.as_view(), name="contact_index"),
    path("contact", ContactListView.as_view(), name="contact_cancel"),
    path("contact/create/", ContactCreateView.as_view(), name="contact_create"),
    path("contact/<object_id:pk>/", ContactDetailView.as_view(), name="contact_view"),
    path(
        "contact/<object_id:pk>/update/",
        ContactUpdateView.as_view(),
        name="contact_edit",
    ),
    path(
        "contact/<object_id:pk>/delete/",
        ContactDeleteView.as_view(),
        name="contact_delete",
    ),
    path(
        "contact/<object_id:pk>/copy/", ContactCopyView.as_view(), name="contact_copy"
    ),
]

urlpatterns += [
    path("note", NoteListView.as_view(), name="note_index"),
    path("note", NoteListView.as_view(), name="note_cancel"),
    path("note/fullscreen", NoteListFullScreen.as_view(), name="note-fullscreen"),
    path("note/create/", NoteCreateView.as_view(), name="note_create"),
    path("note/<object_id:pk>/", NoteDetailView.as_view(), name="note_view"),
    path("note/<object_id:pk>/update/", NoteUpdateView.as_view(), name="note_edit"),
    path("note/<object_id:pk>/delete/", NoteDeleteView.as_view(), name="note_delete"),
    path("note/<object_id:pk>/copy/", NoteCopyView.as_view(), name="note_copy"),
    path(
        "note/mail-text/<object_id:object_id>/",
        NoteEmailTextView.as_view(),
        name="note_email_text",
    ),
]

urlpatterns += [
    path("client", ClientListView.as_view(), name="client_index"),
    path("client", ClientListView.as_view(), name="client_cancel"),
    path("client/create/", ClientCreateView.as_view(), name="client_create"),
    path("client/<object_id:pk>/", ClientDetailView.as_view(), name="client_view"),
    path(
        "client/<object_id:pk>/update/", ClientUpdateView.as_view(), name="client_edit"
    ),
    path(
        "client/<object_id:pk>/delete/",
        ClientDeleteView.as_view(),
        name="client_delete",
    ),
    path("client/<object_id:pk>/copy/", ClientCopyView.as_view(), name="client_copy"),
]

urlpatterns += [
    path("invoice/", InvoiceListView.as_view(), name="invoice_index"),
    path("invoice/", InvoiceListView.as_view(), name="invoice_cancel"),
    path("invoice/create/", InvoiceCreateView.as_view(), name="invoice_create"),
    path("invoice/<object_id:pk>/", InvoiceDetailView.as_view(), name="invoice_view"),
    path(
        "invoice/<object_id:pk>/update/",
        InvoiceUpdateView.as_view(),
        name="invoice_edit",
    ),
    path(
        "invoice/<object_id:pk>/delete/",
        InvoiceDeleteView.as_view(),
        name="invoice_delete",
    ),
    path(
        "invoice/<object_id:pk>/copy/", InvoiceCopyView.as_view(), name="invoice_copy"
    ),
    path(
        "invoice/export-pdf/<object_id:object_id>",
        InvoiceExportPDFView.as_view(),
        name="invoice_export_pdf",
    ),
    path(
        "invoice/mail-pdf/<object_id:object_id>/",
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
