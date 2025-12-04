# api/views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
from products.models import Product
from orders.models import Order, OrderItem

@require_http_methods(["GET"])
def api_products(request):
    """GET /api/products/ — список товаров"""
    products = Product.objects.all()
    data = []
    for p in products:
        data.append({
            'id': p.id,
            'name': p.name,
            'price': float(p.price),
            'collection': p.collection,
            'color': p.color,
            'width': float(p.width) if p.width else None,
            'height': float(p.height) if p.height else None,
            'depth': float(p.depth) if p.depth else None,
            'image': request.build_absolute_uri(p.image.url) if p.image else None,
        })
    return JsonResponse({'products': data}, safe=False)

@csrf_exempt
@require_http_methods(["POST"])
def api_cart_add(request):
    """POST /api/cart/add/ — добавить в корзину (требует product_id в теле)"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        if not product_id:
            return JsonResponse({'error': 'product_id is required'}, status=400)

        product = get_object_or_404(Product, id=product_id)

        cart = request.session.get('cart', {})
        cart = dict(cart)
        pid = str(product_id)

        if pid in cart:
            cart[pid]['quantity'] += 1
        else:
            cart[pid] = {
                'name': product.name,
                'price': str(product.price),
                'quantity': 1
            }

        request.session['cart'] = cart
        request.session.modified = True

        return JsonResponse({'message': 'Товар добавлен в корзину', 'cart_count': sum(i['quantity'] for i in cart.values())})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def api_order_create(request):
    """POST /api/orders/create/ — создать заказ из корзины"""
    cart = request.session.get('cart', {})
    if not cart:
        return JsonResponse({'error': 'Корзина пуста'}, status=400)

    try:
        data = json.loads(request.body)
        address = data.get('address', '')
        phone = data.get('phone', '')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    order = Order.objects.create(
        user=request.user,
        status='pending',
        total_amount=0
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

    request.session['cart'] = {}
    request.session.modified = True

    return JsonResponse({
        'message': 'Заказ создан',
        'order_id': order.id,
        'status': order.get_status_display(),
        'total': float(order.total_amount)
    })