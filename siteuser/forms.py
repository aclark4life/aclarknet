from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field
from django import forms

from .models import SiteUser


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information."""
    
    class Meta:
        model = SiteUser
        fields = ("first_name", "last_name", "email", "rate")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(
                Field("first_name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(
                Field("last_name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(
                Field("email", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(
                Field("rate", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            css_class="row",
        )
