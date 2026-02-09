// static/admin/js/kanban.js
document.addEventListener('DOMContentLoaded', function () {
    const kanbanBoard = document.getElementById('kanban-board');
    if (!kanbanBoard) return;

    let draggedTask = null;
    let draggedOverElement = null;

    // Включаем drag для задач
    document.querySelectorAll('.kanban-task').forEach(task => {
        task.addEventListener('dragstart', e => {
            draggedTask = task;
            const taskId = task.dataset.taskId;
            if (!taskId) {
                console.error('❌ Задача без data-task-id:', task);
                return;
            }
            e.dataTransfer.setData('text/plain', taskId);
            task.style.opacity = '0.5';
        });
        task.addEventListener('dragend', () => {
            if (draggedTask) {
                draggedTask.style.opacity = '1';
                draggedTask = null;
            }
        });
    });

    // Прием задач в колонки
    document.querySelectorAll('.kanban-column-body').forEach(column => {
        column.addEventListener('dragover', e => e.preventDefault());
        column.addEventListener('dragenter', e => {
            e.preventDefault();
            if (draggedOverElement) {
                draggedOverElement.classList.remove('drag-over');
            }
            column.classList.add('drag-over');
            draggedOverElement = column;
        });
        column.addEventListener('dragleave', e => {
            if (e.target === column) {
                column.classList.remove('drag-over');
                draggedOverElement = null;
            }
        });
        column.addEventListener('drop', e => {
            e.preventDefault();
            if (!draggedTask) return;

            const taskId = e.dataTransfer.getData('text/plain');
            const newStatus = column.closest('.kanban-column').dataset.status;

            // Визуальное перемещение
            const cloned = draggedTask.cloneNode(true);
            column.insertBefore(cloned, column.firstChild);
            draggedTask.remove();

            // AJAX: обновляем статус на сервере
            fetch(`/admin/tasks/task/${taskId}/update_status/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({ status: newStatus })
            })
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    console.log('✅ Статус обновлён:', data);
                    showNotification('Задача перемещена');
                } else {
                    throw new Error(data.error || 'Неизвестная ошибка');
                }
            })
            .catch(err => {
                console.error('❌ Ошибка:', err);
                showNotification('Ошибка: не удалось обновить статус', 'error');
                // Откатываем перемещение
                cloned.remove();
                draggedTask.style.display = '';
            });

            draggedTask = null;
            if (draggedOverElement) {
                draggedOverElement.classList.remove('drag-over');
                draggedOverElement = null;
            }
        });
    });

    function showNotification(message, type = 'success') {
        const n = document.createElement('div');
        n.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 6px;
            color: white;
            font-weight: bold;
            z-index: 9999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            animation: slideIn 0.3s ease;
        `;
        n.textContent = message;
        if (type === 'success') {
            n.style.background = 'linear-gradient(135deg,#2a9d8f,#264653)';
        } else {
            n.style.background = 'linear-gradient(135deg,#e76f51,#f4a261)';
        }
        document.body.appendChild(n);
        setTimeout(() => {
            n.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => n.remove(), 300);
        }, 3000);
    }

    // Анимации
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn { from { transform: translateX(400px); opacity:0; } to { transform: translateX(0); opacity:1; } }
        @keyframes slideOut { from { transform: translateX(0); opacity:1; } to { transform: translateX(400px); opacity:0; } }
    `;
    document.head.appendChild(style);
});