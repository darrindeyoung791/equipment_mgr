document.addEventListener('DOMContentLoaded', function() {
    const usernameElement = document.getElementById('username');
    const userTypeLabelElement = document.getElementById('user-type-label');
    const logoutButton = document.getElementById('logout-btn');
    const deviceCard = document.querySelector('a[href="/devices"]');
    const reviewCard = document.querySelector('a[href="/review"]');

    // 获取用户信息并控制卡片显示
    fetch('/api/user-info')
        .then(response => response.json())
        .then(data => {
            if (data.username) {
                usernameElement.textContent = data.username;
                
                // 根据用户类型设置标签和控制卡片显示
                if (data.user_type === 1) {
                    userTypeLabelElement.textContent = '（学生）';
                    deviceCard?.classList.add('hidden');
                    reviewCard?.classList.add('hidden');
                } else {
                    userTypeLabelElement.textContent = '（管理员）';
                }
            }
        })
        .catch(error => console.error('Error:', error));

    // 退出登录
    logoutButton.addEventListener('click', function() {
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
});
