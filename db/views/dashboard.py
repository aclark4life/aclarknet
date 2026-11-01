import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import F, Q, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.utils import timezone
from django.views.generic import ListView

from .base import BaseView
from ..models import Client, Invoice, Note, Time

User = get_user_model()


class DashboardView(BaseView, UserPassesTestMixin, ListView):
    """Dashboard view for authenticated users."""

    template_name = "dashboard/index.html"
    dashboard = True

    def get_queryset(self):
        """Return empty queryset as data is added in context."""
        return []

    def test_func(self):
        """Test if user is authenticated."""
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        """Redirect to login if not authenticated."""
        return HttpResponseRedirect(reverse("account_login"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["overview_nav"] = True

        def get_base_queryset(model):
            return model.objects.all()

        # Filter times by user - non-superusers only see their own time entries
        # Exclude time entries from paid invoices (where balance = 0)
        times_queryset = (
            get_base_queryset(Time)
            .order_by("-date")
            .filter(Q(invoice__isnull=True) | Q(invoice__balance__gt=0))
        )
        if not self.request.user.is_superuser:
            times_queryset = times_queryset.filter(user=self.request.user)

        # Get recent invoices ordered by issue date (newest first), limit to 10
        invoices_queryset = get_base_queryset(Invoice).order_by("-issue_date")[:10]

        context.update(
            {
                "invoices": invoices_queryset,
                "times": times_queryset,
            }
        )

        times = context["times"]
        entered = times.aggregate(total=Sum(F("hours")))["total"] or 0
        approved = (
            times.filter(invoice__isnull=False).aggregate(total=Sum(F("hours")))[
                "total"
            ]
            or 0
        )

        def invoice_totals(queryset):
            totals = queryset.aggregate(
                gross=Sum("amount"), cost=Sum("cost"), net=Sum("net")
            )
            return {key: value or 0 for key, value in totals.items()}

        cumulative = invoice_totals(get_base_queryset(Invoice))
        gross, cost, net = cumulative["gross"], cumulative["cost"], cumulative["net"]

        today = timezone.localdate()
        month_start = today.replace(day=1)
        next_month_start = (month_start + timezone.timedelta(days=32)).replace(day=1)
        # Monthly: unpaid invoices issued since the start of last month.
        last_month_start = (month_start - timezone.timedelta(days=1)).replace(day=1)
        monthly = invoice_totals(
            get_base_queryset(Invoice).filter(
                balance__gt=0, issue_date__gte=last_month_start
            )
        )

        # Sparkline trend for the cumulative row: running invoice totals over
        # the last 12 months.
        months = [month_start]
        for _ in range(11):
            months.insert(0, (months[0] - timezone.timedelta(days=1)).replace(day=1))
        monthly_trend = {key: [0.0] * len(months) for key in ("gross", "cost", "net")}
        index = {month: i for i, month in enumerate(months)}
        window = get_base_queryset(Invoice).filter(
            issue_date__gte=months[0], issue_date__lt=next_month_start
        )
        for issue_date, amount, invoice_cost, invoice_net in window.values_list(
            "issue_date", "amount", "cost", "net"
        ):
            i = index[issue_date.replace(day=1)]
            monthly_trend["gross"][i] += float(amount or 0)
            monthly_trend["cost"][i] += float(invoice_cost or 0)
            monthly_trend["net"][i] += float(invoice_net or 0)

        baseline = invoice_totals(
            get_base_queryset(Invoice).filter(issue_date__lt=months[0])
        )
        cumulative_trend = {}
        for key, values in monthly_trend.items():
            running = float(baseline[key])
            cumulative_trend[key] = []
            for value in values:
                running += value
                cumulative_trend[key].append(running)

        trend_labels = json.dumps([month.strftime("%b %Y") for month in months])

        def sparklines(trend):
            return {key: json.dumps([values]) for key, values in trend.items()}

        context.update(
            {
                "statcard": {
                    "times": {
                        "entered": entered,
                        "approved": approved,
                    }
                },
                "statcards": {
                    "dashboard": {
                        "label": "Cumulative",
                        "invoices": cumulative,
                        "sparklines": sparklines(cumulative_trend),
                        "sparkline_labels": trend_labels,
                    },
                    "monthly": {
                        "label": f"{last_month_start:%B %Y}",
                        "invoices": monthly,
                    },
                },
                "dataset_times": [int(entered), int(approved)],
                "dataset_invoices": [int(gross), int(cost), int(net)],
                "dashboard": self.dashboard,
            }
        )

        return context


class AnalyticsView(BaseView, UserPassesTestMixin, ListView):
    """Internal analytics dashboard: a few app-tracked stats plus a link
    out to Google Analytics for full traffic reporting."""

    template_name = "dashboard/analytics.html"
    dashboard = True

    def get_queryset(self):
        """Return empty queryset as data is added in context."""
        return []

    def test_func(self):
        """Only superusers may view analytics."""
        return self.request.user.is_superuser

    def handle_no_permission(self):
        """Redirect to login if not authenticated/authorized."""
        return HttpResponseRedirect(reverse("account_login"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["overview_nav"] = True
        context["analytics_nav"] = True
        context["dashboard"] = self.dashboard

        try:
            from blog.models import Entry
        except ImportError:  # pragma: no cover - blog app always installed
            Entry = None

        now = timezone.now()
        since_datetime = now - timezone.timedelta(days=30)
        since_date = now.date() - timezone.timedelta(days=30)

        contact_submissions = Note.objects.filter(
            name__startswith="Contact form submission"
        )
        testimonials = Note.objects.filter(is_testimonial=True)
        entries = Entry.objects.filter(status=Entry.PUBLISHED) if Entry else None

        context["analytics"] = {
            "contacts": {
                "total": contact_submissions.count(),
                "last_30_days": contact_submissions.filter(
                    created__gte=since_datetime
                ).count(),
            },
            "testimonials": {
                "total": testimonials.count(),
                "featured": testimonials.filter(is_featured=True).count(),
            },
            "clients": {
                "total": Client.objects.count(),
                "featured": Client.objects.filter(featured=True).count(),
            },
            "blog": {
                "published": entries.count() if entries is not None else 0,
                "last_30_days": (
                    entries.filter(pub_date__gte=since_date).count()
                    if entries is not None
                    else 0
                ),
            },
        }

        context["ga_measurement_id"] = getattr(settings, "GA_MEASUREMENT_ID", "")
        context["ga_dashboard_url"] = getattr(
            settings,
            "GA_DASHBOARD_URL",
            "https://analytics.google.com/analytics/web/",
        )

        return context


def display_mode(request):
    mode = request.GET.get("display-mode", "dark")
    profile = request.user.profile
    profile.dark = mode == "dark"
    profile.save()
    return HttpResponseRedirect(request.headers.get("Referer"))


@login_required
def lounge(request):
    context = {"lounge_nav": True}
    return render(request, "lounge.html", context)
