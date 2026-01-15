from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class BaseModel(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    updated = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.updated = timezone.now()
        super(BaseModel, self).save(*args, **kwargs)

    def get_model_name(self):
        return self._meta.verbose_name

    def __str__(self):
        return f"{self.__class__.__name__.lower()}-{self.pk}"

    def get_absolute_url(self):
        raise NotImplementedError(
            "Subclass of ModelWithUrl must define get_absolute_url()"
        )


class Client(BaseModel):
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.URLField("Website", blank=True, null=True)
    email = models.EmailField(blank=True, null=True, default="aclark@aclark.net")

    class Meta:
        ordering = ["name"]

    company = models.ForeignKey(
        "Company", blank=True, null=True, on_delete=models.SET_NULL
    )

    def get_absolute_url(self):
        return reverse("client_view", args=[str(self.id)])


class Company(BaseModel):
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.URLField("Website", blank=True, null=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "companies"

    def get_absolute_url(self):
        return reverse("company_view", args=[str(self.id)])


class Contact(BaseModel):
    first_name = models.CharField(max_length=300, blank=True, null=True)
    last_name = models.CharField(max_length=300, blank=True, null=True)
    email = models.EmailField("E-Mail Address", blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    number = models.CharField(max_length=300, blank=True, null=True)
    url = models.URLField("URL", max_length=300, blank=True, null=True)
    client = models.ForeignKey(
        "Client", blank=True, null=True, on_delete=models.SET_NULL
    )

    def get_absolute_url(self):
        return reverse("contact_view", args=[str(self.id)])

    def save(self, *args, **kwargs):
        if not self.name:
            if self.first_name and self.last_name:
                self.name = f"{self.first_name} {self.last_name}"
        super().save(*args, **kwargs)


class Invoice(BaseModel):
    issue_date = models.DateField(
        "Issue Date", blank=True, default=timezone.now, null=True
    )
    due_date = models.DateField("Due", blank=True, null=True)
    start_date = models.DateField(
        "Start Date", blank=True, default=timezone.now, null=True
    )
    end_date = models.DateField("End Date", blank=True, default=timezone.now, null=True)
    amount = models.DecimalField(
        "Invoice Amount", blank=True, null=True, max_digits=12, decimal_places=2
    )
    paid_amount = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    balance = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    project = models.ForeignKey(
        "Project", blank=True, null=True, on_delete=models.SET_NULL
    )
    currency = models.CharField(
        default="United States Dollar - USD", max_length=300, blank=True, null=True
    )

    class Meta:
        ordering = ["name"]

    gross = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    net = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    cost = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    hours = models.DecimalField(
        "Hours", default=1.0, blank=True, null=True, max_digits=12, decimal_places=2
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )

    reset = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("invoice_view", args=[str(self.id)])

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.__str__()
        super().save(*args, **kwargs)


class Note(BaseModel):
    text = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )

    def get_absolute_url(self):
        return reverse("note_view", args=[str(self.id)])


class Project(BaseModel):
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL)
    team = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    code = models.IntegerField("Project Code", blank=True, null=True)
    total_hours = models.FloatField(blank=True, null=True)
    billable_hours = models.FloatField(blank=True, null=True)
    amount = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    budget = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    budget_spent = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    budget_remaining = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    total_costs = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    team_costs = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    cost = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    expenses = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    description = models.TextField(blank=True, null=True)
    companies = models.ManyToManyField(Company)
    default_task = models.ForeignKey(
        "Task",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="project_defaults",
        help_text="Default task for this project's time entries",
    )

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("project_view", args=[str(self.id)])


class Task(BaseModel):
    project = models.ForeignKey(
        "Project",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        help_text="Project this task belongs to (optional)",
    )
    rate = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    unit = models.DecimalField(
        "Unit", default=1.0, blank=True, null=True, max_digits=12, decimal_places=2
    )

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("task_view", args=[str(self.id)])

    @classmethod
    def get_default_task(cls):
        """Get or create the default task for time entries."""
        task, created = cls.objects.get_or_create(
            name="Default Task",
            defaults={
                "rate": 100.0,
                "unit": 1.0,
            },
        )
        return task


class Testimonial(BaseModel):
    description = models.TextField(blank=True, null=True)
    issue_date = models.DateField(
        "Issue Date", blank=True, null=True, default=timezone.now
    )

    def get_absolute_url(self):
        return reverse("testimonial_view", args=[str(self.id)])


class Time(BaseModel):
    project = models.ForeignKey(
        Project,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    task = models.ForeignKey(
        Task,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )
    invoice = models.ForeignKey(
        Invoice,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="times",
    )
    date = models.DateField(default=timezone.now, blank=True, null=True)
    hours = models.DecimalField(
        "Hours", default=1.0, blank=True, null=True, max_digits=12, decimal_places=2
    )
    description = models.TextField(blank=True, null=True)

    amount = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    cost = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    net = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        # Assign task with priority: project task > time task > default task
        # Priority: project default > explicit task > global default

        # Check for project-specific default task (highest priority)
        if self.project and self.project.default_task:
            self.task = self.project.default_task
        # If no project default but task is explicitly set, keep it
        elif self.task_id:
            pass  # Keep the explicit task
        # Fall back to global default task
        else:
            self.task = Task.get_default_task()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("time_view", args=[str(self.id)])
