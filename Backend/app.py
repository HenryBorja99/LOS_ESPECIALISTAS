from flask import Flask, request, jsonify #pip install Flask
from flask_cors import CORS # Necesitas instalar 'flask-cors': pip install Flask-Cors
from pymongo import MongoClient # Usaremos MongoDB, instala pymongo: pip install pymongo
import bcrypt # pip install bcrypt
import jwt # pip install PyJWT
import os
from dotenv import load_dotenv # pip install python-dotenv
from functools import wraps
from bson.objectid import ObjectId # pip install pymongo
from dotenv import load_dotenv
load_dotenv() # Carga las variables de entorno del archivo .env

app = Flask(__name__)
CORS(app) # Habilita CORS para todas las rutas

MONGO_URI = os.getenv('MONGO_URI')
JWT_SECRET = os.getenv('JWT_SECRET')

# Conexión a MongoDB
client = MongoClient(MONGO_URI)
db = client.los_especialistas # Nombre de tu base de datos
users_collection = db.users # Colección de usuarios

# Ruta de Registro
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'especialista')  # Por defecto, el rol es 'especialista'

    if not all([name, email, password]):
        return jsonify({'message': 'Faltan campos obligatorios'}), 400
    if users_collection.find_one({'name': name}):
        return jsonify({'message': 'El nombre de usuario ya está registrado'}), 409

    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'El correo electrónico ya está registrado'}), 409

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    user_id = users_collection.insert_one({
        'name': name,
        'email': email,
        'password': hashed_password.decode('utf-8'),
        'role': role,
        'specialty': '', # Campos iniciales vacíos
        'skills': [],
        'location': '',
        'summary': ''
    }).inserted_id

    return jsonify({'message': 'Usuario registrado con éxito', 'userId': str(user_id)}), 201

# Ruta de Actualización de Perfil
@app.route('/api/profile/update', methods=['PUT'])
def update_profile():
    data = request.get_json()
    email = data.get('email')  # identificador único del usuario

    if not email:
        return jsonify({'message': 'El correo electrónico es obligatorio'}), 400

    user = users_collection.find_one({'email': email})
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    

    updated_fields = {}
    if 'name' in data:
        updated_fields['name'] = data['name']
    if 'specialty' in data:
        updated_fields['specialty'] = data['specialty']
    if 'skills' in data:
        updated_fields['skills'] = [s.strip() for s in data['skills'].split(',')] if isinstance(data['skills'], str) else data['skills']
    if 'location' in data:
        updated_fields['location'] = data['location']
    if 'summary' in data:
        updated_fields['summary'] = data['summary']

    users_collection.update_one({'email': email}, {'$set': updated_fields})

    return jsonify({'message': 'Perfil actualizado correctamente'}), 200

# Ruta de Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({'email': email})

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'message': 'Credenciales inválidas'}), 401

    token = jwt.encode({'user_id': str(user['_id'])}, JWT_SECRET, algorithm='HS256')
    return jsonify({'token': token}), 200

# Middleware para proteger rutas (ejemplo)
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]

        if not token:
            return jsonify({'message': 'Token es requerido'}), 401

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user = users_collection.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                return jsonify({'message': 'Usuario no encontrado'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token ha expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

from functools import wraps
from bson.objectid import ObjectId # pip install pymongo

# Ruta de Perfil (protegida)
@app.route('/api/profile', methods=['GET', 'PUT'])
@token_required
def profile(current_user):
    if request.method == 'GET':
        user_data = {
            'name': current_user.get('name'),
            'email': current_user.get('email'),
            'role': current_user.get('role'),
            'specialty': current_user.get('specialty'),
            'skills': current_user.get('skills'),
            'location': current_user.get('location'),
            'summary': current_user.get('summary')
            # No devolver el password
        }
        return jsonify(user_data), 200
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        # Filtrar solo los campos permitidos para actualización
        update_fields = {}
        if 'name' in data: update_fields['name'] = data['name']
        if 'email' in data: update_fields['email'] = data['email']
        if 'specialty' in data: update_fields['specialty'] = data['specialty']
        if 'skills' in data: update_fields['skills'] = data['skills']
        if 'location' in data: update_fields['location'] = data['location']
        if 'summary' in data: update_fields['summary'] = data['summary']

        users_collection.update_one({'_id': current_user['_id']}, {'$set': update_fields})
        return jsonify({'message': 'Perfil actualizado con éxito'}), 200

# Ruta para obtener todos los candidatos
@app.route('/api/candidatos', methods=['GET'])
def get_candidatos():
    candidatos = list(users_collection.find({}, {
        '_id': 0,
        'name': 1,
        'email': 1,
        'specialty': 1,
        'skills': 1,
        'location': 1,
        'summary': 1
    }))
    return jsonify(candidatos), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000) # Corre en http://localhost:5000
