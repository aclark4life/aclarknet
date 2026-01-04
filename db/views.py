"""Views for the db app."""

from django.apps import apps
from django.db import transaction

# Import your models explicitly or use apps.get_model safely
from django.contrib.auth.models import User

# Standard library imports
import ast
import decimal
import io
import locale
import random
from itertools import chain

# Third-party imports
import chess
from docx import Document
from html2docx import html2docx
from rest_framework import viewsets
from texttable import Texttable
from xhtml2pdf import pisa

# Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import F, Q, Sum
from django.http import FileResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.defaults import permission_denied
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

# Local imports
from .forms import (
    AdminReportForm,
    AdminTimeForm,
    ClientForm,
    CompanyForm,
    ContactForm,
    InvoiceForm,
    NoteForm,
    ProjectForm,
    ReportForm,
    TaskForm,
    TimeForm,
    UserForm,
)
from .models import Client, Company, Contact, Invoice, Note, Project, Report, Task, Time
from .serializers import ClientSerializer
from .utils import get_archived_annotation, get_model_class, get_queryset


class BaseView:
    """Base view class with common functionality for all model views."""

    OBJECT_URLS = {"copy", "edit", "delete", "view"}

    _queryset_related = None

    @property
    def queryset_related(self):
        if self.model is None:
            return None
        return self._queryset_related

    # ---- View behavior ----
    paginated = False
    page_number = 1
    has_related = False
    has_preview = False
    dashboard = False

    # ---- Model-dependent helpers ----
    def _if_model(self, value):
        return value if self.model is not None else None

    @property
    def order_by(self):
        return self._if_model(["archived", "-created"])

    @property
    def exclude(self):
        return self._if_model(["contacts"])

    @property
    def search(self):
        return bool(self.model)

    def _model_url(self, action: str):
        if self.model is None:
            return None

        name = f"{self.model._meta.model_name}_{action}"

        if action in self.OBJECT_URLS:
            obj = getattr(self, "object", None)
            if obj is None:
                return None
            return reverse(name, args=[obj.pk])

        return reverse(name)

    @property
    def url_cancel(self):
        return self._model_url("cancel")

    @property
    def url_copy(self):
        return self._model_url("copy")

    @property
    def url_create(self):
        return self._model_url("create")

    @property
    def url_delete(self):
        return self._model_url("delete")

    @property
    def url_edit(self):
        return self._model_url("edit")

    @property
    def url_index(self):
        return self._model_url("index")

    @property
    def url_view(self):
        return self._model_url("view")

    def _model_meta(self):
        return self.model._meta if self.model is not None else None

    @property
    def model_name(self):
        meta = self._model_meta()
        return meta.model_name if meta else None

    @property
    def model_name_plural(self):
        meta = self._model_meta()
        return meta.verbose_name_plural if meta else None

    def get_archived(self, obj):
        """Get archived status of an object, falling back to is_active."""
        return getattr(obj, "archived", not getattr(obj, "is_active", True))

    def _get_int_param(self, key, default):
        """Helper to safely parse integer GET parameters."""
        try:
            return int(self.request.GET.get(key, default))
        except (ValueError, TypeError):
            return default

    def get_context_data(self, **kwargs):
        """Get context data for template rendering."""
        context = super().get_context_data(**kwargs)

        # 1. Model Metadata
        if self.model_name:
            context["model_name"] = self.model_name
            context[f"{self.model_name}_nav"] = True
            context["model_name_plural"] = (
                self.model_name_plural or f"{self.model_name}s"
            )

        # 2. Parameters from Request
        self.per_page = self._get_int_param("items_per_page", 10)
        self.page_number = self._get_int_param("page", 1)

        paginated_str = self.request.GET.get("paginated", "true").lower()
        self.paginated = paginated_str != "false"

        context.update(
            {
                "items_per_page": self.per_page,
                "page_number": self.page_number,
                "paginated": self.paginated,
                "urls": self.get_urls(),
                "statcard": self.get_statcards(),
                "statcards": {},  # Kept for backward compatibility
            }
        )

        # 3. Queryset Handling
        queryset = self.get_queryset()
        related = False

        if self.has_related and self.queryset_related is not None:
            context["has_related"] = True
            queryset = self.queryset_related
            related = True

        # Only call order_by if it's a QuerySet, not a list
        if hasattr(queryset, "order_by") and not self.search:
            queryset = queryset.order_by(*self.order_by)

        if self.has_preview:
            context["has_preview"] = True

        # 4. Pagination
        paginator = Paginator(queryset, self.per_page)
        if self.paginated:
            page_obj = paginator.get_page(self.page_number)
        else:
            page_obj = queryset
        context["page_obj"] = page_obj

        # 5. Field Extraction Logic
        field_values_page = []

        # Handle search-specific display
        if self.search:
            context["search"] = self.search
            field_values_page = self.get_field_values(page_obj, search=True)
            context["search_results"] = len(field_values_page) > 0
            context["field_values_page"] = field_values_page

        # Handle standard list display
        elif hasattr(self, "form_class"):
            field_values_page = self.get_field_values(page_obj, related=related)
            context["field_values_page"] = field_values_page

        # Extract table headers from the first row of results
        if field_values_page and len(field_values_page) > 0:
            context["table_headers"] = [i[0] for i in field_values_page[0]]

        # Detail view specific context
        if hasattr(self, "object"):
            if hasattr(self, "form_class"):
                context["field_values"] = self.get_field_values()
            if self.model:
                context["page_obj_detail_view"] = self.get_page_obj_detail_view()

        return context

    def get_field_values(self, page_obj=None, search=False, related=False):
        """Get field values for display in templates."""
        if page_obj is not None:
            results = []
            attrs_to_check = ["amount", "cost", "net", "hours"]

            for item in page_obj:
                if item is None:
                    continue

                field_values = [
                    ("type", item._meta.model_name),
                    ("id", item.id),
                ]

                # If it's a single object (not a paginator object list)
                if not hasattr(page_obj, "object_list"):
                    field_values.append(("archived", self.get_archived(item)))
                    field_values.append(("item", item))

                # Dynamically add specific attributes if they exist
                for attr in attrs_to_check:
                    if hasattr(item, attr):
                        field_values.append((attr, getattr(item, attr)))

                results.append(field_values)
            return results

        # Logic for Detail View field extraction
        try:
            object_fields = self.form_class().fields.keys()
            return [
                (f, getattr(self.object, f))
                for f in object_fields
                if f not in self.exclude and self.request.user.is_superuser
            ]
        except (AttributeError, TypeError):
            return []

    def get_page_obj_detail_view(self):
        """Get pagination context for detail view navigation."""
        user = self.request.user
        if user.is_authenticated and not user.is_superuser:
            objects = self.model.objects.filter(user=user)
        else:
            objects = self.model.objects.all()

        count = objects.count()
        page_number = self._get_int_param("page_number_detail", 1)

        # Use slicing for better performance on large querysets
        try:
            current_obj = objects[page_number - 1]
            next_obj = objects[page_number] if page_number < count else None
            prev_obj = objects[page_number - 2] if page_number > 1 else None
        except (IndexError, AssertionError):
            current_obj = next_obj = prev_obj = None

        return {
            "page_obj": current_obj,
            "next_object": next_obj,
            "previous_object": prev_obj,
            "first_object": objects.first(),
            "last_object": objects.last(),
            "count": count,
        }

    def get_statcards(self):
        """Get statistics cards data (stub)."""
        return {
            "times": {"entered": 0, "approved": 0},
            "invoices": {"gross": 0, "cost": 0, "net": 0},
        }

    def get_url_names(self):
        """Get URL pattern names (not reversed URLs) for use with {% url %} tag.

        Returns an empty dict if model is None (e.g., for non-model-based views).
        """
        if self.model is None:
            return {}

        return {
            "url_cancel": f"{self.model_name}_cancel",
            "url_copy": f"{self.model_name}_copy",
            "url_create": f"{self.model_name}_create",
            "url_delete": f"{self.model_name}_delete",
            "url_edit": f"{self.model_name}_edit",
            "url_index": f"{self.model_name}_index",
            "url_view": f"{self.model_name}_view",
        }

    def get_urls(self):
        """Get URL names for various actions."""
        return self.get_url_names()


