def get_app_list(self, request):
    app_list = super().get_app_list(request)
    new_app_list = []
    category_model = None

    # Сначала ищем категории в продуктах, чтобы сохранить ссылку
    for app in app_list:
        if app['app_label'] == 'products':
            for model in app['models']:
                if model['object_name'].lower() == 'category':
                    category_model = model

    for app in app_list:
        # Очищаем вложенные модели сразу, чтобы они не рисовались (те самые кнопки на англ)
        app_label = app['app_label']

        # Настраиваем ссылки для заголовков
        if app_label == 'tasks':
            app['app_url'] = '/admin/tasks/task/?view=kanban' # ЗАДАЧИ -> Канбан
        elif app_label == 'products':
            app['app_url'] = '/admin/products/product/'      # ТОВАРЫ -> Список товаров
        elif app_label == 'orders':
            app['app_url'] = '/admin/orders/order/'          # ЗАКАЗЫ -> Список заказов
        elif app_label == 'accounts':
            app['app_url'] = '/admin/accounts/customuser/'   # ПОЛЬЗОВАТЕЛИ -> Список юзеров
        elif app_label == 'cart':
            app['app_url'] = '/admin/cart/cart/'             # КОРЗИНЫ
        elif app_label == 'reviews':
            app['app_url'] = '/admin/reviews/review/'        # ОТЗЫВЫ
        elif app['models']:
            # Для всех остальных — ведем на первую модель в списке
            app['app_url'] = app['models'][0]['admin_url']

        # ГЛАВНОЕ: Убиваем вложенные пункты, чтобы не было "смешного" раскрытия
        app['models'] = []
        new_app_list.append(app)

    # Добавляем КАТЕГОРИИ отдельной большой кнопкой
    if category_model:
        new_app_list.insert(2, {
            'name': 'КАТЕГОРИИ',
            'app_label': 'categories_custom',
            'app_url': category_model['admin_url'],
            'models': [],
            'has_module_perms': True,
        })

    return new_app_list