from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from faker import Faker
import random


class Command(BaseCommand):
    help = "Generate fake data for a given model using Faker."

    def add_arguments(self, parser):
        parser.add_argument("model", type=str, help="Name of the model (e.g., Company)")
        parser.add_argument("n", type=int, help="Number of instances to create")

    def handle(self, *args, **options):
        model_name = options["model"]
        n = options["n"]

        # Get model dynamically from all registered apps
        try:
            model = apps.get_model(app_label="db", model_name=model_name)
        except LookupError:
            # Try to find the model in any app if app_label not specified
            for app_config in apps.get_app_configs():
                try:
                    model = app_config.get_model(model_name)
                    break
                except LookupError:
                    continue
            else:
                raise CommandError(
                    f"Model '{model_name}' not found in any installed app."
                )

        fake = Faker()
        created = []

        # Add support for known model types (start with Company)
        if model_name.lower() == "company":
            for _ in range(n):
                instance = model.objects.create(
                    name=fake.company(),
                    address=fake.address(),
                    website=fake.url(),
                )
                created.append(instance)
        else:
            raise CommandError(f"Model '{model_name}' is not yet supported.")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {len(created)} {model_name}(s).")
        )
