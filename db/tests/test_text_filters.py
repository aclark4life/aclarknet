"""Tests for text_filters template tags."""
from django.test import TestCase
from db.templatetags.text_filters import title_case, format_field_value


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


class FormatFieldValueFilterTest(TestCase):
    """Test the format_field_value template filter."""

    def test_currency_field_formatting(self):
        """Test that currency fields are formatted with USD currency."""
        # Test amount field
        result = format_field_value(100.50, 'amount')
        self.assertIn('100', result)  # Should contain the number
        
        # Test paid_amount field
        result = format_field_value(250.75, 'paid_amount')
        self.assertIn('250', result)
        
        # Test cost field
        result = format_field_value(50.25, 'cost')
        self.assertIn('50', result)
        
        # Test net field
        result = format_field_value(150.00, 'net')
        self.assertIn('150', result)
        
        # Test balance field
        result = format_field_value(75.50, 'balance')
        self.assertIn('75', result)

    def test_currency_field_with_none_value(self):
        """Test that currency fields default to 0 when value is None."""
        result = format_field_value(None, 'amount')
        # Should format 0 as currency
        self.assertIn('0', result)

    def test_hours_field_formatting(self):
        """Test that hours field displays numeric value."""
        result = format_field_value(10, 'hours')
        self.assertEqual(result, 10)
        
        result = format_field_value(25.5, 'hours')
        self.assertEqual(result, 25.5)

    def test_hours_field_with_none_value(self):
        """Test that hours field defaults to 0 when value is None."""
        result = format_field_value(None, 'hours')
        self.assertEqual(result, 0)

    def test_regular_field_formatting(self):
        """Test that regular fields are displayed as-is."""
        result = format_field_value('Test Name', 'name')
        self.assertEqual(result, 'Test Name')
        
        result = format_field_value('http://example.com', 'url')
        self.assertEqual(result, 'http://example.com')
        
        result = format_field_value('Description text', 'description')
        self.assertEqual(result, 'Description text')

    def test_regular_field_with_none_value(self):
        """Test that regular fields default to empty string when value is None."""
        result = format_field_value(None, 'name')
        self.assertEqual(result, '')
        
        result = format_field_value(None, 'description')
        self.assertEqual(result, '')
