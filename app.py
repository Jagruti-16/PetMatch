from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.utils import secure_filename

import base64
app = Flask(__name__)
CORS(app)
app.config.from_pyfile('config.py')

mysql = MySQL(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    age = data.get('age')
    address = data.get('address')
    contact_number = data.get('contact_number')
    email = data.get('email')

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO users (username, password, first_name, last_name, age, address, contact_number, email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                   (username, hashed_password, first_name, last_name, age, address, contact_number, email))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'msg': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()

    if user and bcrypt.check_password_hash(user[2], password):
        access_token = create_access_token(identity={'username': username,'user_id': user[0]})
        return jsonify({
            'token': access_token,
            'user_id': user[0],   # Add user_id to response
            'username': username  # Add username to response
        }), 200
    return jsonify({'msg': 'Invalid credentials'}), 401

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT username, first_name, last_name, age, address, contact_number, email FROM users WHERE username = %s', (current_user['username'],))
    user = cursor.fetchone()
    cursor.close()
    user_data = {
        'username': user[0],
        'first_name': user[1],
        'last_name': user[2],
        'age': user[3],
        'address': user[4],
        'contact_number': user[5],
        'email': user[6]
    }
    return jsonify(user_data), 200


@app.route('/api/recent_pets', methods=['GET'])
def recent_pets():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT name, breed, age, date_added,image FROM pets WHERE adopted=FALSE ORDER BY date_added DESC LIMIT 5')
    pets = cursor.fetchall()
    cursor.close()

    pets_list = []
    for pet in pets:
        pet_data = {
            'name': pet[0],
            'breed': pet[1],
            'age': pet[2],
            'date_added': pet[3].strftime('%Y-%m-%d %H:%M:%S'),
            'image': base64.b64encode(pet[4]).decode('utf-8') if pet[4] else None
        }
        pets_list.append(pet_data)

    return jsonify(pets_list), 200

@app.route('/api/add_pet', methods=['POST'])
def add_pet():
    try:
        
        print(request.form)
        print(request.files)

       
        name = request.form.get('name')
        breed = request.form.get('breed')
        age = request.form.get('age')
        owner_id = request.form.get('owner_id')

       
        image = request.files.get('image')
        if image:
           
            filename = secure_filename(image.filename)
            image_data = image.read()
        else:
            image_data = None

       
        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO pets (name, breed, age, owner_id, image) VALUES (%s, %s, %s, %s, %s)',
            (name, breed, age, owner_id, image_data)
        )
        mysql.connection.commit()
        cursor.close()

        return jsonify({'msg': 'Pet added successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@app.route('/api/pets/<int:pet_id>', methods=['GET'])
def get_pet_by_id(pet_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT name, breed, age, date_added, image FROM pets WHERE id = %s', (pet_id,))
    pet = cursor.fetchone()
    cursor.close()

    if pet:
        pet_data = {
            'name': pet[0],
            'breed': pet[1],
            'age': pet[2],
            'date_added': pet[3].strftime('%Y-%m-%d %H:%M:%S'),
            'image': base64.b64encode(pet[4]).decode('utf-8') if pet[4] else None
        }
        return jsonify(pet_data), 200
    else:
        return jsonify({'msg': 'Pet not found'}), 404
@app.route('/api/pets', methods=['GET'])
def get_pets():
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT 
            pets.id, pets.name, pets.breed, pets.age, pets.date_added, pets.image, 
            users.first_name, users.last_name, users.address
        FROM 
            pets
        LEFT JOIN 
            users ON pets.owner_id = users.id
        WHERE 
            pets.adopted = FALSE
    ''')
    pets = cursor.fetchall()
    cursor.close()

    pets_list = []
    for pet in pets:
        pet_data = {
            'id': pet[0],
            'name': pet[1],
            'breed': pet[2],
            'age': pet[3],
            'date_added': pet[4].strftime('%Y-%m-%d %H:%M:%S'),
            'image': base64.b64encode(pet[5]).decode('utf-8') if pet[5] else None,
            'owner': {
                'first_name': pet[6],
                'last_name': pet[7],
                'address': pet[8]
            }
        }
        pets_list.append(pet_data)

    return jsonify(pets_list), 200
@app.route('/api/get_user_id', methods=['POST'])
def get_user_id():
    data = request.json
    username = data.get('username')

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
    user_id = cursor.fetchone()
    cursor.close()

    if user_id:
        return jsonify({'user_id': user_id[0]}), 200
    else:
        return jsonify({'error': 'User not found'}), 404
@app.route('/api/adopt_pet', methods=['POST'])
@jwt_required()
def adopt_pet():
    current_user = get_jwt_identity()
    data = request.get_json()
    pet_id = data.get('pet_id')

    cursor = mysql.connection.cursor()

   
    cursor.execute('SELECT * FROM pets WHERE id = %s', (pet_id,))
    pet = cursor.fetchone()

    if not pet:
        cursor.close()
        return jsonify({'msg': 'Pet not found'}), 404

   
    if pet[-1]:  
        cursor.close()
        return jsonify({'msg': 'Pet is already adopted'}), 400

   
    cursor.execute('INSERT INTO adoptions (pet_id, adopter_id) VALUES (%s, %s)', (pet_id, current_user['user_id']))

    
    cursor.execute('UPDATE pets SET adopted = TRUE WHERE id = %s', (pet_id,))
    
    mysql.connection.commit()
    cursor.close()

    return jsonify({'msg': 'Pet adopted successfully'}), 201

@app.route('/api/profile/update', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user = get_jwt_identity()
    data = request.get_json()

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE users SET first_name = %s, last_name = %s, age = %s, address = %s, contact_number = %s 
        WHERE username = %s
    """, (data['first_name'], data['last_name'], data['age'], data['address'], data['contact_number'], current_user['username']))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'msg': 'Profile updated successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
