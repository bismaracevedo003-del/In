# backend/app.py
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import hashlib
from dotenv import load_dotenv
import base64

# --- CARGAR .env ---
load_dotenv()

# --- INICIALIZACIÓN ---
app = Flask(__name__)
CORS(app, supports_credentials=True)  # Crucial para cookies

app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # True en producción
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# --- BASE DE DATOS ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mssql+pymssql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# --- IMPORTAR MODELOS ---
from models import db, User, Finca
db.init_app(app)

# --- CREAR TABLAS (SEGURO Y COMPATIBLE) ---
with app.app_context():
    try:
        # Verifica conexión con una consulta simple
        db.session.execute(db.text("SELECT 1"))
        db.session.commit()
        print("Conexión a la base de datos exitosa.")
        
        # Crea tablas si no existen
        db.create_all()
        print("Tablas verificadas/creadas correctamente.")
        
    except Exception as e:
        print(f"No se pudo conectar a la base de datos: {e}")
        print("   → Crea las tablas manualmente en Somee.com o revisa las credenciales.")
        print("   → Asegúrate de que pymssql esté instalado: pip install pymssql")

# --- UTILIDADES ---
def hash_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"status": "error", "message": "No autorizado"}), 401
        return f(*args, **kwargs)
    return decorated

# --- API REST ---
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.form
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Faltan datos"}), 400

    user = User.query.filter_by(
        username=username,
        password_hash=hash_text(password)
    ).first()

    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({"status": "success", "message": "Login exitoso"})
    
    return jsonify({"status": "error", "message": "Credenciales inválidas"}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.form
    foto = request.files.get('foto_perfil')

    required = ['username', 'password', 'nombre', 'apellido', 'codigo_asociado']
    if not all(data.get(field) for field in required):
        return jsonify({"status": "error", "message": "Faltan campos"}), 400

    # Verificar código de asociado
    codigo_hash = hash_text(data['codigo_asociado'])
    finca = Finca.query.filter_by(codigo_hash=codigo_hash).first()
    if not finca:
        return jsonify({"status": "error", "message": "Código inválido"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"status": "error", "message": "Usuario existe"}), 400

    # Procesar foto
    foto_blob = None
    foto_mime = 'image/png'
    if foto and foto.filename:
        if foto.content_length > 5 * 1024 * 1024:
            return jsonify({"status": "error", "message": "Imagen > 5MB"}), 400
        if foto.mimetype not in {'image/png', 'image/jpeg', 'image/webp', 'image/gif'}:
            return jsonify({"status": "error", "message": "Formato no permitido"}), 400
        foto_blob = foto.read()
        foto_mime = foto.mimetype

    # Crear usuario
    user = User(
        username=data['username'],
        password_hash=hash_text(data['password']),
        nombre=data['nombre'],
        apellido=data['apellido'],
        codigo_asociado_hash=codigo_hash,
        foto_perfil=foto_blob,
        foto_mime=foto_mime
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"status": "success", "message": "Registro exitoso"})

@app.route('/api/user')
@login_required
def api_user():
    user = User.query.get(session['user_id'])
    finca = Finca.query.filter_by(codigo_hash=user.codigo_asociado_hash).first()
    codigo_plano = finca.codigo_original if finca else "Desconocido"

    foto_src = "/img/usuarios/default-user.png"
    if user.foto_perfil:
        foto_base64 = base64.b64encode(user.foto_perfil).decode()
        foto_src = f"data:{user.foto_mime};base64,{foto_base64}"

    return jsonify({
        "username": user.username,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "codigo_asociado": codigo_plano,
        "foto_src": foto_src
    })

@app.route('/api/cambiar-foto', methods=['POST'])
@login_required
def cambiar_foto():
    foto = request.files.get('foto_perfil')
    if not foto or not foto.filename:
        return jsonify({"status": "error", "message": "No se envió foto"}), 400

    if foto.mimetype not in {'image/png', 'image/jpeg', 'image/webp', 'image/gif'}:
        return jsonify({"status": "error", "message": "Formato no permitido"}), 400

    foto_blob = foto.read()
    user = User.query.get(session['user_id'])
    user.foto_perfil = foto_blob
    user.foto_mime = foto.mimetype
    db.session.commit()

    return jsonify({"status": "success", "message": "Foto actualizada"})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"status": "success", "message": "Sesión cerrada"})

# --- INICIAR ---
if __name__ == '__main__':
    print("API corriendo en http://localhost:5000")
    app.run(debug=True, port=5000)