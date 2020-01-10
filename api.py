# -*- encoding: utf-8 -*-
<<<<<<< HEAD
from flask import Flask, jsonify, request, abort, make_response, url_for
from flask_httpauth import HTTPBasicAuth
from flask_paginate import Pagination, get_page_parameter
import psycopg2

auth = HTTPBasicAuth()


# Класс для работы с базой данных PostgresSQL
class dbWorker:

    # Конструктор
=======
from flask import Flask, jsonify, request, abort
import psycopg2


class dbWorker:
>>>>>>> master
    def __init__(self, user, password, host, port):
        self.user = user
        self.password = password
        self.host = host
        self.port = port

<<<<<<< HEAD
    # Метод открытия соединения с базой данных
=======
>>>>>>> master
    def open_connection(self):
        self.connection = psycopg2.connect(
          database="postgres",
          user=self.user,
          password=self.password,
          host=self.host,
          port=self.port
        )
        self.cursor = self.connection.cursor()

<<<<<<< HEAD
    # Метод закрывающий соединение с базой данных
=======
>>>>>>> master
    def close_connection(self):
      self.connection.commit()
      self.connection.close()

<<<<<<< HEAD
    # Метод создания таблицы с заданными полями
    def create_table(self, tablename):
        db.open_connection()
        self.tablename = tablename
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self.tablename}
        (id SERIAL NOT NULL,
        name TEXT,
        description TEXT,
        primarylink TEXT,
        additionallinks TEXT,
        price INT,
        data TIMESTAMP);''')
        self.connection.commit()
        db.close_connection()

    # Метод добавления записи в таблицу
    def create_record(self, name, desc, links, price):
        db.open_connection()
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
        db.close_connection()

    # Метод для получения списка всех объявлений из базы данных
    def get_advert_list(self, start = 0, order = "", up = ""):
        db.open_connection()
        if order == "" and up == "":
            self.cursor.execute(f"SELECT name, primarylink, price FROM {self.tablename} LIMIT {10} OFFSET {start}")
            queryres = self.cursor.fetchall()
        else:
            if up == "down":
                self.cursor.execute(f"SELECT name, primarylink, price FROM {self.tablename} ORDER BY {order} DESC  LIMIT {10} OFFSET {start}")
                queryres = self.cursor.fetchall()
            else:
                self.cursor.execute(f"SELECT name, primarylink, price FROM {self.tablename} ORDER BY {order}  LIMIT {10} OFFSET {start}")
                queryres = self.cursor.fetchall()
        result = []
        for line in queryres:
            record = {"title": line[0],
                      "link": line[1],
                      "price": line[2]
                      }
            result.append(record)
        db.close_connection()
        return result

    # Метод для получения записи по переданному id из базы данных
    def get_advert_by_id(self, id, fields):
        db.open_connection()
        s = ""
        if fields != "":
            s = fields.split(',')
            sep = ","
        else:
            sep = ""
        self.cursor.execute(f"SELECT name, primarylink, price {sep} {fields} FROM {self.tablename} WHERE id = {id};")
        record = list(self.cursor.fetchone())
        record.reverse()
        result = {"title": record.pop(),
                  "link":  record.pop(),
                  "price": record.pop()
                  }
        if len(s) > 0:
            result[s.pop()] = record.pop()
            if len(s) > 0:
                result[s.pop()] = record.pop()
        db.close_connection()
        return result


app = Flask(__name__)
# Инициализируем экземпляр db класса dbWorker со следующими параметрами
# login = "postgres"
# password = "admin"
# host = "127.0.0.1"
# port = "5432"
db = dbWorker("postgres", "admin", "127.0.0.1", "5432")
db.create_table("advert")


# Метод получения списка объявлений с возможностью сортировки по возрастанию и убыванию по любому из полей таблицы
@app.route('/adverts', methods=['GET'])
@app.route('/adverts/page=<int:page>', methods=['GET'])
@app.route('/adverts/<string:sort>/<string:up>', methods=['GET'])
@app.route('/adverts/page=<int:page>/<string:sort>/<string:up>', methods=['GET'])
@auth.login_required
def get_adverts(page = 1, up = "", sort = ""):
    next_page_url = {}
    if len(db.get_advert_list((page)*10)) > 0:
            if sort != "":
                if up != "":
                    next_page_url = {"next_page": f'/adverts/page={page + 1}/{sort}/{up}'}
            else:
                next_page_url = {"next_page": f'/adverts/page={page + 1}'}
    a = {'adverts': db.get_advert_list((page - 1)*10, sort, up)}
    a.update(next_page_url)
    return jsonify(a), 200


# Метод получения конкретного объявления по id, с возможностью получить опциональные поля
@app.route('/advert/<int:advert_id>', methods=['GET'])
@app.route('/advert/<int:advert_id>/fields=<string:fields>', methods=['GET'])
@auth.login_required
def get_advert(advert_id, fields = ""):
    query = db.get_advert_by_id(advert_id, fields)
    if query == None:
        abort(404)
    return jsonify({"adverts": query}), 200


# Метод создания объявления
@app.route('/add_advert', methods=['POST'])
@auth.login_required
def create_advert():
    if not request.json:
        abort(404)
    elif (len(request.json['name']) <= 200 and len(request.json['links'].split(',')) <=3 and len(request.json['description']) <= 1000):
        id, result = db.create_record(request.json['name'], request.json['description'], request.json['links'], request.json['price'])
        return jsonify({"id": id,
                        "result": result}), 201
    else:
        return jsonify({"result": "Error",
                        "Length(name) <= 200":  len(request.json['name']) <= 200,
                        "Count(links) <= 3":  len(request.json['links']) <= 3,
                        "Length(description) <= 1000":  len(request.json['description']) <= 1000
                        }), 400


# Метод обработки ошибки 404
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# Метод аунтефикации пользователя python с паролем python
@auth.get_password
def get_password(username):
    if username == 'python':
        return 'python'
    return None


# Метод обработки ошибки аунтефикации
@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)
=======
    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Advert
        (id SERIAL NOT NULL,
        name TEXT,
        description TEXT,
        photolinks TEXT,
        price INT,
        data TIMESTAMP)''')
        self.connection.commit()

    def create_record(self, name, desc, links, price):
        try:
            self.cursor.execute(f"INSERT INTO Advert (name, description, photolinks, price, data) VALUES ('{name}', '{desc}', '{links}', {price}, now()) RETURNING id;")
            return cursor.fetchone(), 1
        except Exception as ex:
            return ex, 0
        finally:
            self.connection.commit()

    def get_advert_list(self, order = None, up = None):
        if order == None:
            self.cursor.execute("SELECT * FROM Advert")
            return self.cursor.fetchall()
        else:
            if up == False:
                self.cursor.execute(f"SELECT * FROM Advert ORDER BY {order} DESC")
                return self.cursor.fetchall()
            else:
                self.cursor.execute(f"SELECT * FROM Advert ORDER BY {order}")
                return self.cursor.fetchall()

    def get_advert_by_id(self, id):
        self.cursor.execute(f"SELECT * FROM Advert WHERE id = {id};")
        return self.cursor.fetchone()



app = Flask(__name__)
db = dbWorker("postgres","admin","127.0.0.1","5432")
db.open_connection()
db.create_table()

@app.route('/')
def index():
    return "Api"

@app.route('/adverts/<string:sort>/<int:up>', methods=['GET'])
def get_adverts(sort,up ):
    if sort != None and up != None:
        return jsonify({'adverts': db.get_advert_list(sort,up)})
    else:
        return jsonify({'adverts': db.get_advert_list()})


@app.route('/advert/<int:advert_id>', methods=['GET'])
def get_advert(advert_id):
    query = db.get_advert_by_id(advert_id)
    if query == None:
        abort(404);
    return jsonify({"adverts" : query})


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
>>>>>>> master


if __name__ == '__main__':
    app.run(debug=True)
