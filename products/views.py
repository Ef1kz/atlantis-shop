# products/views.py
from django.shortcuts import render
from .models import Product

def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'products/list.html', {'products': products})

def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    reviews = product.reviews.all()
    return render(request, 'products/detail.html', {
        'product': product,
        'reviews': reviews
    })

def product_list_by_collection(request, collection_slug):
    # Чёткое соответствие slug → название коллекции
    slug_to_name = {
        'vanny': 'ВАННЫ',
        'rakoviny': 'РАКОВИНЫ',
        'unitazy-i-bide': 'УНИТАЗЫ И БИДЕ',
        'smesiteli': 'СМЕСИТЕЛИ'
    }

    collection_name = slug_to_name.get(collection_slug)
    if not collection_name:
        from django.http import Http404
        raise Http404("Категория не найдена")

    products = Product.objects.filter(category__name=collection_name).order_by('-created_at')
    return render(request, 'products/list.html', {
        'products': products,
        'category_title': collection_name
    })