from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
import csv
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo para SQLite
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Usuario {self.nombre}>'

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Formulario para ingresar datos
@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

# Guardar datos en TXT, JSON, CSV y SQLite
@app.route('/guardar', methods=['POST'])
def guardar():
    nombre = request.form['nombre']
    email = request.form['email']

    # Guardar en TXT
    with open('datos/datos.txt', 'a', encoding='utf-8') as f:
        f.write(f'{nombre},{email}\n')

    # Guardar en JSON
    datos_json = []
    if os.path.exists('datos/datos.json'):
        with open('datos/datos.json', 'r', encoding='utf-8') as f:
            try:
                datos_json = json.load(f)
            except json.JSONDecodeError:
                datos_json = []
    datos_json.append({'nombre': nombre, 'email': email})
    with open('datos/datos.json', 'w', encoding='utf-8') as f:
        json.dump(datos_json, f, indent=4)

    # Guardar en CSV
    file_exists = os.path.isfile('datos/datos.csv')
    with open('datos/datos.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['nombre', 'email'])
        writer.writerow([nombre, email])

    # Guardar en SQLite
    nuevo_usuario = Usuario(nombre=nombre, email=email)
    db.session.add(nuevo_usuario)
    db.session.commit()

    return redirect(url_for('resultado'))

# Mostrar resultado simple
@app.route('/resultado')
def resultado():
    return render_template('resultado.html')

# Leer datos desde TXT
@app.route('/leer_txt')
def leer_txt():
    datos = []
    if os.path.exists('datos/datos.txt'):
        with open('datos/datos.txt', 'r', encoding='utf-8') as f:
            for linea in f:
                nombre, email = linea.strip().split(',')
                datos.append({'nombre': nombre, 'email': email})
    return jsonify(datos)

# Leer datos desde JSON
@app.route('/leer_json')
def leer_json():
    datos = []
    if os.path.exists('datos/datos.json'):
        with open('datos/datos.json', 'r', encoding='utf-8') as f:
            try:
                datos = json.load(f)
            except json.JSONDecodeError:
                datos = []
    return jsonify(datos)

# Leer datos desde CSV
@app.route('/leer_csv')
def leer_csv():
    datos = []
    if os.path.exists('datos/datos.csv'):
        with open('datos/datos.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                datos.append(row)
    return jsonify(datos)

# Leer datos desde SQLite
@app.route('/leer_sqlite')
def leer_sqlite():
    usuarios = Usuario.query.all()
    datos = [{'nombre': u.nombre, 'email': u.email} for u in usuarios]
    return jsonify(datos)

if __name__ == '__main__':
    # Crear base de datos si no existe
    if not os.path.exists('database'):
        os.makedirs('database')
    if not os.path.exists('datos'):
        os.makedirs('datos')
    db.create_all()
    app.run(debug=True)
