"""Views for the CMS app."""

from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import ContactFormPublic


class BaseCMSView(TemplateView):
    """Base view for CMS pages with common context."""

    page_name = None

    def get_context_data(self, **kwargs):
        """Add common CMS context data."""
        context = super().get_context_data(**kwargs)
        if self.page_name:
            context["page_name"] = self.page_name
        return context


class AboutView(BaseCMSView):
    """About page view displaying company information."""

    template_name = "about.html"
    page_name = "about"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company_name"] = getattr(settings, "COMPANY_NAME", "ACLARK.NET, LLC")
        context["founded_year"] = getattr(settings, "COMPANY_FOUNDED_YEAR", 2003)
        return context


class CareersView(BaseCMSView):
    """Careers page view displaying open positions."""

    template_name = "careers.html"
    page_name = "careers"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["open_positions"] = getattr(
            settings,
            "OPEN_POSITIONS",
            [
                "Software Engineer",
                "Product Manager",
                "UX Designer",
                "Data Scientist",
            ],
        )
        return context


class ClientsView(BaseCMSView):
    """Clients page view displaying client list."""

    template_name = "clients.html"
    page_name = "clients"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Try to get clients from database first, fall back to settings
        try:
            from collections import defaultdict

            from db.models import Client, Note

            # Get only featured clients
            featured_clients = Client.objects.filter(featured=True).order_by(
                "category", "name"
            )

            # Group clients by category
            categories = defaultdict(list)
            for client in featured_clients:
                # Get the display name for the category, or use "Other" if not set
                category_display = (
                    client.get_category_display()
                    if client.category
                    else "Other"
                )
                categories[category_display].append(client)

            # Convert to regular dict and pass to context
            context["categories"] = dict(categories)
            context["clients"] = featured_clients
            
            # Get testimonials (Notes marked as testimonials)
            context["testimonials"] = Note.objects.filter(
                is_testimonial=True
            ).order_by("-created")
        except (ImportError, Exception):
            # Fallback to settings if database is not available
            context["categories"] = {
                "Featured": getattr(
                    settings,
                    "FEATURED_CLIENTS",
                    [
                        "Client A",
                        "Client B",
                        "Client C",
                        "Client D",
                    ],
                )
            }
            context["testimonials"] = []
        return context


class ContactView(FormView):
    """Contact page view displaying contact information and handling form submissions."""

    template_name = "contact.html"
    form_class = ContactFormPublic
    success_url = reverse_lazy("contact")
    page_name = "contact"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] = self.page_name
        context["email"] = getattr(
            settings, "CONTACT_EMAIL", settings.DEFAULT_FROM_EMAIL
        )
        context["phone"] = getattr(settings, "CONTACT_PHONE", "+1-202-555-0000")
        return context

    def form_valid(self, form):
        """Handle successful form submission."""
        # Get form data
        name = form.cleaned_data.get("name")
        email = form.cleaned_data.get("email")
        how_did_you_hear = form.cleaned_data.get("how_did_you_hear_about_us")
        message_text = form.cleaned_data.get("how_can_we_help")

        # TODO: Send email or save to database
        # For now, just display a success message
        messages.success(
            self.request,
            f"Thank you for contacting us, {name}! We'll get back to you at {email} soon.",
        )
        
        return super().form_valid(form)

    def form_invalid(self, form):
        """Handle invalid form submission."""
        messages.error(
            self.request,
            "There was an error with your submission. Please check the form and try again.",
        )
        return super().form_invalid(form)


class HomeView(BaseCMSView):
    """Home page view."""

    template_name = "home.html"
    page_name = "home"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message"] = getattr(
            settings, "HOMEPAGE_MESSAGE", "Welcome to ACLARK.NET!"
        )
        
        # Get featured testimonial for homepage
        try:
            from db.models import Note
            
            # Get the most recently created featured testimonial
            testimonial = Note.objects.filter(
                is_testimonial=True, is_featured=True
            ).order_by("-created").first()
            context["testimonial"] = testimonial
        except (ImportError, Exception):
            context["testimonial"] = None
            
        return context


class ServicesView(BaseCMSView):
    """Services page view displaying available services."""

    template_name = "services.html"
    page_name = "services"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["services"] = getattr(
            settings,
            "SERVICES_LIST",
            [
                "Web Development",
                "App Development",
                "SEO Optimization",
                "Digital Marketing",
            ],
        )
        return context
