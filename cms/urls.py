from django.urls import path
from .views import (
    AboutView,
    CareersView,
    ClientsView,
    ContactView,
    DesignPreviewView,
    HomeView,
    ServicesView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("careers/", CareersView.as_view(), name="careers"),
    path("clients/", ClientsView.as_view(), name="clients"),
    path("contact-us/", ContactView.as_view(), name="contact"),
    path("services/", ServicesView.as_view(), name="services"),
    path("design-preview/", DesignPreviewView.as_view(), name="design_preview"),
]
