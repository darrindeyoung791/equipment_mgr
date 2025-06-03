document.addEventListener('DOMContentLoaded', () => {
    let companies = [];
    let currentIndex = 0;
    let totalCompanies = 0;
    let reviewedCompanies = 0;
    
    // 修改API路径
    fetch('/api/companies')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                companies = data.companies;
                // 更新全局变量
                totalCompanies = data.total;
                reviewedCompanies = data.reviewed;
                
                updateProgress();
                if (companies.length > 0) {
                    loadCompany(currentIndex);
                } else {
                    showCompleteDialog();
                }
            } else {
                throw new Error(data.message || '获取数据失败');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showSnackbar('加载企业数据失败');
        });

    // 加载公司信息
    function loadCompany(index) {
        if (index >= 0 && index < companies.length) {
            const company = companies[index];
            document.getElementById('company-name').textContent = company.company_name || '未获取信息';
            document.getElementById('company-license').textContent = company.company_LicenseNumber || '未获取信息';
            document.getElementById('company-location').textContent = company.company_location || '未获取信息';
            
            // 更新搜索链接
            document.querySelectorAll('.search-link').forEach(link => {
                const site = link.dataset.site;
                const type = link.dataset.type;
                let query = '';
                
                if (type === 'company') {
                    query = company.company_name || '';
                } else if (type === 'license') {
                    query = company.company_LicenseNumber || '';
                } else if (type === 'map') {
                    query = company.company_location || '';
                }
                
                if (site === 'baidu') {
                    link.href = type === 'map' ? `https://map.baidu.com/search/${encodeURIComponent(query)}` : `https://www.baidu.com/s?wd=${encodeURIComponent(query)}`;
                } else if (site === 'bing') {
                    link.href = `https://www.bing.com/search?q=${encodeURIComponent(query)}`;
                } else if (site === 'qichacha') {
                    link.href = `https://www.qcc.com/web/search?key=${encodeURIComponent(query)}`;
                } else if (site === 'tianyancha') {
                    link.href = `https://www.tianyancha.com/search?key=${encodeURIComponent(query)}`;
                }
            });
        }
    }

    // 更新进度条
    function updateProgress() {
        if (!totalCompanies) {
            document.getElementById('progress-text').textContent = '0/0';
            document.getElementById('progress-fill').style.width = '0%';
            return;
        }
        
        // 使用已审核总数而不是当前索引
        const percent = (reviewedCompanies / totalCompanies) * 100;
        
        // 更新显示
        document.getElementById('progress-text').textContent = `${reviewedCompanies}/${totalCompanies}`;
        document.getElementById('progress-fill').style.width = `${percent}%`;
    }

    // 复制功能
    document.querySelectorAll('.copy-btn').forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.dataset.target;
            const text = document.getElementById(targetId).textContent;
            
            navigator.clipboard.writeText(text).then(() => {
                showSnackbar('复制成功');
            }).catch(err => {
                console.error('复制失败:', err);
            });
        });
    });

    // 显示snackbar
    function showSnackbar(message) {
        const snackbar = document.getElementById('snackbar');
        snackbar.querySelector('span:last-child').textContent = message;
        snackbar.classList.add('show');
        
        setTimeout(() => {
            snackbar.classList.remove('show');
        }, 3000);
    }

    // 显示完成对话框
    function showCompleteDialog() {
        const dialog = document.getElementById('complete-dialog');
        dialog.classList.remove('hidden');
        document.getElementById('close-btn').focus();
    }

    // 修改审核请求
    function reviewCompany(isApproved) {
        const company = companies[currentIndex];
        if (!company) return;

        fetch(`/api/companies/${company.company_id}/review`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                is_verified: isApproved
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentIndex++;
                reviewedCompanies++; // 增加已审核数量
                updateProgress();
                if (currentIndex < companies.length) {
                    loadCompany(currentIndex);
                } else {
                    showCompleteDialog();
                }
            } else {
                throw new Error(data.message || '审核失败');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showSnackbar('审核操作失败');
        });
    }

    // 确认对话框
    function showConfirmDialog(isApproved) {
        const dialog = document.getElementById('confirm-dialog');
        dialog.classList.remove('hidden');
        
        // 添加一次性ESC监听器
        const escListener = (e) => {
            if (e.key === 'Escape') {
                hideConfirmDialog();
                document.removeEventListener('keydown', escListener);
            }
        };
        document.addEventListener('keydown', escListener);
        
        document.getElementById('confirm-title').textContent = isApproved ? '确认通过' : '确认不通过';
        document.getElementById('confirm-message').textContent = isApproved 
            ? '您确定要通过此企业的审核吗？' 
            : '您确定要不通过此企业的审核吗？';
        
        const confirmBtn = document.getElementById('confirm-btn');
        confirmBtn.focus();
        
        confirmBtn.onclick = () => {
            hideConfirmDialog();
            reviewCompany(isApproved);
        };
    }

    // 添加隐藏对话框函数
    function hideConfirmDialog() {
        document.getElementById('confirm-dialog').classList.add('hidden');
    }

    // 事件监听
    document.getElementById('approve-btn').addEventListener('click', () => {
        showConfirmDialog(true);
    });

    document.getElementById('reject-btn').addEventListener('click', () => {
        showConfirmDialog(false);
    });

    document.getElementById('cancel-btn').addEventListener('click', () => {
        hideConfirmDialog();
    });

    document.getElementById('close-btn').addEventListener('click', () => {
        window.close(); // 关闭标签页
        // 如果window.close()不起作用，提示用户手动关闭
        setTimeout(() => {
            document.getElementById('complete-dialog').classList.add('hidden');
            showSnackbar('请手动关闭此标签页');
        }, 100);
    });

    // 退出登录
    document.getElementById('logout-btn').addEventListener('click', () => {
        window.location.href = '/logout';
    });

    // 键盘快捷键
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            showConfirmDialog(true);
        } else if (e.ctrlKey && e.key === 'Backspace') {
            e.preventDefault();
            showConfirmDialog(false);
        }
    });

    // 搜索链接点击事件
    document.querySelectorAll('.search-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const url = link.href;
            if (url) {
                window.open(url, '_blank');
            } else {
                showSnackbar('信息不完整，无法搜索');
            }
        });
    });
});
