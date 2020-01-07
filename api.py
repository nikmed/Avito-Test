# -*- encoding: utf-8 -*-
from flask import Flask, jsonify, request, abort, make_response
from flask_httpauth import HTTPBasicAuth
import psycopg2

auth = HTTPBasicAuth()


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

    def create_table(self, tablename):
        self.tablename = tablename
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self.tablename}
        (id SERIAL NOT NULL,
        name TEXT,
        description TEXT,
        primarylink TEXT,
        additionallinks TEXT,
        price INT,
        data TIMESTAMP)''')
        self.connection.commit()

    def create_record(self, name, desc, links, price):
        splitedlinks = links.split(',')
        primarylink = splitedlinks[0]
        splitedlinks.remove(splitedlinks[0])
        additionallinks = splitedlinks
        try:
            self.cursor.execute(f"INSERT INTO {self.tablename} (name, description, primarylink, additionallinks, price, data) VALUES ('{name}', '{desc}', '{primarylink}', '{','.join(additionallinks)}', '{price}', now()) RETURNING id;")
            return self.cursor.fetchone()[0], "Success"
        except Exception as ex:
            return str(ex), "Error"
        finally:
            self.connection.commit()

    def get_advert_list(self, order = None, up = None):
        if order == None and up == None:
            self.cursor.execute(f"SELECT name, primarylink, price FROM {self.tablename}")
            return self.cursor.fetchall()
        else:
            if up == False:
                self.cursor.execute(f"SELECT name, primarylink, price FROM {self.tablename} ORDER BY {order} DESC")
                return self.cursor.fetchall()
            else:
                self.cursor.execute(f"SELECT name, primarylink, price FROM {self.tablename} ORDER BY {order}")
                return self.cursor.fetchall()

    def get_advert_by_id(self, id, desc = 0, addlinks = 0):
        if desc == True and addlinks == True:
            self.cursor.execute(f"SELECT name, price, primarylink, description, additionallinks FROM {self.tablename} WHERE id = {id};")
        elif desc == False and addlinks == False:
            self.cursor.execute(f"SELECT name, price, primarylink FROM {self.tablename} WHERE id = {id};")
        elif desc == True:
            self.cursor.execute(f"SELECT name, price, primarylink, description FROM {self.tablename} WHERE id = {id};")
        else:
            self.cursor.execute(f"SELECT name, price, primarylink, additionallinks FROM {self.tablename} WHERE id = {id};")
        return self.cursor.fetchone()



app = Flask(__name__)
db = dbWorker("postgres","admin","127.0.0.1","5432")
db.open_connection()
db.create_table("advert")

@app.route('/')
def index():
    return "Api"

@app.route('/adverts/', defaults = {'page' : 0}, methods=['GET'])
@app.route('/adverts/<int:page>', methods=['GET'])
@app.route('/adverts/<string:sort>/<int:up>', defaults = {'page' : 0}, methods=['GET'])
@app.route('/adverts/<string:sort>/<int:up>/page=<int:page>', methods=['GET'])
@auth.login_required
def get_adverts(page, up = None, sort = None):
    return jsonify({'adverts': db.get_advert_list(sort,up)})


@app.route('/advert/<int:advert_id>/<int:desc>/<int:addlinks>', methods=['GET'])
@auth.login_required
def get_advert(advert_id, desc = False, addlinks = False):
    query = db.get_advert_by_id(advert_id, desc, addlinks)
    if query == None:
        abort(404);
    return jsonify({"adverts" : query})


@app.route('/add_advert', methods=['POST'])
@auth.login_required
def create_advert():
    id, result = db.create_record(request.json['name'], request.json['description'], request.json['links'], request.json['price'])
    return jsonify({"id" : id,
                    "result" : result})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@auth.get_password
def get_password(username):
    if username == 'python':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)

if __name__ == '__main__':
    app.run(debug=True)
