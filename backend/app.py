from flask import Flask, send_from_directory, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import os
import hashlib
from dotenv import load_dotenv

# --- CARGAR VARIABLES DE ENTORNO ---
load_dotenv()  # Carga .env automáticamente

# --- INICIALIZACIÓN ---
app = Flask(__name__, static_folder='../frontend')

# Clave secreta desde .env
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_secret_key_dev")

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

db = SQLAlchemy(app)

# --- MODELOS ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

class Finca(db.Model):
    __tablename__ = 'fincas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo_hash = db.Column(db.String(255), nullable=False, unique=True)

# --- CREAR TABLAS (SEGURAMENTE) ---
with app.app_context():
    try:
        # Intenta conectar
        db.engine.execute("SELECT 1")
        db.create_all()
        print("Base de datos conectada y tablas verificadas.")
    except Exception as e:
        print(f"Advertencia: No se pudo conectar a la BD: {e}")
        print("   → Asegúrate de haber creado las tablas manualmente en Somee.com")

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

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Faltan datos"}), 400

    password_hash = hash_text(password)
    user = User.query.filter_by(username=username, password_hash=password_hash).first()

    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({"status": "success", "redirect": "/inicio"})
    else:
        return jsonify({"status": "error", "message": "Usuario o contraseña incorrectos"}), 401

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    codigo_asociado = request.form.get('codigo_asociado')

    if not all([username, password, codigo_asociado]):
        return jsonify({"status": "error", "message": "Todos los campos son obligatorios"}), 400

    codigo_hash = hash_text(codigo_asociado)
    finca = Finca.query.filter_by(codigo_hash=codigo_hash).first()
    if not finca:
        return jsonify({"status": "error", "message": "Código de asociado inválido"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "El usuario ya existe"}), 400

    new_user = User(username=username, password_hash=hash_text(password))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"status": "success", "message": "Registro exitoso. Ahora puedes iniciar sesión."})

@app.route('/api/user')
@login_required
def api_user():
    user = User.query.get(session['user_id'])
    return jsonify({"username": user.username})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- EJECUTAR ---
if __name__ == "__main__":
    print("Servidor iniciado en http://localhost:5000")
    app.run(debug=True, port=5000)