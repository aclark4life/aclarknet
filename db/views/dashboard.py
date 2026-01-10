"""Dashboard and utility views."""

from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, reverse
from django.views.generic import ListView

from .base import BaseView
from django.contrib.auth.mixins import UserPassesTestMixin
from ..models import (
    Client,
    Company,
    Contact,
    Invoice,
    Note,
    Project,
    Report,
    Task,
    Time,
)


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

        context = super().get_context_data(**kwargs)
        context["overview_nav"] = True

        # 1. Define the common filtering logic once
        user = self.request.user
        is_admin = user.is_superuser

        # 2. Helper to get a filtered queryset based on user status
        def get_base(model):
            if is_admin:
                return model.objects.filter(archived=False)
            return model.objects.filter(archived=False, user=user)

        # 3. Assign context variables using native Django chaining
        invoices = get_base(Invoice)
        context["invoices"] = invoices
        context["companies"] = get_base(Company).order_by("name")
        context["projects"] = get_base(Project).order_by("name")
        context["notes"] = get_base(Note).order_by("-created")
        context["tasks"] = get_base(Task).order_by("name")
        context["contacts"] = get_base(Contact).order_by("last_name")
        context["clients"] = get_base(Client).order_by("name")
        context["reports"] = get_base(Report).order_by("-created")

        # Handle specific ordering for 'times'
        times = get_base(Time).order_by("-archived", "-date")
        context["times"] = times

        entered = times.aggregate(total=Sum(F("hours")))
        approved = times.filter(invoice__isnull=False).aggregate(total=Sum(F("hours")))

        context["statcard"]["times"]["entered"] = entered
        context["statcard"]["times"]["approved"] = approved

        entered = entered["total"] or 0
        approved = approved["total"] or 0

        gross = invoices.aggregate(amount=Sum(F("amount")))["amount"]
        cost = invoices.aggregate(cost=Sum(F("cost")))["cost"]
        net = invoices.aggregate(net=Sum(F("net")))["net"]

        gross = gross or 0
        cost = cost or 0
        net = net or 0

        context["statcards"] = {}
        context["statcards"]["dashboard"] = {}
        context["statcards"]["dashboard"]["invoices"] = {}
        context["statcards"]["dashboard"]["invoices"]["gross"] = gross
        context["statcards"]["dashboard"]["invoices"]["cost"] = cost
        context["statcards"]["dashboard"]["invoices"]["net"] = net

        context["dataset_times"] = [int(entered), int(approved)]
        context["dataset_invoices"] = [int(gross), int(cost), int(net)]
        context["dashboard"] = self.dashboard

        return context


def display_mode(request):
    mode = request.GET.get("display-mode", "dark")
    if mode == "light":
        request.user.profile.dark = False
        request.user.profile.save()
    elif mode == "dark":
        request.user.profile.dark = True
        request.user.profile.save()
    return HttpResponseRedirect(request.headers.get("Referer"))


def save_positions(request):
    if request.method == "POST":
        profile = request.user.profile
        positions = request.POST.get("positions")
        profile.draggable_positions = positions
        profile.save()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})


def html_mode(request):
    from django.apps import apps
    from django.shortcuts import get_object_or_404

    html = request.GET.get("html", "true")
    model = request.GET.get("model")
    obj_id = request.GET.get("id")
    html = False if html.lower() == "false" else True
    ModelClass = apps.get_model(app_label="db", model_name=model.capitalize())
    obj = get_object_or_404(ModelClass, pk=obj_id)
    if html:
        obj.html = True
    else:
        obj.html = False
    obj.save()
    return HttpResponseRedirect(request.headers.get("Referer"))


@login_required
def lounge(request):
    context = {}
    context["lounge_nav"] = True
    return render(request, "lounge.html", context)


class FakeTextView(ListView):
    """
    Placeholder view for generating fake text data.

    Currently unimplemented. When implemented, this view will use Faker
    to generate sample paragraph text via JSON response.
    """

    def get(self, request, *args, **kwargs):
        """Return HTTP 501 Not Implemented for now."""
        return JsonResponse(
            {"error": "This feature is not yet implemented."}, status=501
        )
