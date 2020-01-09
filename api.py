# -*- encoding: utf-8 -*-
from flask import Flask, jsonify, request, abort, make_response
from flask_httpauth import HTTPBasicAuth
import psycopg2

auth = HTTPBasicAuth()


# Класс для работы с базой данных PostgresSQL
class dbWorker:

    # Конструктор
    def __init__(self, user, password, host, port):
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    # Метод открытия соединения с базой данных
    def open_connection(self):
        self.connection = psycopg2.connect(
          database="postgres",
          user=self.user,
          password=self.password,
          host=self.host,
          port=self.port
        )
        self.cursor = self.connection.cursor()

    # Метод закрывающий соединение с базой данных
    def close_connection(self):
      self.connection.commit()
      self.connection.close()

    # Метод создания таблицы с заданными полями
    def create_table(self, tablename):
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

    # Метод добавления записи в таблицу
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

    # Метод для получения списка всех объявлений из базы данных
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

    # Метод для получения записи по переданному id из базы данных
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
# Инициализируем экземпляр db класса dbWorker со следующими параметрами
# login = "postgres"
# password = "admin"
# host = "127.0.0.1"
# port = "5432"
db = dbWorker("postgres", "admin", "127.0.0.1", "5432")
db.open_connection()
db.create_table("advert")


# Метод получения списка объявлений с возможностью сортировки по возрастанию и убыванию по любому из полей таблицы
@app.route('/adverts/', defaults = {'page' : 0}, methods=['GET'])
@app.route('/adverts/<int:page>', methods=['GET'])
@app.route('/adverts/<string:sort>/<int:up>', defaults = {'page' : 0}, methods=['GET'])
@app.route('/adverts/<string:sort>/<int:up>/page=<int:page>', methods=['GET'])
@auth.login_required
def get_adverts(page, up = None, sort = None):
    return jsonify({'adverts': db.get_advert_list(sort,up)})


# Метод получения конкретного объявления по id, с возможностью получить опциональные поля
@app.route('/advert/<int:advert_id>', methods=['GET'])
@app.route('/advert/<int:advert_id>/<int:desc>', methods=['GET'])
@app.route('/advert/<int:advert_id>/<int:addlinks>', methods=['GET'])
@app.route('/advert/<int:advert_id>/<int:desc>/<int:addlinks>', methods=['GET'])
@auth.login_required
def get_advert(advert_id, desc = False, addlinks = False):
    query = db.get_advert_by_id(advert_id, desc, addlinks)
    if query == None:
        abort(404);
    return jsonify({"adverts" : query})


# Метод создания объявления
@app.route('/add_advert', methods=['POST'])
@auth.login_required
def create_advert():
    if (len(request.json['name']) <= 200 and len(request.json['links'].split(',')) <=3 and len(request.json['description']) <= 1000):
        id, result = db.create_record(request.json['name'], request.json['description'], request.json['links'], request.json['price'])
        return jsonify({"id" : id,
                    "result" : result})
    else:
        return jsonify({"result" : "Error",
                        "Length(name) <= 200" :  len(request.json['name']) <= 200,
                        "Count(links) <= 3" :  len(request.json['links']) <= 3,
                        "Length(description) <= 1000" :  len(request.json['description']) <= 1000
                         })


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
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


if __name__ == '__main__':
    app.run(debug=True)
