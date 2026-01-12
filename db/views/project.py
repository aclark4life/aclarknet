"""Project-related views."""

from itertools import chain

from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .base import BaseView, FakeDataMixin, SuperuserRequiredMixin
from ..forms import ProjectForm
from ..models import Client, Invoice, Project


class BaseProjectView(BaseView, SuperuserRequiredMixin):
    """Base view for Project model operations."""

    model = Project
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = ProjectForm
    form_class = ProjectForm
    template_name = "edit.html"
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"


class ProjectListView(BaseProjectView, ListView):
    model = Project
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url_create"] = "%s_create" % self.model_name
        context["url_view"] = "%s_view" % self.model_name
        return context


class ProjectCreateView(FakeDataMixin, BaseProjectView, CreateView):
    model = Project
    form_model = ProjectForm
    success_url = reverse_lazy("project_view")
    fake_data_function = "get_fake_project_data"

    def get_success_url(self):
        client_id = self.request.GET.get("client_id")
        if client_id:
            return reverse_lazy("client_view", args=[client_id])
        else:
            return reverse_lazy("project_view", args=[self.object.pk])

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     now = timezone.now()
    #     client = None
    #     client_id = self.request.GET.get("client_id")
    #     if client_id:
    #         client = Client.objects.get(id=client_id)
    #     context["form"].initial = {
    #         "start_date": now,
    #         "end_date": now + timezone.timedelta(days=366),
    #         "client": client,
    #     }
    #     return context

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
        client = project.client
        company = None
        if client:
            company = client.company
        invoices = Invoice.objects.filter(project=project).order_by("-created")
        queryset_related = [q for q in [notes, invoices] if q.exists()]
        queryset_related = list(chain(*queryset_related))
        if company:
            queryset_related.insert(0, company)
        if client:
            queryset_related.insert(0, client)
        self._queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)
        context["is_detail_view"] = True
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
