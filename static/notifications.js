document.addEventListener('DOMContentLoaded', function() {
    const notificationsList = document.getElementById('notifications-list');
    const emptyState = document.getElementById('empty-state');
    const markAllReadBtn = document.getElementById('mark-all-read');
    const refreshBtn = document.getElementById('refresh-btn');

    const notificationTypes = {
        1: { text: '审批通过', icon: 'check_circle' },
        2: { text: '审批拒绝', icon: 'cancel' },
        3: { text: '归还提醒', icon: 'schedule' },
        4: { text: '维修完成', icon: 'build' }
    };

    function formatDate(dateString) {
        return new Date(dateString).toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function loadNotifications() {
        fetch('/api/notifications')
            .then(response => response.json())
            .then(data => {
                if (data.notifications && data.notifications.length > 0) {
                    const unreadNotifications = data.notifications.filter(n => !n.read_status);
                    const readNotifications = data.notifications.filter(n => n.read_status);
                    
                    let html = '';
                    
                    if (unreadNotifications.length > 0) {
                        html += '<div class="notification-section"><h3>未读通知</h3>';
                        html += unreadNotifications.map(notification => `
                            <div class="notification-item unread">
                                <span class="material-icons notification-icon">
                                    ${notificationTypes[notification.type].icon}
                                </span>
                                <div class="notification-content">
                                    <div class="notification-title">${notification.content}</div>
                                    <div class="notification-meta">
                                        <span class="notification-type">
                                            ${notificationTypes[notification.type].text}
                                        </span>
                                        <span>${formatDate(notification.created_at)}</span>
                                    </div>
                                </div>
                                <button class="mark-read-btn" data-id="${notification.notification_id}">
                                    <span class="material-icons">check_circle_outline</span>
                                </button>
                            </div>
                        `).join('');
                        html += '</div>';
                    }
                    
                    if (readNotifications.length > 0) {
                        html += '<div class="notification-section"><h3>已读通知</h3>';
                        html += readNotifications.map(notification => `
                            <div class="notification-item">
                                <span class="material-icons notification-icon">
                                    ${notificationTypes[notification.type].icon}
                                </span>
                                <div class="notification-content">
                                    <div class="notification-title">${notification.content}</div>
                                    <div class="notification-meta">
                                        <span class="notification-type">
                                            ${notificationTypes[notification.type].text}
                                        </span>
                                        <span>${formatDate(notification.created_at)}</span>
                                    </div>
                                </div>
                            </div>
                        `).join('');
                        html += '</div>';
                    }
                    
                    notificationsList.innerHTML = html;
                    
                    // 添加已读按钮事件监听
                    document.querySelectorAll('.mark-read-btn').forEach(btn => {
                        btn.addEventListener('click', function() {
                            const notificationId = this.dataset.id;
                            fetch(`/api/notifications/mark-read/${notificationId}`, {
                                method: 'POST'
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    loadNotifications();
                                }
                            });
                        });
                    });
                    
                    notificationsList.classList.remove('hidden');
                    emptyState.classList.add('hidden');
                } else {
                    notificationsList.classList.add('hidden');
                    emptyState.classList.remove('hidden');
                }
            });
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

    refreshBtn.addEventListener('click', function() {
        loadNotifications();
    });

    loadNotifications();
});
