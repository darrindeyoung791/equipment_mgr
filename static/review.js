document.addEventListener('DOMContentLoaded', function() {
    // 检查用户登录状态和管理员权限
    fetch('/api/user-info')
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                window.location.href = '/login';
            } else if (data.user_type === 1) {
                // 如果是学生用户，重定向到首页
                window.location.href = '/index';
            }
        });
    
    // 审批功能将在后续实现
});
