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


if __name__ == '__main__':
    app.run(debug=True)