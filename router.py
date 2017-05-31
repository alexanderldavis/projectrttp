import psycopg2
from flask import Flask, render_template, request
import os
import urllib.parse
import json
import requests as req
import bcrypt

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

# PASSWORD AUTHENTICATION
def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    # Check hased password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)

@app.route("/plogin")
def loginProfessor():
    email = request.args['email']
    password = request.args['hash']
    hashpassword = get_hashed_password(password)
    cur.execute("""SELECT hashpswd from professor where email = %s;""", (email,))
    lst = cur.fetchall()
    if lst[0][0] == hashpassword:
        cur.execute("""SELECT * from professor where email = %s;""", (email,))
        lst = cur.fetchall()
        return str(lst)
    return "Professor account not created. Please create an account first."


@app.route("/pcreate")
def createProfessor():
    email = request.args['email']
    password = request.args['hash']
    gameName = request.args['gameName']
    hashpassword = get_hashed_password(password)

    cur.execute("""SELECT * from professor where email = %s;""", (email,))
    if len(lst) == 0:
        return "Professor Account already exists! Please login to your account."

    cur.execute("""INSERT INTO professor (email, hashpswd) VALUES (%s, %s);""",(email,hashpassword))
    conn.commit()
    cur.execute("""INSERT INTO game (title) VALUES (%s);""", (gameName,))
    conn.commit()
    cur.execute("""INSERT INTO professor_game (pid, gid) VALUES (SELECT pid from professor where email = %s, SELECT gid from game where title = %s);""", (email, gameName))
    conn.commit()
    return "Professor Account Created!"
