from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from faker import Faker
import random


class Command(BaseCommand):
    help = "Generate fake data for a given model (with embedded submodels if applicable)."

    def add_arguments(self, parser):
        parser.add_argument("model", type=str, help="Name of the model (e.g., Company)")
        parser.add_argument("n", type=int, help="Number of model instances to create")
        parser.add_argument(
            "--projects",
            type=int,
            default=3,
            help="Number of projects to embed in each company (default: 3)",
        )

    def handle(self, *args, **options):
        model_name = options["model"]
        n = options["n"]
        num_projects = options["projects"]

        fake = Faker()

        # Try to locate the model dynamically from all apps
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
            # Import your embedded model
            from db.models import Project

            for _ in range(n):
                # Create embedded Project objects
                projects = [
                    Project(
                        name=fake.bs().title(),
                        description=fake.text(max_nb_chars=120),
                        start_date=fake.date_this_decade(),
                        end_date=fake.date_between(start_date="+30d", end_date="+180d"),
                    )
                    for _ in range(num_projects)
                ]

                # Create the Company with embedded projects
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
                    f"each with {num_projects} Project(s)."
                )
            )

        else:
            raise CommandError(f"Model '{model_name}' is not yet supported.")
