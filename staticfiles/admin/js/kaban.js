// static/js/kanban.js
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const kanbanBoard = document.getElementById('kanban-board');
        if (!kanbanBoard) return;

        // Функция для получения CSRF токена
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        const csrfToken = getCookie('csrftoken');

        // Проверяем, что токен получен
        if (!csrfToken) {
            console.warn('CSRF токен не найден. Проверьте настройки cookies.');
        }

        let draggedTask = null;

        // Включаем drag для задач
        document.querySelectorAll('.kanban-task').forEach(task => {
            task.setAttribute('draggable', 'true');

            task.addEventListener('dragstart', e => {
                draggedTask = task;
                const taskId = task.dataset.taskId;
                if (!taskId) {
                    console.error('❌ Задача без data-task-id:', task);
                    return;
                }
                e.dataTransfer.setData('text/plain', taskId);
                e.dataTransfer.effectAllowed = 'move';
                task.style.opacity = '0.5';
                task.classList.add('dragging');

                console.log(`Начало перетаскивания задачи #${taskId}`);
            });

            task.addEventListener('dragend', () => {
                if (draggedTask) {
                    draggedTask.style.opacity = '1';
                    draggedTask.classList.remove('dragging');
                    draggedTask = null;
                }
                console.log('Завершено перетаскивание');
            });
        });

        // Прием задач в колонки
        document.querySelectorAll('.kanban-column-body').forEach(column => {
            column.addEventListener('dragover', e => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                column.classList.add('drag-over');
            });

            column.addEventListener('dragleave', () => {
                column.classList.remove('drag-over');
            });

            column.addEventListener('drop', async e => {
                e.preventDefault();
                column.classList.remove('drag-over');

                if (!draggedTask) return;

                const taskId = e.dataTransfer.getData('text/plain');
                const newStatus = column.closest('.kanban-column').dataset.status;

                console.log(`Перенос задачи #${taskId} в статус: ${newStatus}`);

                // Сохраняем исходную позицию для отката
                const originalColumn = draggedTask.closest('.kanban-column-body');
                const originalPosition = draggedTask;

                try {
                    // AJAX: обновляем статус
                    const response = await fetch(`/tasks/task/${taskId}/update_status/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken,
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: JSON.stringify({
                            status: newStatus,
                            csrfmiddlewaretoken: csrfToken
                        })
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.error || `HTTP error! status: ${response.status}`);
                    }

                    if (data.success) {
                        // Визуальное перемещение
                        console.log('✅ Статус обновлен успешно:', data.message);

                        // Клонируем и перемещаем задачу
                        const clonedTask = draggedTask.cloneNode(true);
                        column.insertBefore(clonedTask, column.firstChild);
                        draggedTask.remove();
                        draggedTask = clonedTask;

                        // Обновляем счетчик в заголовке колонки
                        updateColumnCounts();

                        // Показываем уведомление
                        showNotification('Статус задачи обновлен', 'success');
                    } else {
                        console.error('❌ Ошибка от сервера:', data.error);
                        showNotification(`Ошибка: ${data.error}`, 'error');
                    }
                } catch (err) {
                    console.error('❌ Ошибка при обновлении статуса:', err);

                    // Возвращаем задачу на место в случае ошибки
                    if (originalColumn && originalPosition) {
                        originalColumn.appendChild(draggedTask);
                    }

                    showNotification('Ошибка сети при обновлении статуса задачи', 'error');
                }

                draggedTask = null;
            });
        });

        // Функция обновления счетчиков всех колонок
        function updateColumnCounts() {
            document.querySelectorAll('.kanban-column').forEach(column => {
                const countElement = column.querySelector('.kanban-column-count');
                if (countElement) {
                    const taskCount = column.querySelectorAll('.kanban-task').length;
                    countElement.textContent = taskCount;
                }
            });
        }

        // Функция для отображения уведомлений
        function showNotification(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = `kanban-notification kanban-notification-${type}`;
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 20px;
                border-radius: 6px;
                color: white;
                font-weight: bold;
                z-index: 10000;
                animation: fadeIn 0.3s, fadeOut 0.3s 2.7s;
            `;

            if (type === 'success') {
                notification.style.backgroundColor = '#2a9d8f';
            } else if (type === 'error') {
                notification.style.backgroundColor = '#e63946';
            } else {
                notification.style.backgroundColor = '#457b9d';
            }

            document.body.appendChild(notification);

            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 3000);
        }

        // Добавляем стили для анимации уведомлений
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes fadeOut {
                from { opacity: 1; transform: translateY(0); }
                to { opacity: 0; transform: translateY(-20px); }
            }
        `;
        document.head.appendChild(style);
    });
})();