"""Test SearchView to ensure it handles missing model correctly."""
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory

from db.views.search import SearchView

User = get_user_model()


class SearchViewTest(TestCase):
    """Test the SearchView class."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="testpass123"
        )

    def test_search_view_has_dashboard_true(self):
        """Test that SearchView has dashboard=True to prevent URL errors."""
        # This attribute prevents the dashhead.html template from trying to
        # render the "Add" button which would cause a NoReverseMatch error
        # since SearchView doesn't have a model
        self.assertTrue(SearchView.dashboard)

    def test_search_view_has_search_true(self):
        """Test that SearchView has search=True."""
        self.assertTrue(SearchView.search)

    def test_search_view_template_name(self):
        """Test that SearchView uses the correct template."""
        self.assertEqual(SearchView.template_name, "search.html")

    def test_search_view_url_index(self):
        """Test that SearchView has the correct url_index."""
        self.assertEqual(SearchView.url_index, "search_index")

    def test_search_view_get_context_includes_query(self):
        """Test that get_context_data includes the search query."""
        request = self.factory.get('/dashboard/search?q=test')
        request.user = self.superuser
        
        view = SearchView()
        view.request = request
        view.object_list = []
        
        context = view.get_context_data(object_list=[])
        
        self.assertIn('q', context)
        self.assertEqual(context['q'], 'test')

    def test_search_view_empty_query_returns_empty_queryset(self):
        """Test that an empty query returns an empty queryset."""
        request = self.factory.get('/dashboard/search')
        request.user = self.superuser
        
        view = SearchView()
        view.request = request
        
        queryset = view.get_queryset()
        
        self.assertEqual(len(queryset), 0)
