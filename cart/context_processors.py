# cart/context_processors.py
def cart(request):
    """
    Контекст-процессор для отображения количества товаров в корзине.
    Безопасен для работы до полной настройки корзины.
    """
    try:
        from cart.models import Cart

        cart_items_count = 0

        if request.user.is_authenticated:
            # Для авторизованных пользователей ищем корзину по пользователю
            cart_obj = Cart.objects.filter(user=request.user).first()
        else:
            # Для анонимных пользователей ищем по ключу сессии
            session_key = request.session.session_key
            if session_key:
                cart_obj = Cart.objects.filter(session_key=session_key).first()
            else:
                cart_obj = None

        # Считаем количество товаров в корзине
        if cart_obj and hasattr(cart_obj, 'items'):
            cart_items_count = cart_obj.items.count()

        return {'cart_items_count': cart_items_count}

    except Exception:
        # При любой ошибке (миграции не применены, модель не загружена и т.д.)
        # возвращаем 0, чтобы не сломать весь сайт
        return {'cart_items_count': 0}