class SuperuserRequiredMixin(UserPassesTestMixin):
    """Mixin to require superuser access."""

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


class AuthenticatedRequiredMixin(SuperuserRequiredMixin):
    """
    Allow superusers or authenticated users.
    """

    def test_func(self):
        return self.request.user.is_authenticated


class RedirectToObjectViewMixin:
    """
    Redirect to object detail view after create/update/copy.
    """

    def get_success_url(self):
        return reverse_lazy(
            f"{self.model._meta.model_name}_view",
            args=[self.object.pk],
        )


class FilterByUserMixin:
    """
    Non-superusers only see their own objects.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)
        return queryset


class ModelCopyMixin:
    """
    Generic copy behavior for models.
    """

    def get_initial(self):
        original = self.model.objects.get(pk=self.kwargs["pk"])
        initial = {}
        for field in original._meta.fields:
            if field.name not in self.exclude:
                initial[field.name] = getattr(original, field.name)
        return initial

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.pk = None
        obj.save()
        return super().form_valid(form)


def custom_403(request, exception=None):
    """Handle 403 Forbidden errors."""
    return permission_denied(request, exception=exception, template_name="403.html")


def custom_404(request, exception=None):
    """Handle 404 Not Found errors."""
    return render(request, template_name="404.html")


def custom_500(request, exception=None):
    """Handle 500 Internal Server errors."""
    return render(request, template_name="500.html")


def trigger_500(request):
    """Deliberately trigger a 500 error for testing."""
    raise Exception("This is a deliberate 500 error.")


def archive(request):
    """
    Archive or unarchive an object.

    Handles archiving for both db models and users.
    For invoices, also archives associated time entries.
    """
    archive = request.GET.get("archive", "true")
    model = request.GET.get("model")
    obj_id = request.GET.get("id")
    obj = None
    if model == "user":
        ModelClass = get_model_class("User", app_label="siteuser")
        archive_field = "is_active"
    else:
        ModelClass = get_model_class(model)
        archive_field = "archived"
    field_value = False if archive == "false" else True
    obj = get_object_or_404(ModelClass, id=obj_id)
    if model == "user":
        field_value = not (field_value)
    setattr(obj, archive_field, field_value)
    if model == "invoice":
        for time_entry in obj.times.all():
            setattr(time_entry, archive_field, field_value)
            time_entry.save()

    obj.save()
    return HttpResponseRedirect(request.headers.get("Referer"))


# Archived annotation for filtering archived users
archived_annotation = get_archived_annotation()


def redirect_admin_to_about_book(request):
    return redirect("/about/#book")


def blog(request):
    """Redirect to external blog."""
    return HttpResponseRedirect("https://blog.aclark.net")


class ChessBoardView(TemplateView):
    template_name = "chess_board.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = chess.Board()
        html = chess.svg.board(board=board).replace("svg", "svg style='width:100%;'")
        context["chess_board"] = html
        context["chess_nav"] = True
        display_mode = (
            {"bg": "dark", "text": "light"}
            if self.request.user.profile.dark
            else {"bg": "light", "text": "dark"}
        )
        context["display_mode"] = display_mode
        return context


class ClientAPIViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.filter(publish=True).order_by("name")
    serializer_class = ClientSerializer


class BaseClientView(BaseView, SuperuserRequiredMixin):
    """Base view for Client model operations."""

    model = Client
    form_model = ClientForm
    form_class = ClientForm
    order_by = ["archived", "name"]
    exclude = [
        "publish",
        "link",
        "company",
        "tags",
        "address",
        "url",
        "description",
    ]


class ClientListView(BaseClientView, ListView):
    model = Client
    template_name = "index.html"


class ClientCreateView(BaseClientView, CreateView):
    template_name = "edit.html"

    def get_success_url(self):
        return reverse_lazy("client_view", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        companies = Company.objects.all()
        if companies:
            company = companies.first()
            context["form"].initial = {
                "company": company,
            }
        return context

    def form_valid(self, form):
        company_id = self.request.GET.get("company_id")
        obj = form.save()
        if company_id:
            company = Company.objects.get(pk=company_id)
            company.client_set.add(obj)
            return HttpResponseRedirect(reverse("company_view", args=[company_id]))
        return super().form_valid(form)


class ClientDetailView(BaseClientView, DetailView):
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        client = self.get_object()
        notes = client.notes.all()
        projects = client.project_set.all().order_by("archived")
        company = client.company
        contacts = client.contact_set.all()
        invoices = Invoice.objects.filter(project__in=projects)
        reports = client.report_set.all().order_by("-created")
        invoices = invoices.order_by("archived", "-created")
        tasks = Task.objects.filter(project__in=projects)
        queryset_related = [
            q
            for q in [notes, projects, contacts, invoices, tasks, reports]
            if q.exists()
        ]
        if company:
            queryset_related.insert(0, [company])
        queryset_related = list(chain(*queryset_related))
        queryset_related = sorted(queryset_related, key=self.get_archived)
        self._queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)
        return context


class ClientUpdateView(BaseClientView, UpdateView):
    template_name = "edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url_cancel"] = f"{self.model_name}_view"
        context["pk"] = self.kwargs["pk"]
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("client_view", args=[self.object.pk])


class ClientDeleteView(BaseClientView, DeleteView):
    template_name = "delete.html"
    success_url = reverse_lazy("client_index")

    def get_queryset(self):
        return Client.objects.all()


class ClientCopyView(BaseClientView, CreateView):
    template_name = "edit.html"

    def get_queryset(self):
        return Client.objects.all()

    def get_initial(self):
        original_client = Client.objects.get(pk=self.kwargs["pk"])
        return {
            "name": original_client.name,
        }

    def form_valid(self, form):
        new_client = form.save(commit=False)
        new_client.pk = None
        new_client.save()
        return super().form_valid(form)


class BaseCompanyView(BaseView, SuperuserRequiredMixin):
    """Base view for Company model operations."""

    model = Company
    form_model = CompanyForm
    form_class = CompanyForm
    order_by = ["archived", "name"]
    exclude = ["client_set", "description", "url"]


class CompanyListView(BaseCompanyView, ListView):
    template_name = "index.html"


class CompanyCreateView(
    BaseCompanyView,
    RedirectToObjectViewMixin,
    CreateView,
):
    template_name = "edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clients = list(Client.objects.all())
        random_clients = random.sample(clients, k=len(clients))  # Select random clients
        initial_values = [client.pk for client in random_clients]
        context["form"].initial = {
            "client_set": initial_values,
        }
        return context

    def form_valid(self, form):
        form.instance.creator = self.request.user
        company = form.save(commit=False)
        company.save()
        company.client_set.set(form.cleaned_data["client_set"])
        form.save_m2m()
        return super().form_valid(form)


class CompanyDetailView(BaseCompanyView, DetailView):
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        company = self.get_object()
        clients = company.client_set.all().order_by("archived", "name")
        projects = Project.objects.filter(client__in=clients).order_by(
            "archived", "name"
        )
        notes = company.notes.all()
        tasks = Task.objects.filter(project__in=projects).order_by("archived", "name")
        contacts = Contact.objects.filter(client__in=clients).order_by(
            "archived", "name"
        )
        queryset_related = [
            q for q in [clients, contacts, notes, projects, tasks] if q.exists()
        ]
        queryset_related = list(chain(*queryset_related))
        queryset_related = sorted(queryset_related, key=self.get_archived)
        self._queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)
        return context


class CompanyUpdateView(
    BaseCompanyView,
    RedirectToObjectViewMixin,
    UpdateView,
):
    template_name = "edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.client_set.set(form.cleaned_data["client_set"])
        return response

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])


class CompanyDeleteView(BaseCompanyView, DeleteView):
    template_name = "delete.html"
    success_url = reverse_lazy("company_index")

    def get_queryset(self):
        return Company.objects.all()


class CompanyCopyView(
    BaseCompanyView,
    RedirectToObjectViewMixin,
    CreateView,
):
    template_name = "edit.html"

    def get_initial(self):
        original_company = Company.objects.get(pk=self.kwargs["pk"])
        return {
            "name": original_company.name,
        }

    def form_valid(self, form):
        new_company = form.save(commit=False)
        new_company.pk = None
        new_company.save()
        return super().form_valid(form)


class BaseContactView(BaseView, SuperuserRequiredMixin):
    """Base view for Contact model operations."""

    model = Contact
    form_model = ContactForm
    form_class = ContactForm
    template_name = "edit.html"
    order_by = ["archived", "name"]
    exclude = ["first_name", "last_name", "url", "number"]


class ContactListView(BaseContactView, ListView):
    template_name = "index.html"


class ContactCreateView(
    BaseContactView,
    RedirectToObjectViewMixin,
    CreateView,
):
    pass


class ContactDetailView(BaseContactView, DetailView):
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        contact = self.get_object()
        notes = contact.notes.all()
        client = contact.client
        queryset_related = [q for q in [notes] if q.exists()]
        if client:
            queryset_related.insert(0, client)
        self._queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)
        return context


class ContactUpdateView(
    BaseContactView,
    RedirectToObjectViewMixin,
    UpdateView,
):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])


class ContactDeleteView(BaseContactView, DeleteView):
    template_name = "delete.html"
    success_url = reverse_lazy("contact_index")

    def get_queryset(self):
        return Contact.objects.all()


class ContactCopyView(
    BaseContactView,
    RedirectToObjectViewMixin,
    CreateView,
):
    def form_valid(self, form):
        new_contact = form.save(commit=False)
        new_contact.pk = None
        new_contact.save()
        return super().form_valid(form)


def get_queryset_related(self):
    """Get related querysets for a report."""
    report = self.get_object()
    company = report.company
    notes = report.notes.all()
    clients = report.clients.all()
    invoices = report.invoices.all()
    projects = report.projects.all()
    contacts = report.contacts.all()
    reports = report.reports.all()
    queryset_related = [
        q for q in [clients, contacts, invoices, notes, projects, reports] if q.exists()
    ]
    return company, projects, invoices, report, contacts, queryset_related


class DashboardView(BaseView, UserPassesTestMixin, ListView):
    """Dashboard view for authenticated users."""

    template_name = "dashboard/index.html"
    dashboard = True

    def get_queryset(self):
        """Return empty queryset as data is added in context."""
        return []

    def test_func(self):
        """Test if user is authenticated."""
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        """Redirect to login if not authenticated."""
        return HttpResponseRedirect(reverse("account_login"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["overview_nav"] = True

        filter_by = {"archived": False}

        invoices = get_queryset(
            Invoice,
            filter_by={"archived": False},
            order_by=["-created"],
        )

        context["invoices"] = invoices
        context["companies"] = get_queryset(
            Company, filter_by=filter_by, order_by=["name"]
        )
        context["projects"] = get_queryset(
            Project, filter_by=filter_by, order_by=["name"]
        )
        context["notes"] = get_queryset(
            Note, filter_by=filter_by, order_by=["-created"]
        )
        context["tasks"] = get_queryset(Task, filter_by=filter_by, order_by=["name"])
        context["contacts"] = get_queryset(
            Contact, filter_by=filter_by, order_by=["last_name"]
        )
        context["clients"] = get_queryset(
            Client, filter_by=filter_by, order_by=["name"]
        )
        context["reports"] = get_queryset(
            Report, filter_by=filter_by, order_by=["-created"]
        )

        if not self.request.user.is_superuser:
            filter_by = {"archived": False, "user": self.request.user}

        times = get_queryset(Time, filter_by=filter_by, order_by=["-archived", "-date"])

        context["times"] = times

        entered = times["queryset"].aggregate(total=Sum(F("hours")))
        approved = (
            times["queryset"]
            .filter(invoice__isnull=False)
            .aggregate(total=Sum(F("hours")))
        )

        context["statcard"]["times"]["entered"] = entered
        context["statcard"]["times"]["approved"] = approved

        entered = entered["total"] or 0
        approved = approved["total"] or 0

        gross = invoices["queryset"].aggregate(amount=Sum(F("amount")))["amount"]
        cost = invoices["queryset"].aggregate(cost=Sum(F("cost")))["cost"]
        net = invoices["queryset"].aggregate(net=Sum(F("net")))["net"]

        gross = gross or 0
        cost = cost or 0
        net = net or 0

        context["statcards"] = {}
        context["statcards"]["dashboard"] = {}
        context["statcards"]["dashboard"]["invoices"] = {}
        context["statcards"]["dashboard"]["invoices"]["gross"] = gross
        context["statcards"]["dashboard"]["invoices"]["cost"] = cost
        context["statcards"]["dashboard"]["invoices"]["net"] = net

        context["dataset_times"] = [int(entered), int(approved)]
        context["dataset_invoices"] = [int(gross), int(cost), int(net)]
        context["dashboard"] = self.dashboard

        return context


def display_mode(request):
    mode = request.GET.get("display-mode", "dark")
    if mode == "light":
        request.user.profile.dark = False
        request.user.profile.save()
    elif mode == "dark":
        request.user.profile.dark = True
        request.user.profile.save()
    return HttpResponseRedirect(request.headers.get("Referer"))


def save_positions(request):
    if request.method == "POST":
        profile = request.user.profile
        positions = request.POST.get("positions")
        profile.draggable_positions = positions
        profile.save()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})


def html_mode(request):
    html = request.GET.get("html", "true")
    model = request.GET.get("model")
    obj_id = request.GET.get("id")
    html = False if html.lower() == "false" else True
    ModelClass = apps.get_model(app_label="db", model_name=model.capitalize())
    obj = get_object_or_404(ModelClass, pk=obj_id)
    if html:
        obj.html = True
    else:
        obj.html = False
    obj.save()
    return HttpResponseRedirect(request.headers.get("Referer"))


class BaseInvoiceView(BaseView, SuperuserRequiredMixin):
    """Base view for Invoice model operations."""

    model = Invoice
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = InvoiceForm
    form_class = InvoiceForm
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    template_name = "edit.html"
    exclude = [
        "contacts",
        "company",
        "start_date",
        "end_date",
        "due_date",
        "client",
        "project",
        "task",
        "issue_date",
    ]

    @staticmethod
    def generate_docx(html_content, title):
        """Generate DOCX document from HTML content."""
        docx_content = html2docx(html_content, title=title)
        doc = Document(docx_content)
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer


class InvoiceListView(BaseInvoiceView, ListView):
    model = Invoice
    template_name = "index.html"


class InvoiceCreateView(BaseInvoiceView, CreateView):
    success_url = reverse_lazy("invoice_view")

    def get_success_url(self):
        return reverse_lazy("invoice_view", args=[self.object.pk])

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

        context["preview_template"] = "dashboard/table/invoice.html"

        return context


class InvoiceUpdateView(BaseInvoiceView, UpdateView):
    template_name = "edit.html"

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

    def get_success_url(self):
        return reverse_lazy("invoice_view", args=[self.object.pk])

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)


class InvoiceDeleteView(BaseInvoiceView, DeleteView):
    model = Invoice
    form_model = InvoiceForm
    success_url = reverse_lazy("invoice_index")
    template_name = "delete.html"

    def get_queryset(self):
        return Invoice.objects.all()


class InvoiceCopyView(BaseInvoiceView, CreateView):
    model = Invoice
    form_model = InvoiceForm
    success_url = reverse_lazy("invoice_index")

    def get_queryset(self):
        return Invoice.objects.all()

    def get_initial(self):
        original_invoice = Invoice.objects.get(pk=self.kwargs["pk"])
        return {
            "name": original_invoice.name,
        }

    def form_valid(self, form):
        new_invoice = form.save(commit=False)
        new_invoice.pk = None
        new_invoice.save()
        return super().form_valid(form)


class InvoiceExportDOCView(BaseInvoiceView, View):
    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["object_id"]
        obj = get_object_or_404(self.model, id=object_id)
        self.template_name = "dashboard/table/invoice.html"
        context = {}
        context["pdf"] = True
        context["object"] = obj
        context["times"] = obj.times.all().order_by("date")
        template = get_template(self.template_name)
        html_content = template.render(context)
        subject = obj.subject
        buffer = self.generate_docx(html_content, title=subject)
        response = FileResponse(
            buffer,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{self.model_name}_{object_id}.docx"'
        )
        return response


class InvoiceExportPDFView(BaseInvoiceView, View):
    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["object_id"]
        obj = get_object_or_404(self.model, id=object_id)
        self.template_name = "dashboard/table/invoice.html"
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


class InvoiceEmailDOCView(BaseInvoiceView, View):
    model = Invoice
    template_name = None

    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["object_id"]
        obj = get_object_or_404(self.model, id=object_id)
        self.template_name = "dashboard/table/invoice.html"
        context = {}
        context["pdf"] = True
        context["object"] = obj
        context["times"] = obj.times.all().order_by("date")
        template = get_template(self.template_name)
        html_content = template.render(context)
        subject = obj.subject
        buffer = self.generate_docx(html_content, title=subject)
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
                    f"{subject.replace(' ', '_')}.docx",
                    buffer.getvalue(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
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
                f"{subject.replace(' ', '_')}.docx",
                buffer.getvalue(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            email.send()
            messages.success(
                request, f"Email sent successfully to: {settings.DEFAULT_FROM_EMAIL}"
            )
        return redirect(obj)


class InvoiceEmailPDFView(BaseInvoiceView, View):
    model = Invoice
    template_name = None

    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["object_id"]
        obj = get_object_or_404(self.model, id=object_id)
        self.template_name = "dashboard/table/invoice.html"
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


class InvoiceEmailTextView(BaseInvoiceView, View):
    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["object_id"]
        obj = get_object_or_404(self.model, id=object_id)
        subject = obj.subject
        header = Texttable()
        header.set_deco(Texttable.VLINES)
        header.set_cols_align(["r", "l", "r", "l"])
        header.add_rows(
            [
                ["", "", "", ""],
                ["Id:", obj.id, "From:", obj.company or "Some company"],
                ["", "", "", ""],
                [
                    "Issue Date:",
                    f"{obj.issue_date.strftime('%B %d, %Y')}" or "",
                    "",
                    "",
                ],
                [
                    "Due Date:",
                    f"{obj.due_date.strftime('%B %d, %Y')}" if obj.due_date else "",
                    "For:",
                    (
                        f"{obj.client}\n{obj.client.address}"
                        if obj.client and obj.client.address
                        else ""
                    )
                    or (
                        f"{obj.user.first_name} {obj.user.last_name}\n{obj.user.profile.address}"
                        if obj.user and obj.user.profile.address
                        else ""
                    ),
                ]
                if obj.due_date or obj.client
                else ["", "", "", ""],
                ["Subject:", subject, "", ""],
                ["", "", "", ""],
                [
                    "Period of\nperformance",
                    f"{obj.start_date.strftime('%B %d, %Y')} - {obj.end_date.strftime('%B %d, %Y')}",
                    "",
                    "",
                ],
                ["", "", "", ""],
            ]
        )
        text_content = f"{header.draw()}\n\n"
        table = Texttable()
        table.add_row(
            ["Date", "Task", "Description", "Quantity", "Unit Price", "Amount"]
        )
        total = {}
        total["amount"] = 0
        total["hours"] = 0
        total["rate"] = 0
        if obj.project:
            if obj.project.task:
                total["rate"] = obj.project.task.rate
        for entry in obj.times.all():
            rate = 0
            amount = entry.amount
            hours = entry.hours
            if entry.project:
                if entry.project.task:
                    rate = entry.project.task.rate
            total["amount"] += amount
            total["hours"] += hours
            table.add_row(
                [
                    entry.date,
                    entry.task,
                    entry.description,
                    entry.quantity,
                    rate,
                    amount,
                ]
            )
        table.add_row(
            ["Total", "", "", "", "", locale.currency(total["amount"], grouping=True)]
        )
        text_content += f"{table.draw()}\n\n"
        notes = obj.notes.all()
        if notes:
            text_content += "Notes\n\n"
            for note in notes:
                text_content += f"- {note}\n\n"
        html_content = f"<pre>{text_content}</pre>"
        subject = obj.subject
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
        )
        email.attach_alternative(html_content, "text/html")
        contact_emails = [
            contact.email for contact in obj.contacts.all() if contact.email is not None
        ]
        if contact_emails:
            for contact_email in contact_emails:
                email.to = [contact_email]
                email.send()
                messages.success(
                    request, f"Email sent successfully to: {contact_email}"
                )
        else:
            email.to = [settings.DEFAULT_FROM_EMAIL]
            email.send()
            messages.success(
                request, f"Email sent successfully to: {settings.DEFAULT_FROM_EMAIL}"
            )
        return redirect(obj)


class FakeTextView(View):
    """
    Placeholder view for generating fake text data.

    Currently unimplemented. When implemented, this view will use Faker
    to generate sample paragraph text via JSON response.
    """

    def get(self, request, *args, **kwargs):
        """Return HTTP 501 Not Implemented for now."""
        return JsonResponse(
            {"error": "This feature is not yet implemented."}, status=501
        )


@login_required
def lounge(request):
    context = {}
    context["lounge_nav"] = True
    return render(request, "lounge.html", context)


class BaseNoteView(BaseView, SuperuserRequiredMixin):
    """Base view for Note model operations."""

    model = Note
    form_model = NoteForm
    form_class = NoteForm
    template_name = "edit.html"
    exclude = ["html"]


class NoteListView(BaseNoteView, ListView):
    model = Note
    template_name = "index.html"


class NoteListFullScreen(NoteListView, ListView):
    model = Note
    template_name = "notes/fullscreen.html"


class NoteCreateView(BaseNoteView, CreateView):
    model = Note
    form_model = NoteForm
    success_url = reverse_lazy("note_view")

    def get_success_url(self):
        return reverse_lazy("note_view", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class NoteDetailView(BaseNoteView, DetailView):
    model = Note
    template_name = "view.html"
    url_export_pdf = "note_export_pdf"
    url_email_pdf = "note_email_pdf"
    url_email_text = "note_email_text"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url_export_pdf"] = self.url_export_pdf
        context["url_email_pdf"] = self.url_email_pdf
        context["url_email_text"] = self.url_email_text
        return context


class NoteUpdateView(BaseNoteView, UpdateView):
    model = Note
    form_model = NoteForm
    success_url = reverse_lazy("note_view")

    def form_valid(self, form):
        html = form.initial["html"]
        if html:
            form.instance.html = html
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url_cancel"] = f"{self.model_name}_view"
        context["pk"] = self.kwargs["pk"]
        return context

    def get_queryset(self):
        # Retrieve the object to be edited
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("note_view", args=[self.object.pk])


class NoteDeleteView(BaseNoteView, DeleteView):
    model = Note
    form_model = NoteForm
    success_url = reverse_lazy("note_index")
    template_name = "delete.html"

    def get_queryset(self):
        return Note.objects.all()


class NoteCopyView(BaseNoteView, CreateView):
    model = Note
    form_model = NoteForm
    success_url = reverse_lazy("note_index")

    def get_queryset(self):
        return Note.objects.all()

    def form_valid(self, form):
        new_note = form.save(commit=False)
        new_note.pk = None
        new_note.save()
        return super().form_valid(form)


class NoteEmailTextView(BaseNoteView, View):
    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["object_id"]
        obj = get_object_or_404(self.model, id=object_id)

        email = EmailMessage(
            subject=obj.title,
            body=obj.text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.DEFAULT_FROM_EMAIL],
        )

        contacts = obj.contacts.all()

        successes = []
        failures = []

        if contacts:
            for contact in contacts:
                email.to = [contact.email]
                try:
                    email.send()
                except Exception:
                    failures.append(contact.email)
                else:
                    successes.append(contact.email)
        else:
            try:
                email.send()
            except Exception:
                failures.append(settings.DEFAULT_FROM_EMAIL)
            else:
                successes.append(settings.DEFAULT_FROM_EMAIL)
        if successes:
            messages.success(
                request, f"Email sent successfully to: {', '.join(successes)}."
            )
        if failures:
            messages.warning(
                request, f"Failed to send email to: {', '.join(failures)}."
            )

        return redirect(obj)


class BaseProjectView(BaseView, SuperuserRequiredMixin):
    """Base view for Project model operations."""

    model = Project
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = ProjectForm
    form_class = ProjectForm
    template_name = "edit.html"
    order_by = ["archived", "name", "-created"]
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    exclude = ["client", "start_date", "end_date", "team", "description"]


class ProjectListView(BaseProjectView, ListView):
    model = Project
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url_create"] = "%s_create" % self.model_name
        context["url_view"] = "%s_view" % self.model_name
        return context


class ProjectCreateView(BaseProjectView, CreateView):
    model = Project
    form_model = ProjectForm
    success_url = reverse_lazy("project_view")

    def get_success_url(self):
        client_id = self.request.GET.get("client_id")
        if client_id:
            return reverse_lazy("client_view", args=[client_id])
        else:
            return reverse_lazy("project_view", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        client = None
        client_id = self.request.GET.get("client_id")
        if client_id:
            client = Client.objects.get(id=client_id)
        context["form"].initial = {
            "start_date": now,
            "end_date": now + timezone.timedelta(days=366),
            "client": client,
        }
        return context

    def form_valid(self, form):
        client_id = self.request.GET.get("client_id")
        obj = form.save()
        if client_id:
            client = Client.objects.get(pk=client_id)
            client.project_set.add(obj)
            return HttpResponseRedirect(reverse("client_view", args=[client_id]))
        return super().form_valid(form)


class ProjectDetailView(BaseProjectView, DetailView):
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        project = self.get_object()
        notes = project.notes.all()
        tasks = Task.objects.filter(project=project)
        client = project.client
        company = None
        contacts = Contact.objects.none()
        if client:
            company = client.company
            contacts = client.contact_set.all()
        invoices = Invoice.objects.filter(project=project).order_by(
            "-created", "archived"
        )
        queryset_related = [q for q in [contacts, tasks, notes, invoices] if q.exists()]
        queryset_related = list(chain(*queryset_related))
        if company:
            queryset_related.insert(0, company)
        if client:
            queryset_related.insert(0, client)
        queryset_related = sorted(queryset_related, key=self.get_archived)
        self._queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)
        return context


class ProjectUpdateView(BaseProjectView, UpdateView):
    model = Project
    form_model = ProjectForm
    success_url = reverse_lazy("project_view")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url_cancel"] = f"{self.model_name}_view"
        context["pk"] = self.kwargs["pk"]
        return context

    def get_queryset(self):
        # Retrieve the object to be edited
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("project_view", args=[self.object.pk])


class ProjectDeleteView(BaseProjectView, DeleteView):
    model = Project
    form_model = ProjectForm
    success_url = reverse_lazy("project_index")
    template_name = "delete.html"

    def get_queryset(self):
        return Project.objects.all()


class ProjectCopyView(BaseProjectView, CreateView):
    model = Project
    form_model = ProjectForm
    success_url = reverse_lazy("project_index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return Project.objects.all()

    def get_initial(self):
        original_project = Project.objects.get(pk=self.kwargs["pk"])
        return {
            "name": original_project.name,
        }

    def form_valid(self, form):
        new_project = form.save(commit=False)
        new_project.pk = None
        new_project.save()
        return super().form_valid(form)


def update_related_entries(request):
    """
    Update multiple related entries (archive, delete, save, etc.).

    Handles bulk operations on database entries from the dashboard.
    """
    if request.method == "POST":
        entry_ids = request.POST.getlist("entry_id")
        if not entry_ids:
            messages.error(request, "No entries selected.")
            return HttpResponseRedirect(reverse("dashboard"))

        summary_message = ""

        for entry_id in entry_ids:
            try:
                model_name, pk = entry_id.split("-")
            except ValueError:
                messages.error(request, "Invalid entry ID format.")
                return HttpResponseRedirect(reverse("dashboard"))

            if model_name == "user":
                ModelClass = apps.get_model(app_label="auth", model_name="User")
            else:
                try:
                    ModelClass = apps.get_model(
                        app_label="db", model_name=model_name.capitalize()
                    )
                except LookupError:
                    messages.error(request, f"Invalid model name: {model_name}")
                    return HttpResponseRedirect(reverse("dashboard"))

            try:
                entry = ModelClass.objects.get(pk=pk)
            except ModelClass.DoesNotExist:
                messages.error(
                    request, f"{model_name.capitalize()} entry not found: {entry_id}"
                )
                return HttpResponseRedirect(reverse(f"{model_name}_index"))

            action = request.POST.get("action")
            if action == "delete":
                try:
                    entry.delete()
                    summary_message += (
                        f"Successfully deleted {model_name} entry: {entry_id}\n"
                    )
                except Exception as e:
                    messages.error(
                        request,
                        f"Failed to delete {model_name} entry {entry_id}: {str(e)}",
                    )
            elif action == "archive":
                if model_name == "user":
                    entry.is_active = False
                else:
                    entry.archived = True
                entry.save()
                summary_message += (
                    f"Successfully archived {model_name} entry: {entry_id}\n"
                )
            elif action == "unarchive":
                if model_name == "user":
                    entry.is_active = True
                else:
                    entry.archived = False
                entry.save()
                summary_message += (
                    f"Successfully unarchived {model_name} entry: {entry_id}\n"
                )
            elif action == "html":
                if model_name == "note":
                    entry.html = True
                    entry.save()
                    summary_message += (
                        f"Successfully HTMLed {model_name} entry: {entry_id}\n"
                    )
                else:
                    messages.error(request, "Invalid action requested.")
            elif action == "unhtml":
                if model_name == "note":
                    entry.html = False
                    entry.save()
                    summary_message += (
                        f"Successfully Un-HTMLed {model_name} entry: {entry_id}\n"
                    )
                else:
                    messages.error(request, "Invalid action requested.")
            elif action == "save":
                try:
                    entry.save()
                    summary_message += (
                        f"Successfully saved {model_name} entry: {entry_id}\n"
                    )
                except Exception as e:
                    messages.error(
                        request,
                        f"Failed to save {model_name} entry {entry_id}: {str(e)}",
                    )
            else:
                messages.error(request, "Invalid action requested.")

        if summary_message:
            messages.success(request, summary_message)

    return HttpResponseRedirect(request.headers.get("Referer"))


class BaseReportView(BaseView, SuperuserRequiredMixin):
    """Base view for Report model operations."""

    model = Report
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = ReportForm
    form_class = ReportForm
    template_name = "edit.html"
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"

    url_export_pdf = "report_export_pdf"
    url_email_pdf = "report_email_pdf"
    url_email_text = "report_email_text"

    exclude = [
        "date",
        "hours",
        "amount",
        "cost",
        "net",
        "clients",
        "invoices",
        "projects",
        "tasks",
        "contacts",
        "user",
        "company",
        "team",
    ]

    def get_context_data(self, **kwargs):
        """Add export and email URLs to context."""
        context = super().get_context_data(**kwargs)
        context["url_export_pdf"] = self.url_export_pdf
        context["url_email_pdf"] = self.url_email_pdf
        context["url_email_text"] = self.url_email_text
        return context


class ReportDetailView(BaseReportView, DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        company, projects, invoices, report, contacts, queryset_related = (
            get_queryset_related(self)
        )

        context["invoices"] = invoices

        if company:
            queryset_related.insert(0, [company])

        queryset_related = list(chain(*queryset_related))

        for project in projects:
            for team_member in project.team.all():
                if team_member and team_member not in queryset_related:
                    queryset_related.append(team_member)

        for invoice in invoices:
            for time_entry in invoice.times.all():
                if time_entry:
                    queryset_related.append(time_entry)

        self._queryset_related = queryset_related
        self.has_related = True

        contact_emails = []

        for contact in contacts:
            if contact.email:
                contact_emails.append(contact.email)
        context["contact_emails"] = ", ".join(contact_emails)
        context["field_values"].append(("Contacts", ""))

        if contacts:
            for contact in contacts:
                context["field_values"].append(("↳", contact))

        return context

    template_name = "view.html"


class CreateOrUpdateReportView(BaseReportView):
    update = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        last_month = now - timezone.timedelta(days=now.day)
        last_month = last_month.strftime("%B")

        if not self.update:
            context["form"].initial = {
                "name": f"{last_month} {now.year}",
            }

        clients = Client.objects.filter(archived=False)
        invoices = Invoice.objects.filter(archived=False)
        companies = Company.objects.filter(archived=False)

        projects = [invoice.project for invoice in invoices if invoice.project]
        tasks = [project.task for project in projects]

        report_hours = invoices.aggregate(hours=Sum("hours"))["hours"]
        report_amount = invoices.aggregate(amount=Sum(F("amount")))["amount"]
        report_cost = invoices.aggregate(cost=Sum(F("cost")))["cost"]
        report_net = invoices.aggregate(net=Sum(F("net")))["net"]

        team = {}
        for project in projects:
            team[project.name] = {}
            task = project.task

            gross, cost, net, rate = 0, 0, 0, 0

            for member in project.team.all():
                times = Time.objects.filter(
                    user=member, project=project, archived=False
                )

                approved = times.filter(invoice__isnull=False).aggregate(
                    total=Sum(F("hours"))
                )
                approved = approved["total"] or 0
                approved = decimal.Decimal(approved)

                if task:
                    gross = approved * task.rate

                profile = member.profile

                if profile:
                    rate = member.profile.rate
                    if rate:
                        cost = approved * member.profile.rate
                    if gross and cost:
                        net = gross - cost

                team[project.name][member.username] = {}
                team[project.name][member.username]["rate"] = str(rate)
                team[project.name][member.username]["hours"] = str(approved)
                team[project.name][member.username]["gross"] = str(gross)
                team[project.name][member.username]["cost"] = str(cost)
                team[project.name][member.username]["net"] = str(net)

            context["form"].initial.update(
                {
                    "clients": clients,
                    "projects": projects,
                    "tasks": tasks,
                    "invoices": invoices,
                    "hours": f"{report_hours or 0:.2f}",
                    "amount": f"{report_amount or 0:.2f}",
                    "cost": f"{report_cost or 0:.2f}",
                    "net": f"{report_net or 0:.2f}",
                    "user": self.request.user,
                    "company": companies.first(),
                    "team": team,
                }
            )

        return context


class ReportListView(BaseReportView, ListView):
    template_name = "index.html"


class ReportCreateView(CreateOrUpdateReportView, CreateView):
    success_url = reverse_lazy("report_view")

    def get_form(self, form_class=None):
        companies = Company.objects.filter(archived=False)
        if self.request.user.is_superuser:
            form_class = AdminReportForm
        form = super().get_form(form_class)
        form.fields["company"].queryset = companies
        return form

    def get_success_url(self):
        return reverse_lazy("report_view", args=[self.object.pk])


class ReportUpdateView(CreateOrUpdateReportView, UpdateView):
    update = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs["pk"]
        return context

    def get_form(self, form_class=None):
        if self.request.user.is_superuser:
            form_class = AdminReportForm
        form = super().get_form(form_class)
        return form

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("report_view", args=[self.object.pk])


class ReportDeleteView(BaseReportView, DeleteView):
    template_name = "delete.html"
    success_url = reverse_lazy("report_index")

    def get_queryset(self):
        return Report.objects.all()


class ReportCopyView(BaseReportView, CreateView):
    success_url = reverse_lazy("report_index")

    def get_queryset(self):
        return Report.objects.all()

    def get_initial(self):
        original_report = Report.objects.get(pk=self.kwargs["pk"])
        return {
            "name": original_report.name,
        }

    def form_valid(self, form):
        new_report = form.save(commit=False)
        new_report.pk = None
        new_report.save()
        return super().form_valid(form)


class ReportEmailTextView(BaseReportView, View):
    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["object_id"]
        obj = get_object_or_404(self.model, id=object_id)

        subject = f"{obj.name} Report"

        text_content = f"{self.model_name.upper()}\n\n"

        header = Texttable()
        header.set_deco(Texttable.VLINES)
        header.set_cols_align(["r", "l", "r", "l"])

        net, cost, amount = 0, 0, 0
        if obj.net:
            net = obj.net
        if obj.cost:
            cost = obj.cost
        if obj.amount:
            amount = obj.amount

        contacts = obj.contacts.all()

        header.add_rows(
            [
                ["", "", "", ""],
                ["Id:", obj.id, "Issue Date:", f"{obj.date.strftime('%B %d, %Y')}"],
                ["Name:", obj.name, "From:", obj.company or "Some company"],
                ["Hours:", obj.hours, "Net:", locale.currency(net, grouping=True)],
                [
                    "Gross:",
                    locale.currency(amount, grouping=True),
                    "Cost:",
                    locale.currency(cost, grouping=True),
                ],
                ["", "", "", ""] if contacts else ["", "", "", ""],
                ["", "", "", ""],
            ]
        )

        text_content += f"{header.draw()}\n\n"

        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.add_row(
            ["Invoice", "Issue Date", "Hourly Rate", "Hours", "Gross", "Cost", "Net"]
        )

        for invoice in obj.invoices.all():
            rate = 0
            cost = 0
            net = 0
            if invoice.project:
                if invoice.project.task:
                    rate = invoice.project.task.rate
            if invoice.cost:
                cost = invoice.cost
            if invoice.net:
                net = invoice.net
            table.add_row(
                [
                    invoice.subject,
                    f"{invoice.issue_date.strftime('%B %d, %Y')}",
                    locale.currency(rate, grouping=True),
                    invoice.hours,
                    locale.currency(invoice.amount, grouping=True),
                    locale.currency(cost, grouping=True),
                    locale.currency(net, grouping=True),
                ]
            )
            if obj.team:
                for project in obj.team:
                    team_member_data = ast.literal_eval(obj.team[project]).items()
                    if invoice.project:
                        if invoice.project.name == project:
                            for field in team_member_data:
                                user = User.objects.get(username=field[0])
                                full_name = "↳ " + " ".join(
                                    [user.first_name, user.last_name]
                                )
                                try:
                                    table.add_row(
                                        [
                                            full_name or user.username,
                                            "",
                                            locale.currency(float(field[1]["rate"])),
                                            float(field[1]["hours"]),
                                            locale.currency(float(field[1]["gross"])),
                                            locale.currency(float(field[1]["net"])),
                                            locale.currency(float(field[1]["cost"])),
                                        ]
                                    )
                                except ValueError:
                                    table.add_row(
                                        [
                                            full_name or user.username,
                                            "",
                                            locale.currency(float(0)),
                                            float(field[1]["hours"]),
                                            locale.currency(float(field[1]["gross"])),
                                            locale.currency(float(field[1]["net"])),
                                            locale.currency(float(field[1]["cost"])),
                                        ]
                                    )

        text_content += table.draw()

        html_content = f"<pre>{text_content}</pre>"

        contact_emails = [
            contact.email for contact in contacts if contact.email is not None
        ]

        if contact_emails:
            for contact_email in contact_emails:
                email = EmailMultiAlternatives(
                    subject, text_content, settings.DEFAULT_FROM_EMAIL, [contact_email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
                messages.success(
                    request, f"Email sent successfully to: {contact_email}"
                )
        else:
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            messages.success(
                request, f"Email sent successfully to: {settings.DEFAULT_FROM_EMAIL}"
            )
        return redirect(obj)


SEARCH_MODELS = (
    Client,
    Company,
    Contact,
    Invoice,
    Note,
    Project,
    Report,
    Task,
    Time,
    User,
)


class SearchView(SuperuserRequiredMixin, BaseView, ListView):
    """Search view for searching across multiple models."""

    search = True
    template_name = "search.html"
    url_index = "search_index"

    def get_context_data(self, **kwargs):
        """Add search query to context."""
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q")
        context["q"] = query
        return context

    def get_queryset(self):
        """Search across multiple models."""
        queryset = []
        query = self.request.GET.get("q")
        if query:
            query = query.split()
            for search_model in SEARCH_MODELS:
                q = Q()
                for search_term in query:
                    for field in search_model._meta.fields:
                        # Only search text fields
                        if field.__class__.__name__ == "CharField":
                            q |= Q(**{f"{field.name}__icontains": search_term})
                if q:
                    queryset += search_model.objects.filter(q)
        return queryset


def get_model_config(model_name):
    """
    Returns configuration for allowed models to prevent arbitrary access.
    Maps string names to Model Class and specific field settings.
    Includes has_user_field to indicate if the model should be filtered by user.
    """
    # Configuration map: 'slug': {'model': Class, 'archive_field': 'field_name', 'has_user_field': bool}
    config = {
        "user": {
            "model": User,
            "archive_field": "is_active",
            "active_val": True,
            "has_user_field": False,
        },
        "report": {
            "model": apps.get_model("db", "Report"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": True,
        },
        "invoice": {
            "model": apps.get_model("db", "Invoice"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": True,
        },
        "note": {
            "model": apps.get_model("db", "Note"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": True,
        },
        "time": {
            "model": apps.get_model("db", "Time"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": True,
        },
        "task": {
            "model": apps.get_model("db", "Task"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": False,
        },
        "client": {
            "model": apps.get_model("db", "Client"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": False,
        },
        "company": {
            "model": apps.get_model("db", "Company"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": False,
        },
        "contact": {
            "model": apps.get_model("db", "Contact"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": False,
        },
        "project": {
            "model": apps.get_model("db", "Project"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": False,
        },
    }
    return config.get(model_name)


@transaction.atomic
def update_selected_entries(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("dashboard"))

    model_name = request.POST.get("model_name")
    action = request.POST.get("action")
    entry_ids = request.POST.getlist("entry_id")

    # 1. Validation and Configuration Lookup
    model_conf = get_model_config(model_name)

    if not model_conf:
        messages.error(request, "Invalid model selected.")
        return HttpResponseRedirect(reverse("dashboard"))

    if not entry_ids:
        messages.error(request, "No entries selected.")
        return HttpResponseRedirect(reverse(f"{model_name}_index"))

    ModelClass = model_conf["model"]

    # 2. Fetch Entries with user filtering applied early
    # Filter returns empty queryset, it does not raise DoesNotExist
    entries = ModelClass.objects.filter(pk__in=entry_ids)

    # Apply user filtering for non-superusers if model has user field
    # This is done early to prevent information leakage about entry existence
    if not request.user.is_superuser and model_conf.get("has_user_field", False):
        entries = entries.filter(user=request.user)

    count = entries.count()

    if count == 0:
        # Provide appropriate message based on whether user filtering was applied
        if not request.user.is_superuser and model_conf.get("has_user_field", False):
            messages.warning(
                request,
                f"No {model_name} entries found that you have permission to modify.",
            )
        else:
            messages.warning(request, f"Selected {model_name} entries not found.")
        return HttpResponseRedirect(reverse(f"{model_name}_index"))

    # 3. Action Dispatcher
    try:
        if action == "delete":
            # delete() returns (total_count, {model_label: count})
            deleted_count, _ = entries.delete()
            if deleted_count > 0:
                messages.success(
                    request,
                    f"Successfully deleted {deleted_count} {model_name} entries.",
                )
            else:
                messages.warning(request, f"No {model_name} entries were deleted.")

        elif action == "archive":
            target_field = model_conf["archive_field"]
            target_value = not model_conf[
                "active_val"
            ]  # e.g., is_active=False or archived=True

            entries.update(**{target_field: target_value})

            # Handle Invoice specific relationship update
            if model_name == "invoice":
                # Optimization: Update related items in one query rather than looping
                # Assuming 'times' is the related_name for a TimeEntry model
                for invoice in entries:
                    invoice.times.all().update(archived=True)

            messages.success(
                request, f"Successfully archived {count} {model_name} entries."
            )

        elif action == "unarchive":
            target_field = model_conf["archive_field"]
            target_value = model_conf[
                "active_val"
            ]  # e.g., is_active=True or archived=False

            entries.update(**{target_field: target_value})

            if model_name == "invoice":
                for invoice in entries:
                    invoice.times.all().update(archived=False)

            messages.success(
                request, f"Successfully unarchived {count} {model_name} entries."
            )

        elif action in ["html", "unhtml"]:
            if model_name != "note":
                messages.error(request, "HTML action only applicable to Notes.")
            else:
                is_html = action == "html"
                entries.update(html=is_html)
                status_text = "HTMLed" if is_html else "Un-HTMLed"
                messages.success(
                    request, f"Successfully {status_text} {count} {model_name} entries."
                )

        elif action == "save":
            # Iterate to trigger save() signals (bulk_update does not trigger signals)
            for entry in entries:
                entry.save()
            messages.success(
                request, f"Successfully saved {count} {model_name} entries."
            )

        else:
            messages.error(request, "Invalid action requested.")

    except Exception as e:
        # Catch unexpected DB errors
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(reverse(f"{model_name}_index"))


class BaseTaskView(BaseView, SuperuserRequiredMixin):
    """Base view for Task model operations."""

    model = Task
    form_model = TaskForm
    form_class = TaskForm
    template_name = "edit.html"
    order_by = ["archived", "name", "-created"]


class TaskListView(BaseTaskView, ListView):
    template_name = "index.html"


class TaskCreateView(BaseTaskView, CreateView):
    form_model = TaskForm
    success_url = reverse_lazy("task_view")

    def get_success_url(self):
        return reverse_lazy("task_view", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        project_id = self.request.GET.get("project_id")
        obj = form.save()
        if project_id:
            project = Project.objects.get(pk=project_id)
            obj.project_set.add(project)
            return HttpResponseRedirect(reverse("project_view", args=[project_id]))
        return super().form_valid(form)


class TaskDetailView(BaseTaskView, DetailView):
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        task = self.get_object()
        notes = task.notes.all()
        projects = Project.objects.filter(task=task)
        queryset_related = [q for q in [notes, projects] if q.exists()]
        queryset_related = list(chain(*queryset_related))
        queryset_related = sorted(queryset_related, key=self.get_archived)
        self._queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)
        return context


class TaskUpdateView(BaseTaskView, UpdateView):
    form_model = TaskForm
    success_url = reverse_lazy("task_view")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs["pk"]
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("task_view", args=[self.object.pk])


class TaskDeleteView(BaseTaskView, DeleteView):
    form_model = TaskForm
    success_url = reverse_lazy("task_index")
    template_name = "delete.html"

    def get_queryset(self):
        return Task.objects.all()


class TaskCopyView(BaseTaskView, CreateView):
    form_model = TaskForm
    success_url = reverse_lazy("task_index")

    def get_queryset(self):
        return Task.objects.all()

    def get_initial(self):
        original_task = Task.objects.get(pk=self.kwargs["pk"])
        return {
            "name": original_task.name,
        }

    def form_valid(self, form):
        new_task = form.save(commit=False)
        new_task.pk = None
        new_task.save()
        return super().form_valid(form)


class BaseTimeView(BaseView, AuthenticatedRequiredMixin):
    """Base view for Time model operations."""

    model = Time
    form_model = TimeForm
    form_class = TimeForm
    template_name = "edit.html"

    _exclude = ["client", "project", "task", "invoice"]

    def get_form(self, form_class=None):
        if self.request.user.is_superuser:
            form_class = AdminTimeForm

        form = super().get_form(form_class)

        projects = Project.objects.filter(
            team__in=[self.request.user],
            archived=False,
        )

        if not self.request.user.is_superuser:
            invoices = Invoice.objects.filter(
                project__in=projects,
                archived=False,
            )

            if projects:
                form.fields["project"].empty_label = None
                form.fields["project"].queryset = projects

            if invoices:
                form.fields["invoice"].empty_label = None
                form.fields["invoice"].queryset = invoices
            else:
                form.fields["invoice"].queryset = Invoice.objects.none()

            form.fields["user"].empty_label = None
            form.fields["user"].queryset = User.objects.filter(pk=self.request.user.id)

        else:
            project = projects.first()
            if project:
                form.fields["project"].empty_label = None
                form.fields["project"].queryset = projects

                if project.task:
                    form.fields["task"].empty_label = None
                    form.fields["task"].queryset = Task.objects.filter(
                        project__in=projects
                    )

                form.fields["client"].empty_label = None
                form.fields["client"].queryset = Client.objects.filter(
                    project__in=projects
                )

        return form


class TimeCreateView(
    BaseTimeView,
    RedirectToObjectViewMixin,
    CreateView,
):
    pass


class TimeListView(
    BaseTimeView,
    FilterByUserMixin,
    ListView,
):
    template_name = "index.html"


class TimeDetailView(BaseTimeView, DetailView):
    template_name = "view.html"

    def test_func(self):
        time = self.get_object()
        return self.request.user.is_superuser or self.request.user == time.user

    def get_context_data(self, **kwargs):
        time = self.get_object()
        if time.invoice:
            self._queryset_related = [time.invoice]
            self.has_related = True
        return super().get_context_data(**kwargs)


class TimeUpdateView(
    BaseTimeView,
    RedirectToObjectViewMixin,
    UpdateView,
):
    def form_valid(self, form):
        user_id = form.initial.get("user")
        if user_id:
            form.instance.user = User.objects.get(pk=user_id)
        return super().form_valid(form)


class TimeCopyView(
    BaseTimeView,
    ModelCopyMixin,
    RedirectToObjectViewMixin,
    CreateView,
):
    pass


class BaseUserView(BaseView):
    """Base view for User model operations."""

    model = User
    form_class = UserForm
    form_model = UserForm
    order_by = ["-is_active", "username"]
    exclude = ["rate", "mail", "address", "first_name", "last_name"]


class BaseUserMixin(SuperuserRequiredMixin):
    """Mixin for User views that require superuser access."""

    pass


class UserListView(BaseUserMixin, BaseUserView, ListView):
    template_name = "index.html"


class UserDetailView(BaseUserMixin, BaseUserView, DetailView):
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        user = self.get_object()
        projects = Project.objects.filter(team__in=[user])
        times = Time.objects.filter(user=user)
        invoices = Invoice.objects.filter(times__in=times)

        queryset_related = list(chain(projects, times, invoices))
        queryset_related = sorted(queryset_related, key=self.get_archived)
        self._queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)

        times = Time.objects.filter(user=user, archived=False)
        entered = times.aggregate(total=Sum(F("hours")))
        approved = times.filter(invoice__isnull=False).aggregate(total=Sum(F("hours")))

        context["statcard"]["times"]["entered"] = entered
        context["statcard"]["times"]["approved"] = approved

        approved = approved["total"] or 0

        gross = 0
        for project in projects:
            task = project.task
            if task:
                gross = approved * project.task.rate

            cost = 0
            if hasattr(user, "profile"):
                rate = user.profile.rate
                if rate:
                    cost = approved * user.profile.rate

            net = 0
            if gross and cost:
                net = gross - cost

            gross = gross or 0
            cost = cost or 0
            net = net or 0

            context["statcards"][project.name] = {}
            context["statcards"][project.name]["name"] = project.name
            context["statcards"][project.name]["invoices"] = {}
            context["statcards"][project.name]["invoices"]["gross"] = f"{gross:.2f}"
            context["statcards"][project.name]["invoices"]["cost"] = f"{cost:.2f}"
            context["statcards"][project.name]["invoices"]["net"] = f"{net:.2f}"

        context["user"] = self.request.user
        context["user_view"] = True

        return context


class UserCreateView(BaseUserView, CreateView):
    success_url = reverse_lazy("user_index")
    template_name = "edit.html"

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True  # Set is_active to True
        user.save()
        return super().form_valid(form)


class UserUpdateView(BaseUserMixin, BaseUserView, UpdateView):
    success_url = reverse_lazy("user_view")
    template_name = "edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["url_cancel"] = f"{self.model_name}_view"
        context["pk"] = self.kwargs["pk"]
        return context

    def form_valid(self, form):
        is_active = form.initial["is_active"]
        if is_active:
            form.instance.is_active = is_active
        return super().form_valid(form)

    def get_success_url(self):
        user = self.get_object()
        user_id = user.id
        return reverse("user_view", args=[user_id])


class TimeDeleteView(BaseTimeView, FilterByUserMixin, DeleteView):
    template_name = "delete.html"

    def test_func(self):
        time = self.get_object()
        return self.request.user.is_superuser or self.request.user == time.user

    def get_success_url(self):
        return (
            reverse_lazy("time_index")
            if self.request.user.is_superuser
            else reverse_lazy("dashboard")
        )


class UserDeleteView(BaseUserMixin, BaseUserView, DeleteView):
    success_url = reverse_lazy("user_index")
    template_name = "delete.html"

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        username = user.username
        user.delete()
        messages.success(request, f"You deleted {username}!")
        return HttpResponseRedirect(reverse("user_index"))


class UserCopyView(BaseUserMixin, BaseUserView, CreateView):
    success_url = reverse_lazy("user_index")
    template_name = "edit.html"


class UserToContactView(BaseUserView, View):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        contact = Contact(
            first_name=user.first_name, last_name=user.last_name, email=user.email
        )
        contact.save()
        return HttpResponseRedirect(reverse("contact_view", args=[contact.id]))
