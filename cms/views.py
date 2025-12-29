from django.views.generic import TemplateView                             
from django.shortcuts import render                                       
                                                                          
# Create your views here.                                                 
                                                                          
class HomeView(TemplateView):                                             
    template_name = "home.html"                                           
                                                                          
    def get_context_data(self, **kwargs):                                 
        context = super().get_context_data(**kwargs)                      
        context['message'] = "Welcome to the Home Page!"                  
        return context

