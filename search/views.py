"""Search views for Wagtail pages."""

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse

from wagtail.models import Page

# To enable logging of search queries for use with the "Promoted search results" module
# <https://docs.wagtail.org/en/stable/reference/contrib/searchpromotions.html>
# uncomment the following line and enable in search function below
# (after adding wagtail.contrib.search_promotions to INSTALLED_APPS):

# from wagtail.contrib.search_promotions.models import Query


RESULTS_PER_PAGE = 10


def search(request):
    """
    Handle search requests for Wagtail pages.
    
    Args:
        request: HTTP request with optional 'query' and 'page' GET parameters
        
    Returns:
        TemplateResponse with search results and pagination
    """
    search_query = request.GET.get("query", None)
    page = request.GET.get("page", 1)

    # Perform search if query provided
    if search_query:
        search_results = Page.objects.live().search(search_query)

        # Optional: Log search query for promoted results module
        # Uncomment after enabling wagtail.contrib.search_promotions:
        # query = Query.get(search_query)
        # query.add_hit()

    else:
        search_results = Page.objects.none()

    # Paginate results
    paginator = Paginator(search_results, RESULTS_PER_PAGE)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return TemplateResponse(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results": search_results,
        },
    )
