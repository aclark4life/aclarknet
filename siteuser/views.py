"""Views for user profile management."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, UpdateView

from .forms import UserProfileForm
from .models import SiteUser


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """View for displaying user profile."""
    
    model = SiteUser
    template_name = "siteuser/profile_view.html"
    context_object_name = "profile_user"
    
    def get_object(self):
        """Return the current logged-in user."""
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dashboard"] = True
        context["profile_nav"] = True
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View for editing user profile."""
    
    model = SiteUser
    form_class = UserProfileForm
    template_name = "siteuser/profile_edit.html"
    context_object_name = "profile_user"
    
    def get_object(self):
        """Return the current logged-in user."""
        return self.request.user
    
    def get_success_url(self):
        """Redirect to profile view after successful update."""
        return reverse("profile_view")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dashboard"] = True
        context["profile_nav"] = True
        return context
