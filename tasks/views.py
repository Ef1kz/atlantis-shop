# tasks/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from .models import Task
import json
import logging

logger = logging.getLogger(__name__)

@require_GET
@require_GET
def task_detail(request, task_id):
    try:
        task = get_object_or_404(Task, id=task_id)

        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description or '',
                'status': task.status,
                'priority': task.priority,
                'assigned_to': task.assigned_to.id if task.assigned_to else None,
                'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else '',
                'comments': [{
                    'author': str(c.author),
                    'text': c.content,
                    'date': c.created_at.strftime('%d.%m %H:%M'),
                    'file_url': c.attachment.url if c.attachment else None,
                    'file_name': c.attachment.name.split('/')[-1] if c.attachment else None  # Для красивого имени файла
                } for c in task.comments.all()]
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def update_status(request, task_id):
    try:
        # Поддержка и JSON (Postman), и form-data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        new_status = data.get('status')
        if not new_status:
            return JsonResponse({'success': False, 'error': 'Статус не указан'}, status=400)

        task = get_object_or_404(Task, id=task_id)
        old_status = task.status
        task.status = new_status
        task.save()

        logger.info(f"Task {task_id} status updated: {old_status} -> {new_status}")

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
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        logger.error(f"Error in update_status: {e}")
        return JsonResponse({'success': False, 'error': 'Внутренняя ошибка'}, status=500)