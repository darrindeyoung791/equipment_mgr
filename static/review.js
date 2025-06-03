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
    
    let currentRequests = [];
    let currentIndex = 0;

    const requestCard = document.querySelector('.request-card');
    const emptyState = document.getElementById('empty-state');
    const refreshBtn = document.getElementById('refresh-btn');

    function formatDate(dateString) {
        return new Date(dateString).toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function loadRequests() {
        fetch('/api/borrow-requests/pending')
            .then(response => response.json())
            .then(data => {
                if (data.requests && data.requests.length > 0) {
                    currentRequests = data.requests;
                    currentIndex = 0;
                    loadRequest(currentIndex);
                    requestCard.classList.remove('hidden');
                    emptyState.classList.add('hidden');
                } else {
                    requestCard.classList.add('hidden');
                    emptyState.classList.remove('hidden');
                }
            });
    }

    function loadRequest(index) {
        if (index >= 0 && index < currentRequests.length) {
            const request = currentRequests[index];
            document.getElementById('user-name').textContent = request.user_name;
            document.getElementById('user-department').textContent = request.department;
            document.getElementById('device-name').textContent = request.device_name;
            document.getElementById('device-id').textContent = `#${request.device_id}`;
            document.getElementById('available-count').textContent = request.available_count;
            document.getElementById('apply-time').textContent = formatDate(request.apply_time);
        }
    }

    function showConfirmDialog(isApproved) {
        const dialog = document.getElementById('confirm-dialog');
        const title = document.getElementById('confirm-title');
        const message = document.getElementById('confirm-message');
        const duration = document.getElementById('duration').value;
        
        dialog.classList.remove('hidden');
        
        if (isApproved) {
            title.textContent = '确认批准';
            message.textContent = `确定批准此借用申请 ${duration} 天吗？`;
        } else {
            title.textContent = '确认拒绝';
            message.textContent = '确定拒绝此借用申请吗？';
        }

        return new Promise((resolve) => {
            const confirmBtn = document.getElementById('confirm-btn');
            const cancelBtn = document.getElementById('cancel-btn');
            
            const cleanup = () => {
                dialog.classList.add('hidden');
                confirmBtn.onclick = null;
                cancelBtn.onclick = null;
            };

            confirmBtn.onclick = () => {
                cleanup();
                resolve(true);
            };

            cancelBtn.onclick = () => {
                cleanup();
                resolve(false);
            };

            // ESC键关闭对话框
            const handleEsc = (e) => {
                if (e.key === 'Escape') {
                    cleanup();
                    resolve(false);
                    document.removeEventListener('keydown', handleEsc);
                }
            };
            document.addEventListener('keydown', handleEsc);
        });
    }

    function handleReview(isApproved) {
        const request = currentRequests[currentIndex];
        if (!request) return;

        showConfirmDialog(isApproved).then(confirmed => {
            if (!confirmed) return;

            const duration = isApproved ? document.getElementById('duration').value : null;
            
            fetch('/api/borrow-requests/review', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    record_id: request.record_id,
                    approved: isApproved,
                    duration: duration
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadRequests();  // 重新加载请求列表
                } else {
                    console.error('Review failed:', data.message);
                    alert(data.message || '审批失败，请重试');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('审批操作失败');
            });
        });
    }

    // 事件监听
    document.getElementById('approve-btn').addEventListener('click', () => {
        handleReview(true);
    });

    document.getElementById('reject-btn').addEventListener('click', () => {
        handleReview(false);
    });

    refreshBtn.addEventListener('click', loadRequests);

    // 键盘快捷键
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            handleReview(true);
        } else if (e.ctrlKey && e.key === 'Backspace') {
            e.preventDefault();
            handleReview(false);
        }
    });

    // 初始加载
    loadRequests();
});
