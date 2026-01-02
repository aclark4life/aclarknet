import ast
import chess
import decimal
import io
import locale
import random
from django.shortcuts import render, reverse, redirect, get_object_or_404
from .models import Client, Company, Contact, Invoice, Project, Note, Task, Time, Report
from django.conf import settings
from rest_framework import viewsets
from django.views.generic import (
    View,
    CreateView,
    UpdateView,
    DetailView,
    ListView,
    DeleteView,
    TemplateView,
)
from django.contrib import messages
from django.db.models import F, Sum
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from itertools import chain
from .forms.user import UserForm
from .forms.time import TimeForm, AdminTimeForm
from .forms.task import TaskForm
from .forms.project import ProjectForm
from .forms.report import AdminReportForm, ReportForm
from .forms.note import NoteForm
from .forms.invoice import InvoiceForm
from .forms.contact import ContactForm
from .forms.company import CompanyForm
from .forms.client import ClientForm
from django.utils import timezone
from django import apps
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from texttable import Texttable
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import FileResponse, JsonResponse, HttpResponseRedirect
from docx import Document
from html2docx import html2docx
from .serializers import ClientSerializer
from django.core.paginator import Paginator
from django.db.models import BooleanField, Case, Value, When
from django.views.defaults import permission_denied
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

User = get_user_model()


def custom_403(request, exception=None):
    return permission_denied(request, exception=exception, template_name="403.html")


def custom_404(request, exception=None):
    return render(request, exception=exception, template_name="404.html")


def custom_500(request, exception=None):
    return render(request, exception=exception, template_name="500.html")


def trigger_500(request):
    raise Exception("This is a deliberate 500 error.")


def archive(request):
    archive = request.GET.get("archive", "true")
    model = request.GET.get("model")
    obj_id = request.GET.get("id")
    obj = None
    if model == "user":
        ModelClass = apps.get_model(app_label="siteuser", model_name="User")
        archive_field = "is_active"
    else:
        ModelClass = apps.get_model(app_label="db", model_name=model.capitalize())
        archive_field = "archived"
    field_value = False if archive == "false" else True
    obj = ModelClass.objects.get(id=obj_id)
    if model == "user":
        field_value = not (field_value)
    setattr(obj, archive_field, field_value)
    if model == "invoice":
        for time_entry in obj.times.all():
            setattr(time_entry, archive_field, field_value)
            time_entry.save()

    if obj:
        obj.save()
    return HttpResponseRedirect(request.headers.get("Referer"))


archived_annotation = Case(
    When(is_active=False, then=Value(True)),
    default=Value(False),
    output_field=BooleanField(),
)


def redirect_admin_to_about_book(request):
    return redirect("/about/#book")


