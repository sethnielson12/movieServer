This is the server for the makeshiftIMDB website project. Fully REST-ful, can handle all data changes necessary to manage the movies data, and is also able to create users.

Name of resource: **Movie**

- Attributes:
  - title
  - producer
  - length
  - rating
  - genre

Name of resource: **User**

- Attributes:
  - first name
  - last name
  - email
  - password stored as a hash

### SCHEMA:

```
 CREATE TABLE movies (
   ...> id INTEGER PRIMARY KEY,
   ...> title TEXT,
   ...> producer TEXT,
   ...> length INTEGER,
   ...> rating INTEGER,
   ...> genre TEXT);
```

```
CREATE TABLE users (
   ...> id INTEGER PRIMARY KEY,
   ...> fname TEXT,
   ...> lname TEXT,
   ...> email TEXT,
   ...> hash TEXT);
```

### RESTFUL:

- List:
  - Method: GET
  - Path: "http://localhost:8080/movies"
- Retrieve:
  - Method: GET
  - Path: `http://localhost:8080/movies/${id}`
- Replace:
  - Method: PUT
  - Path: `http://localhost:8080/movies/${id}`
- Delete:
  - Method: DELETE
  - Path: `http://localhost:8080/movies/${id}`
- Create:
  - Method POST
  - Path: "http://localhost:8080/movies"
  - Path: "http://localhost:8080/users"
  - Path: "http://localhost:8080/sessions"

Using **from passlib.hash import bcrypt** to have passwords and they are stored in the DB.
