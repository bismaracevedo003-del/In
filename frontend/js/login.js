const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const messageBox = document.getElementById('message-box');

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(loginForm);
    const response = await fetch('/login', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    messageBox.textContent = data.message;
    messageBox.className = data.status; // 'success' o 'error' para estilos

    // Limpiar el formulario
    loginForm.reset();

    if (data.status === 'success' && data.redirect) {
        window.location.href = data.redirect;
    }
});

registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(registerForm);
    const response = await fetch('/register', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    messageBox.textContent = data.message;
    messageBox.className = data.status;

    // Limpiar el formulario
    registerForm.reset();
});

document.addEventListener('DOMContentLoaded', () => {
    const showRegister = document.getElementById('show-register');
    const showLogin = document.getElementById('show-login');
    const registerSection = document.getElementById('register-section');
    const loginForm = document.getElementById('login-form');
    const registerToggle = document.getElementById('register-toggle'); // Texto a ocultar

    // Al hacer clic en "Regístrate aquí"
    showRegister.addEventListener('click', (e) => {
        e.preventDefault();
        registerSection.classList.add('active');
        loginForm.classList.add('hidden');
        registerToggle.classList.add('hidden'); // Ocultar el texto
    });

    // Al hacer clic en "Volver al inicio de sesión"
    showLogin.addEventListener('click', (e) => {
        e.preventDefault();
        registerSection.classList.remove('active');
        loginForm.classList.remove('hidden');
        registerToggle.classList.remove('hidden'); // Mostrar el texto
    });
});