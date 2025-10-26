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


class Project(EmbeddedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
