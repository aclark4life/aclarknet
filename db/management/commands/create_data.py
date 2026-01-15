import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from faker import Faker

from db.models import Company, Client, Contact, Project, Invoice, Time, Task

from siteuser.models import SiteUser

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

        # Create Users and Profiles with different rates
        users = []
        # Define a set of different rates for users
        rates = [
            Decimal("75.00"),
            Decimal("100.00"),
            Decimal("125.00"),
            Decimal("150.00"),
            Decimal("200.00"),
        ]
        for i in range(num_users):
            # Cycle through rates to ensure users have different rates
            rate = rates[i % len(rates)]
            user = SiteUser.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password=fake.password(),
                rate=rate,
                mail=True,
            )
            users.append(user)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {num_users} users with rates")
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
                name=fake.sentence(),
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

        # Create Time Entries with calculated amounts based on user rates
        for _ in range(num_times):
            task = random.choice(tasks)
            user = random.choice(users)
            hours = fake.random_int(min=1, max=40)  # More realistic hours
            # Calculate amount from user rate * hours (prioritize user rate over task rate)
            rate = (
                user.rate if user.rate else (task.rate if task.rate else Decimal("0"))
            )
            amount = Decimal(str(rate)) * Decimal(str(hours))

            Time.objects.create(
                name=fake.sentence(),
                date=fake.date_this_decade(),
                hours=hours,
                project=random.choice(projects),
                task=task,
                user=user,
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
