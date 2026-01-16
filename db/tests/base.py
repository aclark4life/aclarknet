from django.test import TestCase
from django.utils import timezone

from db.models import BaseModel


# Create a subclass of BaseModel for testing
class TestModel(BaseModel):
    pass


class BaseModelTest(TestCase):
    def setUp(self):
        self.base_model = TestModel.objects.create(
            name="Test Name",
        )

    def test_created_field(self):
        self.assertIsInstance(self.base_model.created, timezone.datetime)
        # self.assertGreaterEqual(self.base_model.created, timezone.now())

    def test_updated_field(self):
        self.assertIsInstance(self.base_model.updated, timezone.datetime)
        # self.assertGreaterEqual(self.base_model.updated, timezone.now())

    def test_name_field(self):
        self.assertEqual(self.base_model.name, "Test Name")

    def test_save_method_updates_updated_field(self):
        original_updated = self.base_model.updated
        self.base_model.save()
        self.assertNotEqual(original_updated, self.base_model.updated)

    def test_get_model_name(self):
        self.assertEqual(self.base_model.get_model_name(), "test model")

    def test_str_method(self):
        self.assertEqual(str(self.base_model), "Test Name")

    def test_get_absolute_url_raises_notimplementederror(self):
        with self.assertRaises(NotImplementedError):
            self.base_model.get_absolute_url()
