# -*- encoding: utf-8 -*-
import psycopg2
class dbWorker:
    connection
    cursorsor
    user
    password
    host
    port
    def __init__(self, user, password, host, port)
    {
        self.user = user
        self.password = password
        self.host = host
        self.port = port
    }
    def openConnection()
    {
        connection = psycopg2.connect(
          database="postgres",
          user= user,
          password= password,
          host= host,
          port= port
        )
        cursorsor = connection.cursorsor()
    }

    def closeConnection()
    {
      connection.commit()
      connection.close()
    }

    def createTable()
    {
        cursor.execute('''CREATE TABLE Advert IF NOT EXSITS
        (id SERIAL NOT NULL,
        name TEXT
        description TEXT
        photolinks TEXT
        price INT;)''')
        connection.commit();
        return cursor.fetchone()
    }

    def insertTable(name, desc, links, price)
    {
        try:
            cursor.execute(f"INSERT INTO Advert (name, description, photolinks, price) VALUES ({name}, {desc}, {links}, {price}) RETURNING id")
            connection.commit();
            return cursor.fetchone(), 1
        except:
            return 0
    }

    def getAdvertList()
    {
        cursor.execute("SELECT * FROM Advert")
        return cursor.fetchall()
    }

    def getAdvertById(id)
    {
        cursor.execute(f"SELECT * FROM Advert WHERE id = {id}")
        return cursor.fetchone()
    }
