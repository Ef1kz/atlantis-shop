# tasks/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from .models import Task

@staff_member_required
@require_POST
@csrf_exempt
def change_status(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        new_status = request.POST.get('status')

        if new_status in dict(Task.TaskStatus.choices):
            task.status = new_status
            task.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
    except Task.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)

@staff_member_required
@require_POST
@csrf_exempt
def add_task(request):
    try:
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        status = request.POST.get('status', 'new')
        assigned_to_id = request.POST.get('assigned_to')

        if not title or not assigned_to_id:
            return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)

        task = Task.objects.create(
            title=title,
            description=description,
            status=status,
            assigned_to_id=assigned_to_id
        )

        return JsonResponse({'success': True, 'task_id': task.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)