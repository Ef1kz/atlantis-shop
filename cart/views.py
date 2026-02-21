from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from products.models import Product
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required  # ← Добавь импорт
from orders.models import Order, OrderItem  # ← Добавь импорт моделей заказов
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
            request.session['cart_active'] = True

        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)

    return cart

@csrf_exempt
@require_POST
def add(request, product_id):
    try:
        cart = get_or_create_cart(request)
        product = get_object_or_404(Product, id=product_id)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            item.quantity += 1
            item.save()

        return JsonResponse({
            'success': True,
            'count': sum(i.quantity for i in cart.items.all())
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def detail(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()

    total = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'cart/detail.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total': total
    })


# 🔥 ДОБАВЛЕН checkout
def checkout(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()

    if not cart_items:
        return redirect('cart:detail')  # Если корзина пуста — назад

    total = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        # Создаём заказ
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            total_amount=total,
            delivery_address=request.POST.get('delivery_address', ''),
            phone=request.POST.get('phone', ''),
            email=request.POST.get('email', request.user.email if request.user.is_authenticated else '')
        )

        # Копируем товары из корзины в заказ
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Очищаем корзину
        cart.items.all().delete()

        return redirect('cart:checkout_success')

    # GET — показываем форму оформления
    return render(request, 'cart/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })


# 🔥 ДОБАВЛЕН checkout_success
def checkout_success(request):
    return render(request, 'cart/checkout_success.html')


def count(request):
    cart = get_or_create_cart(request)
    return JsonResponse({'count': sum(i.quantity for i in cart.items.all())})

def remove(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return redirect('cart:detail')  # Редирект обратно в корзину