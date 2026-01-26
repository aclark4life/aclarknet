"""Time-related views."""

from itertools import chain

from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .base import (
    AuthenticatedRequiredMixin,
    BaseView,
    FakeDataMixin,
    FilterByUserMixin,
    ModelCopyMixin,
    RedirectToObjectViewMixin,
)
from ..forms import TimeForm
from ..models import Time, Invoice, Task


class BaseTimeView(BaseView, AuthenticatedRequiredMixin):
    """Base view for Time model operations."""

    model = Time
    form_model = TimeForm
    form_class = TimeForm
    template_name = "edit.html"
    field_values_exclude = [
        "invoice",
        "name",
        "project",
        "task",
    ]
    # Override related_title_fields to exclude description
    # This allows description to appear in the card text with a label
    related_title_fields = ["name", "title", "subject"]


class TimeCreateView(
    FakeDataMixin,
    BaseTimeView,
    RedirectToObjectViewMixin,
    CreateView,
):
    fake_data_function = "get_fake_time_data"

    def get_form_kwargs(self):
        """Pass the user to the form."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self):
        """Set initial values for the form."""
        initial = super().get_initial()
        # Set the user to the logged-in user by default
        initial["user"] = self.request.user
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice_id = self.request.GET.get("invoice_id")
        if invoice_id:
            if "form" in context and hasattr(context["form"], "initial"):
                # Only set invoice initial if field exists (admin users)
                if "invoice" in context["form"].fields:
                    context["form"].initial["invoice"] = invoice_id

        # Only set default task if user is admin and task field is available
        if (
            self.request.user.is_superuser
            and "form" in context
            and "task" in context["form"].fields
        ):
            default_task = Task.get_default_task()
            context["form"].initial["task"] = default_task
        return context

    def form_valid(self, form):
        invoice_id = self.request.GET.get("invoice_id")
        obj = form.save(commit=False)
        # Always assign the logged-in user to new time entries
        obj.user = self.request.user
        obj.save()
        if invoice_id:
            invoice = Invoice.objects.get(pk=invoice_id)
            invoice.times.add(obj)
            return HttpResponseRedirect(reverse("invoice_view", args=[invoice_id]))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("time_index")


class TimeListView(
    BaseTimeView,
    FilterByUserMixin,
    ListView,
):
    template_name = "index.html"


class TimeDetailView(BaseTimeView, DetailView):
    template_name = "view.html"

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        time = self.get_object()
        return self.request.user.is_superuser or self.request.user == time.user

    def get_context_data(self, **kwargs):
        time = self.get_object()
        queryset_related = []

        # Add invoice if exists
        if time.invoice:
            queryset_related.append([time.invoice])

        # Add project if exists
        if time.project:
            queryset_related.append([time.project])

            # Add client through project if exists
            if time.project.client:
                queryset_related.append([time.project.client])

                # Add company through client if exists
                if time.project.client.company:
                    queryset_related.append([time.project.client.company])

        # Flatten the list and set as related queryset
        if queryset_related:
            self._queryset_related = list(chain(*queryset_related))
            self.has_related = True

        context = super().get_context_data(**kwargs)
        context["is_detail_view"] = True
        return context


class TimeUpdateView(
    BaseTimeView,
    RedirectToObjectViewMixin,
    UpdateView,
):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        time = self.get_object()
        return self.request.user.is_superuser or self.request.user == time.user

    def get_form_kwargs(self):
        """Pass the user to the form."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Preserve the original user - the user field may not be in the form for non-admins
        # Get the instance before saving to preserve the user field
        obj = form.save(commit=False)
        # If user is not set (likely because it wasn't in the form), use the original value
        if obj.user is None:
            original_obj = self.get_object()
            obj.user = original_obj.user
        obj.save()
        self.object = obj
        return super().form_valid(form)


class TimeCopyView(
    BaseTimeView,
    ModelCopyMixin,
    RedirectToObjectViewMixin,
    CreateView,
):
    def get_form_kwargs(self):
        """Pass the user to the form."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        obj = form.save(commit=False)
        # Always assign the logged-in user to copied time entries
        obj.user = self.request.user
        # Set pk to None to create a new entry (copy behavior)
        obj.pk = None
        obj.save()
        self.object = obj
        return HttpResponseRedirect(self.get_success_url())


class TimeDeleteView(BaseTimeView, FilterByUserMixin, DeleteView):
    template_name = "delete.html"

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        time = self.get_object()
        return self.request.user.is_superuser or self.request.user == time.user

    def get_success_url(self):
        return (
            reverse_lazy("time_index")
            if self.request.user.is_superuser
            else reverse_lazy("dashboard")
        )
