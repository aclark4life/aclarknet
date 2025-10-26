from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from faker import Faker
import random
from datetime import timedelta, date

class Command(BaseCommand):
    help = "Create fake data for a given model with embedded submodels (projects, invoices, times)."

    def add_arguments(self, parser):
        parser.add_argument("model", type=str, help="Name of the model (e.g., Company)")
        parser.add_argument("n", type=int, help="Number of model instances to create")
        parser.add_argument(
            "--projects",
            type=int,
            default=3,
            help="Number of projects to embed in each company (default: 3)",
        )
        parser.add_argument(
            "--invoices",
            type=int,
            default=2,
            help="Number of invoices to embed in each project (default: 2)",
        )
        parser.add_argument(
            "--times",
            type=int,
            default=5,
            help="Number of time entries to embed in each invoice (default: 5)",
        )

    def handle(self, *args, **options):
        model_name = options["model"]
        n = options["n"]
        num_projects = options["projects"]
        num_invoices = options["invoices"]
        num_times = options["times"]

        fake = Faker()

        # Locate model dynamically
        try:
            model = apps.get_model(app_label="db", model_name=model_name)
        except LookupError:
            for app_config in apps.get_app_configs():
                try:
                    model = app_config.get_model(model_name)
                    break
                except LookupError:
                    continue
            else:
                raise CommandError(f"Model '{model_name}' not found in any installed app.")

        created = []

        if model_name.lower() == "company":
            # Import embedded models
            from db.models import Project, Invoice, Time

            for _ in range(n):
                projects = []

                for _ in range(num_projects):
                    invoices = []

                    for _ in range(num_invoices):
                        # Create embedded Time entries
                        times = [
                            Time(
                                date=fake.date_this_year(),
                                hours=round(random.uniform(0.5, 8.0), 2),
                                description=fake.sentence(nb_words=6),
                            )
                            for _ in range(num_times)
                        ]

                        # Create invoice with embedded times
                        invoice = Invoice(
                            number=f"{fake.random_int(1000, 9999)}",
                            date=fake.date_this_year(),
                            amount=round(random.uniform(100, 5000), 2),
                            times=times,
                        )
                        invoices.append(invoice)

                    # Create project with embedded invoices
                    project = Project(
                        name=fake.bs().title(),
                        description=fake.text(max_nb_chars=120),
                        start_date=fake.date_this_decade(),
                        end_date=fake.date_between(start_date="+30d", end_date="+180d"),
                        invoices=invoices,
                    )
                    projects.append(project)

                # Create company with embedded projects
                company = model.objects.create(
                    name=fake.company(),
                    address=fake.address(),
                    website=fake.url(),
                    projects=projects,
                )
                created.append(company)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {len(created)} Company(ies), "
                    f"each with {num_projects} Project(s), {num_invoices} Invoice(s) per project, "
                    f"and {num_times} Time entry(ies) per invoice."
                )
            )

        else:
            raise CommandError(f"Model '{model_name}' is not yet supported.")

