"""Client-related views."""

from itertools import chain, groupby

from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .base import BaseView, FakeDataMixin, GroupedListMixin, SuperuserRequiredMixin
from ..forms import ClientForm
from ..models import Client, Company, Invoice, Project


class BaseClientView(BaseView, SuperuserRequiredMixin):
    """Base view for Client model operations."""

    model = Client
    form_model = ClientForm
    form_class = ClientForm
    # Exclude description from title fields so it appears in card text with a label
    related_title_fields = ["name", "title", "subject"]


class ClientListView(GroupedListMixin, BaseClientView, ListView):
    model = Client
    template_name = "index.html"
    field_values_include = ["name", "category", "featured"]

    def get_groups(self, clients):
        """Clients with a current project first, then by year of their last project."""
        today = timezone.localdate()
        projects = {}
        for project in Project.objects.exclude(client=None):
            projects.setdefault(project.client_id, []).append(project)

        current, past, no_projects = [], [], []
        for client in clients:
            client_projects = projects.get(client.pk)
            if not client_projects:
                no_projects.append(client)
            elif any(p.is_current(today) for p in client_projects):
                current.append(client)
            else:
                last = max(p.last_date for p in client_projects)
                past.append((last, client))

        groups = [("Current", current, True)]
        past.sort(key=lambda lc: lc[0], reverse=True)
        for year, items in groupby(past, key=lambda lc: lc[0].year):
            groups.append((str(year), [client for _, client in items], False))
        groups.append(("No projects", no_projects, False))
        return groups


class ClientCreateView(FakeDataMixin, BaseClientView, CreateView):
    template_name = "edit.html"
    fake_data_function = "get_fake_client_data"

    def get_success_url(self):
        return reverse_lazy("client_view", args=[self.object.pk])

    def get_initial(self):
        initial = super().get_initial()
        companies = Company.objects.all()
        if companies:
            company = companies.first()
            initial["company"] = company
        return initial

    def form_valid(self, form):
        company_id = self.request.GET.get("company_id")
        obj = form.save()
        if company_id:
            company = Company.objects.get(pk=company_id)
            obj.company = company
            obj.save()
            return HttpResponseRedirect(reverse("company_view", args=[company_id]))
        return super().form_valid(form)


class ClientDetailView(BaseClientView, DetailView):
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        client = self.get_object()
        projects = client.projects.all()
        company = client.company
        invoices = Invoice.objects.filter(project__in=projects)
        invoices = invoices.order_by("-created")
        queryset_related = [q for q in [projects, invoices] if q.exists()]
        if company:
            queryset_related.insert(0, [company])
        queryset_related = list(chain(*queryset_related))
        self._queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)
        context["is_detail_view"] = True
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
    # BaseClientView sets form_class = ClientForm for edit/create, but
    # DeleteView only needs a confirmation POST with no fields (see
    # InvoiceDeleteView for the bug this avoids).
    form_class = forms.Form

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
