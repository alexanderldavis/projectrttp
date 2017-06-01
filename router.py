import psycopg2
from flask import Flask, render_template, request
import os
import urllib.parse
import json
import requests as req
from werkzeug.security import generate_password_hash, check_password_hash

urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
conn = psycopg2.connect(database=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port)
cur = conn.cursor()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login")
def createUser():
    email = request.args['email']
    charid = request.args['charid']
    name = request.args['name']
    gid = charid.split("-")[0]
    characterid = charid.split("-")[1]
    cur.execute("""SELECT * from students where email = %s;""",(email,))
    lst = cur.fetchall()
    if len(lst) == 0:
        print("LINKING NEW STUDENT EMAIL TO CHARACTER")
        # the email address is not already taken
        cur.execute("""INSERT INTO students (email, name, charid, gid, characterid) VALUES (%s, %s, %s, %s, %s);""",(email, name, charid, gid, characterid))
        conn.commit()
        print("INSERTED NEW USER")
    print("USER EMAIL ACQUIRED")
    print("SIGNING INTO USER LOGIN")
    cur.execute("""SELECT characterid, name from students where email = %s;""", (email,))
    lst = cur.fetchall()
    print(lst)
    print("SIGNED IN, NOW LOADING PAGE")
    return render_template('main.html', uid = lst)

def hashed_password(password):
        return generate_password_hash(password)

@app.route("/pcreate/<email>/<password>")
def newProfessor(email, password):
    cur.execute("""SELECT * from professor where email = %s;""", (email,))
    lst = cur.fetchall()
    if len(lst) != 0:
        return "Professor Account already exists! Please login to your account."
    hashpassword = hashed_password(password)
    print("CREATED PASSWORD HASH")
    cur.execute("""INSERT INTO professor (email, hashpswd) VALUES (%s, %s);""",(email,hashpassword))
    print("PROFESSOR ACCOUNT CREATED")
    conn.commit()
    return "Professor account created!"

@app.route("/plogin/<email>/<password>")
def loginProfessor(email, password):
    cur.execute("""SELECT hashpswd from professor where email = %s;""", (email,))
    lst = cur.fetchall()
    # Check password to hashed pass in table
    if check_password_hash(lst[0][0], password):
        cur.execute("""SELECT * from professor where email = %s;""", (email,))
        lst = cur.fetchall()
        return str(lst)
    if not check_password_hash(lst[0][0], password):
        return "Password is wrong. Shame on you."
    return "Professor account not created. Please create an account first."


# @app.route("/pcreate/<email>/<password>/<gameName>")
# def createProfessor(email, password, gameName):
#     hashpassword = hashed_password(password)
#     print("CREATED PASSWORD HASH")
#
#     # ALREADY EXISTS CHECK
#     cur.execute("""SELECT * from game where title = %s;""", (gameName,))
#     lst = cur.fetchall()
#     if len(lst) != 0:
#         return "Game name is taken"
#     cur.execute("""SELECT * from professor where email = %s;""", (email,))
#     lst = cur.fetchall()
#     if len(lst) != 0:
#         return "Professor Account already exists! Please login to your account."
#
#     # INSERT STATEMENTS
#     cur.execute("""INSERT INTO professor (email, hashpswd) VALUES (%s, %s);""",(email,hashpassword))
#     print("PROFESSOR ACCOUNT CREATED")
#     cur.execute("""INSERT INTO game (title) VALUES (%s);""", (gameName,))
#     print("CREATED GAME ENTRY")
#     cur.execute("""INSERT INTO professor_game (pid, gid) VALUES ((SELECT pid from professor where email = %s), (SELECT gid from game where title = %s));""", (email, gameName))
#     print("PROFESSOR_GAME RELATION CREATED")
#     conn.commit()
#     return "Professor Account Created!"
