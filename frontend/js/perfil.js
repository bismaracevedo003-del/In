document.addEventListener('DOMContentLoaded', () => {
    const photoInput = document.getElementById('cambiar-foto');
    const photoImg = document.getElementById('user-photo');

    // CARGAR DATOS DEL USUARIO
    fetch('/api/user', { credentials: 'include' })
        .then(res => {
            if (!res.ok) throw new Error('No autorizado');
            return res.json();
        })
        .then(data => {
            document.getElementById('fullname').textContent = `${data.nombre} ${data.apellido}`;
            document.getElementById('username').textContent = `@${data.username}`;
            document.getElementById('codigo_asociado').textContent = data.codigo_asociado;
            if (data.foto_src) photoImg.src = data.foto_src;
        })
        .catch(() => window.location.href = '/');

    // CAMBIAR FOTO (CORREGIDO)
    photoInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Validar tamaño
        if (file.size > 5 * 1024 * 1024) {
            alert('Imagen demasiado grande. Máximo 5MB.');
            e.target.value = '';
            return;
        }

        // Validar tipo
        const allowed = ['image/png', 'image/jpeg', 'image/webp', 'image/gif'];
        if (!allowed.includes(file.type)) {
            alert('Formato no permitido. Usa PNG, JPG, WEBP o GIF.');
            e.target.value = '';
            return;
        }

        const formData = new FormData();
        formData.append('foto_perfil', file);

        // Mostrar loading
        const originalSrc = photoImg.src;
        photoImg.src = '/static/img/loading.gif'; // Opcional: spinner

        fetch('/api/cambiar-foto', {
            method: 'POST',
            body: formData,
            credentials: 'include'
        })
        .then(res => {
            // MANEJA ERRORES HTTP
            if (!res.ok) {
                return res.json().then(err => { throw err; });
            }
            return res.json();
        })
        .then(data => {
            if (data.status === 'success') {
                const reader = new FileReader();
                reader.onload = () => {
                    photoImg.src = reader.result;
                };
                reader.readAsDataURL(file);
            } else {
                throw new Error(data.message || 'Error desconocido');
            }
        })
        .catch(err => {
            console.error('Error al cambiar foto:', err);
            alert(err.message || 'No se pudo subir la foto');
            photoImg.src = originalSrc; // Restaurar imagen anterior
            e.target.value = ''; // Resetear input
        });
    });
});