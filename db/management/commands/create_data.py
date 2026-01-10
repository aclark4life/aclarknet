import random
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from db.models import Company, Client, Contact, Project, Invoice, Time, Task, Profile

fake = Faker()


class Command(BaseCommand):
    help = "Creates fake data for Companies, Clients, Contacts, Projects, Invoices, and Times"

    def add_arguments(self, parser):
        parser.add_argument(
            "--companies", type=int, default=10, help="Number of companies to create"
        )
        parser.add_argument(
            "--clients", type=int, default=20, help="Number of clients to create"
        )
        parser.add_argument(
            "--contacts", type=int, default=30, help="Number of contacts to create"
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
        num_contacts = options["contacts"]
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
                company=random.choice(companies),
            )
            clients.append(client)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {num_clients} clients")
        )

        # Create Contacts
        contacts = []
        for _ in range(num_contacts):
            contact = Contact.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                address=fake.address(),
                number=fake.phone_number(),
                url=fake.url(),
                title=fake.job(),
                client=random.choice(clients),
            )
            contacts.append(contact)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {num_contacts} contacts")
        )

        # Create Tasks
        tasks = []
        for _ in range(num_projects):  # Using num_projects for simplicity
            task = Task.objects.create(
                name=fake.sentence(),
                rate=100,
                unit=1,
            )
            tasks.append(task)

        # Create Projects
        projects = []
        for _ in range(num_projects):
            project = Project.objects.create(
                name=fake.sentence(),
                start_date=fake.date_this_decade(),
                end_date=fake.date_this_decade(),
                code=fake.random_int(min=1000, max=9999),
                description=fake.text(),
                client=random.choice(clients),
            )
            projects.append(project)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {num_projects} projects")
        )

        # Create Invoices (without amounts initially)
        invoices = []
        for _ in range(num_invoices):
            invoice = Invoice.objects.create(
                subject=fake.sentence(),
                issue_date=fake.date_this_decade(),
                due_date=fake.date_this_decade(),
                amount=0,
                paid_amount=0,
                currency="USD",
                project=random.choice(projects),
            )
            invoices.append(invoice)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {num_invoices} invoices")
        )

        # Create Time Entries with calculated amounts
        for _ in range(num_times):
            task = random.choice(tasks)
            hours = fake.random_int(min=1, max=40)  # More realistic hours
            # Calculate amount from task rate * hours
            amount = (
                Decimal(str(task.rate)) * Decimal(str(hours))
                if task.rate
                else Decimal("0")
            )

            Time.objects.create(
                date=fake.date_this_decade(),
                hours=hours,
                project=random.choice(projects),
                task=task,
                user=random.choice(users),
                invoice=random.choice(invoices) if invoices else None,
                amount=amount,
                description=fake.sentence(),
            )
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {num_times} time entries")
        )

        # Update invoice amounts from their time entries
        for invoice in invoices:
            # Sum all time entries for this invoice
            time_entries = Time.objects.filter(invoice=invoice)
            total_amount = sum((time.amount or Decimal("0")) for time in time_entries)
            invoice.amount = total_amount
            if total_amount > 0:
                invoice.paid_amount = total_amount
            else:
                invoice.paid_amount = Decimal("0")
            invoice.save()

        self.stdout.write(
            self.style.SUCCESS("Successfully updated invoice amounts from time entries")
        )
