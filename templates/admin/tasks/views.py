# tasks/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json
import logging

logger = logging.getLogger(__name__)

# Вспомогательная функция для получения JSON из запроса
def get_request_data(request):
    """Извлекает данные из запроса в зависимости от Content-Type"""
    if request.content_type == 'application/json':
        try:
            return json.loads(request.body)
        except json.JSONDecodeError:
            return {}
    else:
        # Для form-data или x-www-form-urlencoded
        return request.POST.dict()

@require_GET
def task_detail(request, task_id):
    """Получение деталей задачи для модального окна"""
    try:
        task = get_object_or_404(Task, id=task_id)

        # Используем get_FOO_display() для человекочитаемых значений
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description or 'Описание отсутствует',
                'status': task.status,
                'status_label': task.get_status_display(),
                'priority': task.priority,
                'priority_label': task.get_priority_display(),
                'impact': task.impact,
                'impact_label': task.get_impact_display(),
                'due_date': task.due_date.strftime('%d.%m.%Y') if task.due_date else 'Не установлен',
                'created_by': str(task.created_by) if task.created_by else 'Неизвестно',
                'assigned_to': str(task.assigned_to) if task.assigned_to else 'Не назначен',
                'created_at': task.created_at.strftime('%d.%m.%Y %H:%M') if task.created_at else '',
            }
        })
    except Exception as e:
        logger.error(f"Error in task_detail for task {task_id}: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Внутренняя ошибка сервера'
        }, status=500)

@require_POST
@csrf_exempt
def update_status(request, task_id):
    """Обновление статуса задачи через drag-and-drop"""
    try:
        logger.info(f"=== UPDATE STATUS REQUEST ===")
        logger.info(f"Task ID: {task_id}")
        logger.info(f"Method: {request.method}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Headers: {dict(request.headers)}")

        # Получаем данные
        if request.content_type == 'application/x-www-form-urlencoded':
            # Для FormData
            new_status = request.POST.get('status')
            logger.info(f"From POST data: {new_status}")
        elif request.content_type == 'application/json':
            # Для JSON
            try:
                data = json.loads(request.body)
                new_status = data.get('status')
                logger.info(f"From JSON data: {new_status}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return JsonResponse({
                    'success': False,
                    'error': 'Неверный формат JSON'
                }, status=400)
        else:
            # Пробуем из тела запроса
            try:
                body_str = request.body.decode('utf-8')
                logger.info(f"Raw body: {body_str}")

                # Пробуем разные форматы
                if 'status=' in body_str:
                    new_status = body_str.split('status=')[1]
                    if '&' in new_status:
                        new_status = new_status.split('&')[0]
                else:
                    # Возможно это просто статус
                    new_status = body_str
            except Exception as e:
                logger.error(f"Error parsing body: {e}")
                new_status = None

        logger.info(f"Parsed status: {new_status}")

        if not new_status:
            logger.error("No status provided")
            return JsonResponse({
                'success': False,
                'error': 'Статус не указан'
            }, status=400)

        # Получаем задачу
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            logger.error(f"Task {task_id} not found")
            return JsonResponse({
                'success': False,
                'error': 'Задача не найдена'
            }, status=404)

        # Проверяем валидность статуса
        valid_statuses = [choice[0] for choice in Task.STATUS_CHOICES]
        if new_status not in valid_statuses:
            logger.error(f"Invalid status: {new_status}. Valid: {valid_statuses}")
            return JsonResponse({
                'success': False,
                'error': f'Неверный статус. Допустимые значения: {", ".join(valid_statuses)}'
            }, status=400)

        # Сохраняем старый статус для логирования
        old_status = task.status

        # Обновляем статус
        task.status = new_status
        task.save()

        logger.info(f"Task {task_id} updated: {old_status} -> {new_status}")

        return JsonResponse({
            'success': True,
            'message': 'Статус обновлен',
            'task': {
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'status_label': task.get_status_display()
            }
        })

    except Exception as e:
        logger.error(f"Unexpected error in update_status: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Внутренняя ошибка сервера'
        }, status=500)

def task_list(request):
    """Просто для тестирования"""
    tasks = Task.objects.all()
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

@require_GET
@csrf_exempt
def test_endpoint(request):
    """Простой тестовый эндпоинт"""
    return JsonResponse({
        'success': True,
        'message': 'Test endpoint works',
        'method': request.method,
        'content_type': request.content_type,
        'headers': dict(request.headers)
    })

@require_POST
@csrf_exempt
def test_post(request):
    """Тестовый POST эндпоинт"""
    logger.info("=== TEST POST ===")
    logger.info(f"Content-Type: {request.content_type}")
    logger.info(f"POST data: {dict(request.POST)}")
    logger.info(f"Body: {request.body.decode('utf-8')}")

    return JsonResponse({
        'success': True,
        'message': 'POST works',
        'received_data': {
            'post': dict(request.POST),
            'body': request.body.decode('utf-8'),
            'content_type': request.content_type
        }
    })
