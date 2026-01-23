from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone

# --- Base Classes & Mixins ---


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def get_model_name(self):
        return self._meta.verbose_name

    def __str__(self):
        return self.name or f"{self._meta.model_name}-{self.pk}"

    def get_absolute_url(self):
        raise NotImplementedError("Subclasses must implement get_absolute_url()")


class ContactInfoMixin(models.Model):
    address = models.TextField(blank=True, null=True)
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
    class ClientCategory(models.TextChoices):
        GOVERNMENT = "government", "Government"
        NONPROFIT = "non-profit", "Non-Profit"
        PRIVATE = "private", "Private Sector"
        EDUCATION = "education", "Education"
        HEALTHCARE = "healthcare", "Healthcare"
        OTHER = "other", "Other"

    company = models.ForeignKey(
        Company,
        related_name="clients",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    featured = models.BooleanField(
        default=False,
        help_text="Check to display this client on the public clients page",
    )
    category = models.CharField(
        max_length=50,
        choices=ClientCategory.choices,
        blank=True,
        null=True,
        help_text="Client category for grouping on the public clients page",
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
            name="Software Development",
            defaults={"rate": 187.50, "unit": 1.0},
        )
        return task


class Invoice(BaseModel):
    invoice_number = models.IntegerField("Invoice Number", unique=True, null=True, blank=True)
    issue_date = models.DateField("Issue Date", default=timezone.now)
    start_date = models.DateField("Start Date", blank=True, null=True)
    end_date = models.DateField("End Date", blank=True, null=True)
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
        # Auto-generate invoice number if not set
        if self.invoice_number is None:
            with transaction.atomic():
                # Use select_for_update to prevent race conditions
                max_invoice = Invoice.objects.select_for_update().aggregate(
                    models.Max('invoice_number')
                )['invoice_number__max']
                self.invoice_number = (max_invoice or 0) + 1
        
        if not self.name:
            self.name = f"INV-{self.issue_date}-{self.invoice_number or self.pk or 'NEW'}"
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
    amount = models.DecimalField(
        "Amount", blank=True, null=True, max_digits=12, decimal_places=2
    )

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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notes",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    # Generic foreign key fields to attach notes to any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    object_id = models.CharField(max_length=255, blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        if self.name:
            return self.name
        return (
            (self.description[:30] + "...") if self.description else f"Note {self.id}"
        )

    def get_absolute_url(self):
        return reverse("note_view", args=[self.id])
