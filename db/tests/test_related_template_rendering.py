"""Integration test to verify template rendering with 'in' operator."""

from django.template import Context, Template
from django.test import TestCase


class RelatedTemplateRenderingTest(TestCase):
    """Test that the related.html template renders correctly with 'in' operator."""

    def test_in_operator_works_in_template(self):
        """Verify Django template 'in' operator works with list membership."""
        template_str = """
        {% for field_name, field_value in field_values %}
            {% if field_name in related_title_fields %}TITLE:{{ field_name }}{% endif %}
        {% endfor %}
        """
        template = Template(template_str)
        
        field_values = [
            ("name", "Test Name"),
            ("description", "Test Desc"),
            ("url", "http://test.com"),
        ]
        
        context = Context({
            "field_values": field_values,
            "related_title_fields": ["name", "title", "subject", "description"],
        })
        
        result = template.render(context)
        
        # Should show name and description as title fields
        self.assertIn("TITLE:name", result)
        self.assertIn("TITLE:description", result)
        # Should not show url as title field
        self.assertNotIn("TITLE:url", result)

    def test_not_in_operator_works_in_template(self):
        """Verify Django template 'not in' operator works with list membership."""
        template_str = """
        {% for field_name, field_value in field_values %}
            {% if field_name not in related_excluded_fields %}SHOW:{{ field_name }}{% endif %}
        {% endfor %}
        """
        template = Template(template_str)
        
        field_values = [
            ("type", "client"),
            ("id", "123"),
            ("name", "Test Name"),
            ("url", "http://test.com"),
        ]
        
        context = Context({
            "field_values": field_values,
            "related_excluded_fields": ["type", "id", "item"],
        })
        
        result = template.render(context)
        
        # Should show name and url (not excluded)
        self.assertIn("SHOW:name", result)
        self.assertIn("SHOW:url", result)
        # Should not show type and id (excluded)
        self.assertNotIn("SHOW:type", result)
        self.assertNotIn("SHOW:id", result)

    def test_combined_in_and_not_in_operators(self):
        """Test combined 'in' and 'not in' logic matches our template."""
        template_str = """
        {% for field_name, field_value in field_values %}
            {% if field_name not in related_excluded_fields and field_name not in related_title_fields and field_value %}BODY:{{ field_name }}{% endif %}
        {% endfor %}
        """
        template = Template(template_str)
        
        field_values = [
            ("type", "client"),  # excluded
            ("id", "123"),  # excluded
            ("name", "Test Name"),  # title field
            ("description", "Test Desc"),  # title field
            ("url", "http://test.com"),  # should show in body
            ("email", "test@example.com"),  # should show in body
        ]
        
        context = Context({
            "field_values": field_values,
            "related_title_fields": ["name", "title", "subject", "description"],
            "related_excluded_fields": ["type", "id", "item"],
        })
        
        result = template.render(context)
        
        # Should only show url and email in body (not excluded, not title fields)
        self.assertIn("BODY:url", result)
        self.assertIn("BODY:email", result)
        # Should not show excluded fields
        self.assertNotIn("BODY:type", result)
        self.assertNotIn("BODY:id", result)
        # Should not show title fields in body
        self.assertNotIn("BODY:name", result)
        self.assertNotIn("BODY:description", result)

    def test_actual_related_template_pattern(self):
        """Test the exact pattern used in related.html template."""
        # This is a simplified version of the actual template logic
        template_str = """
        {% for field_values in field_values_page %}
          {% for field_name, field_value in field_values %}
            {% if field_name in related_title_fields %}
              <h5>{{ field_value }}</h5>
            {% endif %}
            {% if field_name not in related_excluded_fields and field_name not in related_title_fields and field_value %}
              <div>{{ field_name }}: {{ field_value }}</div>
            {% endif %}
          {% endfor %}
        {% endfor %}
        """
        template = Template(template_str)
        
        field_values_page = [
            [
                ("type", "client"),
                ("id", 1),
                ("name", "ACME Corp"),
                ("url", "http://acme.com"),
            ],
        ]
        
        context = Context({
            "field_values_page": field_values_page,
            "related_title_fields": ["name", "title", "subject", "description"],
            "related_excluded_fields": ["type", "id", "item"],
        })
        
        result = template.render(context)
        
        # Title should contain the name
        self.assertIn("<h5>ACME Corp</h5>", result)
        # Body should contain the url
        self.assertIn("<div>url: http://acme.com</div>", result)
        # Should not show type or id
        self.assertNotIn("type:", result)
        self.assertNotIn("<div>id:", result)
