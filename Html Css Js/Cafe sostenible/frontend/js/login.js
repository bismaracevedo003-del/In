document.addEventListener('DOMContentLoaded', () => {
    // === Elementos del DOM ===
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const messageBox = document.getElementById('message-box');
    const registerSection = document.getElementById('register-section');
    const showRegister = document.getElementById('show-register');
    const showLogin = document.getElementById('show-login');
    const registerToggle = document.getElementById('register-toggle');
    const fotoInput = document.getElementById('reg_foto');
    const previewContainer = document.getElementById('foto-preview-container');
    const previewImg = document.getElementById('foto-preview');

    // === Mostrar mensaje con auto-ocultar ===
    const showMessage = (msg, type = 'error') => {
        messageBox.textContent = msg;
        messageBox.className = `message ${type}`;
        messageBox.style.display = 'block';

        setTimeout(() => {
            messageBox.textContent = '';
            messageBox.className = 'message';
            messageBox.style.display = 'none';
        }, 5000);
    };

    // === LOGIN (CORREGIDO: credentials: 'include') ===
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = loginForm.querySelector('button');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Entrando...';

            try {
                const formData = new FormData(loginForm);
                const res = await fetch('/login', { 
                    method: 'POST', 
                    body: formData,
                    credentials: 'include'  // ¡CRUCIAL PARA COOKIES!
                });
                const data = await res.json();

                showMessage(data.message || data.error, data.status || 'error');

                if (data.status === 'success' && data.redirect) {
                    setTimeout(() => window.location.href = data.redirect, 800);
                }
            } catch (err) {
                console.error('Error de login:', err);
                showMessage('Error de conexión. Intenta más tarde.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    // === REGISTRO (CORREGIDO: credentials: 'include') ===
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = registerForm.querySelector('button');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Registrando...';

            try {
                const formData = new FormData(registerForm);
                const res = await fetch('/register', { 
                    method: 'POST', 
                    body: formData,
                    credentials: 'include'  // ¡CRUCIAL!
                });
                const data = await res.json();

                showMessage(data.message, data.status);

                if (data.status === 'success') {
                    registerForm.reset();
                    previewContainer.style.display = 'none'; // Resetear foto
                    setTimeout(() => {
                        // Cambiar a login visualmente
                        registerSection.classList.remove('active');
                        loginForm.classList.remove('hidden');
                        registerToggle.classList.remove('hidden');
                    }, 1500);
                }
            } catch (err) {
                console.error('Error de registro:', err);
                showMessage('Error de conexión.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    // === Mostrar/Ocultar Registro (CORREGIDO) ===
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
            // Resetear vista previa
            if (previewContainer) previewContainer.style.display = 'none';
            if (fotoInput) fotoInput.value = '';
        });
    }

    // === VISTA PREVIA DE FOTO (MEJORADO) ===
    if (fotoInput && previewContainer && previewImg) {
        fotoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];

            // Resetear
            previewContainer.style.display = 'none';

            if (!file) return;

            // Validar tamaño
            if (file.size > 5 * 1024 * 1024) {
                showMessage('Imagen demasiado grande (máx 5MB)', 'error');
                e.target.value = '';
                return;
            }

            // Validar tipo
            const allowed = ['image/png', 'image/jpeg', 'image/webp', 'image/gif'];
            if (!allowed.includes(file.type)) {
                showMessage('Formato no permitido. Usa PNG, JPG, WEBP o GIF.', 'error');
                e.target.value = '';
                return;
            }

            // Mostrar vista previa
            const reader = new FileReader();
            reader.onload = function(event) {
                previewImg.src = event.target.result;
                previewContainer.style.display = 'block';
            };
            reader.readAsDataURL(file);
        });
    }
});