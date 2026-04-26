"""Utility functions and views for the db app."""

from django.apps import apps
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import reverse
from django.views.decorators.http import require_GET


def get_model_config(model_name):
    """
    Returns configuration for allowed models to prevent arbitrary access.
    Maps string names to Model Class and specific field settings.
    Includes has_user_field to indicate if the model should be filtered by user.
    """
    User = get_user_model()

    # Configuration map: 'slug': {'model': Class, 'has_user_field': bool}
    config = {
        "user": {
            "model": User,
            "active_val": True,
            "has_user_field": False,
        },
        "invoice": {
            "model": apps.get_model("db", "Invoice"),
            "active_val": False,
            "has_user_field": True,
        },
        "note": {
            "model": apps.get_model("db", "Note"),
            "active_val": False,
            "has_user_field": True,
        },
        "time": {
            "model": apps.get_model("db", "Time"),
            "active_val": False,
            "has_user_field": True,
        },
        "task": {
            "model": apps.get_model("db", "Task"),
            "active_val": False,
            "has_user_field": False,
        },
        "client": {
            "model": apps.get_model("db", "Client"),
            "active_val": False,
            "has_user_field": False,
        },
        "company": {
            "model": apps.get_model("db", "Company"),
            "active_val": False,
            "has_user_field": False,
        },
        "contact": {
            "model": apps.get_model("db", "Contact"),
            "active_val": False,
            "has_user_field": False,
        },
        "project": {
            "model": apps.get_model("db", "Project"),
            "active_val": False,
            "has_user_field": False,
        },
    }
    return config.get(model_name)


@transaction.atomic
def update_selected_entries(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("dashboard"))

    model_name = request.POST.get("model_name")
    action = request.POST.get("action")
    entry_ids = request.POST.getlist("entry_id")

    # 1. Validation and Configuration Lookup
    model_conf = get_model_config(model_name)

    if not model_conf:
        messages.error(request, "Invalid model selected.")
        return HttpResponseRedirect(reverse("dashboard"))

    if not entry_ids:
        messages.error(request, "No entries selected.")
        return HttpResponseRedirect(reverse(f"{model_name}_index"))

    ModelClass = model_conf["model"]

    # 2. Fetch Entries with user filtering applied early
    # Filter returns empty queryset, it does not raise DoesNotExist
    entries = ModelClass.objects.filter(pk__in=entry_ids)

    # Apply user filtering for non-superusers if model has user field
    # This is done early to prevent information leakage about entry existence
    if not request.user.is_superuser and model_conf.get("has_user_field", False):
        entries = entries.filter(user=request.user)

    count = entries.count()

    if count == 0:
        # Provide appropriate message based on whether user filtering was applied
        if not request.user.is_superuser and model_conf.get("has_user_field", False):
            messages.warning(
                request,
                f"No {model_name} entries found that you have permission to modify.",
            )
        else:
            messages.warning(request, f"Selected {model_name} entries not found.")
        return HttpResponseRedirect(reverse(f"{model_name}_index"))

    # 3. Action Dispatcher
    try:
        if action == "delete":
            # delete() returns (total_count, {model_label: count})
            deleted_count, _ = entries.delete()
            if deleted_count > 0:
                messages.success(
                    request,
                    f"Successfully deleted {deleted_count} {model_name} entries.",
                )
            else:
                messages.warning(request, f"No {model_name} entries were deleted.")

        else:
            messages.error(request, "Invalid action requested.")

    except Exception as e:
        # Catch unexpected DB errors
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(reverse(f"{model_name}_index"))


def update_related_entries(request):
    """
    Update multiple related entries (delete, save, etc.).

    Handles bulk operations on database entries from the dashboard.
    """
    if request.method == "POST":
        entry_ids = request.POST.getlist("entry_id")
        if not entry_ids:
            messages.error(request, "No entries selected.")
            return HttpResponseRedirect(reverse("dashboard"))

        summary_message = ""

        for entry_id in entry_ids:
            try:
                model_name, pk = entry_id.split("-")
            except ValueError:
                messages.error(request, "Invalid entry ID format.")
                return HttpResponseRedirect(reverse("dashboard"))

            if model_name == "user":
                ModelClass = get_user_model()
            else:
                try:
                    ModelClass = apps.get_model(
                        app_label="db", model_name=model_name.capitalize()
                    )
                except LookupError:
                    messages.error(request, f"Invalid model name: {model_name}")
                    return HttpResponseRedirect(reverse("dashboard"))

            try:
                entry = ModelClass.objects.get(pk=pk)
            except ModelClass.DoesNotExist:
                messages.error(
                    request, f"{model_name.capitalize()} entry not found: {entry_id}"
                )
                return HttpResponseRedirect(reverse(f"{model_name}_index"))

            action = request.POST.get("action")
            if action == "delete":
                try:
                    entry.delete()
                    summary_message += (
                        f"Successfully deleted {model_name} entry: {entry_id}\n"
                    )
                except Exception as e:
                    messages.error(
                        request,
                        f"Failed to delete {model_name} entry {entry_id}: {str(e)}",
                    )
            else:
                messages.error(request, "Invalid action requested.")

        if summary_message:
            messages.success(request, summary_message)

    return HttpResponseRedirect(request.headers.get("Referer"))


@login_required
@require_GET
def time_api_invoice(request, pk):
    """Return project and default task info for an invoice (used by time form JS)."""
    if not request.user.is_superuser:
        return JsonResponse({"error": "Forbidden"}, status=403)
    Invoice = apps.get_model("db", "Invoice")
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        return JsonResponse({}, status=404)
    data = {
        "project_id": None,
        "project_name": None,
        "default_task_id": None,
        "default_task_name": None,
    }
    if invoice.project:
        data["project_id"] = str(invoice.project.pk)
        data["project_name"] = str(invoice.project)
        if invoice.project.default_task:
            data["default_task_id"] = str(invoice.project.default_task.pk)
            data["default_task_name"] = str(invoice.project.default_task)
    return JsonResponse(data)


@login_required
@require_GET
def time_api_project(request, pk):
    """Return default task info for a project (used by time form JS)."""
    if not request.user.is_superuser:
        return JsonResponse({"error": "Forbidden"}, status=403)
    Project = apps.get_model("db", "Project")
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return JsonResponse({}, status=404)
    data = {"default_task_id": None, "default_task_name": None}
    if project.default_task:
        data["default_task_id"] = str(project.default_task.pk)
        data["default_task_name"] = str(project.default_task)
    return JsonResponse(data)


@login_required
@require_GET
def time_api_task(request, pk):
    """Return project info for a task (used by time form JS)."""
    if not request.user.is_superuser:
        return JsonResponse({"error": "Forbidden"}, status=403)
    Task = apps.get_model("db", "Task")
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return JsonResponse({}, status=404)
    data = {"project_id": None, "project_name": None}
    if task.project:
        data["project_id"] = str(task.project.pk)
        data["project_name"] = str(task.project)
    return JsonResponse(data)
