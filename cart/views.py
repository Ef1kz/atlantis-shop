# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from products.models import Product
from orders.models import Order, OrderItem

@require_POST
def cart_add(request, product_id):
    """Добавление товара в корзину"""
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    cart = dict(cart)

    product_id_str = str(product_id)
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1
        }

    request.session['cart'] = cart
    request.session.modified = True
    print(">>> СЕССИЯ ПОСЛЕ ДОБАВЛЕНИЯ:", request.session.get('cart'))

    return redirect('cart:detail')


def cart_detail(request):
    """Просмотр корзины"""
    cart = request.session.get('cart', {})
    print(">>> СЕССИЯ В КОРЗИНЕ:", cart)

    cart_items = []
    total = 0
    for product_id, item in cart.items():
        try:
            price = float(item['price'])
            quantity = item['quantity']
            subtotal = price * quantity
            total += subtotal
            cart_items.append({
                'product_id': product_id,
                'name': item['name'],
                'price': price,
                'quantity': quantity,
                'subtotal': subtotal
            })
        except (KeyError, ValueError):
            continue

    return render(request, 'cart/detail.html', {
        'cart_items': cart_items,
        'total': total
    })


def cart_count(request):
    """Получение количества товаров в корзине (для AJAX)"""
    cart = request.session.get('cart', {})
    count = sum(item.get('quantity', 0) for item in cart.values())
    return JsonResponse({'count': count})


@login_required
def cart_checkout(request):
    """Оформление заказа"""
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart:detail')

    if request.method == 'POST':
        address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')

        # Создаем заказ
        order = Order.objects.create(
            user=request.user,
            status='pending',
            total_amount=0,
            delivery_address=address,
            phone=phone
        )

        total = 0
        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                price = float(item['price'])
                quantity = item['quantity']
                subtotal = price * quantity
                total += subtotal

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price
                )
            except Product.DoesNotExist:
                continue

        order.total_amount = total
        order.save()

        # Очищаем корзину
        request.session['cart'] = {}
        request.session.modified = True

        return redirect('cart:checkout_success')

    return render(request, 'cart/checkout.html')


def checkout_success(request):
    """Страница успешного оформления заказа"""
    return render(request, 'cart/checkout_success.html')