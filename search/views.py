"""Search views for Wagtail pages."""

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse

from wagtail.models import Page


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
