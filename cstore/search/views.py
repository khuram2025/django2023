from django.contrib.postgres.search import SearchQuery, SearchRank
from django.http import HttpResponse
from django.shortcuts import render
from companies.models import CompanyProfile

from product.models import Product

from django.conf import settings
from django.db.models import Q

def search(request):
    query_string = request.GET.get('sPattern', '')
    print("Search query received:", query_string)

    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
        print("Using PostgreSQL search") # Diagnostic print
        query = SearchQuery(query_string)
        
        product_results = Product.objects.annotate(
            rank=SearchRank('search_vector', query)
        ).filter(rank__gte=0.3).order_by('-rank')

        company_results = CompanyProfile.objects.annotate(
            rank=SearchRank('search_vector', query)
        ).filter(rank__gte=0.3).order_by('-rank')
    else:
        print("Using SQLite search")  # Diagnostic print
        product_results = Product.objects.filter(
            Q(title__icontains=query_string) | Q(description__icontains=query_string)
        )
        company_results = CompanyProfile.objects.filter(
            Q(name__icontains=query_string) | Q(about__icontains=query_string)
        )
    print("Number of products found:", product_results.count())  # Diagnostic print
    print("Number of companies found:", company_results.count())  # Diagnostic print

    return render(request, 'home/search.html', {
        'product_results': product_results,
        'company_results': company_results
    })
