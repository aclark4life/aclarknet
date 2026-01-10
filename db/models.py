from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class BaseModel(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    updated = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=300, blank=True, null=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    archived = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    published = models.BooleanField(default=False)
    notes = models.ManyToManyField("Note", blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.updated = timezone.now()
        super(BaseModel, self).save(*args, **kwargs)

    def get_model_name(self):
        return self._meta.verbose_name

    def __str__(self):
        if self.name:
            return f"{self.name}"
        elif self.title:
            return f"{self.title}"
        else:
            try:
                if self.subject:
                    return f"{self.subject}"
            except AttributeError:
                try:
                    if self.description:
                        return f"{self.description}"
                except AttributeError:
                    pass
        return f"{self.__class__.__name__.lower()}-{self.pk}"

    def get_absolute_url(self):
        raise NotImplementedError(
            "Subclass of ModelWithUrl must define get_absolute_url()"
        )


class Client(BaseModel):
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.URLField("Website", blank=True, null=True)
    publish = models.BooleanField(default=False)
    link = models.BooleanField(default=False)
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
    ein = models.CharField("EIN", max_length=300, blank=True, null=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "companies"

    def get_absolute_url(self):
        return reverse("company_view", args=[str(self.id)])


class Contact(BaseModel):
    """
    Client, First Name, Last Name, Title, Email, Office Phone, Mobile Phone,
    Fax
    """

    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=300, blank=True, null=True)
    last_name = models.CharField(max_length=300, blank=True, null=True)
    email = models.EmailField("E-Mail Address", blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    number = models.CharField(max_length=300, blank=True, null=True)
    url = models.URLField("URL", max_length=300, blank=True, null=True)

    def get_absolute_url(self):
        return reverse("contact_view", args=[str(self.id)])

    def save(self, *args, **kwargs):
        if not self.name:
            if self.first_name and self.last_name:
                self.name = f"{self.first_name} {self.last_name}"
        super().save(*args, **kwargs)


class Invoice(BaseModel):
    """
    Issue Date, Last Payment Date, Invoice ID, PO Number, Client, Subject,
    Invoice Amount, Paid Amount, Balance, Subtotal, Discount, Tax, Tax2,
    Currency, Currency Symbol
    """

    subject = models.CharField(max_length=300, blank=True, null=True)
    issue_date = models.DateField(
        "Issue Date", blank=True, default=timezone.now, null=True
    )
    due_date = models.DateField("Due", blank=True, null=True)
    start_date = models.DateField(
        "Start Date", blank=True, default=timezone.now, null=True
    )
    end_date = models.DateField("End Date", blank=True, default=timezone.now, null=True)
    po_number = models.CharField("PO Number", max_length=300, blank=True, null=True)
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL)
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
        ordering = ["subject"]

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
        if not self.subject:
            self.subject = self.__str__()
        super().save(*args, **kwargs)


class Note(BaseModel):
    text = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )

    def get_absolute_url(self):
        return reverse("note_view", args=[str(self.id)])


class Profile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE
    )
    page_size = models.PositiveIntegerField(blank=True, null=True)
    rate = models.DecimalField(
        "Hourly Rate (United States Dollar - USD)",
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2,
    )
    unit = models.DecimalField(
        "Unit", default=1.0, blank=True, null=True, max_digits=12, decimal_places=2
    )
    avatar_url = models.URLField("Avatar URL", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    job_title = models.CharField(max_length=150, blank=True, null=True)
    twitter_username = models.CharField(max_length=150, blank=True, null=True)
    slug = models.SlugField(max_length=150, blank=True, null=True)
    mail = models.BooleanField(default=False)
    dark = models.BooleanField("Dark Mode", default=True)
    default_task = models.ForeignKey(
        "Task",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="profile_defaults",
        help_text="Default task for this user's time entries",
    )

    def is_staff(self):
        if self.user:
            if self.user.is_staff:
                return True

    def get_absolute_url(self):
        if self.user:
            return reverse("user_view", args=[str(self.user.id)])

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Project(BaseModel):
    """
    Client, Project, Project Code, Start Date, End Date,
    Total Hours, Billable Hours, Billable Amount, Budget, Budget Spent,
    Budget Remaining, Total Costs, Team Costs, Expenses
    """

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
    po_number = models.CharField("PO Number", max_length=300, blank=True, null=True)
    companies = models.ManyToManyField(Company)
    draggable_positions = models.JSONField(null=True, blank=True)
    github_project = models.CharField(
        "GitHub Project", max_length=300, blank=True, null=True
    )
    github_repository = models.CharField(
        "GitHub Repository", max_length=300, blank=True, null=True
    )
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


class Report(BaseModel):
    date = models.DateField(default=timezone.now)
    hours = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    amount = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    cost = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    net = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    clients = models.ManyToManyField("Client", blank=True)
    projects = models.ManyToManyField("Project", blank=True)
    tasks = models.ManyToManyField("Task", blank=True)
    invoices = models.ManyToManyField("Invoice", blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )
    reports = models.ManyToManyField("Report", blank=True)
    company = models.ForeignKey(
        "Company", blank=True, null=True, on_delete=models.SET_NULL
    )

    def get_absolute_url(self):
        return reverse("report_view", args=[str(self.id)])


class Task(BaseModel):
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
    slug = models.SlugField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    issue_date = models.DateField(
        "Issue Date", blank=True, null=True, default=timezone.now
    )

    def get_absolute_url(self):
        return reverse("testimonial_view", args=[str(self.id)])


class Time(BaseModel):
    """
    Date, Client, Project, Project Code, Task, Hours, Billable?,
    Invoiced?, First Name, Last Name, Department, Employee?, Billable
    Rate, Billable Amount, Cost Rate, Cost Amount, Currency,
    External Reference URL
    """

    invoiced = models.BooleanField(default=False)
    client = models.ForeignKey(
        Client,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
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
        # Assign default task if no task is specified
        # Priority: explicit task > project default > user default > global default
        if not self.task_id:
            # Check for project-specific default task
            if self.project and self.project.default_task:
                self.task = self.project.default_task
            # Check for user-specific default task
            elif self.user and hasattr(self.user, 'profile') and self.user.profile.default_task:
                self.task = self.user.profile.default_task
            # Fall back to global default task
            else:
                self.task = Task.get_default_task()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("time_view", args=[str(self.id)])
