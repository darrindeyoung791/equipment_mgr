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

    // 添加菜单切换功能
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    function toggleSidebar() {
        sidebar.classList.toggle('open');
        if (sidebar.classList.contains('open')) {
            document.body.style.overflow = 'hidden';
            overlay.classList.add('visible');
        } else {
            document.body.style.overflow = '';
            overlay.classList.remove('visible');
        }
    }

    menuToggle?.addEventListener('click', toggleSidebar);
    overlay?.addEventListener('click', toggleSidebar);

    // 在窗口调整大小时处理侧边栏状态
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 1024) {
            sidebar?.classList.remove('open');
            document.body.style.overflow = '';
            overlay?.classList.remove('visible');
        }
    });
});
