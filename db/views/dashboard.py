from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import F, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views.generic import ListView

from .base import BaseView
from ..models import Client, Company, Invoice, Note, Project, Report, Task, Time

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

        user = self.request.user
        is_admin = user.is_superuser

        def get_base_queryset(model):
            """Helper to get a filtered queryset based on user status."""
            if is_admin:
                return model.objects.filter(archived=False)
            return model.objects.filter(archived=False, user=user)

        context.update(
            {
                "invoices": get_base_queryset(Invoice),
                "companies": get_base_queryset(Company).order_by("name"),
                "projects": get_base_queryset(Project).order_by("name"),
                "notes": get_base_queryset(Note).order_by("-created"),
                "tasks": get_base_queryset(Task).order_by("name"),
                "clients": get_base_queryset(Client).order_by("name"),
                "reports": get_base_queryset(Report).order_by("-created"),
                "times": get_base_queryset(Time).order_by("-archived", "-date"),
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
