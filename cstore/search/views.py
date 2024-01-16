from django.shortcuts import render
from .documents import ProductDocument  # Make sure this import is correct

def search_view(request):
    query = request.GET.get('sPattern', '')
    print("Search query received:", query)  # Print the received query

    if query:
        search = ProductDocument.search().query("match", title=query)
        response = search.execute()
        results = [{'pk': hit.meta.id, **hit.to_dict()} for hit in response]

        print("Number of results:", len(results))  # Print the number of results
        for res in results:
            print(res)  # Print each result
        for product in results:
            print(product.get('images'))  # Adjust based on how images are stored

    else:
        results = []
    

    return render(request, 'home/search_results.html', {'results': results})
