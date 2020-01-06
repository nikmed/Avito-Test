# -*- encoding: utf-8 -*-
from flask import Flask, jsonify, request, abort
import psycopg2


class dbWorker:
    def __init__(self, user, password, host, port):
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def open_connection(self):
        self.connection = psycopg2.connect(
          database="postgres",
          user=self.user,
          password=self.password,
          host=self.host,
          port=self.port
        )
        self.cursor = self.connection.cursor()

    def close_connection(self):
      self.connection.commit()
      self.connection.close()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Advert
        (id SERIAL NOT NULL,
        name TEXT,
        description TEXT,
        photolinks TEXT,
        price INT)''')
        self.connection.commit()

    def create_record(self, name, desc, links, price):
        try:
            self.cursor.execute(f"INSERT INTO Advert (name, description, photolinks, price) VALUES ('{name}', '{desc}', '{links}', {price}) RETURNING id;")
            return cursor.fetchone(), 1
        except Exception as ex:
            return ex, 0
        finally:
            self.connection.commit()

    def get_advert_list(self):
        self.cursor.execute("SELECT * FROM Advert")
        return self.cursor.fetchall()

    def get_advert_by_id(self, id):
        self.cursor.execute(f"SELECT * FROM Advert WHERE id = {id}")
        return self.cursor.fetchone()



app = Flask(__name__)
db = dbWorker("postgres","admin","127.0.0.1","5432")
db.open_connection()
db.create_table()

@app.route('/')
def index():
    return "Api"

@app.route('/adverts', methods=['GET'])
def get_adverts():
    return jsonify({'adverts': db.get_advert_list()})


@app.route('/advert/<int:advert_id>', methods=['GET'])
def get_advert(advert_id):
    task = filter(lambda t: t['id'] == advert_id, adverts)
    if len(advert) == 0:
        abort(404)
    return jsonify({'advert': db.get_advert_by_id(id)})


@app.route('/adverts', methods=['POST'])
def create_advert():
    advert = {
        'name': request.json['name'],
        'description': request.json['description'],
        'links': request.json['links'],
        'price': request.json['price']
    }
    db.create_record(request.json['name'], request.json['description'], request.json['links'], request.json['price'])
    return jsonify({'advert': advert})


if __name__ == '__main__':
    app.run(debug=True)
