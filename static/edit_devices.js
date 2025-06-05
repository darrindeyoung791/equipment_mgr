document.addEventListener('DOMContentLoaded', function() {
    // 只获取页面实际存在的元素
    const searchField = document.getElementById('search-field');
    const searchValue = document.getElementById('search-value');
    const searchBtn = document.getElementById('search-btn');
    const refreshBtn = document.getElementById('refresh-btn');
    const addDeviceBtn = document.getElementById('add-device-btn');
    const resultsContainer = document.getElementById('search-results');
    const emptyState = document.getElementById('empty-state');
    const cardTemplate = document.getElementById('device-card-template');
    const editDialog = document.getElementById('edit-dialog');
    const editForm = document.getElementById('edit-form');

    const deviceStatusMap = {
        1: { text: '正常', class: 'normal' },
        2: { text: '需要维修', class: 'need-repair' },
        3: { text: '维修中', class: 'repairing' },
        4: { text: '报废', class: 'scrapped' }
    };

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('zh-CN');
    }

    function formatPrice(price) {
        return `¥${parseFloat(price).toFixed(2)}`;
    }

    function showEditDialog(device = null) {
        const isNew = !device;
        const dialogTitle = document.getElementById('dialog-title');
        const submitBtn = document.getElementById('edit-submit-btn');
        
        dialogTitle.textContent = isNew ? '新增设备' : '编辑设备';
        submitBtn.textContent = isNew ? '添加' : '保存';

        // 设置表单字段
        const fields = {
            'edit-device-id': '',
            'edit-name': '',
            'edit-model': '',
            'edit-lab': '',
            'edit-price': '',
            'edit-purchase-date': new Date().toISOString().split('T')[0],
            'edit-status': '1',
            'edit-can-borrow': '1'
        };

        if (!isNew && device) {
            fields['edit-device-id'] = device.device_id;
            fields['edit-name'] = device.device_name;
            fields['edit-model'] = device.model;
            fields['edit-lab'] = device.lab;
            fields['edit-price'] = device.price;
            fields['edit-purchase-date'] = new Date(device.purchase_date).toISOString().split('T')[0];
            fields['edit-status'] = device.status.toString();
            fields['edit-can-borrow'] = device.can_borrow.toString();
        }

        // 设置所有表单字段的值
        Object.keys(fields).forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.value = fields[id];
            }
        });

        editDialog.classList.remove('hidden');
    }

    function showDeleteDialog(device) {
        const deleteDialog = document.getElementById('delete-dialog');
        const deviceId = document.getElementById('delete-device-id');
        const modelDisplay = deleteDialog.querySelector('.device-model-display');
        const confirmInput = document.getElementById('delete-confirm');
        const confirmBtn = document.getElementById('confirm-delete-btn');

        deviceId.value = device.device_id;
        modelDisplay.textContent = device.model;
        confirmInput.value = '';
        confirmBtn.disabled = true;

        deleteDialog.classList.remove('hidden');
    }

    function createDeviceCard(device) {
        const template = cardTemplate.content.cloneNode(true);
        const card = template.querySelector('.device-card');
        
        card.querySelector('.device-name').textContent = device.device_name;
        card.querySelector('.device-id').textContent = `#${device.device_id}`;
        card.querySelector('.device-model').textContent = device.model;
        card.querySelector('.device-lab').textContent = device.lab;
        card.querySelector('.device-price').textContent = formatPrice(device.price);
        card.querySelector('.device-purchase-date').textContent = formatDate(device.purchase_date);

        const statusBadge = card.querySelector('.device-status');
        statusBadge.textContent = deviceStatusMap[device.status].text;
        statusBadge.classList.add(deviceStatusMap[device.status].class);

        const editBtn = card.querySelector('.edit-btn');
        const deleteBtn = card.querySelector('.delete-btn');
        
        editBtn.addEventListener('click', () => showEditDialog(device));
        deleteBtn.addEventListener('click', () => showDeleteDialog(device));
        
        return card;
    }

    function searchDevices() {
        const field = searchField.value;
        const value = searchValue.value.trim();
        
        if (!value && !['status'].includes(field)) return;
        
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
                    emptyState.classList.remove('hidden');
                }
            });
    }

    // 事件绑定前判空
    if (document.getElementById('delete-confirm')) {
        document.getElementById('delete-confirm').addEventListener('input', function() {
            const modelDisplay = document.querySelector('.device-model-display');
            const confirmBtn = document.getElementById('confirm-delete-btn');
            if (modelDisplay && confirmBtn) {
                confirmBtn.disabled = this.value !== modelDisplay.textContent;
            }
        });
    }

    if (document.getElementById('delete-form')) {
        document.getElementById('delete-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const deviceId = document.getElementById('delete-device-id').value;
            
            // 显示加载状态
            const confirmBtn = document.getElementById('confirm-delete-btn');
            const originalText = confirmBtn.innerHTML;
            confirmBtn.innerHTML = '<span class="material-icons">hourglass_empty</span><span>处理中</span>';
            confirmBtn.disabled = true;

            fetch(`/api/devices/delete/${deviceId}`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('delete-dialog').classList.add('hidden');
                    searchDevices();
                } else {
                    alert(data.message || '删除失败，请重试');
                }
            })
            .catch(error => {
                alert('删除失败，请重试');
            })
            .finally(() => {
                // 恢复按钮状态
                confirmBtn.innerHTML = originalText;
                confirmBtn.disabled = false;
            });
        });
    }

    if (document.getElementById('edit-cancel-btn')) {
        document.getElementById('edit-cancel-btn').addEventListener('click', () => {
            document.getElementById('edit-dialog').classList.add('hidden');
        });
    }

    if (document.getElementById('delete-cancel-btn')) {
        document.getElementById('delete-cancel-btn').addEventListener('click', () => {
            document.getElementById('delete-dialog').classList.add('hidden');
        });
    }

    // 批量SQL对话框相关
    const sqlDialog = document.getElementById('sql-dialog');
    const sqlForm = document.getElementById('sql-form');
    const sqlCancelBtn = document.getElementById('sql-cancel-btn');
    const sqlSubmitBtn = document.getElementById('sql-submit-btn');
    const sqlTextarea = document.getElementById('sql-textarea');
    const sqlResult = document.getElementById('sql-result');
    const batchSqlBtn = document.getElementById('batch-sql-btn');

    if (batchSqlBtn && sqlDialog && sqlTextarea && sqlResult) {
        batchSqlBtn.addEventListener('click', () => {
            sqlTextarea.value = '';
            sqlResult.textContent = '';
            sqlDialog.classList.remove('hidden');
        });
    }
    if (sqlCancelBtn && sqlDialog) {
        sqlCancelBtn.addEventListener('click', () => {
            sqlDialog.classList.add('hidden');
        });
    }
    if (sqlForm && sqlTextarea && sqlResult) {
        sqlForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sqlResult.textContent = '正在执行...';
            fetch('/api/admin/batch-sql', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sql: sqlTextarea.value })
            })
            .then(r => r.json())
            .then(data => {
                sqlResult.textContent = data.success ? (data.result || '执行成功') : (data.message || '执行失败');
            })
            .catch(() => {
                sqlResult.textContent = '执行失败';
            });
        });
    }

    // 搜索和刷新按钮
    if (searchBtn) searchBtn.addEventListener('click', searchDevices);
    if (refreshBtn) refreshBtn.addEventListener('click', searchDevices);
    if (addDeviceBtn) addDeviceBtn.addEventListener('click', () => showEditDialog());

    // 监听回车搜索
    if (searchValue) {
        searchValue.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchDevices();
            }
        });
    }

    // 修正表单提交逻辑
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const deviceId = document.getElementById('edit-device-id')?.value || '';
            const deviceName = document.getElementById('edit-name')?.value.trim() || '';
            const model = document.getElementById('edit-model')?.value.trim() || '';
            const lab = document.getElementById('edit-lab')?.value.trim() || '';
            const priceStr = document.getElementById('edit-price')?.value;
            const purchaseDate = document.getElementById('edit-purchase-date')?.value || '';
            const statusStr = document.getElementById('edit-status')?.value;
            const canBorrowStr = document.getElementById('edit-can-borrow')?.value;

            const price = priceStr !== undefined && priceStr !== '' ? parseFloat(priceStr) : NaN;
            const status = statusStr !== undefined && statusStr !== '' ? parseInt(statusStr) : NaN;
            const can_borrow = canBorrowStr !== undefined && canBorrowStr !== '' ? parseInt(canBorrowStr) : NaN;

            if (!deviceName || !model || !lab || isNaN(price) || !purchaseDate || isNaN(status) || isNaN(can_borrow)) {
                alert('请填写所有必填字段');
                return;
            }
            if (price <= 0) {
                alert('价格必须大于0');
                return;
            }

            const formData = {
                device_name: deviceName,
                model: model,
                lab: lab,
                price: price,
                purchase_date: purchaseDate,
                status: status,
                can_borrow: can_borrow
            };
            if (deviceId) {
                formData.device_id = parseInt(deviceId);
            }

            const url = deviceId ? '/api/devices/update' : '/api/devices/create';
            fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    editDialog.classList.add('hidden');
                    searchDevices();
                } else {
                    alert(data.message || '操作失败，请重试');
                }
            })
            .catch(() => {
                alert('操作失败，请重试');
            });
        });
    }

    // 页面加载时自动搜索
    searchDevices();
});
