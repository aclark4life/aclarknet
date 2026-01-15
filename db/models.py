from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

# --- Base Classes & Mixins ---


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=300, blank=True, null=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    active = models.BooleanField(default=True)
    published = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def get_model_name(self):
        return self._meta.verbose_name

    def __str__(self):
        return self.name or self.title or f"{self._meta.model_name}-{self.pk}"

    def get_absolute_url(self):
        raise NotImplementedError("Subclasses must implement get_absolute_url()")


class ContactInfoMixin(models.Model):
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.URLField("Website/URL", max_length=300, blank=True, null=True)

    class Meta:
        abstract = True


# --- Concrete Models ---


class Company(BaseModel, ContactInfoMixin):
    class Meta:
        ordering = ["name"]
        verbose_name_plural = "companies"

    def get_absolute_url(self):
        return reverse("company_view", args=[self.id])


class Client(BaseModel, ContactInfoMixin):
    company = models.ForeignKey(
        Company,
        related_name="clients",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("client_view", args=[self.id])


class Contact(BaseModel, ContactInfoMixin):
    first_name = models.CharField(max_length=300, blank=True, null=True)
    last_name = models.CharField(max_length=300, blank=True, null=True)
    email = models.EmailField("E-Mail Address", blank=True, null=True)
    number = models.CharField(max_length=300, blank=True, null=True)
    client = models.ForeignKey(
        Client,
        related_name="contacts",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def save(self, *args, **kwargs):
        if not self.name and (self.first_name or self.last_name):
            self.name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("contact_view", args=[self.id])


class Project(BaseModel, ContactInfoMixin):
    client = models.ForeignKey(
        Client,
        related_name="projects",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    team = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="projects", blank=True
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    default_task = models.ForeignKey(
        "Task",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="default_for_projects",
    )

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("project_view", args=[self.id])


class Task(BaseModel):
    project = models.ForeignKey(
        Project, related_name="tasks", blank=True, null=True, on_delete=models.SET_NULL
    )
    rate = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    unit = models.DecimalField("Unit", default=1.0, max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("task_view", args=[self.id])

    @classmethod
    def get_default_task(cls):
        task, _ = cls.objects.get_or_create(
            name="Default Task",
            defaults={"rate": 100.0, "unit": 1.0},
        )
        return task


class Invoice(BaseModel):
    issue_date = models.DateField("Issue Date", default=timezone.now)
    due_date = models.DateField("Due", blank=True, null=True)
    amount = models.DecimalField(
        "Invoice Amount", blank=True, null=True, max_digits=12, decimal_places=2
    )
    paid_amount = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    balance = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    net = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    cost = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    hours = models.DecimalField(
        "Hours", default=1.0, blank=True, null=True, max_digits=12, decimal_places=2
    )
    project = models.ForeignKey(
        Project,
        related_name="invoices",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    currency = models.CharField(default="USD", max_length=50)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="invoices",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ["-issue_date", "name"]

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"INV-{self.issue_date}-{self.pk or 'NEW'}"
        if self.amount is not None:
            self.balance = self.amount - (self.paid_amount or 0)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("invoice_view", args=[self.id])


class Time(BaseModel):
    project = models.ForeignKey(
        Project,
        related_name="time_entries",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    task = models.ForeignKey(
        Task,
        related_name="time_entries",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="time_entries",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    invoice = models.ForeignKey(
        Invoice, related_name="times", blank=True, null=True, on_delete=models.SET_NULL
    )
    date = models.DateField(default=timezone.now)
    hours = models.DecimalField("Hours", default=1.0, max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    amount = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    cost = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    net = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.task:
            if self.project and self.project.default_task:
                self.task = self.project.default_task
            else:
                self.task = Task.get_default_task()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("time_view", args=[self.id])


class Note(BaseModel):
    text = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notes",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        if self.name:
            return self.name
        return (self.text[:30] + "...") if self.text else f"Note {self.id}"

    def get_absolute_url(self):
        return reverse("note_view", args=[self.id])
