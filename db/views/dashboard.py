from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import F, Q, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views.generic import ListView

from .base import BaseView
from ..models import Invoice, Time

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

        gross = (
            get_base_queryset(Invoice).aggregate(amount=Sum(F("amount")))["amount"] or 0
        )
        cost = get_base_queryset(Invoice).aggregate(cost=Sum(F("cost")))["cost"] or 0
        net = get_base_queryset(Invoice).aggregate(net=Sum(F("net")))["net"] or 0

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
                        "invoices": {
                            "gross": gross,
                            "cost": cost,
                            "net": net,
                        }
                    }
                },
                "dataset_times": [int(entered), int(approved)],
                "dataset_invoices": [int(gross), int(cost), int(net)],
                "dashboard": self.dashboard,
            }
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
