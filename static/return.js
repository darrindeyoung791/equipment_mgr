document.addEventListener('DOMContentLoaded', function() {
    // 检查用户登录状态
    fetch('/api/user-info')
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                window.location.href = '/login';
            }
        });
    
    const borrowedList = document.getElementById('borrowed-list');
    const pendingList = document.getElementById('pending-list');
    const borrowedEmpty = document.getElementById('borrowed-empty');
    const pendingEmpty = document.getElementById('pending-empty');
    const refreshBtn = document.getElementById('refresh-btn');
    const borrowedTemplate = document.getElementById('borrowed-device-template');
    const pendingTemplate = document.getElementById('pending-device-template');

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('zh-CN');
    }

    function loadDevices() {
        // 加载已借用设备
        fetch('/api/devices/borrowed')
            .then(response => response.json())
            .then(data => {
                borrowedList.innerHTML = '';
                
                if (data.devices && data.devices.length > 0) {
                    data.devices.forEach(device => {
                        const card = borrowedTemplate.content.cloneNode(true);
                        const container = card.querySelector('.device-card');
                        
                        container.querySelector('.device-name').textContent = device.device_name;
                        container.querySelector('.device-id').textContent = `#${device.device_id}`;
                        container.querySelector('.device-model').textContent = device.model;
                        container.querySelector('.device-lab').textContent = device.lab;
                        container.querySelector('.borrow-date').textContent = `借用日期：${formatDate(device.borrow_date)}`;
                        
                        const returnBtn = container.querySelector('.return-btn');
                        returnBtn.addEventListener('click', () => returnDevice(device.record_id));
                        
                        borrowedList.appendChild(container);
                    });
                    borrowedEmpty.classList.add('hidden');
                    borrowedList.classList.remove('hidden');
                } else {
                    borrowedEmpty.classList.remove('hidden');
                    borrowedList.classList.add('hidden');
                }
            });

        // 加载待审批设备
        fetch('/api/devices/pending')
            .then(response => response.json())
            .then(data => {
                pendingList.innerHTML = '';
                
                if (data.devices && data.devices.length > 0) {
                    data.devices.forEach(device => {
                        const card = pendingTemplate.content.cloneNode(true);
                        const container = card.querySelector('.device-card');
                        
                        container.querySelector('.device-name').textContent = device.device_name;
                        container.querySelector('.device-id').textContent = `#${device.device_id}`;
                        container.querySelector('.device-model').textContent = device.model;
                        container.querySelector('.device-lab').textContent = device.lab;
                        container.querySelector('.apply-date').textContent = `申请日期：${formatDate(device.borrow_date)}`;
                        
                        const cancelBtn = container.querySelector('.cancel-btn');
                        cancelBtn.addEventListener('click', () => cancelRequest(device.record_id));
                        
                        pendingList.appendChild(container);
                    });
                    pendingEmpty.classList.add('hidden');
                    pendingList.classList.remove('hidden');
                } else {
                    pendingEmpty.classList.remove('hidden');
                    pendingList.classList.add('hidden');
                }
            });
    }

    function returnDevice(recordId) {
        if (!confirm('确定要归还这个设备吗？')) return;
        
        fetch('/api/return-device', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ record_id: recordId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadDevices();
            } else {
                alert(data.message || '归还失败，请重试');
            }
        });
    }

    function cancelRequest(recordId) {
        if (!confirm('确定要取消这个借用申请吗？')) return;
        
        fetch('/api/cancel-request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ record_id: recordId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadDevices();
            } else {
                alert(data.message || '取消失败，请重试');
            }
        });
    }

    refreshBtn.addEventListener('click', loadDevices);
    loadDevices();
});
