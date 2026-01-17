"""Note-related views."""

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from .base import BaseView, FakeDataMixin, SuperuserRequiredMixin
from ..forms import NoteForm
from ..models import Note


class BaseNoteView(BaseView, SuperuserRequiredMixin):
    """Base view for Note model operations."""

    model = Note
    form_model = NoteForm
    form_class = NoteForm
    template_name = "edit.html"


class NoteListView(BaseNoteView, ListView):
    model = Note
    template_name = "index.html"


class NoteListFullScreen(NoteListView, ListView):
    model = Note
    template_name = "notes/fullscreen.html"


class NoteCreateView(FakeDataMixin, BaseNoteView, CreateView):
    model = Note
    form_model = NoteForm
    success_url = reverse_lazy("note_view")
    fake_data_function = "get_fake_note_data"

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
        context["is_detail_view"] = True
        return context


class NoteUpdateView(BaseNoteView, UpdateView):
    model = Note
    form_model = NoteForm
    success_url = reverse_lazy("note_view")

    def form_valid(self, form):
        # html field is not in the form, so we preserve the existing value
        # The form only has 'text' and 'title' fields (see NoteForm)
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
        new_note = form.save(commit=False)
        new_note.pk = None
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

        successes = []
        failures = []

        try:
            email.send()
        except Exception:
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


class NoteAddToObjectView(FakeDataMixin, BaseNoteView, CreateView):
    """View to add a note to any object via generic foreign key."""

    model = Note
    form_class = NoteForm
    template_name = "note_add_inline.html"
    fake_data_function = "get_fake_note_data"

    def get_initial(self):
        """Pre-populate content_type and object_id from URL parameters."""
        initial = super().get_initial()

        content_type_id = self.request.GET.get("content_type")
        object_id = self.request.GET.get("object_id")

        if content_type_id:
            initial["content_type"] = content_type_id
        if object_id:
            initial["object_id"] = object_id

        return initial

    def form_valid(self, form):
        """Set the user on the note before saving."""
        if not form.instance.user:
            form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect back to the object's detail page."""
        note = self.object
        if note.content_object:
            try:
                return note.content_object.get_absolute_url()
            except AttributeError:
                pass
        return reverse_lazy("note_view", args=[self.object.pk])
