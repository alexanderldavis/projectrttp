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

#urllib.parse.uses_netloc.append("postgres")
#url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
#conn = psycopg2.connect(database=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port)

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
    name = "Firsty Lasty"
    email = "oodle@poodle.com"
    password = "secure password"
    return redirect("/games/"+"fakeSID")

@app.route("/slogin")
def loginStudent():
    name = "Firsty Lasty"
    email = "oodle@poodle.com"
    password = "secure password"
    return redirect("/games/"+"somethin")


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


@app.route("/sjoin/<sid>")
def gameJoinStudent(sid):
    return redirect("/games/"+"fakeSID")

@app.route("/games/<sid>/<gid>")
def getCustomGameChooser(sid,gid):
    return render_template('gamechooser.html', sid = "sid", curid = 1, username='username',
    picurl = "http://mediadirectory.economist.com/wp-content/uploads/2015/09/John-Prideaux-headshot_picmonkeyed.jpg", gameinfo = [('Jacques Guy','France 1823', 'asdf'),('Dag Fishinboi','Minnesota 1993', 'asdf'),('Dumbo','Conflicted Little Guys: Disney through the ages', 'asdf')])

@app.route("/dashboard/<sid>/<gid>")
def getCustomDashboard(sid, gid):
    return render_template('dashboard.html', sid = "sid", curid = 1, username='username', charname='charname',
    picurl = "http://mediadirectory.economist.com/wp-content/uploads/2015/09/John-Prideaux-headshot_picmonkeyed.jpg", gametitle="Dogman in the city: a tragedy 1874")

@app.route("/newspaper/<sid>/<gid>")
def getCustomNewspaper(sid, gid):
    return render_template('newspaper.html', sid=sid, gid=gid, curid=2, username='username')

@app.route("/characterprofile/<sid>")
def getCustomCharacterProfile(sid):
    return render_template('characterprofile.html', sid = 'sid', curid = 3, username='username')
# @app.route("/chat/<sid>")

@app.route("/chat/<sid>")
def getCustomChat(sid):
    return render_template('chat.html', sid=sid, curid = 5, username= 'username')

@app.route("/assignments/<sid>/<gid>")
def getCustomAssignments(sid, gid):
    return render_template('assignments.html', gid = "gid", sid = "sid", curid = 6, username= "username",
    picurl = "http://mediadirectory.economist.com/wp-content/uploads/2015/09/John-Prideaux-headshot_picmonkeyed.jpg",
    assignments = [["123456", "Fish brochure", "Using your skills her der der der der der", "12/5/67"],
    ["123456", "Crusty writeup", "Express very cool knowledge her der der der der der", "5/35/56"],
    ["123456", "Dog brochure", "Using your dog friends her der der der der der", "4/23/65"],
    ["123456", "Apple poster", "Taste numerous large apples, just fo fun her der der der der der", "12/7/67"]])

@app.route("/upload/<sid>/<gid>/<aid>/<securecode>")
def uploadAssignment(sid, gid, aid, securecode):
    return render_template("myaccount.html", gid = gid, sid = sid, curid = 6, username="username", charname="charname", picurl="http://mediadirectory.economist.com/wp-content/uploads/2015/09/John-Prideaux-headshot_picmonkeyed.jpg", aid="1234")


@app.route("/account/<sid>")
def getCustomAccount(sid):
    return render_template('account.html', sid=sid, curid = 6, username = "username")

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
    conn.commit()
    # Check password to hashed pass in table
    if len(lst) == 0:
        return "Professor account not created. Please create an account first."
    if check_password_hash(lst[0][0], password):
        cur.execute("""SELECT pid from professor where email = %s;""", (email,))
        mylst = cur.fetchall()
        conn.commit()
        pid = mylst[0][0]
        return redirect("/admin/dashboard/"+str(pid))
    if not check_password_hash(lst[0][0], password):
        return "Password is wrong. Shame on you."
    return "Some error -- Contact Webmaster"


@app.route("/admin/dashboard/<pid>")
def admindash(pid):
    cur.execute("""SELECT name from professor where pid = %s;""", (pid,))
    name = cur.fetchall()
    conn.commit()
    name = name[0][0]
    cur.execute("""SELECT gid from professor_game where pid = %s;""",(pid,))
    gids = cur.fetchall()
    conn.commit()
    cleangidlist = []
    for gid in gids:
        cleangidlist.append(gid[0])
    cleangamelst = []
    for gid in cleangidlist:
        cur.execute("""SELECT gid, title from game where gid = %s;""", (gid,))
        title = cur.fetchall()
        conn.commit()
        cleangamelst.append((title[0][0], title[0][1]))
    cur.execute("""SELECT count(students.sid) from students JOIN students_game ON (students.sid = students_game.sid) JOIN game ON (game.gid = students_game.gid) JOIN professor_game on (game.gid = professor_game.gid) where pid = %s;""", (pid,))
    studentcount = cur.fetchall()
    conn.commit()
    studentcount = studentcount[0][0]
    return render_template("adminindex.html", pid = pid, username = name, titlelist = cleangamelst, studentcount=studentcount)

