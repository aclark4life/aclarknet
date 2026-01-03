from django.db import models
from django.urls import reverse
from django.utils import timezone
from wagtail.models import Page
from django.conf import settings
from uuid import uuid4
from phonenumber_field.modelfields import PhoneNumberField
from wagtail import blocks
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase, GenericTaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock


class MongoDBTaggedItem(GenericTaggedItemBase):
    """
    Custom TaggedItem model that uses CharField for object_id to support MongoDB ObjectId.
    """
    object_id = models.CharField(max_length=24, db_index=True, verbose_name="object ID")

    class Meta:
        verbose_name = "tagged item"
        verbose_name_plural = "tagged items"
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("content_type", "object_id", "tag"),
                name="db_mongodbtaggeditem_content_type_object_id_tag_uniq",
            )
        ]


class MarketingBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, help_text="Enter the block title")
    content = blocks.RichTextBlock(required=False, help_text="Enter the block content")
    images = blocks.ListBlock(
        ImageChooserBlock(required=False),
        help_text="Select one or two images for column display. Select three or more images for carousel display.",
    )
    image = ImageChooserBlock(
        required=False, help_text="Select one image for background display."
    )
    block_class = blocks.CharBlock(
        required=False,
        help_text="Enter a CSS class for styling the marketing block",
        classname="full title",
        default="vh-100 app-ribbon",
    )
    image_class = blocks.CharBlock(
        required=False,
        help_text="Enter a CSS class for styling the column display image(s)",
        classname="full title",
        default="img-thumbnail p-5",
    )
    layout_class = blocks.CharBlock(
        required=False,
        help_text="Enter a CSS class for styling the layout.",
        classname="full title",
        default="d-flex flex-row",
    )

    class Meta:
        icon = "placeholder"
        template = "blocks/marketing_block.html"


class AboutPage(Page):
    template = "about_page.html"
    marketing_blocks = StreamField(
        [
            ("marketing_block", MarketingBlock()),
        ],
        blank=True,
        null=True,
        use_json_field=True,
    )
    content_panels = Page.content_panels + [
        FieldPanel("marketing_blocks"),
    ]

    class Meta:
        verbose_name = "About Page"


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


class CareersPage(Page):
    template = "careers_page.html"


class Client(BaseModel):
    tags = TaggableManager(blank=True, through=MongoDBTaggedItem)
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


class ClientsPage(Page):
    template = "clients_page.html"

    def get_context(self, request):
        context = super().get_context(request)

        categories = {}

        for tag, category in settings.CLIENT_CATEGORIES.items():
            categories[category] = Client.objects.filter(
                tags__name__in=[tag], publish=True
            )

        context["categories"] = categories

        testimonials = Testimonial.objects.all()
        context["testimonials"] = testimonials

        return context

    class Meta:
        verbose_name = "Clients Page"


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
    mobile_phone = PhoneNumberField("Mobile Phone", blank=True, null=True)
    office_phone = PhoneNumberField("Office Phone", blank=True, null=True)
    phone = models.CharField(max_length=300, blank=True, null=True)
    fax = PhoneNumberField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    uuid = models.UUIDField("UUID", max_length=300, default=uuid4)
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
    last_payment_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(
        "Start Date", blank=True, default=timezone.now, null=True
    )
    end_date = models.DateField("End Date", blank=True, default=timezone.now, null=True)
    po_number = models.CharField("PO Number", max_length=300, blank=True, null=True)
    sa_number = models.CharField(
        "Subcontractor Agreement Number", max_length=300, blank=True, null=True
    )
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL)
    task = models.ForeignKey("Task", blank=True, null=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(
        "Invoice Amount", blank=True, null=True, max_digits=12, decimal_places=2
    )
    paid_amount = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    balance = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    subtotal = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    discount = models.IntegerField(blank=True, null=True)
    ein = models.IntegerField("EIN", blank=True, null=True)
    tax = models.IntegerField(blank=True, null=True)
    tax2 = models.IntegerField(blank=True, null=True)
    project = models.ForeignKey(
        "Project", blank=True, null=True, on_delete=models.SET_NULL
    )
    currency = models.CharField(
        default="United States Dollar - USD", max_length=300, blank=True, null=True
    )
    currency_symbol = models.CharField(
        default="$", max_length=300, blank=True, null=True
    )

    # https://stackoverflow.com/a/6062320/185820
    class Meta:
        ordering = ["subject"]

    doc_type = models.CharField(max_length=300, blank=True, null=True)
    gross = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    net = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    cost = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    hours = models.DecimalField(
        "Hours", default=1.0, blank=True, null=True, max_digits=12, decimal_places=2
    )
    company = models.ForeignKey(
        "Company", blank=True, null=True, on_delete=models.SET_NULL
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )
    contacts = models.ManyToManyField("Contact", blank=True)

    reset = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("invoice_view", args=[str(self.id)])

    def save(self, *args, **kwargs):
        if not self.subject:
            self.subject = self.__str__()
        super().save(*args, **kwargs)


class Note(BaseModel):
    html = models.BooleanField("HTML", default=False)
    text = models.TextField(blank=True, null=True)
    contacts = models.ManyToManyField("Contact", blank=True)
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
    # user_theme_preference = models.CharField(
    #     max_length=10, choices=settings.THEMES, default="light"
    # )
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
    lounge_password = models.CharField(max_length=150, blank=True, null=True)
    lounge_username = models.CharField(max_length=150, blank=True, null=True)
    mail = models.BooleanField(default=False)
    dark = models.BooleanField("Dark Mode", default=True)
    github_access_token = models.CharField(max_length=150, blank=True, null=True)

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
    task = models.ForeignKey("Task", blank=True, null=True, on_delete=models.SET_NULL)
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

    class Meta:  # https://stackoverflow.com/a/6062320/185820
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
    contacts = models.ManyToManyField("Contact", blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )
    reports = models.ManyToManyField("Report", blank=True)
    company = models.ForeignKey(
        "Company", blank=True, null=True, on_delete=models.SET_NULL
    )
    # team = HStoreField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("report_view", args=[str(self.id)])


class Service(BaseModel):
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("service_view", args=[str(self.id)])


class ServicesPage(Page):
    template = "services_page.html"

    def get_context(self, request):
        context = super().get_context(request)
        services = Service.objects.all()
        context["services"] = services
        return context

    class Meta:
        verbose_name = "Services Page"


class Task(BaseModel):
    rate = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    unit = models.DecimalField(
        "Unit", default=1.0, blank=True, null=True, max_digits=12, decimal_places=2
    )

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("task_view", args=[str(self.id)])


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

    # IGCE
    quantity = models.DecimalField(
        "Quantity", default=1.0, blank=True, null=True, max_digits=12, decimal_places=2
    )
    unit = models.CharField(max_length=2, blank=True, null=True)
    unit_price = models.DecimalField(
        "Unit Price",
        default=1.0,
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2,
    )
    total_price = models.DecimalField(
        "Total Price",
        default=1.0,
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2,
    )
    cost = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    net = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)

    def get_absolute_url(self):
        return reverse("time_view", args=[str(self.id)])
