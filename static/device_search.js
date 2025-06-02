document.addEventListener('DOMContentLoaded', function() {
    const resultsContainer = document.getElementById('search-results');
    const emptyState = document.getElementById('empty-state');
    const cardTemplate = document.getElementById('device-card-template');

    const deviceStatus = {
        1: { text: '正常', class: 'status-normal' },
        2: { text: '需要维修', class: 'status-repair' },
        3: { text: '维修中', class: 'status-fixing' },
        4: { text: '报废', class: 'status-scrapped' }
    };

    const searchField = document.getElementById('search-field');
    const searchValue = document.getElementById('search-value');
    const searchOptions = document.getElementById('search-options');

    const fieldOptions = {
        type_name: {
            type: 'text',
            label: '设备类型',
            api: '/api/devices/types'
        },
        model: {
            type: 'text',
            label: '型号',
            api: '/api/devices/models'
        },
        lab: {
            type: 'text',
            label: '所属实验室',
            api: '/api/labs'
        }
    };

    // 加载实验室列表
    fetch('/api/labs')
        .then(response => response.json())
        .then(data => {
            const labSelect = document.getElementById('lab');
            data.labs.forEach(lab => {
                const option = document.createElement('option');
                option.value = lab;
                option.textContent = lab;
                labSelect.appendChild(option);
            });
        });

    function createDeviceCard(device, actionButtons) {
        const template = cardTemplate.content.cloneNode(true);
        const card = template.querySelector('.device-card');
        
        card.querySelector('.device-name').textContent = device.device_name;
        card.querySelector('.device-status').textContent = deviceStatus[device.status].text;
        card.querySelector('.device-status').classList.add(deviceStatus[device.status].class);
        card.querySelector('.device-model').textContent = device.model;
        card.querySelector('.device-lab').textContent = device.lab;
        card.querySelector('.device-purchase-date').textContent = new Date(device.purchase_date).toLocaleDateString();
        card.querySelector('.device-price').textContent = `￥${device.price.toFixed(2)}`;

        // 添加操作按钮
        const actionsContainer = card.querySelector('.device-actions');
        actionButtons.forEach(button => {
            actionsContainer.appendChild(button);
        });

        return card;
    }

    function updateSearchOptions(field) {
        const fieldInfo = fieldOptions[field];
        searchOptions.innerHTML = '';
        
        if (fieldInfo.api) {
            fetch(fieldInfo.api)
                .then(response => response.json())
                .then(data => {
                    data.values.forEach(value => {
                        const option = document.createElement('option');
                        option.value = value;
                        searchOptions.appendChild(option);
                    });
                });
        }
    }

    searchField.addEventListener('change', function() {
        searchValue.value = '';
        updateSearchOptions(this.value);
    });

    function searchDevices() {
        const field = searchField.value;
        const value = searchValue.value.trim();
        
        const params = new URLSearchParams({
            [field]: value
        });

        // 自动添加状态和可借用条件，由后端处理
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

    searchBtn.addEventListener('click', searchDevices);
    // 初始加载
    updateSearchOptions(searchField.value);
});
