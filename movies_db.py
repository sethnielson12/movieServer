import os
import psycopg2
import psycopg2.extras
import urllib.parse


# def dict_factory(cursor, row):
#     d = {}
#     for idx, col in enumerate(cursor.description):
#         d[col[0]] = row[idx]
#     return d

class MoviesDB:

    def __init__(self):
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        self.cursor = self.connection.cursor()

    def __del__(self):
        # disconnect!
        self.connection.close()

    def createMoviesUsersTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS movies (id SERIAL PRIMARY KEY, title TEXT, producer TEXT, length INTEGER, rating INTEGER, genre TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, fname TEXT, lname TEXT, email TEXT, hash TEXT)")
        self.connection.commit()

    def createMovie(self, title, producer, length, rating, genre):
        sql = "INSERT INTO movies (title, producer, length, rating, genre) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(sql, [title, producer, length, rating, genre])
        self.connection.commit()
        return

    def createUser(self, fname, lname, email, hash):
        sql = "INSERT INTO users (fname, lname, email, hash) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(sql, [fname, lname, email, hash])
        self.connection.commit()
        return

    def getAllMovies(self):
        self.cursor.execute("SELECT * FROM movies")
        return self.cursor.fetchall()

    def getMovie(self, id):
        sql = "SELECT * FROM movies WHERE id = %s"
        self.cursor.execute(sql, [id]) # data must be a list
        return self.cursor.fetchone() #returns dictionary or none.

    def getUserByEmail(self, email):
        sql = "SELECT * FROM users WHERE email = %s"
        self.cursor.execute(sql, [email]) # data must be a list
        return self.cursor.fetchone() #returns dictionary or none.

    def deleteMovie(self, id):
        sql = "delete FROM movies WHERE id = %s"
        self.cursor.execute(sql, [id]) # data must be a list
        self.connection.commit()

    def updateMovie(self, title, producer, length, rating, genre, id):
        sql = "UPDATE movies SET title = %s, producer = %s, length = %s, rating = %s, genre = %s WHERE id = %s"
        self.cursor.execute(sql, [title, producer, length, rating, genre, id]) # data must be a list
        self.connection.commit()
