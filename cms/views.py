from django.views.generic import TemplateView

# Create your views here.


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message"] = "Welcome to the Home Page!"
        return context


class ServicesView(TemplateView):
    template_name = "services.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["services"] = [
            "Web Development",
            "App Development",
            "SEO Optimization",
            "Digital Marketing",
        ]
        return context
