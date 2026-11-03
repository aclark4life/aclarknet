"""Tests for the grouped (current / past-by-year) client and project lists."""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from db.models import Client, Project

User = get_user_model()


def group_names(response):
    return {
        g["label"]: {row[2][1] for row in g["rows"]} for g in response.context["groups"]
    }


class GroupedListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="pass"
        )
        self.client.force_login(self.user)
        today = timezone.localdate()

        self.active = Client.objects.create(name="Active Co")
        self.old = Client.objects.create(name="Old Co")
        self.idle = Client.objects.create(name="Idle Co")

        Project.objects.create(
            name="Ongoing", client=self.active, start_date=today - timedelta(days=30)
        )
        Project.objects.create(
            name="Finished",
            client=self.active,
            start_date=date(2016, 1, 1),
            end_date=date(2016, 6, 30),
        )
        Project.objects.create(
            name="Legacy",
            client=self.old,
            start_date=date(2015, 3, 1),
            end_date=date(2015, 9, 30),
        )

    def test_project_groups(self):
        response = self.client.get(reverse("project_index"))
        self.assertEqual(
            group_names(response),
            {"Current": {"Ongoing"}, "2016": {"Finished"}, "2015": {"Legacy"}},
        )
        self.assertEqual(
            response.context["table_headers"],
            ["type", "id", "name", "client", "start_date", "end_date", "amount"],
        )

    def test_client_groups(self):
        response = self.client.get(reverse("client_index"))
        self.assertEqual(
            group_names(response),
            {"Current": {"Active Co"}, "2015": {"Old Co"}, "No projects": {"Idle Co"}},
        )
        self.assertEqual([g["open"] for g in response.context["groups"]], [True, False, False])

    def test_project_ending_today_is_current(self):
        project = Project(end_date=timezone.localdate())
        self.assertTrue(project.is_current())

    def test_open_ended_project_is_current_for_a_year(self):
        today = timezone.localdate()
        recent = Project(start_date=today - timedelta(days=200))
        stale = Project(start_date=date(2013, 5, 15))
        self.assertTrue(recent.is_current(today))
        self.assertFalse(stale.is_current(today))
        self.assertEqual(stale.last_date, date(2013, 5, 15))
