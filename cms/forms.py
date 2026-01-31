"""Forms for the CMS app."""

from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3


class ContactFormPublic(forms.Form):
    """Public contact form for the website."""

    name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"class": "textinput form-control"}),
    )
    email = forms.EmailField(
        max_length=320,
        required=True,
        widget=forms.EmailInput(attrs={"class": "emailinput form-control"}),
    )
    how_did_you_hear_about_us = forms.ChoiceField(
        required=True,
        choices=[
            ("Internet search engine", "Internet search engine"),
            ("Social media", "Social media"),
            (
                "Referral from a friend or family member",
                "Referral from a friend or family member",
            ),
            ("Advertisement", "Advertisement"),
            ("Email marketing", "Email marketing"),
            ("Website or blog", "Website or blog"),
            ("Event or conference", "Event or conference"),
            ("Other", "Other"),
        ],
        widget=forms.Select(attrs={"class": "select form-select"}),
    )
    how_can_we_help = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={"class": "textarea form-control", "cols": "40", "rows": "10"}
        ),
    )
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                "required_score": 0.5,
            }
        ),
        label="",
    )
