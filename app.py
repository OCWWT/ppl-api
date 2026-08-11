import os
import json
from flask import Flask, Response, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy


WD = os.path.dirname(os.path.abspath(__file__))
DATA_F = os.path.join(WD, 'data.json')

db = SQLAlchemy()

def create_app() -> Flask:
    _app = Flask(__name__)
    with _app.app_context():
        _app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(WD, 'database.db')
        _app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(_app)
        db.create_all()
        if Person.query.count() == 0:
            if os.path.exists(DATA_F):
                with open(DATA_F, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for person in data:
                        p = Person(
                            id=person['id'],
                            first_name=person['first_name'],
                            last_name=person['last_name'],
                            email=person['email']
                        )
                        db.session.add(p)
                    db.session.commit()
    return _app

class Person(db.Model):
    __tablename__ = 'people'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(512), nullable=False)

    @staticmethod
    def new(data: dict) -> 'Person':
        p = Person()
        p.first_name = data['first_name']
        p.last_name = data['last_name']
        p.email = data['email']
        db.session.add(p)
        db.session.commit()
        return p

    def toDict(self) -> dict:
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email
        }

app = create_app()

@app.route('/people', methods=['GET'])
def people() -> Response:
    data = []
    for p in Person.query.all():
        data.append(p.toDict())
    return jsonify(data)


@app.route('/people/new', methods=['POST'])
def new_person():
    body = request.get_json()

    if not body or not all(k in body for k in ('first_name', 'last_name', 'email')):
        return jsonify({"error": "Missing required fields"}), 400

    data = {
        'first_name': body['first_name'],
        'last_name': body['last_name'],
        'email': body['email']
    }

    p = Person.new(data)
    sync_json()
    return jsonify(p.toDict()), 201


@app.route('/', methods=['GET'])
def index() -> Response:
    return render_template('index.html')


# [sinczera ]

def sync_json():
    data = [p.toDict() for p in Person.query.all()]
    with open(DATA_F, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# [FUNÇÃO: PUT (edit do email)]

@app.route('/people/<int:person_id>/email', methods=['PUT'])
def update_email(person_id: int):
    body = request.get_json()

    if not body or 'email' not in body:
        return jsonify({"error": "Missing required 'email' field"}), 400

    person = Person.query.get(person_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    person.email = body['email']
    db.session.commit()

    sync_json()

    return jsonify({"message": f"Email for person {person_id} updated successfully"}), 200


# [FUNÇÃO: DLETE]

@app.route('/people/<int:person_id>', methods=['DELETE'])
def delete_person(person_id: int):
    person = Person.query.get(person_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    db.session.delete(person)
    db.session.commit()

    sync_json()

    return jsonify({"message": f"Person {person_id} deleted successfully"}), 200


# [FUNÇÃO UPDATE]

@app.route('/people/<int:person_id>', methods=['PATCH'])
def update_person(person_id: int):
    body = request.get_json()

    if not body:
        return jsonify({"error": "No data provided"}), 400

    person = Person.query.get(person_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    allowed_fields = ['first_name', 'last_name', 'email']
    has_changes = False

    for key, value in body.items():
        if key in allowed_fields:
            setattr(person, key, value)
            has_changes = True

    if not has_changes:
        return jsonify({"error": "No valid fields provided for update"}), 400

    db.session.commit()
    sync_json()

    return jsonify({"message": f"Person {person_id} updated successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True)