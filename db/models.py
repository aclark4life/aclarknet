from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    website = models.URLField()

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
