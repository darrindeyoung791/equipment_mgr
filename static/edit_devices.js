document.addEventListener('DOMContentLoaded', function() {
    // 检查用户登录状态和权限
    fetch('/api/user-info')
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                window.location.href = '/login';
            } else if (data.user_type === 1) {
                window.location.href = '/index';
            }
        });
    
    // 设备管理功能将在后续实现
});
