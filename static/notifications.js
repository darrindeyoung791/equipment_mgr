document.addEventListener('DOMContentLoaded', function() {
    const notificationsList = document.getElementById('notifications-list');
    const markAllReadBtn = document.getElementById('mark-all-read');

    function loadNotifications() {
        fetch('/api/notifications')
            .then(response => response.json())
            .then(data => {
                notificationsList.innerHTML = data.notifications.map(notification => `
                    <div class="notification-item ${notification.read_status ? '' : 'unread'}" 
                         data-id="${notification.notification_id}">
                        <span class="material-icons notification-icon">
                            ${getNotificationIcon(notification.type)}
                        </span>
                        <div class="notification-content">
                            <p>${notification.content}</p>
                            <span class="notification-time">
                                ${new Date(notification.created_at).toLocaleString()}
                            </span>
                        </div>
                    </div>
                `).join('');
            });
    }

    function getNotificationIcon(type) {
        const icons = {
            1: 'check_circle',
            2: 'cancel',
            3: 'update',
            4: 'build'
        };
        return icons[type] || 'notifications';
    }

    markAllReadBtn.addEventListener('click', function() {
        fetch('/api/notifications/mark-all-read', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadNotifications();
            }
        });
    });

    // 初始加载通知
    loadNotifications();
});
