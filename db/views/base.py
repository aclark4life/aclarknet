"""Base views, mixins, and error handlers for the db app."""

# Django imports
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import F, Sum
from django.shortcuts import render, reverse
from django.urls import reverse_lazy
from django.views.defaults import permission_denied

# Standard library imports
from itertools import chain


class BaseView:
    """Base view class with common functionality for all model views."""

    OBJECT_URLS = {"copy", "edit", "delete", "view"}

    _queryset_related = None

    @property
    def queryset_related(self):
        if self.model is None:
            return None
        return self._queryset_related

    # ---- View behavior ----
    paginated = False
    page_number = 1
    has_related = False
    has_preview = False
    dashboard = False

    # ---- Model-dependent helpers ----
    def _if_model(self, value):
        return value if self.model is not None else None

    @property
    def search(self):
        return bool(self.model)

    def _model_url(self, action: str):
        if self.model is None:
            return None

        name = f"{self.model._meta.model_name}_{action}"

        if action in self.OBJECT_URLS:
            obj = getattr(self, "object", None)
            if obj is None:
                return None
            return reverse(name, args=[obj.pk])

        return reverse(name)

    @property
    def url_cancel(self):
        return self._model_url("cancel")

    @property
    def url_copy(self):
        return self._model_url("copy")

    @property
    def url_create(self):
        return self._model_url("create")

    @property
    def url_delete(self):
        return self._model_url("delete")

    @property
    def url_edit(self):
        return self._model_url("edit")

    @property
    def url_index(self):
        return self._model_url("index")

    @property
    def url_view(self):
        return self._model_url("view")

    def _model_meta(self):
        return self.model._meta if self.model is not None else None

    @property
    def model_name(self):
        meta = self._model_meta()
        return meta.model_name if meta else None

    @property
    def model_name_plural(self):
        meta = self._model_meta()
        return meta.verbose_name_plural if meta else None

    def get_archived(self, obj):
        """Get archived status of an object, falling back to is_active."""
        return getattr(obj, "archived", not getattr(obj, "is_active", True))

    def _get_int_param(self, key, default):
        """Helper to safely parse integer GET parameters."""
        try:
            return int(self.request.GET.get(key, default))
        except (ValueError, TypeError):
            return default

    def get_context_data(self, **kwargs):
        """Get context data for template rendering."""
        context = super().get_context_data(**kwargs)

        # 1. Model Metadata
        if self.model_name:
            context["model_name"] = self.model_name
            context[f"{self.model_name}_nav"] = True
            context["model_name_plural"] = (
                self.model_name_plural or f"{self.model_name}s"
            )

        # 2. Parameters from Request
        self.per_page = self._get_int_param("items_per_page", 10)
        self.page_number = self._get_int_param("page", 1)

        paginated_str = self.request.GET.get("paginated", "true").lower()
        self.paginated = paginated_str != "false"

        context.update(
            {
                "items_per_page": self.per_page,
                "page_number": self.page_number,
                "paginated": self.paginated,
                "urls": self.get_urls(),
                "statcard": self.get_statcards(),
                "statcards": {},  # Kept for backward compatibility
            }
        )

        # 3. Queryset Handling
        queryset = self.get_queryset()
        related = False

        if self.has_related and self.queryset_related is not None:
            context["has_related"] = True
            queryset = self.queryset_related
            related = True

        if self.has_preview:
            context["has_preview"] = True

        # 4. Pagination
        paginator = Paginator(queryset, self.per_page)
        if self.paginated:
            page_obj = paginator.get_page(self.page_number)
        else:
            page_obj = queryset
        context["page_obj"] = page_obj

        # 5. Field Extraction Logic
        field_values_page = []

        # Handle search-specific display
        if self.search:
            context["search"] = self.search
            field_values_page = self.get_field_values(page_obj, search=True)
            context["search_results"] = len(field_values_page) > 0
            context["field_values_page"] = field_values_page

        # Handle standard list display
        elif hasattr(self, "form_class"):
            field_values_page = self.get_field_values(page_obj, related=related)
            context["field_values_page"] = field_values_page

        # Extract table headers from the first row of results
        if field_values_page and len(field_values_page) > 0:
            context["table_headers"] = [i[0] for i in field_values_page[0]]

        # Detail view specific context
        if hasattr(self, "object"):
            if hasattr(self, "form_class"):
                context["field_values"] = self.get_field_values()
            if self.model:
                context["page_obj_detail_view"] = self.get_page_obj_detail_view()

        return context

    def get_field_values(self, page_obj=None, search=False, related=False):
        """Get field values for display in templates."""
        if page_obj is not None:
            results = []
            attrs_to_check = ["amount", "cost", "net", "hours"]

            for item in page_obj:
                if item is None:
                    continue

                field_values = [
                    ("type", item._meta.model_name),
                    ("id", item.id),
                ]

                # If it's a single object (not a paginator object list)
                if not hasattr(page_obj, "object_list"):
                    field_values.append(("archived", self.get_archived(item)))
                    field_values.append(("item", item))

                # Dynamically add specific attributes if they exist
                for attr in attrs_to_check:
                    if hasattr(item, attr):
                        field_values.append((attr, getattr(item, attr)))

                results.append(field_values)
            return results

        # Logic for Detail View field extraction
        try:
            object_fields = self.form_class().fields.keys()
            return [
                (f, getattr(self.object, f))
                for f in object_fields
                if self.request.user.is_superuser
            ]
        except (AttributeError, TypeError):
            return []

    def get_page_obj_detail_view(self):
        """Get pagination context for detail view navigation."""
        user = self.request.user
        if user.is_authenticated and not user.is_superuser:
            objects = self.model.objects.filter(user=user)
        else:
            objects = self.model.objects.all()

        count = objects.count()
        page_number = self._get_int_param("page_number_detail", 1)

        # Use slicing for better performance on large querysets
        try:
            current_obj = objects[page_number - 1]
            next_obj = objects[page_number] if page_number < count else None
            prev_obj = objects[page_number - 2] if page_number > 1 else None
        except (IndexError, AssertionError):
            current_obj = next_obj = prev_obj = None

        return {
            "page_obj": current_obj,
            "next_object": next_obj,
            "previous_object": prev_obj,
            "first_object": objects.first(),
            "last_object": objects.last(),
            "count": count,
        }

    def get_statcards(self):
        """Get statistics cards data (stub)."""
        return {
            "times": {"entered": 0, "approved": 0},
            "invoices": {"gross": 0, "cost": 0, "net": 0},
        }

    def get_url_names(self):
        """Get URL pattern names (not reversed URLs) for use with {% url %} tag.

        Returns an empty dict if model is None (e.g., for non-model-based views).
        """
        if self.model is None:
            return {}

        return {
            "url_cancel": f"{self.model_name}_cancel",
            "url_copy": f"{self.model_name}_copy",
            "url_create": f"{self.model_name}_create",
            "url_delete": f"{self.model_name}_delete",
            "url_edit": f"{self.model_name}_edit",
            "url_index": f"{self.model_name}_index",
            "url_view": f"{self.model_name}_view",
        }

    def get_urls(self):
        """Get URL names for various actions."""
        return self.get_url_names()


