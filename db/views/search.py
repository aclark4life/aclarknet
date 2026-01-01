from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.views.generic.list import ListView

from ..models import Note
from ..models import Client
from ..models import Company
from ..models import Contact
from ..models import Invoice
from ..models import Project
from ..models import Report
from ..models import Task
from ..models import Time
from .base import BaseView

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
