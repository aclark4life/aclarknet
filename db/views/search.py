"""Search views."""

from django.contrib.auth.models import User
from django.db.models import Q
from django.views.generic import ListView

from .base import BaseView, SuperuserRequiredMixin
from ..models import (
    Client,
    Company,
    Contact,
    Invoice,
    Note,
    Project,
    Task,
    Time,
)


SEARCH_MODELS = (
    Client,
    Company,
    Contact,
    Invoice,
    Note,
    Project,
    Task,
    Time,
    User,
)


class SearchView(SuperuserRequiredMixin, BaseView, ListView):
    """Search view for searching across multiple models."""

    search = True
    template_name = "search.html"
    url_index = "search_index"
    dashboard = True

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
