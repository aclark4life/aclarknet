import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from faker import Faker

from db.models import Company, Client, Contact, Project, Invoice, Time, Task

from siteuser.models import SiteUser

fake = Faker()


class Command(BaseCommand):
    """
    Django management command to create fake data for testing and development.
    
    Creates fake data for Companies, Clients, Contacts, Projects, Invoices, and Times.
    
    Usage Examples:
        # Create all model types with default counts
        python manage.py create_data
        
        # Create only 50 users
        python manage.py create_data --users-only=50
        
        # Create only 20 companies
        python manage.py create_data --companies-only=20
        
        # Create only 100 time entries (automatically creates required dependencies)
        python manage.py create_data --times-only=100
        
    Dependency Handling:
        When using --*-only flags, the command automatically creates minimum required dependencies:
        - users: no dependencies
        - companies: no dependencies
        - clients: requires companies
        - contacts: requires clients and companies
        - projects: requires clients and companies
        - invoices: requires projects, clients, and companies
        - times: requires all of the above plus tasks and users
        
    If required dependencies don't exist in the database, the command will create them
    automatically (minimum 1 of each) and display a warning message.
    """
    help = "Creates fake data for Companies, Clients, Contacts, Projects, Invoices, and Times"

    def _needs_dependency(self, *dependent_flags):
        """Check if any of the dependent flags are set (not None)."""
        return any(flag is not None for flag in dependent_flags)

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
        # Add --*-only flags to create only specific model types
        parser.add_argument(
            "--users-only",
            type=int,
            help="Create only users (number to create)",
        )
        parser.add_argument(
            "--companies-only",
            type=int,
            help="Create only companies (number to create)",
        )
        parser.add_argument(
            "--clients-only",
            type=int,
            help="Create only clients (number to create, requires companies)",
        )
        parser.add_argument(
            "--contacts-only",
            type=int,
            help="Create only contacts (number to create, requires clients and companies)",
        )
        parser.add_argument(
            "--projects-only",
            type=int,
            help="Create only projects (number to create, requires clients and companies)",
        )
        parser.add_argument(
            "--invoices-only",
            type=int,
            help="Create only invoices (number to create, requires projects, clients, and companies)",
        )
        parser.add_argument(
            "--times-only",
            type=int,
            help="Create only time entries (number to create, requires projects, tasks, users, invoices, clients, and companies)",
        )

    def handle(self, *args, **options):
        # Check for --*-only flags
        users_only = options.get("users_only")
        companies_only = options.get("companies_only")
        clients_only = options.get("clients_only")
        contacts_only = options.get("contacts_only")
        projects_only = options.get("projects_only")
        invoices_only = options.get("invoices_only")
        times_only = options.get("times_only")
        
        # Determine which models to create
        any_only_flag = any([
            users_only is not None,
            companies_only is not None,
            clients_only is not None,
            contacts_only is not None,
            projects_only is not None,
            invoices_only is not None,
            times_only is not None,
        ])
        
        # Set counts based on flags or defaults
        if users_only is not None:
            num_users = users_only
            create_users = True
        else:
            num_users = options["users"]
            create_users = not any_only_flag
        
        if companies_only is not None:
            num_companies = companies_only
            create_companies = True
        else:
            num_companies = options["companies"]
            # Companies are needed as dependency for several other models
            create_companies = not any_only_flag or self._needs_dependency(
                clients_only, contacts_only, projects_only, invoices_only, times_only
            )
        
        if clients_only is not None:
            num_clients = clients_only
            create_clients = True
        else:
            num_clients = options["clients"]
            # Clients are needed as dependency for several other models
            create_clients = not any_only_flag or self._needs_dependency(
                contacts_only, projects_only, invoices_only, times_only
            )
        
        if contacts_only is not None:
            num_contacts = contacts_only
            create_contacts = True
        else:
            num_contacts = options["contacts"]
            create_contacts = not any_only_flag
        
        if projects_only is not None:
            num_projects = projects_only
            create_projects = True
        else:
            num_projects = options["projects"]
            # Projects are needed as dependency for invoices and times
            create_projects = not any_only_flag or self._needs_dependency(
                invoices_only, times_only
            )
        
        if invoices_only is not None:
            num_invoices = invoices_only
            create_invoices = True
        else:
            num_invoices = options["invoices"]
            # Invoices are needed as dependency for times
            create_invoices = not any_only_flag or times_only is not None
        
        if times_only is not None:
            num_times = times_only
            create_times = True
        else:
            num_times = options["times"]
            create_times = not any_only_flag

        # Create Users and Profiles with different rates
        users = []
        if create_users:
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
        else:
            # If not creating users, get existing users for time entries
            users = list(SiteUser.objects.all())
            if not users and times_only is not None:
                self.stdout.write(
                    self.style.WARNING("No users found. Creating 1 user for time entries.")
                )
                user = SiteUser.objects.create_user(
                    username=fake.user_name(),
                    email=fake.email(),
                    password=fake.password(),
                    rate=Decimal("100.00"),
                    mail=True,
                )
                users.append(user)

        # Create Companies
        companies = []
        if create_companies:
            for _ in range(num_companies):
                company = Company.objects.create(
                    name=fake.company(),
                    address=fake.address(),
                    description=fake.text(),
                    url=fake.url(),
                )
                companies.append(company)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created {num_companies} companies")
            )
        else:
            # If not creating companies, get existing ones for clients
            companies = list(Company.objects.all())
            if not companies and self._needs_dependency(clients_only, contacts_only, projects_only, invoices_only, times_only):
                self.stdout.write(
                    self.style.WARNING("No companies found. Creating 1 company for dependencies.")
                )
                company = Company.objects.create(
                    name=fake.company(),
                    address=fake.address(),
                    description=fake.text(),
                    url=fake.url(),
                )
                companies.append(company)

        # Create Clients
        clients = []
        if create_clients:
            for _ in range(num_clients):
                client = Client.objects.create(
                    name=fake.name(),
                    address=fake.address(),
                    description=fake.text(),
                    url=fake.url(),
                    company=random.choice(companies),
                )
                clients.append(client)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created {num_clients} clients")
            )
        else:
            # If not creating clients, get existing ones for contacts/projects
            clients = list(Client.objects.all())
            if not clients and self._needs_dependency(contacts_only, projects_only, invoices_only, times_only):
                self.stdout.write(
                    self.style.WARNING("No clients found. Creating 1 client for dependencies.")
                )
                client = Client.objects.create(
                    name=fake.name(),
                    address=fake.address(),
                    description=fake.text(),
                    url=fake.url(),
                    company=random.choice(companies),
                )
                clients.append(client)

        # Create Contacts
        contacts = []
        if create_contacts:
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

        # Create Tasks (needed for projects and time entries)
        tasks = []
        if create_projects or create_times:
            for _ in range(num_projects if create_projects else 1):  # At least 1 task for time entries
                task = Task.objects.create(
                    name=fake.sentence(),
                    rate=100,
                    unit=1,
                )
                tasks.append(task)
        else:
            # Get existing tasks if needed
            tasks = list(Task.objects.all())
            if not tasks and times_only is not None:
                self.stdout.write(
                    self.style.WARNING("No tasks found. Creating 1 task for time entries.")
                )
                task = Task.objects.create(
                    name=fake.sentence(),
                    rate=100,
                    unit=1,
                )
                tasks.append(task)

        # Create Projects
        projects = []
        if create_projects:
            for _ in range(num_projects):
                project = Project.objects.create(
                    name=fake.sentence(),
                    start_date=fake.date_this_decade(),
                    end_date=fake.date_this_decade(),
                    description=fake.text(),
                    client=random.choice(clients),
                )
                projects.append(project)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created {num_projects} projects")
            )
        else:
            # If not creating projects, get existing ones for invoices
            projects = list(Project.objects.all())
            if not projects and self._needs_dependency(invoices_only, times_only):
                self.stdout.write(
                    self.style.WARNING("No projects found. Creating 1 project for dependencies.")
                )
                project = Project.objects.create(
                    name=fake.sentence(),
                    start_date=fake.date_this_decade(),
                    end_date=fake.date_this_decade(),
                    description=fake.text(),
                    client=random.choice(clients),
                )
                projects.append(project)

        # Create Invoices (without amounts initially)
        invoices = []
        if create_invoices:
            for _ in range(num_invoices):
                invoice = Invoice.objects.create(
                    name=fake.sentence(),
                    issue_date=fake.date_this_decade(),
                    due_date=fake.date_this_decade(),
                    start_date=fake.date_this_decade(),
                    end_date=fake.date_this_decade(),
                    amount=0,
                    paid_amount=0,
                    currency="USD",
                    project=random.choice(projects),
                )
                invoices.append(invoice)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created {num_invoices} invoices")
            )
        else:
            # If not creating invoices, get existing ones for time entries
            invoices = list(Invoice.objects.all())
            if not invoices and times_only is not None:
                self.stdout.write(
                    self.style.WARNING("No invoices found. Creating 1 invoice for time entries.")
                )
                invoice = Invoice.objects.create(
                    name=fake.sentence(),
                    issue_date=fake.date_this_decade(),
                    due_date=fake.date_this_decade(),
                    start_date=fake.date_this_decade(),
                    end_date=fake.date_this_decade(),
                    amount=0,
                    paid_amount=0,
                    currency="USD",
                    project=random.choice(projects),
                )
                invoices.append(invoice)

        # Create Time Entries with calculated amounts based on user rates
        if create_times:
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
        if create_invoices or (create_times and invoices):
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