class SuperuserRequiredMixin(UserPassesTestMixin):
    """Mixin to require superuser access."""

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


class AuthenticatedRequiredMixin(SuperuserRequiredMixin):
    """
    Allow superusers or authenticated users.
    """

    def test_func(self):
        return self.request.user.is_authenticated


class RedirectToObjectViewMixin:
    """
    Redirect to object detail view after create/update/copy.
    """

    def get_success_url(self):
        return reverse_lazy(
            f"{self.model._meta.model_name}_view",
            args=[self.object.pk],
        )


class FilterByUserMixin:
    """
    Non-superusers only see their own objects.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)
        return queryset


class ModelCopyMixin:
    """
    Generic copy behavior for models.
    """

    def get_initial(self):
        original = self.model.objects.get(pk=self.kwargs["pk"])
        initial = {}
        for field in original._meta.fields:
            initial[field.name] = getattr(original, field.name)
        return initial

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.pk = None
        obj.save()
        return super().form_valid(form)


def custom_403(request, exception=None):
    """Handle 403 Forbidden errors."""
    return permission_denied(request, exception=exception, template_name="403.html")


def custom_404(request, exception=None):
    """Handle 404 Not Found errors."""
    return render(request, template_name="404.html")


def custom_500(request, exception=None):
    """Handle 500 Internal Server errors."""
    return render(request, template_name="500.html")


def trigger_500(request):
    """Deliberately trigger a 500 error for testing."""
    raise Exception("This is a deliberate 500 error.")
