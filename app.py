import os
import json
import sqlite3
from flask import Flask, Response, jsonify, render_template, request

WD = os.path.dirname(os.path.abspath(__file__))
DATA_F = os.path.join(WD, 'data.json')
DB_FILE = os.path.join(WD, 'database.db')

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM people")
    if cursor.fetchone()[0] == 0:
        if os.path.exists(DATA_F):
            with open(DATA_F, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for person in data:
                    cursor.execute('''
                        INSERT INTO people (id, first_name, last_name, email)
                        VALUES (?, ?, ?, ?)
                    ''', (person['id'], person['first_name'], person['last_name'], person['email']))
            
    conn.commit()
    conn.close()

init_db()

@app.route('/people', methods=['GET'])
def people() -> Response:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, first_name, last_name, email FROM people")
    rows = cursor.fetchall()
    conn.close()
    
    people_list = [
        {'id': row[0], 'first_name': row[1], 'last_name': row[2], 'email': row[3]}
        for row in rows
    ]
    return jsonify(people_list)


@app.route('/people/new', methods=['POST'])
def new_person():
    body = request.get_json()

    if not body or not all(k in body for k in ('first_name', 'last_name', 'email')):
        return jsonify({"error": "Missing required fields"}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO people (first_name, last_name, email)
        VALUES (?, ?, ?)
    ''', (body['first_name'], body['last_name'], body['email']))
    
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    p = {
        'id': new_id,
        'first_name': body['first_name'],
        'last_name': body['last_name'],
        'email': body['email']
    }

    return jsonify(p), 201


@app.route('/', methods=['GET'])
def index() -> Response:
    return render_template('index.html')

# [sinc do json ;D]

def sync_json():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name, last_name, email FROM people")
    rows = cursor.fetchall()
    conn.close()

    data = [
        {'id': row[0], 'first_name': row[1], 'last_name': row[2], 'email': row[3]}
        for row in rows
    ]
    with open(DATA_F, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# [FUNÇÃO: PUT (edit do email)]

@app.route('/people/<int:person_id>/email', methods=['PUT'])
def update_email(person_id: int):
    body = request.get_json()

    if not body or 'email' not in body:
        return jsonify({"error": "Missing required 'email' field"}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("UPDATE people SET email = ? WHERE id = ?", (body['email'], person_id))
    changes = conn.total_changes
    conn.commit()
    conn.close()

    if changes == 0:
        return jsonify({"error": "Person not found"}), 404


    sync_json()

    return jsonify({"message": f"Email for person {person_id} updated successfully"}), 200


# [FUNÇÃO: DLETE]

@app.route('/people/<int:person_id>', methods=['DELETE'])
def delete_person(person_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM people WHERE id = ?", (person_id,))
    changes = conn.total_changes
    conn.commit()
    conn.close()

    if changes == 0:
        return jsonify({"error": "Person not found"}), 404

    sync_json()

    return jsonify({"message": f"Person {person_id} deleted successfully"}), 200


# [FUNÇÃO: UPDATE]
@app.route('/people/<int:person_id>', methods=['PATCH'])
def update_person(person_id: int):
    body = request.get_json()

    if not body:
        return jsonify({"error": "No data provided"}), 400

    allowed_fields = ['first_name', 'last_name', 'email']
    updates = []
    params = []

    for key, value in body.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            params.append(value)

    if not updates:
        return jsonify({"error": "No valid fields provided for update"}), 400

    params.append(person_id)
    query = f"UPDATE people SET {', '.join(updates)} WHERE id = ?"

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query, params)
    changes = conn.total_changes
    conn.commit()
    conn.close()

    if changes == 0:
        return jsonify({"error": "Person not found"}), 404

    sync_json()

    return jsonify({"message": f"Person {person_id} updated successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True)