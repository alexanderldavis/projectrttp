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
