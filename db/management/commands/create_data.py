import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from db.models import Company, Client, Project, Invoice, Time, Task, Profile

fake = Faker()


class Command(BaseCommand):
    help = "Creates fake data for Companies, Clients, Projects, Invoices, and Times"

    def add_arguments(self, parser):
        parser.add_argument(
            "--companies", type=int, default=10, help="Number of companies to create"
        )
        parser.add_argument(
            "--clients", type=int, default=20, help="Number of clients to create"
        )
        parser.add_argument(
            "--projects", type=int, default=30, help="Number of projects to create"
        )
        parser.add_argument(
            "--invoices", type=int, default=40, help="Number of invoices to create"
        )
        parser.add_argument(
            "--times", type=int, default=50, help="Number of time entries to create"
        )
        parser.add_argument(
            "--users", type=int, default=10, help="Number of users to create"
        )

    def handle(self, *args, **options):
        num_companies = options["companies"]
        num_clients = options["clients"]
        num_projects = options["projects"]
        num_invoices = options["invoices"]
        num_times = options["times"]
        num_users = options["users"]

        # Create Users and Profiles
        users = []
        for _ in range(num_users):
            user = User.objects.create_user(
                username=fake.user_name(), email=fake.email(), password=fake.password()
            )
            Profile.objects.create(
                user=user,
                page_size=fake.random_int(min=10, max=100),
                rate=100,
                unit=1,
                avatar_url=fake.image_url(),
                bio=fake.text(),
                address=fake.address(),
                job_title=fake.job(),
                twitter_username=fake.user_name(),
                slug=fake.slug(),
                mail=fake.boolean(),
                dark=fake.boolean(),
            )
            users.append(user)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {num_users} users and profiles")
        )

        # Create Companies
        companies = []
        for _ in range(num_companies):
            company = Company.objects.create(
                name=fake.company(),
                address=fake.address(),
                description=fake.text(),
                url=fake.url(),
                ein=fake.bothify(text="EIN-##########"),
            )
            companies.append(company)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {num_companies} companies")
        )

        # Create Clients
        clients = []
        for _ in range(num_clients):
            client = Client.objects.create(
                name=fake.name(),
                address=fake.address(),
                description=fake.text(),
                url=fake.url(),
                email=fake.email(),
                company=random.choice(companies) if companies else None,
            )
            clients.append(client)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {num_clients} clients")
        )

        # Create Tasks
        tasks = []
        for _ in range(num_projects):  # Using num_projects for simplicity
            task = Task.objects.create(
                name=fake.sentence(),
                rate=200,
                unit=1,
            )
            tasks.append(task)

        # Create Projects
        projects = []
        for _ in range(num_projects):
            project = Project.objects.create(
                name=fake.sentence(),
                client=random.choice(clients) if clients else None,
                task=random.choice(tasks) if tasks else None,
                start_date=fake.date_this_decade(),
                end_date=fake.date_this_decade(),
                code=fake.random_int(min=1000, max=9999),
                description=fake.text(),
                po_number=fake.bothify(text="PO-#######"),
            )
            projects.append(project)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {num_projects} projects")
        )

        # Create Invoices
        invoices = []
        for _ in range(num_invoices):
            invoice = Invoice.objects.create(
                subject=fake.sentence(),
                issue_date=fake.date_this_decade(),
                due_date=fake.date_this_decade(),
                client=random.choice(clients) if clients else None,
                task=random.choice(tasks) if tasks else None,
                amount=fake.random_number(digits=5, fix_len=True),
                paid_amount=fake.random_number(digits=5, fix_len=True),
                currency="USD",
            )
            invoices.append(invoice)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {num_invoices} invoices")
        )

        # Create Time Entries
        for _ in range(num_times):
            Time.objects.create(
                date=fake.date_this_decade(),
                hours=fake.random_number(digits=2, fix_len=True),
                client=random.choice(clients) if clients else None,
                project=random.choice(projects) if projects else None,
                task=random.choice(tasks) if tasks else None,
                user=random.choice(users),
                invoice=random.choice(invoices) if invoices else None,
                amount=fake.random_number(digits=5, fix_len=True),
            )
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {num_times} time entries")
        )