class BaseView:
    model = None
    model_name = None
    model_name_plural = None
    url_cancel = None
    url_copy = None
    url_create = None
    url_delete = None
    url_edit = None
    url_index = None
    url_view = None
    order_by = ["archived", "-created"]
    paginated = False
    page_number = 1
    # per_page = settings.PER_PAGE
    queryset_related = []
    has_related = False
    has_preview = False
    search = False
    dashboard = False
    exclude = ["contacts"]

    def get_archived(self, obj):
        try:
            return obj.archived
        except:  # noqa
            return not obj.is_active

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.model_name:
            context["model_name"] = self.model_name
            context[f"{self.model_name}_nav"] = True

        if self.model_name_plural:
            context["model_name_plural"] = self.model_name_plural

        context["statcards"] = {}
        context["statcard"] = self.get_statcards()
        context["urls"] = self.get_urls()

        # per_page = self.request.GET.get("items_per_page", settings.PER_PAGE)
        per_page = self.request.GET.get("items_per_page", 10)
        per_page = int(per_page)
        self.per_page = per_page
        context["items_per_page"] = self.per_page

        page_number = self.request.GET.get("page", 1)
        page_number = int(page_number)
        self.page_number = page_number
        context["page_number"] = self.page_number

        paginated = self.request.GET.get("paginated", "true")
        paginated = False if paginated.lower() == "false" else True
        self.paginated = paginated
        context["paginated"] = self.paginated

        queryset = self.get_queryset()
        if queryset and not self.search:
            queryset = queryset.order_by(*self.order_by)

        related = False
        if self.has_related:
            if len(self.queryset_related) > 0:
                context["has_related"] = True
                queryset = self.queryset_related
                related = True

        if self.has_preview:
            context["has_preview"] = True

        paginator = Paginator(queryset, per_page)
        if self.paginated:
            page_obj = paginator.get_page(page_number)
        else:
            page_obj = queryset
        context["page_obj"] = page_obj

        field_values_page = []

        if hasattr(self, "form_class"):
            field_values_page = self.get_field_values(page_obj, related=related)
            context["field_values_page"] = field_values_page

        if hasattr(self, "object") and hasattr(self, "form_class"):
            context["field_values"] = self.get_field_values()

        if hasattr(self, "object") and self.model:
            context["page_obj_detail_view"] = self.get_page_obj_detail_view()

        if self.search:
            context["search"] = self.search
            field_values_page = self.get_field_values(page_obj, search=True)
            if len(field_values_page) > 0:
                context["search_results"] = True
            else:
                context["search_results"] = False
            context["field_values_page"] = field_values_page

        if field_values_page:
            # Table headers via first row
            table_headers = [i[0] for i in field_values_page[0]]
            context["table_headers"] = table_headers

        return context

    def get_field_values(self, page_obj=None, search=False, related=False):
        if page_obj:
            _ = []
            for item in page_obj:
                field_values = []
                if hasattr(page_obj, "object_list"):
                    if page_obj.object_list[0] is not None:
                        field_values.append(("type", item._meta.model_name))
                        field_values.append(("id", item.id))
                        field_values.append(("archived", self.get_archived(item)))
                        field_values.append(("item", item))
                else:
                    field_values.append(("type", item._meta.model_name))
                    field_values.append(("id", item.id))
                    field_values.append(("archived", self.get_archived(item)))
                    field_values.append(("item", item))
                if hasattr(item, "amount"):
                    field_values.append(("amount", item.amount))
                if hasattr(item, "cost"):
                    field_values.append(("cost", item.cost))
                if hasattr(item, "net"):
                    field_values.append(("net", item.net))
                if hasattr(item, "hours"):
                    field_values.append(("hours", item.hours))
                _.append(field_values)
            return _
        else:
            try:
                object_fields = self.form_class().fields.keys()
                field_values = [
                    (field_name, getattr(self.object, field_name))
                    for field_name in object_fields
                    if field_name not in self.exclude and self.request.user.is_superuser
                ]
            except AttributeError:
                field_values = []
            return field_values

    def get_page_obj_detail_view(self):
        context = {}
        first_object = None
        last_object = None
        next_object = None
        previous_object = None
        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            objects = self.model.objects.filter(user=self.request.user)
        else:
            objects = self.model.objects.all()
        paginator = Paginator(objects, 1)
        page_number = self.request.GET.get("page_number_detail", 1)
        page_number = int(page_number)
        page_obj_detail = paginator.get_page(page_number)
        count = paginator.count
        if page_number:
            current_index = paginator.page(page_number).start_index()
            if current_index < count:
                next_object = objects[current_index]
                last_object = objects[count - 1]
            if current_index > 1:
                previous_object = objects[current_index - 2]
                first_object = objects[0]
        context["next_object"] = next_object
        context["previous_object"] = previous_object
        context["first_object"] = first_object
        context["last_object"] = last_object
        context["count"] = count
        context["page_obj"] = page_obj_detail
        return context

    def get_statcards(self):
        context = {}

        context["times"] = {}
        context["invoices"] = {}

        context["times"]["entered"] = 0
        context["times"]["approved"] = 0
        context["invoices"]["gross"] = 0
        context["invoices"]["cost"] = 0
        context["invoices"]["net"] = 0

        return context

    def get_urls(self):
        context = {}

        context["url_cancel"] = self.url_cancel
        context["url_copy"] = self.url_copy
        context["url_create"] = self.url_create
        context["url_delete"] = self.url_delete
        context["url_edit"] = self.url_edit
        context["url_index"] = self.url_index
        context["url_view"] = self.url_view

        return context


def blog(request):
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


class BaseClientView(BaseView, UserPassesTestMixin):
    model = Client
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = ClientForm
    form_class = ClientForm
    order_by = ["archived", "name"]
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    exclude = [
        "publish",
        "link",
        "company",
        "tags",
        "address",
        "url",
        "description",
    ]

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


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
        self.queryset_related = queryset_related
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


class BaseCompanyView(BaseView, UserPassesTestMixin):
    model = Company
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = CompanyForm
    form_class = CompanyForm
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    exclude = ["client_set", "description", "url"]

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


