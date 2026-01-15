"""Tests for text_filters template tags."""
from django.test import TestCase
from db.templatetags.text_filters import title_case


class TitleCaseFilterTest(TestCase):
    """Test the title_case template filter."""

    def test_snake_case_to_title_case(self):
        """Test converting snake_case to Title Case."""
        self.assertEqual(title_case('first_name'), 'First Name')
        self.assertEqual(title_case('last_name'), 'Last Name')
        self.assertEqual(title_case('start_date'), 'Start Date')
        self.assertEqual(title_case('end_date'), 'End Date')
        self.assertEqual(title_case('is_active'), 'Is Active')
        self.assertEqual(title_case('paid_amount'), 'Paid Amount')

    def test_single_word(self):
        """Test single words are capitalized."""
        self.assertEqual(title_case('name'), 'Name')
        self.assertEqual(title_case('url'), 'Url')
        self.assertEqual(title_case('description'), 'Description')

    def test_empty_and_none(self):
        """Test handling of empty strings and None."""
        self.assertEqual(title_case(''), '')
        self.assertEqual(title_case(None), None)

    def test_multiple_underscores(self):
        """Test handling of multiple underscores."""
        self.assertEqual(title_case('created_at_time'), 'Created At Time')
        self.assertEqual(title_case('user_email_address'), 'User Email Address')
