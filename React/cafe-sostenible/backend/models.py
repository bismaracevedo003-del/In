from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    
    # HASH DEL CÓDIGO DE ASOCIADO
    codigo_asociado_hash = db.Column(db.String(255), nullable=False)

    foto_perfil = db.Column(db.LargeBinary, nullable=True)
    foto_mime = db.Column(db.String(50), default='image/png')

    def __repr__(self):
        return f"<User {self.username}>"

class Finca(db.Model):
    __tablename__ = 'fincas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo_hash = db.Column(db.String(255), nullable=False, unique=True)
    codigo_original = db.Column(db.String(50), nullable=False, default='ASOC-0000')  # NUEVO