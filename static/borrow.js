document.addEventListener('DOMContentLoaded', function() {
    // 检查用户登录状态
    fetch('/api/user-info')
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                window.location.href = '/login';
            }
        });
    
    // 借用功能将在后续实现

    const searchField = document.getElementById('search-field');
    const searchValue = document.getElementById('search-value');
    const searchBtn = document.getElementById('search-btn');
    const resultsContainer = document.getElementById('search-results');
    const emptyState = document.getElementById('empty-state');
    const cardTemplate = document.getElementById('device-card-template');
    const refreshBtn = document.getElementById('refresh-btn');

    // 创建设备卡片
    function createDeviceCard(device) {
        const template = cardTemplate.content.cloneNode(true);
        const card = template.querySelector('.device-card');
        
        card.querySelector('.device-name').textContent = device.device_name;
        card.querySelector('.device-id').textContent = `#${device.device_id}`;
        card.querySelector('.device-model').textContent = device.model;
        card.querySelector('.device-lab').textContent = device.lab;

        const borrowBtn = card.querySelector('.borrow-btn');
        borrowBtn.addEventListener('click', () => submitBorrowRequest(device.device_id));

        return card;
    }

    // 提交借用申请
    function submitBorrowRequest(deviceId) {
        fetch('/api/borrow-request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                device_id: deviceId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('借用申请已提交，请等待审批');
                searchDevices(); // 刷新设备列表
            } else {
                alert(data.message || '申请提交失败，请重试');
            }
        });
    }

    // 搜索可用设备
    function searchDevices() {
        const field = searchField.value;
        const value = searchValue.value.trim();
        
        const params = new URLSearchParams({
            [field]: value
        });

        fetch(`/api/devices/search?${params}`)
            .then(response => response.json())
            .then(data => {
                resultsContainer.innerHTML = '';
                
                if (data.devices && data.devices.length > 0) {
                    data.devices.forEach(device => {
                        resultsContainer.appendChild(createDeviceCard(device));
                    });
                    emptyState.classList.add('hidden');
                } else {
                    emptyState.innerHTML = `
                        <span class="material-icons">search_off</span>
                        <p>未找到符合"${value}"的可借用设备</p>
                    `;
                    emptyState.classList.remove('hidden');
                }
            });
    }

    // 回车键触发搜索
    searchValue.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchDevices();
        }
    });

    searchBtn.addEventListener('click', searchDevices);
    refreshBtn.addEventListener('click', searchDevices);
});
