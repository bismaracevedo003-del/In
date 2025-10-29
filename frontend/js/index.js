document.addEventListener('DOMContentLoaded', () => {
    // Verifica si hay sesión activa
    fetch('/api/user', {
        method: 'GET',
        credentials: 'include', // Necesario para cookies de sesión
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('No autorizado');
    })
    .then(data => {
        // Usuario logueado → redirigir al dashboard
        console.log('Sesión activa:', data.username);
        window.location.href = '/inicio';
    })
    .catch(err => {
        // No hay sesión → mostrar página pública
        console.log('Sin sesión, mostrando página pública');
        // No hacer nada: el botón "Iniciar Sesión" ya está visible
    });
});