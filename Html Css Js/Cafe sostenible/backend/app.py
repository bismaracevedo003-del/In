from flask import Flask, send_from_directory, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import os
import hashlib
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import uuid
import base64

# --- CARGAR VARIABLES DE ENTORNO ---
load_dotenv()  # Carga .env automáticamente

# --- INICIALIZACIÓN ---
app = Flask(__name__, static_folder='../frontend')

# Clave secreta desde .env
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_secret_key_dev")
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY", "super-secret-key-dev")
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'      # Crucial para navegación
app.config['SESSION_COOKIE_SECURE'] = False        # True en HTTPS
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600    # 1 hora
# Debug desde .env
app.config['DEBUG'] = os.getenv("FLASK_DEBUG", "False") == "True"

# --- RUTAS ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')
HTML_DIR = os.path.join(FRONTEND_DIR, 'html')
CSS_DIR = os.path.join(FRONTEND_DIR, 'css')
JS_DIR = os.path.join(FRONTEND_DIR, 'js')
IMG_DIR = os.path.join(FRONTEND_DIR, 'img')

# --- CONFIGURACIÓN DE BASE DE DATOS (desde .env) ---
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

# --- FUNCIÓN HASH ---
def hash_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

# --- DECORADOR LOGIN ---
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"status": "error", "message": "Debes iniciar sesión"}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS FRONTEND ---
@app.route('/')
def index():
    """Página pública si no hay sesión, redirige a inicio si hay sesión"""
    if 'user_id' in session:
        return redirect(url_for('inicio'))
    return send_from_directory(HTML_DIR, 'index.html')  # ← nueva página

@app.route('/inicio')
@login_required
def inicio():
    """Dashboard del usuario"""
    return send_from_directory(HTML_DIR, 'inicio.html')

# --- ESTÁTICOS ---
@app.route('/css/<path:filename>')
def css(filename):
    return send_from_directory(CSS_DIR, filename)

@app.route('/js/<path:filename>')
def js(filename):
    return send_from_directory(JS_DIR, filename)

@app.route('/img/<path:filename>')
def img(filename):
    return send_from_directory(IMG_DIR, filename)

# --- API ---
@app.route('/login')
def login_page():
    """Muestra el formulario de login"""
    return send_from_directory(HTML_DIR, 'login.html')

@app.route('/perfil')
@login_required
def perfil():
    return send_from_directory(HTML_DIR, 'perfil.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Faltan datos"}), 400

    password_hash = hash_text(password)
    user = User.query.filter_by(username=username, password_hash=password_hash).first()

    if user:
        # GUARDAR SESIÓN
        session['user_id'] = user.id
        session['username'] = user.username
        print(f"Login exitoso: {user.username} (ID: {user.id})")  # DEBUG
        return jsonify({"status": "success", "redirect": "/inicio"})
    else:
        return jsonify({"status": "error", "message": "Usuario o contraseña incorrectos"}), 401

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    codigo_asociado = request.form.get('codigo_asociado')  # texto plano
    foto = request.files.get('foto_perfil')

    if not all([username, password, nombre, apellido, codigo_asociado]):
        return jsonify({"status": "error", "message": "Todos los campos son obligatorios"}), 400

    # HASHEAR CÓDIGO DE ASOCIADO
    codigo_hash = hash_text(codigo_asociado)

    # VERIFICAR EN TABLA FINCAS
    finca = Finca.query.filter_by(codigo_hash=codigo_hash).first()
    if not finca:
        return jsonify({"status": "error", "message": "Código de asociado inválido"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "El usuario ya existe"}), 400

    # PROCESAR FOTO
    foto_blob = None
    foto_mime = 'image/png'
    if foto and foto.filename:
        if foto.content_length > 5 * 1024 * 1024:
            return jsonify({"status": "error", "message": "Imagen demasiado grande"}), 400
        if foto.mimetype not in {'image/png', 'image/jpeg', 'image/webp', 'image/gif'}:
            return jsonify({"status": "error", "message": "Formato no permitido"}), 400
        foto_blob = foto.read()
        foto_mime = foto.mimetype

    # CREAR USUARIO CON HASH
    new_user = User(
        username=username,
        password_hash=hash_text(password),
        nombre=nombre,
        apellido=apellido,
        codigo_asociado_hash=codigo_hash,  # HASH GUARDADO
        foto_perfil=foto_blob,
        foto_mime=foto_mime
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"status": "success", "message": "Registro exitoso"})

@app.route('/api/user')
@login_required
def api_user():
    user = User.query.get(session['user_id'])
    
    # BUSCAR FINCA PARA OBTENER CÓDIGO PLANO
    finca = Finca.query.filter_by(codigo_hash=user.codigo_asociado_hash).first()
    codigo_plano = finca.codigo_original if finca else "Desconocido"

    foto_base64 = None
    if user.foto_perfil:
        foto_base64 = base64.b64encode(user.foto_perfil).decode('utf-8')

    return jsonify({
        "username": user.username,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "codigo_asociado": codigo_plano,  # TEXTO PLANO
        "foto_src": f"data:{user.foto_mime};base64,{foto_base64}" if foto_base64 else "/img/usuarios/default-user.png"
    })

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"status": "error", "message": "Archivo demasiado grande"}), 413

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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- EJECUTAR ---
if __name__ == "__main__":
    print("Servidor iniciado en http://localhost:5000")
    app.run(debug=True, port=5000)