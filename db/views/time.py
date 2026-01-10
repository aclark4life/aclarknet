"""Time-related views."""

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
    FilterByUserMixin,
    ModelCopyMixin,
    RedirectToObjectViewMixin,
)
from ..forms import TimeForm
from ..models import Time, Invoice


class BaseTimeView(BaseView, AuthenticatedRequiredMixin):
    """Base view for Time model operations."""

    model = Time
    form_model = TimeForm
    form_class = TimeForm
    template_name = "edit.html"


class TimeCreateView(
    BaseTimeView,
    RedirectToObjectViewMixin,
    CreateView,
):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice_id = self.request.GET.get("invoice_id")
        if invoice_id:
            context["form"].initial = {
                "invoice": invoice_id,
            }
        return context

    def form_valid(self, form):
        invoice_id = self.request.GET.get("invoice_id")
        obj = form.save()
        if invoice_id:
            invoice = Invoice.objects.get(pk=invoice_id)
            invoice.times.add(obj)
            return HttpResponseRedirect(reverse("invoice_view", args=[invoice_id]))
        return super().form_valid(form)


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
        context = super().get_context_data(**kwargs)
        context["is_detail_view"] = True
        return context


class TimeUpdateView(
    BaseTimeView,
    RedirectToObjectViewMixin,
    UpdateView,
):
    def form_valid(self, form):
        # User field should already be on the instance or in cleaned_data
        # No need to manually set it from initial values
        return super().form_valid(form)


class TimeCopyView(
    BaseTimeView,
    ModelCopyMixin,
    RedirectToObjectViewMixin,
    CreateView,
):
    pass


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
