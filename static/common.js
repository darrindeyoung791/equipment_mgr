document.addEventListener('DOMContentLoaded', function() {
    const userTypeLabel = document.getElementById('user-type-label');
    const username = document.getElementById('username');
    const logoutBtn = document.getElementById('logout-btn');
    const staffOnlyItems = document.querySelectorAll('[data-role="staff"]');

    // 获取用户信息
    fetch('/api/user-info')
        .then(response => response.json())
        .then(data => {
            if (data.username) {
                username.textContent = data.username;
                userTypeLabel.textContent = data.user_type === 1 ? '（学生）' : '（管理员）';
                
                // 控制staff-only元素显示
                if (data.user_type === 1) {
                    staffOnlyItems.forEach(item => item.style.display = 'none');
                }
            }
        })
        .catch(error => console.error('Error:', error));

    // 退出功能
    logoutBtn.addEventListener('click', function() {
        fetch('/api/logout', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/login';
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // 高亮当前页面对应的导航项
    const currentPath = window.location.pathname;
    document.querySelector(`.nav-item[href="${currentPath}"]`)?.classList.add('active');
});
