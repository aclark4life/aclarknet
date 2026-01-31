"""Company-related views."""

from itertools import chain

from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .base import (
    BaseView,
    FakeDataMixin,
    RedirectToObjectViewMixin,
    SuperuserRequiredMixin,
)
from ..forms import CompanyForm
from ..models import Company, Project, Client


class BaseCompanyView(BaseView, SuperuserRequiredMixin):
    """Base view for Company model operations."""

    model = Company
    form_model = CompanyForm
    form_class = CompanyForm
    # Exclude description from title fields so it appears in card text with a label
    related_title_fields = ["name", "title", "subject"]


class CompanyListView(BaseCompanyView, ListView):
    template_name = "index.html"


class CompanyCreateView(
    FakeDataMixin,
    BaseCompanyView,
    RedirectToObjectViewMixin,
    CreateView,
):
    template_name = "edit.html"
    fake_data_function = "get_fake_company_data"

    def form_valid(self, form):
        form.instance.creator = self.request.user
        company = form.save(commit=False)
        company.save()
        # company.client_set.set(form.cleaned_data["client_set"])
        form.save_m2m()
        return super().form_valid(form)


class CompanyDetailView(BaseCompanyView, DetailView):
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        company = self.get_object()
        # clients = company.client_set.all().order_by("name")
        clients = Client.objects.filter(company=company).order_by("name")
        projects = Project.objects.filter(client__in=clients).order_by("name")
        queryset_related = [q for q in [clients, projects] if q.exists()]
        queryset_related = list(chain(*queryset_related))
        self._queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)
        context["is_detail_view"] = True
        return context


class CompanyUpdateView(
    BaseCompanyView,
    RedirectToObjectViewMixin,
    UpdateView,
):
    template_name = "edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        # form.instance.client_set.set(form.cleaned_data["client_set"])
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
