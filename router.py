import psycopg2
from flask import Flask, render_template, request
import os
import urllib.parse
import json
import requests as req
from werkzeug.security import generate_password_hash, check_password_hash

# Connect the router to the SQL database IDed in the HEROKU variables
urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
conn = psycopg2.connect(database=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port)
cur = conn.cursor()

app = Flask(__name__)

# Function used to generate password hash with the werkzeug.security package
def hashed_password(password):
        return generate_password_hash(password)

@app.route("/")
def index():
    return render_template('index.html')

# DEPRECATED (MOVED TO /slogin)
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

@app.route("/screate/<email>/<password>")
def newStudent(email, password):
    cur.execute("""SELECT * from students where email = %s;""",(email,))
    lst = cur.fetchall()
    if len(lst) == 0:
        print("""NOW ADDING NEW STUDENT""")
        hashpassword = hashed_password(password)
        print("CREATED PASSWORD HASH")
        cur.execute("""INSERT INTO students (email, password) VALUES (%s, %s);""", (email, haspassword))
        conn.commit()
        print("INSERTED NEW STUDENT")
        return "Student Inserted"
    return "Student Exists Already"

@app.route("/slogin/<email>/<password>")
def loginStudent(email, password):
    cur.execute("""SELECT * from students where email = %s;""", (email,))
    lst = cur.fetchall()
    if len(lst) == 0:
        return "Please create a student account first"
    cur.execute("""SELECT hashpassword from students where email = %s;""", (email,))
    lst = cur.fetchall()
    if check_password_hash(lst[0][0], password):
        cur.execute("""SELECT * from student where email = %s;""", (email,))
        lst = cur.fetchall()
        return "Logged in "+str(lst)
    if not check_password_hash(lst[0][0], password):
        return "Password is wrong. Shame on you."
    return "Student account does not exist yet"

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
    if len(lst) == 0:
        return "Professor account not created. Please create an account first."
    if check_password_hash(lst[0][0], password):
        cur.execute("""SELECT * from professor where email = %s;""", (email,))
        lst = cur.fetchall()
        return "Logged in "+str(lst)
    if not check_password_hash(lst[0][0], password):
        return "Password is wrong. Shame on you."
    return "Some error -- Contact Webmaster"

@app.route("/sjoin/<email>/<inviteCode>")
def gameJoinStudent(email, inviteCode):
    if "-" not in inviteCode:
        return "InviteCode invalid"
    characterID = inviteCode.split("-")[0]
    gameName = inviteCode.split("-")[0]
    cur.execute("""SELECT sid from students where email = %s;""")
    lst = cur.fetchall()
    if len(lst) == 0:
        return "You must create a student account first!"
    sid = lst[0][0]
    cur.execute("""SELECT gid from game where title = %s;""", (gameName,))
    lst = cur.fetchall()
    if len(lst) == 0:
        return "Game not yet created"
    gid = lst[0][0]
    cur.execute("""INSERT INTO students_game (sid, gid) VALUES (%s, %s);""", (sid, gid))
    conn.commit()
    print("STUDENT JOINED GAME")
    return "Student " + sid + " joined game " + gid

@app.route("/pjoin/<email>/<gameName>")
def gameJoinProfessor(email, gameName):
    cur.excute("""SELECT * from game where title = %s;""", (gameName,))
    lst = cur.fetchall()
    if len(lst) != 0:
        return "A Game with this name already exists"
    cur.execute("""INSERT INTO game (title) VALUES (%s);""",(gameName,))
    cur.execute("""INSERT INTO professor_game (pid, gid) VALUES ((SELECT pid from professor where email = %s), (SELECT gid from game where title = %s));""", (email, gameName))
    conn.commit()
    return "Professor has created game"

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
