from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import json
import sys
from movies_db import MoviesDB
from passlib.hash import bcrypt
from session_store import SessionStore
from http import cookies

gSessionStore = SessionStore()

class MyRequestHandler(BaseHTTPRequestHandler):

    def end_headers(self):
        self.sendCookie()
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        BaseHTTPRequestHandler.end_headers(self)

    def handle401(self):
         self.send_response(401) #not logged in
         self.end_headers()

    def handleNotFound(self):
        self.send_response(404)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Could not find data you're looking for, or the parameters entered are invalid", "utf-8"))

    def loadCookie(self):
        if "Cookie" in self.headers:
            self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
        else:
            self.cookie = cookies.SimpleCookie()

    def sendCookie(self):
        for morsel in self.cookie.values():
            self.send_header("Set-Cookie", morsel.OutputString())

    def loadSession(self):
        self.loadCookie()
        if "sessionId" in self.cookie:
            #session ID found in the cookie
            sessionId = self.cookie["sessionId"].value
            self.session = gSessionStore.getSessionData(sessionId)
            if self.session == None:
                #session ID no longer found in hte session store
                #create brand new session ID
                sessionId = gSessionStore.createSession()
                self.session = gSessionStore.getSessionData(sessionId)
                self.cookie["sessionId"] = sessionId
        else:
            #no session ID found in the cookie
            #create brand new session ID
            sessionId = gSessionStore.createSession()
            self.session = gSessionStore.getSessionData(sessionId)
            self.cookie["sessionId"] = sessionId

    def isLoggedIn(self):
        if "userId" in self.session:
            return True
        else:
            return False

    def handleMoviesList(self):

        if self.isLoggedIn():
            self.send_response(200)
            # all headers go here:
            self.send_header("Content-type", "application/json")
            self.end_headers()

            db = MoviesDB()
            movies = db.getAllMovies()
            self.wfile.write(bytes(json.dumps(movies), "utf-8"))
        else:
           self.handle401()



    def handleMoviesCreate(self):

        if self.isLoggedIn():
            length = self.headers["Content-length"]
            body = self.rfile.read(int(length)).decode("utf-8")
            print("the text body:", body)
            parsed_body = parse_qs(body)
            print("the parsed body:", parsed_body)

            # save the movie!
            title = parsed_body["title"][0]
            producer = parsed_body["producer"][0]
            length = parsed_body["length"][0]
            rating = parsed_body["rating"][0]
            genre = parsed_body["genre"][0]
            # send these values to the DB!
            db = MoviesDB()
            db.createMovie(title, producer, length, rating, genre)

            self.send_response(201)
            self.end_headers()
        else:
            self.handle401()

    def handleUsersCreate(self):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        print("the text body:", body)
        parsed_body = parse_qs(body)
        print("the parsed body:", parsed_body)

        # save the user!
        fname = parsed_body["fname"][0]
        lname = parsed_body["lname"][0]
        email = parsed_body["email"][0]
        pswrd = parsed_body["password"][0]
        hash = bcrypt.hash(pswrd)
        # send these values to the DB!
        db = MoviesDB()
        user = db.getUserByEmail(email)

        #check for duplicate email

        if user == None:

            db.createUser(fname, lname, email, hash)

            self.send_response(201)
            self.end_headers()
        else:
            self.send_response(422)
            self.end_headers()

    def handleSessionCreate(self):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        print("the text body:", body)
        parsed_body = parse_qs(body)
        print("the parsed body:", parsed_body)

        # save the user!
        email = parsed_body["email"][0]
        pswrd = parsed_body["password"][0]
        # send these values to the DB!
        db = MoviesDB()
        user = db.getUserByEmail(email)

        if user != None:
            userHash = user["hash"]
            print("the hash from the db:", userHash)
            if bcrypt.verify(pswrd, userHash):
                # todo: save user id in session data
                self.session["userId"] = user["id"]
                self.send_response(201)
                self.end_headers()
            else:
                self.handle401()
        else:
            self.send_response(401)
            self.end_headers()


    def handleMoviesDelete(self, id):

        if self.isLoggedIn():
            db = MoviesDB()
            movie = db.getMovie(id)

            if movie == None:
                self.handleNotFound()
            else:
                db.deleteMovie(id)
                self.send_response(200)
                self.end_headers()
        else:
            self.handle401()


    def handleMoviesUpdate(self, id):

        if self.isLoggedIn():
            db = MoviesDB()
            movie = db.getMovie(id)

            if movie == None:
                self.handleNotFound()
            else:
                length = self.headers["Content-length"]
                body = self.rfile.read(int(length)).decode("utf-8")
                print("the text body:", body)
                parsed_body = parse_qs(body)
                print("the parsed body:", parsed_body)

                # save the movie!
                title = parsed_body["title"][0]
                producer = parsed_body["producer"][0]
                length = parsed_body["length"][0]
                rating = parsed_body["rating"][0]
                genre = parsed_body["genre"][0]
                # send these values to the DB!
                db.updateMovie(title, producer, length, rating, genre, id)

                self.send_response(200)
                self.end_headers()
        else:
            self.handle401()

    def handleMoviesRetrieve(self, id):

        if self.isLoggedIn():
            db = MoviesDB()
            movie = db.getMovie(id)

            if movie == None:
                self.handleNotFound()
            else:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(bytes(json.dumps(movie), "utf-8"))
        else:
            self.handle401()



    def do_OPTIONS(self):
        self.loadSession()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-type")

        self.end_headers()

    def do_GET(self):
        self.loadSession()
        # parse the path to find the collection and identifier
        parts = self.path.split('/')[1:]
        collection = parts[0]
        if len(parts) > 1:
            id = parts[1]
        else:
            id = None

        if collection == "movies":
            if id == None:
                self.handleMoviesList()
            else:
                self.handleMoviesRetrieve(id)
        else:
            self.handleNotFound()

    def do_PUT(self):
        self.loadSession()
        # parse the path to find the collection and identifier
        parts = self.path.split('/')[1:]
        collection = parts[0]
        if len(parts) > 1:
            id = parts[1]
        else:
            id = None

        if collection == "movies":
            if id == None:
                #self.handleMoviesList()
                self.handleNotFound()
            else:
                self.handleMoviesUpdate(id)
        else:
            self.handleNotFound()

    def do_POST(self):
        self.loadSession()
        if self.path == "/movies":
            self.handleMoviesCreate()
        elif self.path == "/users":
            self.handleUsersCreate()
        elif self.path == "/sessions":
            self.handleSessionCreate()
        else:
            self.handleNotFound()

    def do_DELETE(self):
        self.loadSession()
        # parse the path to find the collection and identifier
        parts = self.path.split('/')[1:]
        collection = parts[0]
        if len(parts) > 1:
            id = parts[1]
        else:
            id = None

        if collection == "movies":
            if id == None:
                self.handleNotFound()
            else:
                self.handleMoviesDelete(id)
        else:
            self.handleNotFound()

def run():

    db = MoviesDB()
    db.createMoviesUsersTable()
    db = None #disconnect

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = HTTPServer(listen, MyRequestHandler)

    print("Server listening on", "{}:{}".format(*listen))
    server.serve_forever()

run()