class CompanyListView(BaseCompanyView, ListView):
    template_name = "index.html"


class CompanyCreateView(BaseCompanyView, CreateView):
    model = Company
    form_model = CompanyForm
    success_url = reverse_lazy("company_view")
    template_name = "edit.html"

    def get_success_url(self):
        return reverse_lazy("company_view", args=[self.object.pk])

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
    model = Company
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
        self.queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)
        return context


class CompanyUpdateView(BaseCompanyView, UpdateView):
    model = Company
    form_model = CompanyForm
    template_name = "edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.client_set.set(form.cleaned_data["client_set"])
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs["pk"]
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("company_view", args=[self.object.pk])


class CompanyDeleteView(BaseCompanyView, DeleteView):
    model = Company
    form_model = CompanyForm
    success_url = reverse_lazy("company_index")
    template_name = "delete.html"

    def get_queryset(self):
        return Company.objects.all()


class CompanyCopyView(BaseCompanyView, CreateView):
    model = Company
    form_model = CompanyForm
    template_name = "edit.html"

    def get_queryset(self):
        return Company.objects.all()

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


class BaseContactView(BaseView, UserPassesTestMixin):
    model = Contact
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = ContactForm
    form_class = ContactForm
    template_name = "edit.html"
    order_by = ["archived", "name"]
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    exclude = ["first_name", "last_name", "url", "number"]

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


class ContactListView(BaseContactView, ListView):
    template_name = "index.html"


class ContactCreateView(BaseContactView, CreateView):
    def get_success_url(self):
        return reverse_lazy("contact_view", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.model_name
        context["model_name"] = model_name
        model_name_plural = self.model._meta.verbose_name_plural
        context["model_name_plural"] = model_name_plural
        context["url_index"] = "%s_index" % model_name
        context["%s_nav" % model_name] = True
        return context


class ContactDetailView(BaseContactView, DetailView):
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        contact = self.get_object()
        notes = contact.notes.all()
        client = contact.client
        queryset_related = [q for q in [notes] if q.exists()]
        if client:
            queryset_related.insert(0, client)
        self.queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)
        return context


