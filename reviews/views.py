# reviews/views.py
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import Review
from .forms import ReviewForm

@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                Review.objects.get(product=product, user=request.user)
                messages.error(request, 'Вы уже оставляли отзыв на этот товар.')
            except Review.DoesNotExist:
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.is_approved = False  # На модерацию
                review.save()
                messages.success(request, 'Ваш отзыв отправлен на модерацию. Спасибо!')
            return redirect('products:product_detail', pk=pk)
    else:
        form = ReviewForm()

    # Если GET — редирект на деталку (форма будет там)
    return redirect('products:product_detail', pk=pk)