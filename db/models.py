from django.db import models
from django_mongodb_backend.fields import EmbeddedModelArrayField
from django_mongodb_backend.models import EmbeddedModel


class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    website = models.URLField()
    projects = EmbeddedModelArrayField("Project")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"


class Time(EmbeddedModel):
    date = models.DateField(null=True, blank=True)
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.hours}h on {self.date}"


class Invoice(EmbeddedModel):
    number = models.CharField(max_length=50)
    date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    times = EmbeddedModelArrayField("Time")  # embedded time entries

    def __str__(self):
        return f"Invoice {self.number}"


class Project(EmbeddedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    invoices = EmbeddedModelArrayField("Invoice")  # embedded invoices

    def __str__(self):
        return self.name
