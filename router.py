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
import datetime

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
    conn.commit()
    if len(lst) == 0:
        print("""NOW ADDING NEW STUDENT""")
        hashpassword = hashed_password(password)
        print("CREATED PASSWORD HASH")
        cur.execute("""INSERT INTO students (sid, name, email, hashpswd) VALUES ((SELECT floor(random()*(100000-223+1))+10), %s, %s, %s);""", (name, email, hashpassword))
        conn.commit()
        print("INSERTED NEW STUDENT")
        cur.execute("""SELECT sid from students where email = %s;""",(email,))
        sidlst = cur.fetchall()
        conn.commit()
        sid = sidlst[0][0]
        return redirect("http://www.rttportal.com/games/"+str(sid))
    return "User already exists! Log In instead!"

@app.route("/slogin")
def loginStudent():
    email = request.args['email']
    myemail = email.replace('%40', "@")
    password = request.args['hp']
    cur.execute("""SELECT * from students where email = %s;""", (myemail,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Please create a student account first"
    cur.execute("""SELECT hashpswd from students where email = %s;""", (email,))
    lst = cur.fetchall()
    conn.commit()
    if check_password_hash(lst[0][0], password):
        cur.execute("""SELECT sid from students where email = %s;""", (email,))
        lst = cur.fetchall()
        conn.commit()
        return redirect("http://www.rttportal.com/games/"+str(lst[0][0]))
    if not check_password_hash(lst[0][0], password):
        return "Password is wrong. Shame on you."
    return "Student account does not exist yet"

@app.route("/pcreate/<name>/<email>/<password>")
def newProfessor(name, email, password):
    name = name.replace("+", " ")
    cur.execute("""SELECT * from professor where email = %s;""", (email,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) != 0:
        return "Professor Account already exists! Please login to your account."
    hashpassword = hashed_password(password)
    print("CREATED PASSWORD HASH")
    cur.execute("""INSERT INTO professor (pid, name, email, hashpswd) VALUES ((SELECT floor(random()*(2034343003-43434+1))+10), %s, %s, %s);""",(name, email, hashpassword))
    conn.commit()
    print("PROFESSOR ACCOUNT CREATED")
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
    conn.commit()
    if len(lst) == 0:
        return "You must create a student account first!"
    cur.execute("""SELECT gid from game where title = %s;""", (gameName,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Game not yet created or InviteCode invalid"
    gid = lst[0][0]
    cur.execute("""SELECT * from students_chargame where sid = %s and gid = %s;""", (sid, gid))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) != 0:
        return "student already in game"
    cur.execute("""SELECT * from students_chargame where cid = %s and gid = %s;""", (characterID, gid))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) != 0:
        return "character already in game"
    cur.execute("""SELECT * from character where cid = %s;""", (characterID,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Character not yet created or InviteCode invalid"
    cur.execute("""INSERT INTO students_chargame (sid, cid, gid) VALUES (%s, %s, %s);""", (sid, characterID, gid))
    conn.commit()
    print("STUDENT JOINED GAME")
    cur.execute("""INSERT INTO student_character (sid, cid) VALUES (%s, %s);""", (sid, characterID))
    conn.commit()
    print("STUDENT LINKED TO CHARACTER")
    return redirect("http://www.rttportal.com/games/"+str(sid))

@app.route("/games/<sid>")
def getCustomGameChooser(sid):
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    mylst = cur.fetchall()
    conn.commit()
    if len(mylst) == 0:
        return "Create account or log in"
    # return render_template('dashboard.html', sid = sid, curid = 1, username="John", description = charlst[0][2])
    cur.execute("""SELECT gid from students_chargame where sid = %s;""",(sid,))
    gamelst = cur.fetchall()
    conn.commit()
    cur.execute("""SELECT * from student_character where sid = %s;""", (sid,))
    mlst = cur.fetchall()
    conn.commit()
    cleanGamelst = []
    if len(mlst) != 0:
        for (gid,) in gamelst:
            cur.execute("""SELECT title from game where gid = %s;""", (gid,))
            gametitle = cur.fetchall()
            conn.commit()
            gametitle = gametitle[0][0]
            cur.execute("""SELECT name from character where cid = (SELECT cid from students_chargame where sid = %s and gid = %s);""", (sid,gid))
            charname = cur.fetchall()
            conn.commit()
            charname = charname[0][0]
            cleanGamelst.append((charname, gametitle, gid))
    return render_template('gamechooser.html', sid = sid, curid = 0, gamechooser = 0, username=mylst[0][0], gameinfo = cleanGamelst, picurl = "https://cdn.pixabay.com/photo/2016/10/18/18/19/question-mark-1750942_960_720.png")

@app.route("/dashboard/<sid>/<gid>")
def getCustomDashboard(sid, gid):
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Create account or log in"
    name = lst[0][0]
    cur.execute("""SELECT character.imageurl, character.name from character JOIN students_chargame ON (character.cid = students_chargame.cid) where students_chargame.gid = %s and students_chargame.sid = %s;""", (gid, sid))
    charinfo = cur.fetchall()
    picurl = picurls[0][0]
    charname = picurls[0][1]
    print('So far so good', file=sys.stderr)
    cur.execute("""SELECT title from game where gid = %s;""", (gid,))
    print('Post-execution', file=sys.stderr)
    gametitle = cur.fetchall()
    print('Fetched', file=sys.stderr)
    conn.commit()
    print('Committed', file=sys.stderr)
    gametitle = gametitle[0][0]
    print('Gametitle secured', file=sys.stderr)
    return render_template('dashboard.html', gid = gid, sid = sid, curid = 1, username=name, gametitle=gametitle, picurl = picurl, charname = charname)

@app.route("/newspaper/<sid>/<gid>")
def getCustomNewspaper(sid, gid):
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Create account or log in"
    cur.execute("""SELECT character.imageurl, character.name from character JOIN students_chargame ON (character.cid = students_chargame.cid) where students_chargame.gid = %s and students_chargame.sid = %s;""", (gid, sid))
    picurls = cur.fetchall()
    picurl = picurls[0][0]
    charname = picurls[0][1]
    return render_template('newspaper.html', gid = gid, sid = sid, curid = 2, username=lst[0][0], picurl = picurl)

@app.route("/characterprofile/<sid>/<gid>")
def getCustomCharacterProfile(sid, gid):
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Create account or log in"
    cur.execute("""SELECT * FROM character where cid = (SELECT cid FROM student_chargame WHERE sid = %s and gid = %s);""", (sid,gid))
    charlst = cur.fetchall()
    conn.commit()
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    namelst = cur.fetchall()
    conn.commit()
    cur.execute("""SELECT character.imageurl, character.name from character JOIN students_chargame ON (character.cid = students_chargame.cid) where students_chargame.gid = %s and students_chargame.sid = %s;""", (gid, sid))
    picurls = cur.fetchall()
    picurl = picurls[0][0]
    charname = picurls[0][1]
    return render_template('characterprofile.html', gid = gid, sid = sid, curid = 3, username=namelst[0][0], picurl = picurl)

@app.route("/chat/<sid>/<gid>")
def getCustomChat(sid, gid):
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Create account or log in"
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    namelst = cur.fetchall()
    conn.commit()
    cur.execute("""SELECT character.imageurl, character.name from character JOIN students_chargame ON (character.cid = students_chargame.cid) where students_chargame.gid = %s and students_chargame.sid = %s;""", (gid, sid))
    picurls = cur.fetchall()
    picurl = picurls[0][0]
    charname = picurls[0][1]
    return render_template('chat.html', gid = gid, sid=sid, curid = 5, username= namelst[0][0], picurl = picurl)

@app.route("/assignments/<sid>/<gid>")
def getCustomAssignments(sid, gid):
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Create account or log in"
    cur.execute("""SELECT assignments.aid, assignments.title, assignments.description, assignments.due FROM assignments JOIN game_assignments ON (assignments.aid = game_assignments.aid) WHERE gid = %s order by assignments.due ASC;""", (gid,))
    # cur.execute("""SELECT assignments.aid, assignments.title, assignments.description, assignments.due, submissions.link FROM assignments JOIN game_assignments ON (assignments.aid = game_assignments.aid) JOIN assignments_submissions ON (assignments_submissions.aid = assignments.aid) JOIN submissions ON (assignments_submissions.subid = submissions.subid) WHERE gid = %s order by assignments.due ASC;""", (gid,))
    assignments = cur.fetchall()
    cur.execute("""SELECT character.imageurl, character.name from character JOIN students_chargame ON (character.cid = students_chargame.cid) where students_chargame.gid = %s and students_chargame.sid = %s;""", (gid, sid))
    picurls = cur.fetchall()
    picurl = picurls[0][0]
    charname = picurls[0][1]
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    namelst = cur.fetchall()
    conn.commit()
    return render_template('assignments.html', gid = gid, sid = sid, curid = 6, username= namelst[0][0], picurl = picurl, assignments = assignments)

@app.route("/upload/<sid>/<gid>/<aid>/<securecode>")
def uploadAssignment(sid, gid, aid, securecode):
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Create account or log in"
    if int(securecode) != 5739475839475:
        return "uploadAssignment authorization failed"
    cur.execute("""SELECT character.imageurl, character.name from character JOIN students_chargame ON (character.cid = students_chargame.cid) where students_chargame.gid = %s and students_chargame.sid = %s;""", (gid, sid))
    picurls = cur.fetchall()
    picurl = picurls[0][0]
    charname = picurls[0][1]
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    namelst = cur.fetchall()
    conn.commit()
    return render_template("myaccount.html", gid = gid, sid = sid, curid = 6, username= namelst[0][0], picurl = picurl, aid = aid)

### UPLOADS!!!
#DEPRECATED
# @app.route("/myaccount/")
# def myaccount():
#     return render_template("myaccount.html")

@app.route('/sign_s3/')
def sign_s3():
  S3_BUCKET = os.environ.get('S3_BUCKET')
  file_name = id_generator()
  file_name+=".pdf"
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
      print(json.dumps({'data': presigned_post, 'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)}))
      return json.dumps({'data': presigned_post, 'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)})
  return "Wrong!"

@app.route("/submit_form/<gid>/<sid>/<aid>/", methods = ["POST"])
def submit_form(gid, sid, aid):
    avatar_url = str(request.form["file-url"])
    print("IN HERE =================================")
    print(avatar_url)
    addSubmissionFromStudent(avatar_url, sid, aid)
    return redirect("http://www.rttportal.com/assignments/"+sid+"/"+gid)


def addSubmissionFromStudent(url, sid, aid):
    cur.execute("""SELECT assignments_submissions.subid from student_submissions join assignments_submissions on (student_submissions.subid = assignments_submissions.subid) where student_submissions.sid = %s and assignments_submissions.aid = %s;""",(sid, aid))
    lst = cur.fetchall()
    if len(lst) == 0:
        uploaddate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""INSERT into submissions (subid, link, uploadTime) values ((SELECT floor(random()*(2034343003-43434+1))+10), %s, %s) returning subid;""",(url,uploaddate))
        conn.commit()
        subid = cur.fetchall()
        subid = subid[0][0]
        cur.execute("""INSERT into student_submissions (sid, subid) values (%s, %s);""", (sid, subid))
        conn.commit()
        cur.execute("""INSERT into assignments_submissions (aid, subid) values (%s, %s);""", (aid, subid))
        conn.commit()
        print("Added new document")
        return True
    else:
        subid = lst[0][0]
        uploaddate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""UPDATE submissions SET link = %s, uploadTime = %s WHERE subid = %s;""", (url, uploaddate, sid))
        conn.commit()
        print("Upldated submision")
        return True
    return False
    #Add submissions:
    # uploaddate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # cur.execute("""INSERT into submissions (subid, link, uploadTime) values ((SELECT floor(random()*(2034343003-43434+1))+10), %s, %s) returning subid;""",(avatar_url,uploaddate))
    # conn.commit()
    # subid = cur.fetchall()
    # subid = subid[0][0]
    # cur.execute("""INSERT into student_submissions (sid, subid) values (%s, %s);""", (sid, subid))
    # conn.commit()
    # cur.execute("""INSERT into assignments_submissions (aid, subid) values (%s, %s);""", (aid, subid))

#insert into submissions (subid, link, uploadTime) values (112234, 'link', '2004-10-19 10:23:54');
#insert into student_submissions (sid, subid) values (27644, 112234);
#insert into assignments_submissions (aid, subid) values (1134343, 112234);

@app.route("/account/<sid>/<gid>")
def getCustomAccount(sid):
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Create account or log in"
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    namelst = cur.fetchall()
    conn.commit()
    cur.execute("""SELECT character.imageurl, character.name from character JOIN students_chargame ON (character.cid = students_chargame.cid) where students_chargame.gid = %s and students_chargame.sid = %s;""", (gid, sid))
    picurls = cur.fetchall()
    picurl = picurls[0][0]
    charname = picurls[0][1]
    return render_template('account.html', gid = gid, sid=sid, curid = 6, username = namelst[0][0], picurl = picurl)

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
    return redirect("http://www.rttportal.com/games/"+str(sid))

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
        return redirect("http://www.rttportal.com/admin/dashboard/"+str(pid))
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
    cur.execute("""SELECT count(students.sid) from students JOIN students_chargame ON (students.sid = students_chargame.sid) JOIN game ON (game.gid = students_chargame.gid) JOIN professor_game on (game.gid = professor_game.gid) where pid = %s;""", (pid,))
    try:
        studentcount = cur.fetchall()
        conn.commit()
        studentcount = studentcount[0][0]
    except:
        studentcount = 0
    cur.execute("""SELECT count(assignments_submissions.aid) from submissions JOIN assignments_submissions on (submissions.subid = assignments_submissions.subid) JOIN game_assignments ON (game_assignments.aid = assignments_submissions.aid) JOIN professor_game ON (professor_game.gid = game_assignments.gid) where game_assignments.gid = %s;""", (gid,))
    try:
        assignments_submissions = cur.fetchall()
        conn.commit()
        assignments_submissions = assignments_submissions[0][0]
    except:
        assignments_submissions = 0
    return render_template("adminindex.html", pid = pid, username = name, titlelist = cleangamelst, studentcount=studentcount, assignmentcount = assignments_submissions)

@app.route("/admin/addGame/<pid>")
def adminaddgame(pid):
    cur.execute("""SELECT email from professor where pid = %s;""", (pid,))
    email = cur.fetchall()
    conn.commit()
    email = email[0][0]
    cur.execute("""SELECT gtid, title from gametype;""")
    gametypes = cur.fetchall()
    conn.commit()
    return render_template("adminaddgame.html", pid = pid, email = email, gametypes=gametypes, nums = [i for i in range(1, 26)])

@app.route("/admin/addassignment/<pid>/<gid>")
def adminaddassignment(pid, gid):
    cur.execute("""SELECT * from professor where pid = %s;""", (pid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Professor does not exist. Register first."
    cur.execute("""SELECT title from game where gid = %s;""",(gid,))
    gametitle = cur.fetchall()
    if len(gametitle) == 0:
        return "Game does not exist. Create one first."
    gametitle = gametitle[0][0]
    return render_template("adminaddassignment.html", pid = pid, gid = gid, gametitle = gametitle)

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
        cur.execute("""SELECT students.sid, students.name, students.email, character.name from students JOIN students_chargame on (students.sid = students_chargame.sid) JOIN character ON (character.cid = students_chargame.cid) where gid = %s;""",(gid,))
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
    gtid = request.args['gtid']
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
    cur.execute("""INSERT INTO game (gid, title, gtid) VALUES ((SELECT floor(random()*(2034343003-43434+1))+10), %s, %s);""",(gameName, gtid))
    conn.commit()
    cur.execute("""INSERT INTO professor_game (pid, gid) VALUES (%s, (SELECT gid from game where title = %s));""", (pid, gameName))
    conn.commit()
    print("PROFESSOR GAME CREATED AND LINKED TO PID")
    return redirect("http://www.rttportal.com/admin/dashboard/"+str(pid))

@app.route("/admin/game/<pid>/<gid>")
def gameadminassignments(pid, gid):
    cur.execute("""SELECT * from professor where pid = %s;""", (pid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Professor does not exist. Register first."
    cur.execute("""SELECT assignments.aid, assignments.title, assignments.due from assignments JOIN game_assignments on (assignments.aid = game_assignments.aid) where game_assignments.gid = %s order by assignments.due ASC;""", (gid,))
    assignmentlst = cur.fetchall()
    conn.commit()
    cleanassignmentlist = []
    cleanaidlist = []
    titlelst = []
    for assignment in assignmentlst:
        cleanassignmentlist.append((assignment[0],assignment[1]))
        cleanaidlist.append((assignment[0], assignment[1], assignment[2]))
    finalcleansublst = []
    for (aid, title, due) in cleanaidlist:
        cur.execute("""SELECT submissions.uploadTime, students.name, students.email, submissions.link FROM students JOIN student_submissions ON (students.sid = student_submissions.sid) JOIN submissions on (submissions.subid = student_submissions.subid) JOIN assignments_submissions ON (submissions.subid = assignments_submissions.subid) WHERE assignments_submissions.aid = %s;""", (aid,))
        submissioninfolst = cur.fetchall()
        conn.commit()
        cleansubmissionlist = []
        for submission in submissioninfolst:
            cleansubmissionlist.append((submission[0],submission[1],submission[2],submission[3]))
        finalcleansublst.append((aid, title, due, cleansubmissionlist))
    cur.execute("""SELECT title from game where gid = %s;""",(gid,))
    gameName = cur.fetchall()
    print(finalcleansublst)
    gameName= gameName[0][0]
    return render_template("admingameassignment.html", gameName = gameName, pid = pid, gid = gid, assignments = finalcleansublst)

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
    # assignments = cur.fetchall()
    # for (assignment,) in assignments:
    #     cur.execute("""DELETE from assignments where aid = %s;""", (aid,))
    #     #TODO: also delete the submissions that go with the game!
    conn.commit()
    print("GAME "+str(gid)+" DELETED BY PROFESSOR ("+str(pid)+")")
    return redirect("http://www.rttportal.com/admin/students/"+str(pid))

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
    return redirect("http://www.rttportal.com/admin/game/"+pid+"/"+gid)

@app.route("/admin/deleteAssignment/<pid>/<gid>/<aid>/<securecode>")
def deleteAssignment(pid, gid, aid, securecode):
    cur.execute("""SELECT * from professor where pid = %s;""", (pid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Professor does not exist. Register first."
    if int(securecode) != 34554634636346357364:
        return "deleteAssignment authorization failed"
    cur.execute("""DELETE from game_assignments where gid = %s and aid =%s;""", (gid, aid))
    conn.commit()
    print("ASSIGNMENT "+str(aid)+" DELETED BY PROFESSOR ("+str(pid)+") FROM GAME "+str(gid))
    return redirect("http://www.rttportal.com/admin/game/"+str(pid)+"/"+str(gid))

@app.route("/admin/assignments/<pid>")
def adminAssignments(pid):
    cur.execute("""SELECT * from professor where pid = %s;""", (pid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Professor does not exist. Register first."
    cur.execute("""SELECT game.gid, game.title from game JOIN professor_game ON (professor_game.gid = game.gid) where pid = %s;""", (pid,))
    gids = cur.fetchall()
    conn.commit()
    assignmentlist = []
    for (gid, gatitle) in gids:
        cur.execute("""SELECT assignments.aid, assignments.due, assignments.title from assignments JOIN game_assignments ON (assignments.aid = game_assignments.aid) JOIN professor_game ON (game_assignments.gid = professor_game.gid) WHERE game_assignments.gid = %s;""", (gid,))
        aids = cur.fetchall()
        conn.commit()
        subassignmentlist = []
        for (aid, due, astitle) in aids:
            cur.execute("""SELECT count(assignments_submissions.subid) from assignments_submissions where aid = %s;""", (aid,))
            count = cur.fetchall()
            conn.commit()
            subcount = count[0][0]
            subassignmentlist.append((aid, due, astitle, subcount))
        assignmentlist.append((gid, gatitle, subassignmentlist))
    return render_template("adminassignments.html", assignmentlist = assignmentlist, pid = pid)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.errorhandler(500)
def page_not_found(e):
    return render_template('404.html')
