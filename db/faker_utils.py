"""Utility functions for generating fake data in DEBUG mode."""

from django.conf import settings


def get_faker():
    """Get Faker instance only if in DEBUG mode and Faker is available."""
    if not settings.DEBUG:
        return None

    try:
        from faker import Faker

        return Faker()
    except ImportError:
        return None


def get_fake_client_data():
    """Generate fake data for Client model."""
    fake = get_faker()
    if not fake:
        return {}

    return {
        "name": fake.company(),
        "description": fake.catch_phrase(),
        "url": fake.url(),
    }


def get_fake_company_data():
    """Generate fake data for Company model."""
    fake = get_faker()
    if not fake:
        return {}

    return {
        "name": fake.company(),
        "address": fake.address(),
        "description": fake.catch_phrase(),
        "url": fake.url(),
    }


def get_fake_contact_data():
    """Generate fake data for Contact model."""
    fake = get_faker()
    if not fake:
        return {}

    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "number": fake.phone_number(),
        "url": fake.url(),
    }


def get_fake_project_data():
    """Generate fake data for Project model."""
    fake = get_faker()
    if not fake:
        return {}

    return {
        "name": fake.catch_phrase(),
        "description": fake.text(max_nb_chars=200),
    }


def get_fake_task_data():
    """Generate fake data for Task model."""
    fake = get_faker()
    if not fake:
        return {}

    return {
        "name": fake.bs(),
        "rate": fake.random_int(min=50, max=200),
        "unit": 1,
    }


def get_fake_invoice_data():
    """Generate fake data for Invoice model."""
    fake = get_faker()
    if not fake:
        return {}

    return {
        "subject": fake.catch_phrase(),
        "name": fake.sentence(nb_words=4),
    }


def get_fake_time_data():
    """Generate fake data for Time model."""
    fake = get_faker()
    if not fake:
        return {}

    return {
        "description": fake.sentence(),
        "hours": fake.random_int(min=1, max=8),
    }


def get_fake_note_data():
    """Generate fake data for Note model."""
    fake = get_faker()
    if not fake:
        return {}

    return {
        "title": fake.sentence(nb_words=4),
        "text": fake.text(max_nb_chars=500),
    }
