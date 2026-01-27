"""Base views, mixins, and error handlers for the db app."""

# Django imports
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.paginator import Paginator
from django.shortcuts import render, reverse
from django.urls import reverse_lazy
from django.views.defaults import permission_denied

# Standard library imports


class FakeDataMixin:
    """Mixin to populate form initial data with fake values in DEBUG mode.
    
    Usage:
        class MyCreateView(FakeDataMixin, CreateView):
            fake_data_function = 'get_fake_client_data'  # Name of function from faker_utils
    """
    
    fake_data_function = None  # Subclasses should set this to the function name
    
    def get_initial(self):
        """Get initial form data, with fake data added if in DEBUG mode."""
        initial = super().get_initial()
        
        # Only add fake data if in DEBUG mode and function is specified
        if settings.DEBUG and self.fake_data_function:
            try:
                from ..faker_utils import get_faker
                
                # Only proceed if faker is available
                if get_faker() is not None:
                    # Import the module and get the function
                    from .. import faker_utils
                    fake_data_func = getattr(faker_utils, self.fake_data_function, None)
                    
                    if fake_data_func and callable(fake_data_func):
                        fake_data = fake_data_func()
                        # Only add fake values for fields that aren't already set
                        for key, value in fake_data.items():
                            if key not in initial or initial[key] is None:
                                initial[key] = value
            except (ImportError, AttributeError):
                # Silently skip if Faker is not available or function not found
                pass
        
        return initial


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
    dashboard = False

    # ---- Field values customization ----
    # Subclasses can set these to customize which fields are shown in detail views
    field_values_include = None  # List of field names to include (None = all fields)
    field_values_exclude = None  # List of field names to exclude
    field_values_extra = None  # List of (field_name, value) tuples to append
    
    # ---- Related items display customization ----
    # These control how related items are displayed in related.html template
    related_title_fields = ["name", "title", "subject", "description"]  # Fields shown in card title
    related_excluded_fields = ["type", "id", "item"]  # Fields never shown in related cards

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
            context["related_title_fields"] = self.related_title_fields
            context["related_excluded_fields"] = self.related_excluded_fields
            queryset = self.queryset_related
            related = True

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
            # Add notes if they exist for this object
            notes = self._get_notes_for_object()
            if notes:
                context["object_notes"] = notes
            # Add content_type for the "Add Note" button
            if self.object:
                from django.contrib.contenttypes.models import ContentType
                context["content_type"] = ContentType.objects.get_for_model(self.object.__class__)

        return context

    def get_field_values(self, page_obj=None, search=False, related=False):
        """Get field values for display in templates.

        For list views (page_obj provided):
            Returns a list of field value tuples for each item.
            Supports customization options:
            - field_values_include: Only include these fields
            - field_values_exclude: Exclude these fields
            - field_values_extra: Additional (name, value) tuples to append

        For detail views (no page_obj):
            Returns field values from form_class fields, with customization options:
            - field_values_include: Only include these fields
            - field_values_exclude: Exclude these fields
            - field_values_extra: Additional (name, value) tuples to append
        """
        if page_obj is not None:
            results = []

            # Get form fields for list view customization
            if hasattr(self, "form_class"):
                if not hasattr(self, "_cached_form_fields"):
                    self._cached_form_fields = list(self.form_class().fields.keys())
                form_fields = self._cached_form_fields.copy()

                # Apply field_values_include filter if specified
                if self.field_values_include is not None:
                    form_fields = [
                        f for f in form_fields if f in self.field_values_include
                    ]

                # Apply field_values_exclude filter if specified
                if self.field_values_exclude is not None:
                    form_fields = [
                        f for f in form_fields if f not in self.field_values_exclude
                    ]
            else:
                # Fallback to hardcoded attributes if no form_class
                form_fields = ["amount", "cost", "net", "hours"]

            for item in page_obj:
                if item is None:
                    continue

                field_values = [
                    ("type", item._meta.model_name),
                    ("id", item.id),
                ]

                # If it's a single object (not a paginator object list)
                if not hasattr(page_obj, "object_list"):
                    field_values.append(("item", item))

                # For related views, use the item's model-specific form to get fields
                item_form_fields = form_fields
                if related:
                    item_form_fields = self._get_model_form_fields(item)

                # Add form fields that exist on the item
                for field_name in item_form_fields:
                    if hasattr(item, field_name):
                        field_values.append((field_name, getattr(item, field_name)))

                # Append any extra fields specified by the view
                if self.field_values_extra is not None:
                    field_values.extend(self.field_values_extra)

                results.append(field_values)
            return results

        # Logic for Detail View field extraction
        try:
            # Get all form fields (use cached form if available to avoid re-instantiation)
            if not hasattr(self, "_cached_form_fields"):
                self._cached_form_fields = list(self.form_class().fields.keys())
            form_fields = self._cached_form_fields.copy()

            # Apply field_values_include filter if specified
            if self.field_values_include is not None:
                form_fields = [f for f in form_fields if f in self.field_values_include]

            # Apply field_values_exclude filter if specified
            if self.field_values_exclude is not None:
                form_fields = [
                    f for f in form_fields if f not in self.field_values_exclude
                ]

            # Build the base field values list
            result = [(f, getattr(self.object, f)) for f in form_fields]

            # Append any extra fields specified by the view
            if self.field_values_extra is not None:
                result.extend(self.field_values_extra)

            return result
        except (AttributeError, TypeError):
            return []

    def _get_model_form_fields(self, item):
        """Get form fields for a specific model instance.
        
        Args:
            item: A model instance
            
        Returns:
            List of field names from the item's corresponding form
        """
        from .. import forms
        
        # Cache form fields per model to avoid repeated lookups
        model_name = item._meta.model_name
        cache_key = f"_form_fields_{model_name}"
        
        if hasattr(self, cache_key):
            return getattr(self, cache_key)
        
        # Map model names to their form classes
        form_class_name = f"{model_name.capitalize()}Form"
        
        # Try to get the form class from the forms module
        form_class = getattr(forms, form_class_name, None)
        
        if form_class is not None:
            try:
                # For forms that may need user context (like TimeForm), provide basic instantiation
                # Most ModelForms should work fine with no arguments
                form_instance = form_class()
                fields = list(form_instance.fields.keys())
                setattr(self, cache_key, fields)
                return fields
            except (TypeError, ValueError, AttributeError, ImportError):
                # If instantiation fails (e.g., missing required args), try accessing Meta.fields directly
                try:
                    if hasattr(form_class, 'Meta') and hasattr(form_class.Meta, 'fields'):
                        meta_fields = form_class.Meta.fields
                        # Handle both tuple and list
                        fields = list(meta_fields) if meta_fields != '__all__' else None
                        if fields is not None:
                            setattr(self, cache_key, fields)
                            return fields
                except (AttributeError, TypeError):
                    # If Meta.fields access fails, continue to next fallback
                    pass
        
        # Fallback to using the view's form_class if available
        if hasattr(self, "form_class"):
            if not hasattr(self, "_cached_form_fields"):
                self._cached_form_fields = list(self.form_class().fields.keys())
            fields = self._cached_form_fields.copy()
            setattr(self, cache_key, fields)
            return fields
        
        # Final fallback to basic fields
        fields = ["amount", "cost", "net", "hours"]
        setattr(self, cache_key, fields)
        return fields

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

    def _get_notes_for_object(self):
        """Get notes attached to the current object via generic foreign key.
        
        Returns:
            List of Note objects or None if no object or no notes exist
        """
        if not hasattr(self, 'object') or self.object is None:
            return None
        
        try:
            from django.contrib.contenttypes.models import ContentType
            from ..models import Note
            
            content_type = ContentType.objects.get_for_model(self.object.__class__)
            notes = list(Note.objects.filter(
                content_type=content_type,
                object_id=str(self.object.pk)
            ).order_by('-created'))
            
            return notes if notes else None
        except Exception:
            # Silently fail if Note model doesn't exist or other issues
            return None

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
