document.addEventListener('DOMContentLoaded', () => {
    console.log('Cookies:', document.cookie);  // DEBUG

    fetch('/api/user', { 
        credentials: 'include'  // ¡¡CRUCIAL!!
    })
    .then(res => {
        console.log('Status:', res.status);  // Debe ser 200
        if (!res.ok) throw new Error('No autorizado');
        return res.json();
    })
    .then(data => {
        console.log('Usuario:', data);
        document.getElementById('fullname').textContent = `${data.nombre} ${data.apellido}`;
        document.getElementById('username').textContent = `@${data.username}`;
        if (data.foto_src) {
            document.getElementById('user-photo').src = data.foto_src;
        }
    })
    .catch(err => {
        console.error('Error:', err);
        document.getElementById('fullname').textContent = 'Invitado';
        setTimeout(() => window.location.replace('/'), 2000);
    });
});