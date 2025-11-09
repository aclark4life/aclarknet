from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from faker import Faker
import random
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Create fake data for relational models (Company, Client, Project, Invoice, Time, Task, User/Employee)."

    def add_arguments(self, parser):
        parser.add_argument("model", type=str, help="Name of the model (e.g., Company)")
        parser.add_argument("n", type=int, help="Number of model instances to create")
        parser.add_argument(
            "--clients",
            type=int,
            default=1,
            help="Number of clients per company (default: 1)",
        )
        parser.add_argument(
            "--projects",
            type=int,
            default=1,
            help="Number of projects per client (default: 1)",
        )
        parser.add_argument(
            "--invoices",
            type=int,
            default=1,
            help="Number of invoices per project (default: 1)",
        )
        parser.add_argument(
            "--times",
            type=int,
            default=1,
            help="Number of time entries per invoice (default: 1)",
        )
        parser.add_argument(
            "--tasks",
            type=int,
            default=1,
            help="Number of task types to create (default: 1)",
        )
        parser.add_argument(
            "--users",
            type=int,
            default=1,
            help="Number of users/employees to create (default: 1)",
        )

    def handle(self, *args, **options):
        model_name = options["model"]
        n = options["n"]
        num_clients = options["clients"]
        num_projects = options["projects"]
        num_invoices = options["invoices"]
        num_times = options["times"]
        num_tasks = options["tasks"]
        num_users = options["users"]

        fake = Faker()

        # Locate model dynamically
        try:
            apps.get_model(app_label="db", model_name=model_name)
        except LookupError:
            for app_config in apps.get_app_configs():
                try:
                    app_config.get_model(model_name)
                    break
                except LookupError:
                    continue
            else:
                raise CommandError(
                    f"Model '{model_name}' not found in any installed app."
                )

        created = []

        if model_name.lower() == "company":
            from db.models import (
                Company,
                Client,
                Project,
                Invoice,
                Time,
                Task,
                Employee,
            )

            # -------------------------
            # Create Users/Employees
            # -------------------------
            user_list = []
            for _ in range(num_users):
                user = User.objects.create_user(
                    username=fake.user_name(),
                    email=fake.email(),
                    password="password123",  # default password
                )
                # Create Employee profile and set hourly rate
                Employee.objects.create(
                    user=user,
                    hourly_rate=round(random.uniform(25, 150), 2),
                )
                user_list.append(user)

            # -------------------------
            # Create Tasks
            # -------------------------
            task_list = []
            for _ in range(num_tasks):
                task = Task.objects.create(
                    name=fake.job(),
                    hourly_rate=round(random.uniform(25, 150), 2),
                    description=fake.text(max_nb_chars=100),
                )
                task_list.append(task)

            # -------------------------
            # Create Companies/Clients/Projects/Invoices/Times
            # -------------------------
            for _ in range(n):
                company = Company.objects.create(
                    name=fake.company(),
                    address=fake.address(),
                    website=fake.url(),
                )

                for _ in range(num_clients):
                    client = Client.objects.create(
                        company=company,
                        name=fake.company(),
                        email=fake.email(),
                        phone=fake.phone_number(),
                        address=fake.address(),
                    )

                    for _ in range(num_projects):
                        project = Project.objects.create(
                            client=client,
                            name=fake.bs().title(),
                            description=fake.text(max_nb_chars=120),
                            start_date=fake.date_this_decade(),
                            rate=round(random.uniform(25, 150), 2),
                            end_date=fake.date_between(
                                start_date="+30d", end_date="+180d"
                            ),
                        )

                        for _ in range(num_invoices):
                            invoice = Invoice.objects.create(
                                project=project,
                                number=str(fake.random_int(1000, 9999)),
                                date=fake.date_this_year(),
                                amount=round(random.uniform(100, 5000), 2),
                            )

                            times = [
                                Time(
                                    invoice=invoice,
                                    task=random.choice(task_list),
                                    user=random.choice(user_list),
                                    date=fake.date_this_year(),
                                    hours=round(random.uniform(0.5, 8.0), 2),
                                    description=fake.sentence(nb_words=6),
                                )
                                for _ in range(num_times)
                            ]
                            Time.objects.bulk_create(times)

                created.append(company)

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Created {len(created)} Company(ies) with "
                    f"{num_clients} Client(s) per company, {num_projects} Project(s) per client, "
                    f"{num_invoices} Invoice(s) per project, {num_times} Time entry(ies) per invoice, "
                    f"{num_tasks} Task type(s), and {num_users} Users/Employees."
                )
            )

        else:
            raise CommandError(f"Model '{model_name}' is not yet supported.")
