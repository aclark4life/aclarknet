from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"


class Project(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="invoices"
    )
    number = models.CharField(max_length=50)
    date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Invoice {self.number}"


class Time(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="times")
    date = models.DateField(null=True, blank=True)
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.hours}h on {self.date}"