@app.route("/admin/addGame/<pid>")
def adminaddgame(pid):
    cur.execute("""SELECT email from professor where pid = %s;""", (pid,))
    email = cur.fetchall()
    conn.commit()
    email = email[0][0]
    return render_template("adminaddgame.html", pid = pid, email = email)

@app.route("/admin/students/<pid>")
def adminstudents(pid):
    cur.execute("""SELECT gid from professor_game where pid = %s;""", (pid,))
    gidlst = cur.fetchall()
    conn.commit()
    cleangidlst = []
    for gid in gidlst:
        cleangidlst.append(gid[0])
    cleanstudentgidlist = []
    for gid in cleangidlst:
        cur.execute("""SELECT students.sid, students.name, students.email, character.name from students JOIN students_game on (students.sid = students_game.sid) JOIN student_character ON (students.sid = student_character.sid) JOIN character ON (character.cid = student_character.cid) where gid = %s;""",(gid,))
        studentlist = cur.fetchall()
        conn.commit()
        cur.execute("""SELECT title from game where gid = %s;""", (gid,))
        title = cur.fetchall()
        conn.commit()
        title = title[0][0]
        cleanstudentgidlist.append((gid, title, studentlist))
    print(cleanstudentgidlist)
    return render_template("adminstudents.html", pid= pid, cleanstudentgidlist = cleanstudentgidlist)

@app.route("/pjoin/<pid>")
def gameJoinProfessor(pid):
    gameName = request.args['gameName']
    cur.execute("""SELECT * from professor where pid = %s;""", (pid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Professor does not exist. Register first."
    cur.execute("""SELECT * from game where title = %s;""", (gameName,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) != 0:
        return "A Game with this name already exists"
    cur.execute("""INSERT INTO game (title) VALUES (%s);""",(gameName,))
    conn.commit()
    cur.execute("""INSERT INTO professor_game (pid, gid) VALUES (%s, (SELECT gid from game where title = %s));""", (pid, gameName))
    conn.commit()
    print("PROFESSOR GAME CREATED AND LINKED TO PID")
    return redirect("/admin/dashboard/"+str(pid))

@app.route("/admin/game/<pid>/<gid>")
def gameadminassignments(pid, gid):
    return render_template("admingameassignment.html", pid = "pid", gid = "gid", assignments = ["assignment1", "assignment2"])

@app.route("/admin/getinvitecodes/<pid>/<gid>")
def getInviteCodes(pid, gid):
    cur.execute("""SELECT * from professor where pid = %s;""", (pid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Professor does not exist. Register first."
    cur.execute("""SELECT game.title, gametype.title from game JOIN gametype ON (game.gtid = gametype.gtid) where game.gid = %s;""",(gid,))
    titles = cur.fetchall()
    title = titles[0][0]
    gtname = titles[0][1]
    cur.execute("""SELECT cid, name, descriptionURL, imageURL FROM character where gtid = (SELECT gtid from game where gid = %s);""", (gid,))
    cinfos = cur.fetchall()
    conn.commit()
    cleanfinalcinfolst = []
    for (cid, name, des, image) in cinfos:
        cleanfinalcinfolst.append(((str(title)+"-"+str(cid)), cid, name, des, image))
    return render_template("admininvitecodes.html", cinfo = cleanfinalcinfolst, title = title, pid = pid, gtname = gtname)

@app.route("/admin/deleteGame/<pid>/<gid>/<securecode>")
def deleteGame(pid, gid, securecode):
    cur.execute("""SELECT * from professor where pid = %s;""", (pid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Professor does not exist. Register first."
    if int(securecode) != 848374949384743937:
        return "deleteGame authorization failed"
    cur.execute("""DELETE from game_assignments where gid = %s; DELETE from professor_game where gid = %s; DELETE from students_chargame where gid = %s;  DELETE from game where gid = %s;""", (gid, gid, gid, gid))
    conn.commit()
    print("GAME "+str(gid)+" DELETED BY PROFESSOR ("+str(pid)+")")
    return redirect("/admin/students/"+str(pid))

@app.route("/paddassignment/<pid>/<gid>")
def addassignmentadmin(pid, gid):
    title = request.args['assignmentName']
    description = request.args['title']
    duedate = request.args['due']
    cur.execute("""INSERT into assignments (aid, title, description, due) values ((SELECT floor(random()*(2034343003-43434+1))+10), %s, %s, %s) RETURNING aid;""",(title,description,duedate))
    conn.commit()
    print("ADDED ASSIGNMENT TO RELATION ASSIGNMENTS")
    aid = cur.fetchall()
    aid = aid[0][0]
    cur.execute("""INSERT into game_assignments (gid, aid) values (%s, %s);""",(gid,aid))
    conn.commit()
    print("ADDED ASSIGNMENT TO RELATION GAME_ASSIGNMENTS")
    return redirect("/admin/game/"+pid+"/"+gid)

#Add submissions:
#insert into submissions (subid, link, uploadTime) values (112234, 'link', '2004-10-19 10:23:54');
#insert into student_submissions (sid, subid) values (27644, 112234);
#insert into assignments_submissions (aid, subid) values (1134343, 112234);

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.errorhandler(500)
def page_not_found(e):
    return render_template('404.html')

app.run(debug=True)
