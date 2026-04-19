from django.shortcuts import get_object_or_404
from django.views.generic import ListView, TemplateView

from .models import Entry


class EntryListView(ListView):
    model = Entry
    template_name = "blog/entry_list.html"
    context_object_name = "entries"
    paginate_by = 20

    def get_queryset(self):
        return Entry.objects.only("title", "slug", "pub_date", "tags", "source")


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
        context["entry"] = get_object_or_404(
            Entry, pub_date=pub_date, slug=self.kwargs["slug"]
        )
        return context
