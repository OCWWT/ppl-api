import os
import json

from flask import Flask, Response, jsonify, render_template, request

WD = os.path.dirname(os.path.abspath(__file__))
DATA_F = os.path.join(WD, 'data.json')


def read_data() -> list[dict]:
    with open(DATA_F, 'r', encoding='utf-8') as f:
        return json.load(f)


app = Flask(__name__)


@app.route('/people', methods=['GET'])
def people() -> Response:
    return jsonify(read_data())


@app.route('/people/new', methods=['POST'])
def new_person():

    data = read_data()
    body = request.get_json()

    new_id = 1 if not data else data[-1]['id'] + 1

    p = {
        'id': new_id,
        'first_name': body['first_name'],
        'last_name': body['last_name'],
        'email': body['email']
    }

    data.append(p)

    with open(DATA_F, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return jsonify(p), 201


@app.route('/', methods=['GET'])
def index() -> Response:
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)