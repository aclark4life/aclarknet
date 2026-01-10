"""User-related views."""

from itertools import chain

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import F, Sum
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

from .base import BaseView, SuperuserRequiredMixin
from ..forms import UserForm
from ..models import Invoice, Project, Time


class BaseUserView(BaseView):
    """Base view for User model operations."""

    model = User
    form_class = UserForm
    form_model = UserForm


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
        self._queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)

        times = Time.objects.filter(user=user)
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
        context["is_detail_view"] = True

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
        # is_active is already handled by the form, no need to manually set it
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
