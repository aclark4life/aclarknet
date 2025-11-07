from django.conf import settings
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"


class Client(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="clients"
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employee"
    )
    hourly_rate = models.FloatField()

    def __str__(self):
        return f"{self.user.username} (${self.hourly_rate}/hr)"


class Project(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Represents a type of task with an hourly rate.
    Can be associated with multiple Time entries.
    """

    name = models.CharField(max_length=255)
    hourly_rate = models.FloatField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} (${self.hourly_rate}/h)"


class Invoice(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="invoices"
    )
    number = models.CharField(max_length=50)
    date = models.DateField(null=True, blank=True)
    amount = models.FloatField()

    def __str__(self):
        return f"Invoice {self.number}"


class Time(models.Model):
    invoice = models.ForeignKey(
        "Invoice", on_delete=models.CASCADE, related_name="times"
    )
    task = models.ForeignKey(
        "Task",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="times",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="times",
    )
    date = models.DateField(null=True, blank=True)
    hours = models.FloatField()
    description = models.TextField(blank=True)

    @property
    def cost(self):
        """Use employee’s hourly rate if present, else task’s rate."""
        if (
            self.user
            and hasattr(self.user, "employee")
            and self.user.employee.hourly_rate
        ):
            return self.hours * self.user.employee.hourly_rate
        elif self.task:
            return self.hours * self.task.hourly_rate
        return 0

    def __str__(self):
        task_name = self.task.name if self.task else "No Task"
        user_name = self.user.username if self.user else "Anonymous"
        return f"{self.hours}h by {user_name} on {self.date} ({task_name})"
