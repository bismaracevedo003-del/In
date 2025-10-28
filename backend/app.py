from flask import Flask, send_from_directory, request, redirect, url_for, flash, jsonify, session, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import hashlib

app = Flask(__name__)
app.secret_key = "clave_segura_flask"

# --- Configuración de rutas ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

# --- Configuración de conexión SQL Server remota usando pymssql ---
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mssql+pymssql://bismar-ac_SQLLogin_1:uex7yg16hs@"
    "MQ135esp8266.mssql.somee.com/MQ135esp8266"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Modelo de usuario ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)  # Cambio a password_hash

# --- Modelo de Finca ---
class Finca(db.Model):
    __tablename__ = 'fincas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo_hash = db.Column(db.String(255), nullable=False)  # almacena hash del código

# --- Crear tabla si no existe ---
with app.app_context():
    db.create_all()

# --- Rutas de frontend ---
@app.route('/')
def index():
    return send_from_directory(os.path.join(FRONTEND_DIR, 'html'), 'login.html')

@app.route('/inicio')
def inicio():
    username = session.get('username', 'Invitado')
    return send_from_directory(os.path.join(FRONTEND_DIR, 'html'), 'inicio.html')

@app.route('/css/<path:filename>')
def css(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'css'), filename)

@app.route('/js/<path:filename>')
def js(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'js'), filename)

@app.route('/img/<path:filename>')
def img(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'img'), filename)

# --- Función para verificar contraseña ---
def verify_password(password_input, stored_hash):
    hashed_input = hashlib.sha256(password_input.encode()).hexdigest()
    return hashed_input == stored_hash

# --- Ruta para procesar el login ---
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    password_hash = hash_text(password)

    user = User.query.filter_by(username=username, password_hash=password_hash).first()
    if user:
        # Aquí ya no necesitamos session
        return jsonify({"status": "success", "redirect": "/inicio"})
    else:
        return jsonify({"status": "error", "message": "Usuario o contraseña incorrectos"})

    
# --- Ruta para registrar usuarios ---
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    codigo_asociado = request.form.get('codigo_asociado')

    if not username or not password or not codigo_asociado:
        return jsonify({"status": "error", "message": "Todos los campos son obligatorios"})

    codigo_hash = hash_text(codigo_asociado)
    finca = Finca.query.filter_by(codigo_hash=codigo_hash).first()
    if not finca:
        return jsonify({"status": "error", "message": "Código de asociado inválido"})

    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "El usuario ya existe"})

    new_user = User(username=username, password_hash=hash_text(password))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"status": "success", "message": "Usuario registrado correctamente"})


def hash_text(text):
    return hashlib.sha256(text.encode()).hexdigest()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
