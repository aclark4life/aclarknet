from django.db import models
from db.models.base import BaseModel
from django.shortcuts import reverse


class Service(BaseModel):
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("service_view", args=[str(self.id)])