class ContactUpdateView(BaseContactView, UpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url_cancel"] = f"{self.model_name}_view"
        context["pk"] = self.kwargs["pk"]
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("contact_view", args=[self.object.pk])


class ContactDeleteView(BaseContactView, DeleteView):
    success_url = reverse_lazy("contact_index")
    template_name = "delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return Contact.objects.all()


class ContactCopyView(BaseContactView, CreateView):
    success_url = reverse_lazy("contact_index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.model._meta.model_name
        context["model_name"] = model_name
        context["%s_nav" % model_name] = True
        return context

    def get_queryset(self):
        return Contact.objects.all()

    def form_valid(self, form):
        original_contact = Contact.objects.get(pk=self.kwargs["pk"])
        new_contact = original_contact
        new_contact.save()
        return super().form_valid(form)


def get_queryset(model_class, filter_by=None, order_by=None):
    _ = {}

    queryset = model_class.objects.all()

    if filter_by:
        queryset = queryset.filter(**filter_by)

    if order_by:
        queryset = queryset.order_by(*order_by)

    _["queryset"] = queryset

    return _


class DashboardView(BaseView, UserPassesTestMixin, ListView):
    template_name = "dashboard/index.html"
    dashboard = True

    def get_queryset(self):
        return []

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
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


class BaseInvoiceView(BaseView, UserPassesTestMixin):
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

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied

    @staticmethod
    def generate_docx(html_content, title):
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
        subject = None
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
        self.queryset_related = queryset_related
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
                    from_email=User,
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
                from_email=User,
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
    pass
    # def get(self, request, *args, **kwargs):
    #     fake = Faker()
    #     fake_data = {"paragraph": [fake.paragraph() for i in range(2)]}
    #     return JsonResponse(fake_data)


@login_required
def lounge(request):
    context = {}
    context["lounge_nav"] = True
    return render(request, "lounge.html", context)


class BaseNoteView(BaseView, UserPassesTestMixin):
    model = Note
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = NoteForm
    form_class = NoteForm
    template_name = "edit.html"
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    exclude = ["html"]

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


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
        original_note = Note.objects.get(pk=self.kwargs["pk"])
        new_note = original_note
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
                except:  # noqa
                    failures.append(contact.email)
                else:
                    successes.append(contact.email)
        else:
            try:
                email.send()
            except:  # noqa
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


class BaseProjectView(BaseView, UserPassesTestMixin):
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

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            return False


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
        self.queryset_related = queryset_related
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


locale.setlocale(locale.LC_ALL, "")


def get_queryset_related(self):
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


class BaseReportView(BaseView, UserPassesTestMixin):
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

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied

    def get_context_data(self, **kwargs):
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

        self.queryset_related = queryset_related
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


class SearchView(UserPassesTestMixin, BaseView, ListView):
    search = True
    template_name = "search.html"
    url_index = "search_index"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q")
        context["q"] = query
        return context

    def get_queryset(self):
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


def update_selected_entries(request):
    if request.method == "POST":
        model_name = request.POST.get("model_name")
        action = request.POST.get("action")

        if not model_name:
            messages.error(request, "Invalid model selected.")
            return HttpResponseRedirect(reverse("dashboard"))

        if model_name == "user":
            from django.contrib.auth.models import User as ModelClass
        else:
            ModelClass = apps.get_model(
                app_label="db", model_name=model_name.capitalize()
            )

        entry_ids = request.POST.getlist("entry_id")
        if not entry_ids:
            messages.error(request, "No entries selected.")
            return HttpResponseRedirect(reverse(f"{model_name}_index"))

        try:
            entries = ModelClass.objects.filter(pk__in=entry_ids)
        except ModelClass.DoesNotExist:
            messages.error(request, f"Selected {model_name} entries not found.")
            return HttpResponseRedirect(reverse(f"{model_name}_index"))

        if action == "delete":
            deleted_entries = entries.delete()
            if len(deleted_entries) > 0:
                if deleted_entries[0]:
                    if model_name == "report":
                        message = f"Successfully deleted {deleted_entries[1]['db.Report']} {model_name} entries."
                    else:
                        message = f"Successfully deleted {deleted_entries[0]} {model_name} entries."
                    messages.success(request, message)
                else:
                    messages.warning(request, f"No {model_name} entries were deleted.")
            else:
                messages.warning(request, f"No {model_name} entries were deleted.")

        elif action == "archive":
            if model_name == "user":
                entries.update(is_active=False)
            else:
                entries.update(archived=True)
            if model_name == "invoice":
                [i.times.all().update(archived=True) for i in entries]
            messages.success(
                request, f"Successfully archived {len(entry_ids)} {model_name} entries."
            )
        elif action == "unarchive":
            if model_name == "user":
                entries.update(is_active=True)
            else:
                entries.update(archived=False)
            if model_name == "invoice":
                [i.times.all().update(archived=False) for i in entries]
            messages.success(
                request,
                f"Successfully unarchived {len(entry_ids)} {model_name} entries.",
            )
        elif action == "html":
            if model_name == "note":
                entries.update(html=True)
                messages.success(
                    request,
                    f"Successfully HTMLed {len(entry_ids)} {model_name} entries.",
                )
            else:
                messages.error(request, "Invalid action requested.")
        elif action == "unhtml":
            if model_name == "note":
                entries.update(html=False)
                messages.success(
                    request,
                    f"Successfully Un-HTMLed {len(entry_ids)} {model_name} entries.",
                )
            else:
                messages.error(request, "Invalid action requested.")
        elif action == "save":
            [i.save() for i in entries]
            messages.success(
                request,
                f"Successfully saved {len(entry_ids)} {model_name} entries.",
            )
        else:
            messages.error(request, "Invalid action requested.")

    return HttpResponseRedirect(reverse(f"{model_name}_index"))


class BaseTaskView(BaseView, UserPassesTestMixin):
    model = Task
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = TaskForm
    form_class = TaskForm
    template_name = "edit.html"
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    order_by = ["archived", "name", "-created"]

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


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
        self.queryset_related = queryset_related
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


class BaseTimeView(BaseView, UserPassesTestMixin):
    model = Time
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = TimeForm
    form_class = TimeForm
    template_name = "edit.html"
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    exclude = ["client", "project", "task", "invoice"]

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied

    def get_form(self, form_class=None):
        if self.request.user.is_superuser:
            form_class = AdminTimeForm

        form = super().get_form(form_class)

        projects = Project.objects.filter(team__in=[self.request.user], archived=False)

        if not self.request.user.is_superuser:
            invoices = Invoice.objects.filter(project__in=projects, archived=False)
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

        if self.request.user.is_superuser:
            project = projects.first()
            if project:
                form.fields["task"].empty_label = None
                if project.task:
                    form.fields["task"].queryset = Task.objects.filter(
                        project__in=projects,
                    )
                form.fields["project"].empty_label = None
                form.fields["project"].queryset = projects
                form.fields["client"].empty_label = None
                form.fields["client"].queryset = Client.objects.filter(
                    project__in=projects,
                )

        return form


class TimeCreateView(BaseTimeView, CreateView):
    success_url = reverse_lazy("time_view")

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        elif self.request.user.is_authenticated:
            return True
        else:
            return False

    def get_success_url(self):
        return reverse_lazy("time_view", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = None
        description = None
        project_id = None
        task_id = None

        context["form"].initial = {
            "description": description,
            "user": self.request.user.id,
        }

        invoice_id = self.request.GET.get("invoice_id")

        try:
            invoice = Invoice.objects.get(pk=invoice_id)
        except (ValueError, Invoice.DoesNotExist):
            invoice = None

        if invoice:
            if invoice.client:
                client_id = invoice.client.id
            if invoice.project:
                project_id = invoice.project.id

                if invoice.project.task:
                    task_id = invoice.project.task.id

        context["form"].initial.update(
            {
                "client": client_id,
                "invoice": invoice_id,
                "project": project_id,
                "task": task_id,
            }
        )
        return context


class TimeListView(BaseTimeView, ListView):
    template_name = "index.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        elif self.request.user.is_authenticated:
            return True
        else:
            return False


class TimeDetailView(BaseTimeView, DetailView):
    template_name = "view.html"

    def test_func(self):
        time_entry = self.get_object()
        time_user = time_entry.user
        if self.request.user.is_superuser:
            return True
        elif self.request.user.is_authenticated and self.request.user == time_user:
            return True
        else:
            return False

    def get_context_data(self, **kwargs):
        time = self.get_object()
        if time.invoice:
            queryset_related = list(chain([time.invoice]))
            self.queryset_related = queryset_related
            self.has_related = True
        context = super().get_context_data(**kwargs)
        return context


class TimeUpdateView(BaseTimeView, UpdateView):
    success_url = reverse_lazy("time_view")

    def form_valid(self, form):
        user_id = form.initial["user"]
        if user_id:
            user = User.objects.get(pk=user_id)
            form.instance.user = user
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        elif self.request.user.is_authenticated:
            return True
        else:
            return False

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("time_view", args=[self.object.pk])


class TimeDeleteView(BaseTimeView, DeleteView):
    success_url = reverse_lazy("time_index")
    template_name = "delete.html"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        elif self.request.user.is_authenticated:
            return True
        else:
            return False

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy("time_index")
        else:
            return reverse_lazy("dashboard")

    def get_queryset(self):
        return Time.objects.all()


class TimeCopyView(BaseTimeView, CreateView):
    success_url = reverse_lazy("time_index")

    def get_success_url(self):
        return reverse_lazy("time_view", args=[self.object.pk])

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        elif self.request.user.is_authenticated:
            return True
        else:
            return False

    def get_queryset(self):
        return Time.objects.all()

    def get_initial(self):
        original_time = Time.objects.get(pk=self.kwargs["pk"])
        return {
            "user": original_time.user,
            "name": original_time.name,
            "hours": original_time.hours,
            "description": original_time.description,
            "date": timezone.now,
            "invoice": original_time.invoice,
            "task": original_time.task,
            "project": original_time.project,
            "client": original_time.client,
        }

    def form_valid(self, form):
        new_time = form.save(commit=False)
        new_time.pk = None
        new_time.save()
        return super().form_valid(form)


class BaseUserView(BaseView):
    model = User
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_class = UserForm
    form_model = UserForm
    order_by = ["-is_active", "username"]
    exclude = ["rate", "mail", "address", "first_name", "last_name"]
    url_cancel = f"{model_name.lower()}_cancel"
    url_create = f"{model_name.lower()}_create"
    url_copy = f"{model_name.lower()}_copy"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"


class BaseUserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


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
        self.queryset_related = queryset_related
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
        try:
            user = User.objects.get(id=user_id)
            contact = Contact(
                first_name=user.first_name, last_name=user.last_name, email=user.email
            )
            contact.save()
            return HttpResponseRedirect(reverse("contact_view", args=[contact.id]))
        except User.DoesNotExist:
            return render("error.html")
