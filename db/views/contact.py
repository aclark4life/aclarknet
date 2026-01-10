"""Contact-related views."""

from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .base import BaseView, RedirectToObjectViewMixin, SuperuserRequiredMixin
from ..forms import ContactForm
from ..models import Contact


class BaseContactView(BaseView, SuperuserRequiredMixin):
    """Base view for Contact model operations."""

    model = Contact
    form_model = ContactForm
    form_class = ContactForm
    template_name = "edit.html"


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
        context["is_detail_view"] = True
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
