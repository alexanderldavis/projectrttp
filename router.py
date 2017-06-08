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
char_name = ""

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
    name = request.args['name']
    email = request.args['email']
    email = email.replace('%40', "@")
    password = request.args['hp']
    cur.execute("""SELECT * from students where email = %s;""",(email,))
    lst = cur.fetchall()
    if len(lst) == 0:
        print("""NOW ADDING NEW STUDENT""")
        hashpassword = hashed_password(password)
        print("CREATED PASSWORD HASH")
        cur.execute("""INSERT INTO students (sid, name, email, hashpswd) VALUES ((SELECT floor(random()*(100000-223+1))+10), %s, %s, %s);""", (name, email, hashpassword))
        conn.commit()
        print("INSERTED NEW STUDENT")
        cur.execute("""SELECT sid from students where email = %s;""",(email,))
        sidlst = cur.fetchall()
        sid = sidlst[0][0]
        return redirect("http://www.rttportal.com/dashboard/"+str(sid))
    return "User already exists! Log In instead!"

@app.route("/slogin")
def loginStudent():
    email = request.args['email']
    myemail = email.replace('%40', "@")
    password = request.args['hp']
    cur.execute("""SELECT * from students where email = %s;""", (myemail,))
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

@app.route("/pcreate/<name>/<email>/<password>")
def newProfessor(name, email, password):
    cur.execute("""SELECT * from professor where email = %s;""", (email,))
    lst = cur.fetchall()
    if len(lst) != 0:
        return "Professor Account already exists! Please login to your account."
    hashpassword = hashed_password(password)
    print("CREATED PASSWORD HASH")
    cur.execute("""INSERT INTO professor (pid, name, email, hashpswd) VALUES ((SELECT floor(random()*(2034343003-4343434+1))+10), %s, %s, %s);""",(name, email, hashpassword))
    print("PROFESSOR ACCOUNT CREATED")
    conn.commit()
    return "Professor account created!"

