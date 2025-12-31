from django.urls import path
from .views import HomeView, ServicesView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("services", ServicesView.as_view(), name="services"),
]
