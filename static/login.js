document.addEventListener('DOMContentLoaded', function() {
    const loginBtn = document.getElementById('login-btn');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const errorMessage = document.getElementById('error-message');
    const togglePassword = document.getElementById('toggle-password');
    const attemptsCounter = document.getElementById('attempts-counter');
    const signUpLink = document.getElementById('sign-up-link');

    // 显示/隐藏密码
    togglePassword.addEventListener('click', function() {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            togglePassword.textContent = 'visibility';
        } else {
            passwordInput.type = 'password';
            togglePassword.textContent = 'visibility_off';
        }
    });

    // 登录按钮点击事件
    loginBtn.addEventListener('click', function() {
        performLogin();
    });

    // 密码输入框回车事件
    passwordInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            performLogin();
        }
    });

    // 用户名输入框回车事件
    usernameInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            passwordInput.focus();
        }
    });

    // 注册链接点击事件
    signUpLink.addEventListener('click', function(event) {
        event.preventDefault();
        window.location.href = '/register';
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

    // 登录请求函数
    async function performLogin() {
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        // 输入验证
        if (!username || !password) {
            errorMessage.textContent = '请填写所有字段';
            return;
        }

        try {
            const hashedPassword = await hashPassword(password);
            console.log('Debug - Hashed password:', hashedPassword); // 调试用

            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    username: username,
                    password: hashedPassword 
                })
            });

            const data = await response.json();
            console.log('Debug - Server response:', data); // 调试用

            if (data.success) {
                window.location.href = '/index';
            } else {
                errorMessage.textContent = data.message;
                passwordInput.value = '';
            }
        } catch (error) {
            console.error('Login error:', error);
            errorMessage.textContent = '登录失败，请重试';
        }
    }
});
