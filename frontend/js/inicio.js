document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/user')
        .then(res => {
            if (!res.ok) throw new Error('No autorizado');
            return res.json();
        })
        .then(data => {
            document.getElementById('username').textContent = data.username;
        })
        .catch(err => {
            console.error(err);
            document.getElementById('username').textContent = 'Invitado';
            setTimeout(() => window.location.href = '/', 2000);
        });
});