from django.shortcuts import get_object_or_404
from django.views.generic import ListView, TemplateView

from .models import Entry


class EntryListView(ListView):
    model = Entry
    template_name = "blog/entry_list.html"
    context_object_name = "entries"
    paginate_by = 20

    def get_queryset(self):
        qs = Entry.objects.only(
            "title", "slug", "pub_date", "tags", "source", "body", "status"
        )
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            qs = qs.filter(status=Entry.PUBLISHED)
        return qs

    def get_paginate_by(self, queryset):
        if self.request.GET.get("page") == "all":
            return None
        return self.paginate_by


class EntryDetailView(TemplateView):
    template_name = "blog/entry_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        import datetime

        pub_date = datetime.date(
            int(self.kwargs["year"]),
            int(self.kwargs["month"]),
            int(self.kwargs["day"]),
        )
        entry = get_object_or_404(Entry, pub_date=pub_date, slug=self.kwargs["slug"])
        # Drafts are only visible to staff
        if entry.status == Entry.DRAFT and not (
            self.request.user.is_staff or self.request.user.is_superuser
        ):
            from django.http import Http404

            raise Http404
        context["entry"] = entry
        context["prev_entry"] = (
            Entry.objects.filter(pub_date__lt=entry.pub_date, status=Entry.PUBLISHED)
            .only("title", "slug", "pub_date")
            .first()
        )
        context["next_entry"] = (
            Entry.objects.filter(pub_date__gt=entry.pub_date, status=Entry.PUBLISHED)
            .only("title", "slug", "pub_date")
            .order_by("pub_date")
            .first()
        )
        return context
