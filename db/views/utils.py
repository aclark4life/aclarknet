"""Utility functions and views for the db app."""

from django.apps import apps
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, reverse

from ..utils import get_model_class


def archive(request):
    """
    Archive or unarchive an object.

    Handles archiving for both db models and users.
    For invoices, also archives associated time entries.
    """
    archive = request.GET.get("archive", "true")
    model = request.GET.get("model")
    obj_id = request.GET.get("id")
    obj = None
    if model == "user":
        ModelClass = get_model_class("User", app_label="siteuser")
        archive_field = "is_active"
    else:
        ModelClass = get_model_class(model)
        archive_field = "archived"
    field_value = False if archive == "false" else True
    obj = get_object_or_404(ModelClass, id=obj_id)
    if model == "user":
        field_value = not (field_value)
    setattr(obj, archive_field, field_value)
    if model == "invoice":
        for time_entry in obj.times.all():
            setattr(time_entry, archive_field, field_value)
            time_entry.save()

    obj.save()
    return HttpResponseRedirect(request.headers.get("Referer"))


def get_model_config(model_name):
    """
    Returns configuration for allowed models to prevent arbitrary access.
    Maps string names to Model Class and specific field settings.
    Includes has_user_field to indicate if the model should be filtered by user.
    """
    from django.contrib.auth.models import User
    
    # Configuration map: 'slug': {'model': Class, 'archive_field': 'field_name', 'has_user_field': bool}
    config = {
        "user": {
            "model": User,
            "archive_field": "is_active",
            "active_val": True,
            "has_user_field": False,
        },
        "report": {
            "model": apps.get_model("db", "Report"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": True,
        },
        "invoice": {
            "model": apps.get_model("db", "Invoice"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": True,
        },
        "note": {
            "model": apps.get_model("db", "Note"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": True,
        },
        "time": {
            "model": apps.get_model("db", "Time"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": True,
        },
        "task": {
            "model": apps.get_model("db", "Task"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": False,
        },
        "client": {
            "model": apps.get_model("db", "Client"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": False,
        },
        "company": {
            "model": apps.get_model("db", "Company"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": False,
        },
        "contact": {
            "model": apps.get_model("db", "Contact"),
            "archive_field": "archived",
            "active_val": False,
            "has_user_field": False,
        },
        "project": {
            "model": apps.get_model("db", "Project"),
            "archive_field": "archived",
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

        elif action == "archive":
            target_field = model_conf["archive_field"]
            target_value = not model_conf[
                "active_val"
            ]  # e.g., is_active=False or archived=True

            entries.update(**{target_field: target_value})

            # Handle Invoice specific relationship update
            if model_name == "invoice":
                # Optimization: Update related items in one query rather than looping
                # Assuming 'times' is the related_name for a TimeEntry model
                for invoice in entries:
                    invoice.times.all().update(archived=True)

            messages.success(
                request, f"Successfully archived {count} {model_name} entries."
            )

        elif action == "unarchive":
            target_field = model_conf["archive_field"]
            target_value = model_conf[
                "active_val"
            ]  # e.g., is_active=True or archived=False

            entries.update(**{target_field: target_value})

            if model_name == "invoice":
                for invoice in entries:
                    invoice.times.all().update(archived=False)

            messages.success(
                request, f"Successfully unarchived {count} {model_name} entries."
            )

        elif action == "save":
            # Iterate to trigger save() signals (bulk_update does not trigger signals)
            for entry in entries:
                entry.save()
            messages.success(
                request, f"Successfully saved {count} {model_name} entries."
            )

        else:
            messages.error(request, "Invalid action requested.")

    except Exception as e:
        # Catch unexpected DB errors
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(reverse(f"{model_name}_index"))


def update_related_entries(request):
    """
    Update multiple related entries (archive, delete, save, etc.).

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
                ModelClass = apps.get_model(app_label="auth", model_name="User")
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
            elif action == "archive":
                if model_name == "user":
                    entry.is_active = False
                else:
                    entry.archived = True
                entry.save()
                summary_message += (
                    f"Successfully archived {model_name} entry: {entry_id}\n"
                )
            elif action == "unarchive":
                if model_name == "user":
                    entry.is_active = True
                else:
                    entry.archived = False
                entry.save()
                summary_message += (
                    f"Successfully unarchived {model_name} entry: {entry_id}\n"
                )
            elif action == "save":
                try:
                    entry.save()
                    summary_message += (
                        f"Successfully saved {model_name} entry: {entry_id}\n"
                    )
                except Exception as e:
                    messages.error(
                        request,
                        f"Failed to save {model_name} entry {entry_id}: {str(e)}",
                    )
            else:
                messages.error(request, "Invalid action requested.")

        if summary_message:
            messages.success(request, summary_message)

    return HttpResponseRedirect(request.headers.get("Referer"))
