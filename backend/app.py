from flask import Flask, send_from_directory, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import urllib
import os

app = Flask(__name__)
app.secret_key = "clave_segura_flask"

# --- Configuración de rutas ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

# --- Configuración de conexión SQL Server remota ---
params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=MQ135esp8266.mssql.somee.com;"
    "DATABASE=MQ135esp8266;"
    "UID=bismar-ac_SQLLogin_1;"
    "PWD=uex7yg16hs;"
    "TrustServerCertificate=yes;"
)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc:///?odbc_connect={params}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Modelo de usuario ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

# --- Crear tabla si no existe ---
with app.app_context():
    db.create_all()

# --- Rutas de frontend ---
@app.route('/')
def index():
    return send_from_directory(os.path.join(FRONTEND_DIR, 'html'), 'login.html')

@app.route('/inicio')
def inicio():
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

# --- Ruta para procesar el login ---
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username, password=password).first()

    if user:
        flash(f"Bienvenido, {username}", "success")
        return redirect(url_for('inicio'))  # Redirige a inicio.html
    else:
        flash("Usuario o contraseña incorrectos", "error")
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