@app.route("/sjoin/<sid>")
def gameJoinStudent(sid):
    inviteCode = request.args['inviteCode']
    if "-" not in inviteCode:
        return "InviteCode invalid"
    characterID = inviteCode.split("-")[1]
    gameName = inviteCode.split("-")[0]
    cur.execute("""SELECT * from students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    if len(lst) == 0:
        return "You must create a student account first!"
    cur.execute("""SELECT gid from game where title = %s;""", (gameName,))
    lst = cur.fetchall()
    if len(lst) == 0:
        return "Game not yet created or InviteCode invalid"
    gid = lst[0][0]
    cur.execute("""SELECT * from students_game where sid = %s and gid = %s;""", (sid, gid))
    lst = cur.fetchall()
    if len(lst) != 0:
        return "student already in game"
    cur.execute("""INSERT INTO students_game (sid, gid) VALUES (%s, %s);""", (sid, gid))
    conn.commit()
    print("STUDENT JOINED GAME")
    cur.execute("""SELECT * from character where cid = %s;""", (characterID,))
    lst = cur.fetchall()
    if len(lst) == 0:
        return "Charcter not yet created or InviteCode invalid"
    cur.execute("""INSERT INTO student_character (sid, cid) VALUES (%s, %s);""", (sid, characterID))
    conn.commit()
    print("STUDENT LINKED TO CHARACTER")
    return redirect("http://www.rttportal.com/dashboard/"+str(sid))

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
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    mylst = cur.fetchall()
    if len(mylst) == 0:
        return "Create account or log in"
    # return render_template('dashboard.html', sid = sid, curid = 1, username="John", description = charlst[0][2])
    cur.execute("""SELECT gid from students_game where sid = %s;""",(sid,))
    gamelst = cur.fetchall()
    cur.execute("""SELECT * from student_character where sid = %s;""", (sid,))
    mlst = cur.fetchall()
    cleanGamelst = []
    if len(mlst) != 0:
        for (gid,) in gamelst:
            print(gid)
            cur.execute("""SELECT title from game where gid = %s;""", (gid,))
            gametitle = cur.fetchall()
            gametitle = gametitle[0][0]
            cur.execute("""SELECT name from character where cid = (SELECT cid from student_character where sid = %s);""", (sid,))
            charname = cur.fetchall()
            charname = charname[0][0]
            cleanGamelst.append((charname, gametitle))
    print("###########ENDGAME###########")
    return render_template('dashboard.html', sid = sid, curid = 1, username=mylst[0][0], gameinfo = cleanGamelst)

@app.route("/newspaper/<sid>")
def getCustomNewspaper(sid):
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    if len(lst) == 0:
        return "Create account or log in"
    return render_template('newspaper.html', sid = sid, curid = 2, username=lst[0][0])

@app.route("/characterprofile/<sid>")
def getCustomCharacterProfile(sid):
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    if len(lst) == 0:
        return "Create account or log in"
    cur.execute("""SELECT * FROM character where cid = (SELECT cid FROM student_character WHERE sid = %s);""", (sid,))
    charlst = cur.fetchall()
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    namelst = cur.fetchall()
    return render_template('characterprofile.html', sid = sid, curid = 3, username=namelst[0][0])

@app.route("/chat/<sid>")
def getCustomChat(sid):
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    if len(lst) == 0:
        return "Create account or log in"
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    namelst = cur.fetchall()
    return render_template('chat.html', sid=sid, curid = 5, username= namelst[0][0])

@app.route("/account/<sid>")
def getCustomAccount(sid):
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    if len(lst) == 0:
        return "Create account or log in"
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    namelst = cur.fetchall()
    return render_template('account.html', sid=sid, curid = 6, username = namelst[0][0])

@app.route("/accountUpdate/<sid>")
def accountUpdate(sid):
    name = request.args['name']
    password = request.args['password']
    if name != "":
        name.replace("+", " ")
        name = name.title()
        cur.execute("""UPDATE students SET name = %s WHERE sid = %s;""", (name, sid))
        conn.commit()
    if password != "":
        hashpassword = hashed_password(password)
        cur.execute("""UPDATE students SET hashpswd = %s WHERE sid = %s;""", (hashpassword, sid))
        conn.commit()
    return redirect("http://www.rttportal.com/dashboard/"+str(sid))





### UPLOADS!!!


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


##### ADMIN #####
@app.route("/admin")
def adminLogin():
    return render_template("adminlogin.html")

@app.route("/plogin")
def loginProfessor():
    email = request.args['email']
    password = request.args['password']
    cur.execute("""SELECT hashpswd from professor where email = %s;""", (email,))
    lst = cur.fetchall()
    # Check password to hashed pass in table
    if len(lst) == 0:
        return "Professor account not created. Please create an account first."
    if check_password_hash(lst[0][0], password):
        cur.execute("""SELECT pid from professor where email = %s;""", (email,))
        mylst = cur.fetchall()
        pid = mylst[0][0]
        return redirect("http://www.rttportal.com/admin/dashboard/"+str(pid))
    if not check_password_hash(lst[0][0], password):
        return "Password is wrong. Shame on you."
    return "Some error -- Contact Webmaster"


@app.route("/admin/dashboard/<pid>")
def admindash(pid):
    cur.execute("""SELECT name from professor where pid = %s;""", (pid,))
    name = cur.fetchall()
    name = name[0][0]
    cur.execute("""SELECT gid from professor_game where pid = %s;""",(pid,))
    gids = cur.fetchall()
    cleangidlist = []
    for gid in gids:
        cleangidlist.append(gid[0])
    cleangamelst = []
    for gid in cleangidlist:
        cur.execute("""SELECT gid, title from game where gid = %s;""", (gid,))
        title = cur.fetchall()
        cleangamelst.append((title[0][0], title[0][1]))
    return render_template("adminindex.html", pid = pid, username = name, titlelist = cleangamelst)
