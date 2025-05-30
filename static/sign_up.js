document.addEventListener('DOMContentLoaded', function() {
    const signupBtn = document.getElementById('signup-btn');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const errorMessage = document.getElementById('error-message');
    const togglePassword = document.getElementById('toggle-password');
    const toggleConfirmPassword = document.getElementById('toggle-confirm-password');
    const signUpLink = document.getElementById('sign-up-link');

    // 显示/隐藏密码
    function setupPasswordToggle(inputId, toggleId) {
        const input = document.getElementById(inputId);
        const toggle = document.getElementById(toggleId);
        toggle.addEventListener('click', function() {
            if (input.type === 'password') {
                input.type = 'text';
                toggle.textContent = 'visibility';
            } else {
                input.type = 'password';
                toggle.textContent = 'visibility_off';
            }
        });
    }

    setupPasswordToggle('password', 'toggle-password');
    setupPasswordToggle('confirm-password', 'toggle-confirm-password');

    // 注册按钮点击事件
    signupBtn.addEventListener('click', function() {
        performSignup();
    });

    // 注册链接点击事件
    signUpLink.addEventListener('click', function(event) {
        event.preventDefault();
        window.location.href = '/templates/login.html';
    });

    // 返回登录链接点击事件
    const loginLink = document.getElementById('login-link');
    loginLink.addEventListener('click', function(event) {
        event.preventDefault();
        window.location.href = '/login';
    });

    // 密码哈希函数
    async function hashPassword(password) {
        const encoder = new TextEncoder();
        const data = encoder.encode(password);
        const hash = await crypto.subtle.digest('SHA-256', data);
        return Array.from(new Uint8Array(hash))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    }

    // 注册请求函数
    async function performSignup() {
        const username = usernameInput.value.trim();
        const name = document.getElementById('name').value.trim();
        const gender = document.getElementById('gender').value;
        const department = document.getElementById('department').value.trim();
        const password = passwordInput.value.trim();
        const confirmPassword = confirmPasswordInput.value.trim();

        // 输入验证
        if (!username || !name || !gender || !department || !password || !confirmPassword) {
            errorMessage.textContent = '请填写所有字段';
            return;
        }

        // 长度验证
        if (username.length > 100 || password.length > 100) {
            errorMessage.textContent = '用户名和密码长度不能超过100个字符';
            return;
        }

        // 用户名格式验证
        if (!/^[a-zA-Z0-9_]+$/.test(username)) {
            errorMessage.textContent = '用户名只能包含英文字母、数字和下划线';
            return;
        }

        // 密码匹配验证
        if (password !== confirmPassword) {
            errorMessage.textContent = '两次输入的密码不一致';
            return;
        }

        try {
            const hashedPassword = await hashPassword(password);
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    username: username,
                    name: name,
                    gender: parseInt(gender),
                    department: department,
                    password: hashedPassword 
                })
            });

            const data = await response.json();
            if (data.success) {
                window.location.href = '/login';
            } else {
                errorMessage.textContent = data.message;
                if (data.message === '用户名已存在') {
                    usernameInput.focus();
                }
            }
        } catch (error) {
            console.error('Error:', error);
            errorMessage.textContent = '注册失败，请重试或联系管理员';
        }
    }
});
