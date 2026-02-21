# products/views.py
from django.shortcuts import render
from .models import Product
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from reviews.forms import ReviewForm
from reviews.models import Review

def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'products/list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.filter(is_approved=True)  # Только одобренные

    review_form = None
    has_reviewed = False

    if request.user.is_authenticated:
        if Review.objects.filter(product=product, user=request.user).exists():
            has_reviewed = True
        else:
            review_form = ReviewForm()

    return render(request, 'products/detail.html', {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'has_reviewed': has_reviewed,
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