import psycopg2
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import urllib.parse
import json
import string
import random
import boto3
import requests as req
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug import secure_filename

# Connect the router to the SQL database IDed in the HEROKU variables
urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
conn = psycopg2.connect(database=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port)
cur = conn.cursor()

app = Flask(__name__)

# Function used to generate password hash with the werkzeug.security package
def hashed_password(password):
        return generate_password_hash(password)

def id_generator(size=20, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.route("/")
def index():
    return render_template('index.html', curid = 0)

@app.route("/login")
def mainLogin():
    return render_template('login.html', curid = 0)

@app.route("/screatefrontend")
def mainSCreate():
    return render_template('screate.html', curid = 0)

@app.route("/screate")
def newStudent():
    email = request.args['email']
    email = email.replace('%40', "@")
    password = request.args['hp']
    cur.execute("""SELECT * from students where email = %s;""",(email,))
    lst = cur.fetchall()
    if len(lst) == 0:
        print("""NOW ADDING NEW STUDENT""")
        hashpassword = hashed_password(password)
        print("CREATED PASSWORD HASH")
        cur.execute("""INSERT INTO students (sid, email, hashpswd) VALUES ((SELECT floor(random()*(100000-223+1))+10), %s, %s);""", (email, hashpassword))
        conn.commit()
        print("INSERTED NEW STUDENT")
        cur.execute("""SELECT sid from students where email = %s;"""(email,))
        sidlst = cur.fetchall()
        sid = sidlst[0][0]
        return redirect("http://www.rttportal.com/dashboard/"+str(sid))
    return "User already exists! Log In instead!"

@app.route("/slogin")
def loginStudent():
    email = request.args['email']
    email = email.replace('%40', "@")
    password = request.args['hp']
    cur.execute("""SELECT * from students where email = %s;""", (email,))
    lst = cur.fetchall()
    if len(lst) == 0:
        return "Please create a student account first"
    cur.execute("""SELECT hashpswd from students where email = %s;""", (email,))
    lst = cur.fetchall()
    if check_password_hash(lst[0][0], password):
        cur.execute("""SELECT sid from students where email = %s;""", (email,))
        lst = cur.fetchall()
        cur.execute("""SELECT * FROM character where cid = (SELECT cid FROM student_character WHERE sid = %s);""", (lst[0][0],))
        charlst = cur.fetchall()
        #return render_template('dashboard.html', sid = lst[0][0], curid = 1, username="John", description = charlst[0][2])
        return redirect("http://www.rttportal.com/dashboard/"+str(lst[0][0]))
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
    cur.execute("""INSERT INTO professor (pid, email, hashpswd) VALUES ((SELECT floor(random()*(20003-434+1))+10), %s, %s);""",(email,hashpassword))
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
    cur.execute("""SELECT * from professor where email = %s;""", (email,))
    lst = cur.fetchall()
    if len(lst) == 0:
        return "Professor does not exist. Register first."
    cur.execute("""SELECT * from game where title = %s;""", (gameName,))
    lst = cur.fetchall()
    if len(lst) != 0:
        return "A Game with this name already exists"
    cur.execute("""INSERT INTO game (title) VALUES (%s);""",(gameName,))
    cur.execute("""INSERT INTO professor_game (pid, gid) VALUES ((SELECT pid from professor where email = %s), (SELECT gid from game where title = %s));""", (email, gameName))
    conn.commit()
    return "Professor has created game"

@app.route("/dashboard/<sid>")
def getCustomDashboard(sid):
    cur.execute("""SELECT * FROM character where cid = (SELECT cid FROM student_character WHERE sid = %s);""", (sid,))
    charlst = cur.fetchall()
    # return render_template('dashboard.html', sid = sid, curid = 1, username="John", description = charlst[0][2])
    return render_template('dashboard.html', sid = sid, curid = 1, username="John")

@app.route("/newspaper/<sid>")
def getCustomNewspaper(sid):
    return render_template('newspaper.html', sid = sid, curid = 2, username="John")

# @app.route("/characterprofile/<sid>")
#
# @app.route("/chat/<sid>")

### UPLOADS!!!
@app.route("/account/")
def account():
    return render_template('account.html')

@app.route("/myaccount/")
def myaccount():
    return render_template("myaccount.html")

@app.route('/sign_s3/')
def sign_s3():
  S3_BUCKET = os.environ.get('S3_BUCKET')
  file_name1 = request.args.get('file_name')
  ext = file_name1.split(".")[1]
  file_name = id_generator()
  file_name+=ext
  file_type = request.args.get('file_type')
  print(file_name)
  print(file_type)
  s3 = boto3.client('s3')
  if file_type == "application/pdf":
      presigned_post = s3.generate_presigned_post(
          Bucket = S3_BUCKET,
          Key = file_name,
          Fields = {"acl": "public-read", "Content-Type": file_type},
          Conditions = [
                 {"acl": "public-read"},
                 {"Content-Type": file_type}
           ],
           ExpiresIn = 3600
           )
      return json.dumps({'data': presigned_post, 'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)})
  return "Wrong!"

@app.route("/submit_form/", methods = ["POST"])
def submit_form():
    avatar_url = request.form["file-url"]
    print(avatar_url)
    
    return str(avatar_url)
