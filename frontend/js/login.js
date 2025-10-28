// /js/login.js
document.addEventListener('DOMContentLoaded', () => {
    // === Elementos del DOM ===
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const messageBox = document.getElementById('message-box');
    const registerSection = document.getElementById('register-section');
    const showRegister = document.getElementById('show-register');
    const showLogin = document.getElementById('show-login');
    const registerToggle = document.getElementById('register-toggle');

    // === Mostrar mensaje con auto-ocultar ===
    const showMessage = (msg, type = 'error') => {
        messageBox.textContent = msg;
        messageBox.className = type;
        messageBox.style.display = 'block';

        setTimeout(() => {
            messageBox.textContent = '';
            messageBox.className = '';
            messageBox.style.display = 'none';
        }, 5000);
    };

    // === LOGIN ===
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = loginForm.querySelector('button');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Entrando...';

            try {
                const formData = new FormData(loginForm);
                const res = await fetch('/login', { method: 'POST', body: formData });
                const data = await res.json();

                showMessage(data.message, data.status);

                if (data.status === 'success' && data.redirect) {
                    setTimeout(() => window.location.href = data.redirect, 800);
                }
            } catch (err) {
                showMessage('Error de conexión. Intenta más tarde.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    // === REGISTRO ===
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = registerForm.querySelector('button');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Registrando...';

            try {
                const formData = new FormData(registerForm);
                const res = await fetch('/register', { method: 'POST', body: formData });
                const data = await res.json();

                showMessage(data.message, data.status);

                if (data.status === 'success') {
                    registerForm.reset();
                    setTimeout(() => showLogin.click(), 1500);
                }
            } catch (err) {
                showMessage('Error de conexión.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    // === Mostrar/Ocultar Registro ===
    if (showRegister && registerSection && loginForm && registerToggle) {
        showRegister.addEventListener('click', (e) => {
            e.preventDefault();
            registerSection.classList.add('active');
            loginForm.classList.add('hidden');
            registerToggle.classList.add('hidden');
            showMessage('');
        });
    }

    if (showLogin && registerSection && loginForm && registerToggle) {
        showLogin.addEventListener('click', (e) => {
            e.preventDefault();
            registerSection.classList.remove('active');
            loginForm.classList.remove('hidden');
            registerToggle.classList.remove('hidden');
            showMessage('');
        });
    }
});
