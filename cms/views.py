from django.views.generic import TemplateView

# Create your views here.


class AboutView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company_name"] = "Tech Solutions Inc."
        context["founded_year"] = 2010
        return context


class CareersView(TemplateView):
    template_name = "careers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["open_positions"] = [
            "Software Engineer",
            "Product Manager",
            "UX Designer",
            "Data Scientist",
        ]
        return context


class ClientsView(TemplateView):
    template_name = "clients.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["clients"] = [
            "Client A",
            "Client B",
            "Client C",
            "Client D",
        ]
        return context


class ContactView(TemplateView):
    template_name = "contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email"] = ""
        context["phone"] = "+1-234-567-8900"
        return context


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
