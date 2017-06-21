import flask
import flask_login
import psycopg2
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
from flask_mail import Mail
from flask_mail import Message

urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
conn = psycopg2.connect(database=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port)
cur = conn.cursor()

app = flask.Flask(__name__)
app.secret_key = 'super secret string'  # TODO: !!Change this!!

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

mail=Mail(app) # TODO: !!Change this!!
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'rttpatluther@gmail.com'
app.config['MAIL_PASSWORD'] = 'RTTPISFUN!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# @app.route("/send_mail") #https://stackoverflow.com/questions/20477749/flask-mail-attributeerror-function-object-has-no-attribute-send
def mail_confirmation(name, email, sid):
   msg = Message('Verify your account with RTTPortal.com', sender = 'RTTP at Luther College', recipients = [str(email)])
   msg.html = """<h1><b>Hello """+str(name)+"""! Welcome to RTTPortal!</b></h1>\n
                <h3>To finish setting up your account, click <a href= 'https://www.rttportal.com/validate/"""+str(sid)+"""'>here</a> to validate your email!</h3>

                <h6>If you did not request an account with us, simply click <a href='https://www.rttportal.com/errvalidate/"""+str(sid)+"""'>here</a>.</h6>

                <h3>Have a great day!</h3>
                <h3>RTTPortal.com</h3>
                """
   msg.txt = "Message not displaying correctly? Click here to validate your account with rttportal.com: https://www.rttportal.com/validate/"+str(sid)
   mail.send(msg)
   return "Sent"

def hashed_password(password):
    return generate_password_hash(password)

class User(flask_login.UserMixin):
    pass

# @login_manager.user_loader
# def user_loader(sid):
#     print(sid)
#     cur.execute("""SELECT email from students where sid = %s;""", (sid,))
#     lst = cur.fetchall()
#     print("IN user_loader: THIS IS THE lst RESULT (before init return): ", str(lst))
#     if len(lst) == 0:
#         return
#     user = User()
#     email = lst[0][0]
#     print("IN user_loader: THIS IS THE sid RESULT: ", str(sid))
#     print("IN user_loader: THIS IS THE email RESULT: ", str(email))
#     user.id = sid
#     return user

@login_manager.user_loader
def user_loader(uid):
    print(uid)
    cur.execute("""SELECT email from users where uid = %s;""", (uid,))
    lst = cur.fetchall()
    print("IN user_loader: THIS IS THE lst RESULT (before init return): ", str(lst))
    if len(lst) == 0:
        return
    user = User()
    email = lst[0][0]
    print("IN user_loader: THIS IS THE uid RESULT: ", str(uid))
    print("IN user_loader: THIS IS THE email RESULT: ", str(email))
    user.id = uid
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    cur.execute("""SELECT uid, student from users where email = %s;""", (email,))
    userList = cur.fetchall()
    conn.commit()
    if len(userList) == 0:
        return "Wrong email"
    uid = userList[0][0]
    student = userList[0][1]
    if student:
        cur.execute("""SELECT sid from students where email = %s;""", (email,))
        lst = cur.fetchall()
        print("IN request_loader: THIS IS THE lst RESULT (before init return): ", str(lst))
        if len(lst) == 0:
            return
        user = User()
        sid = lst[0][0]
        user.id = sid
        print("IN request_loader: THIS IS THE sid RESULT: ", str(sid))
        cur.execute("""SELECT hashpswd from students where email = %s;""", (email,))
        lst = cur.fetchall()
        conn.commit()
        print("IN request_loader: THIS IS THE lst RESULT: ", str(lst), "AND THE hashpswd RESULT: ", str(lst[0][0]))
        user.is_authenticated = check_password_hash(lst[0][0], request.form['pw'])
        return user
    if not student:
        pid = uid
        user.id = pid
        print("IN request_loader: THIS IS THE pid RESULT: ", str(pid))
        cur.execute("""SELECT hashpswd from professor where pid = %s;""", (email,))
        lst = cur.fetchall()
        conn.commit()
        user.is_authenticated = check_password_hash(lst[0][0], request.form['pw'])
        return user
    return "Failed request_loader"

################################################################################
#############                                                      #############
#############                   VIEWS - ALL                        #############
#############                                                      #############
################################################################################

#=========================# STUDENT CREATION + LOGIN #=========================#
@app.route("/")
def index():
    return flask.render_template('index.html', curid = 0)

@app.route('/screate', methods=['GET', 'POST'])
def setUp():
    if flask.request.method == 'GET':
        return flask.render_template("screate.html", curid = 0)
    name = flask.request.form['name']
    email = flask.request.form['email']
    cur.execute("""SELECT * from students where email = %s;""", (email,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) != 0:
        return "Student already exists"
    email = email.replace('%40', "@")
    password = flask.request.form['pw']
    hashpassword = hashed_password(password)
    print("CREATED PASSWORD HASH")
    cur.execute("""INSERT INTO students (sid, name, email, hashpswd, validated) VALUES ((SELECT floor(random()*(9999999-223+1))+10), %s, %s, %s, FALSE) returning sid;""", (name, email, hashpassword))
    conn.commit()
    sid = cur.fetchall()
    sid = sid[0][0]
    cur.execute("""INSERT INTO users (uid, email, student) VALUES (%s, %s, TRUE);""", (sid, email))
    conn.commit()
    print("TEST STUDENT CREATED")
    mail_confirmation(name, email, sid)
    return flask.redirect(flask.url_for('index'))

@app.route('/validate/<sid>', methods=["GET", "POST"])
def verify_student(sid):
    if not sid:
        return "Error"
    cur.execute("""SELECT * from students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) != 0:
        cur.execute("""UPDATE students set validated = TRUE WHERE sid = %s;""", (sid,))
        conn.commit()
        print("VERIFICATION SUCCESS")
        return flask.redirect(flask.url_for('login'))
    return "Verification fail"

@app.route('/errvalidate/<sid>', methods=["GET", "POST"])
def verify_undo(sid):
    cur.execute("""SELECT * from students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) != 0:
        cur.execute("""DELETE from students where sid = %s;""", (sid,))
        conn.commit()
        print("STUDENT", str(sid), "DELETED")
        return flask.redirect(flask.url_for('index'))
    return "Verification error failure"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return flask.render_template("login.html", curid = 0)
    email = flask.request.form['email']
    print("IN /LOGIN: THIS IS THE email RESULT:", str(email))
    cur.execute("""SELECT hashpswd, sid, validated from students where email = %s;""", (email,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) != 0:
        print("IN /LOGIN: THIS IS lst RESULT:", str(lst))
        if not lst[0][2]:
            return "You must validate your account first!"
        print("IN /LOGIN: THIS IS check_password_hash RESULT:", str(check_password_hash(lst[0][0], flask.request.form['pw'])))
        if check_password_hash(lst[0][0], flask.request.form['pw']):
            user = User()
            user.id = lst[0][1]
            flask_login.login_user(user)
            return flask.redirect(flask.url_for('student_games'))
    return 'Bad login'

#==========================# STUDENT PROTECTED VIEW #==========================#
@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id

@app.route("/sjoin")
@flask_login.login_required
def gameJoinStudent():
    sid = flask_login.current_user.id
    inviteCode = flask.request.args['inviteCode']
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
    return flask.redirect(flask.url_for("student_games"))

@app.route('/games')
@flask_login.login_required
def student_games():
    sid = flask_login.current_user.id
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    mylst = cur.fetchall()
    conn.commit()
    if len(mylst) == 0:
        return "Create account or log in"
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
    return flask.render_template('gamechooser.html', sid = sid, curid=0, gamechooser=0, username=mylst[0][0], gameinfo=cleanGamelst, picurl="https://cdn0.iconfinder.com/data/icons/user-pictures/100/unknown_1-2-512.png")

@app.route("/dashboard/<gid>")
@flask_login.login_required
def student_dashboard(gid):
    sid = flask_login.current_user.id
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Create account or log in"
    name = lst[0][0]
    cur.execute("""SELECT character.imageurl, character.name from character JOIN students_chargame ON (character.cid = students_chargame.cid) where students_chargame.gid = %s and students_chargame.sid = %s;""", (gid, sid))
    charinfo = cur.fetchall()
    picurl = charinfo[0][0]
    charname = charinfo[0][1]
    cur.execute("""SELECT title from game where gid = %s;""", (gid,))
    gametitle = cur.fetchall()
    gametitle = gametitle[0][0]
    return flask.render_template('dashboard.html', sid = sid, gid=gid, curid=1, username=name, gametitle=gametitle, picurl=picurl, charname=charname)

@app.route("/newspaper/<gid>")
@flask_login.login_required
def getCustomNewspaper(gid):
    sid = flask_login.current_user.id
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Create account or log in"
    cur.execute("""SELECT character.imageurl, character.name from character JOIN students_chargame ON (character.cid = students_chargame.cid) where students_chargame.gid = %s and students_chargame.sid = %s;""", (gid, sid))
    picurls = cur.fetchall()
    picurl = picurls[0][0]
    charname = picurls[0][1]
    return flask.render_template('newspaper.html', sid = sid, gid = gid, curid = 2, username=lst[0][0], charname=charname, picurl = picurl)

@app.route("/characterprofile/<gid>")
@flask_login.login_required
def getCustomCharacterProfile(gid):
    sid = flask_login.current_user.id
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Create account or log in"
    cur.execute("""SELECT * FROM character where cid = (SELECT cid FROM students_chargame WHERE sid = %s and gid = %s);""", (sid,gid))
    charlst = cur.fetchall()
    conn.commit()
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    namelst = cur.fetchall()
    conn.commit()
    cur.execute("""SELECT character.imageurl, character.name from character JOIN students_chargame ON (character.cid = students_chargame.cid) where students_chargame.gid = %s and students_chargame.sid = %s;""", (gid, sid))
    picurls = cur.fetchall()
    picurl = picurls[0][0]
    charname = picurls[0][1]
    return flask.render_template('characterprofile.html', sid = sid, gid = gid, curid = 3, username=namelst[0][0], charname=charname, picurl = picurl)

@app.route("/chat/<gid>")
@flask_login.login_required
def getCustomChat(gid):
    sid = flask_login.current_user.id
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
    return flask.render_template('chat.html', sid = sid, gid = gid, curid = 5, username= namelst[0][0], charname=charname, picurl = picurl)

@app.route("/assignments/<gid>")
@flask_login.login_required
def getCustomAssignments(gid):
    sid = flask_login.current_user.id
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    lst = cur.fetchall()
    conn.commit()
    if len(lst) == 0:
        return "Create account or log in"
    cur.execute("""SELECT assignments.aid, assignments.title, assignments.description, assignments.due FROM assignments JOIN game_assignments ON (assignments.aid = game_assignments.aid) WHERE gid = %s order by assignments.due ASC;""", (gid,))
    assignments = cur.fetchall()
    cur.execute("""SELECT character.imageurl, character.name from character JOIN students_chargame ON (character.cid = students_chargame.cid) where students_chargame.gid = %s and students_chargame.sid = %s;""", (gid, sid))
    picurls = cur.fetchall()
    picurl = picurls[0][0]
    charname = picurls[0][1]
    cur.execute("""SELECT name FROM students where sid = %s;""", (sid,))
    namelst = cur.fetchall()
    conn.commit()
    return flask.render_template('assignments.html', sid = sid, gid = gid, curid = 6, username= namelst[0][0], charname=charname, picurl = picurl, assignments = assignments)

@app.route("/upload/<gid>/<aid>/<securecode>")
@flask_login.login_required
def uploadAssignment(gid, aid, securecode):
    sid = flask_login.current_user.id
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
    return flask.render_template("upload.html", sid = sid, gid = gid, curid = 6, username= namelst[0][0], charname=charname, picurl = picurl, aid = aid)

@app.route('/sign_s3/')
@flask_login.login_required
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

@app.route("/submit_form/<gid>/<aid>/", methods = ["POST"])
@flask_login.login_required
def submit_form(gid, aid):
    sid = flask_login.current_user.id
    avatar_url = str(request.form["file-url"])
    print("IN HERE =================================")
    print(avatar_url)
    addSubmissionFromStudent(avatar_url, sid, aid)
    return flask.redirect("https://www.rttportal.com/assignments/"+gid)

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

@app.route("/account/<gid>")
@flask_login.login_required
def getCustomAccount(gid):
    sid = flask_login.current_user.id
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
    return flask.render_template('account.html', sid = sid, gid = gid, curid = 6, username = namelst[0][0], picurl = picurl)


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
    cur.execute("""INSERT INTO professor (pid, name, email, hashpswd) VALUES ((SELECT floor(random()*(2034343003-43434+1))+10), %s, %s, %s) returning pid;""",(name, email, hashpassword))
    conn.commit()
    pid = cur.fetchall()
    pid = pid[0][0]
    cur.execute("""INSERT INTO users (uid, email, student) VALUES (%s, %s, FALSE);""", (pid, email))
    conn.commit()
    print("PROFESSOR ACCOUNT CREATED")
    return "Professor account created!"

@app.route("/accountUpdate/<sid>")
@flask_login.login_required
def accountUpdate():
    sid = flask_login.current_user.id
    name = flask.request.args['name']
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
    return flask.redirect(flask.url_for('student_games'))

@app.route('/logout')
def student_logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('index'))

#===========================# ADMIN PROTECTED VIEW #===========================#
@app.route("/admin")
def adminLogin():
    return flask.render_template("adminlogin.html")

@app.route("/plogin")
def loginProfessor():
    email = flask.request.args['email']
    password = flask.request.args['pw']
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
        user = User()
        user.id = pid
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('admin_dashboard'))
    if not check_password_hash(lst[0][0], password):
        return "Password is wrong. Shame on you."
    return "Some error -- Contact Webmaster"

@app.route("/admin/dashboard")
@flask_login.login_required
def admin_dashboard():
    pid = flask_login.current_user.id
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
    assignments_submissions = 0
    studentcount = 0
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
    return flask.render_template("adminindex.html", pid = pid, username = name, titlelist = cleangamelst, studentcount=studentcount, assignmentcount = assignments_submissions)

@app.route("/admin/addGame")
@flask_login.login_required
def adminaddgame():
    pid = flask_login.current_user.id
    cur.execute("""SELECT email from professor where pid = %s;""", (pid,))
    email = cur.fetchall()
    conn.commit()
    email = email[0][0]
    cur.execute("""SELECT gtid, title from gametype;""")
    gametypes = cur.fetchall()
    conn.commit()
    return flask.render_template("adminaddgame.html", pid = pid, email = email, gametypes=gametypes, nums = [i for i in range(1, 26)])

@app.route("/admin/addassignment/<gid>")
@flask_login.login_required
def adminaddassignment(gid):
    pid = flask_login.current_user.id
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
    return flask.render_template("adminaddassignment.html", pid = pid, gid = gid, gametitle = gametitle)

@app.route("/paddassignment/<gid>")
@flask_login.login_required
def addassignmentadmin(gid):
    pid = flask_login.current_user.id
    title = flask.request.args['assignmentName']
    description = flask.request.args['title']
    duedate = flask.request.args['due']
    cur.execute("""INSERT into assignments (aid, title, description, due) values ((SELECT floor(random()*(2034343003-43434+1))+10), %s, %s, %s) RETURNING aid;""",(title,description,duedate))
    conn.commit()
    print("ADDED ASSIGNMENT TO RELATION ASSIGNMENTS")
    aid = cur.fetchall()
    aid = aid[0][0]
    cur.execute("""INSERT into game_assignments (gid, aid) values (%s, %s);""",(gid,aid))
    conn.commit()
    print("ADDED ASSIGNMENT TO RELATION GAME_ASSIGNMENTS")
    return flask.redirect("/admin/game/"+gid)

@app.route("/admin/deleteAssignment/<gid>/<aid>/<securecode>")
@flask_login.login_required
def deleteAssignment(gid, aid, securecode):
    pid = flask_login.current_user.id
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
    return flask.redirect("https://www.rttportal.com/admin/game/"+str(gid))

@app.route("/admin/game/<gid>")
@flask_login.login_required
def gameadminassignments(gid):
    pid = flask_login.current_user.id
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
    return flask.render_template("admingameassignment.html", gameName = gameName, pid = pid, gid = gid, assignments = finalcleansublst)

@app.route("/admin/students")
@flask_login.login_required
def adminstudents():
    pid = flask_login.current_user.id
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
    return flask.render_template("adminstudents.html", pid= pid, cleanstudentgidlist = cleanstudentgidlist)


@app.route("/pjoin")
@flask_login.login_required
def gameJoinProfessor():
    pid = flask_login.current_user.id
    gameName = flask.request.args['gameName']
    gtid = flask.request.args['gtid']
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
    return flask.redirect(flask.url_for('admin_dashboard'))


@app.route("/admin/getinvitecodes/<gid>")
@flask_login.login_required
def getInviteCodes(gid):
    pid = flask_login.current_user.id
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
    return flask.render_template("admininvitecodes.html", cinfo = cleanfinalcinfolst, title = title, pid = pid, gtname = gtname)


@app.route("/admin/deleteGame/<gid>/<securecode>")
@flask_login.login_required
def deleteGame(gid, securecode):
    pid = flask_login.current_user.id
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
    return flask.redirect(flask.url_for('adminstudents'))


@app.route("/admin/assignments")
@flask_login.login_required
def adminAssignments():
    pid = flask_login.current_user.id
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
    return flask.render_template("adminassignments.html", assignmentlist = assignmentlist, pid = pid)

@app.route('/admin/logout')
def admin_logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('adminLogin'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'You are no longer logged in. Please sign in again.'

@app.errorhandler(404)
def page_not_found(e):
    return flask.render_template('404.html')

@app.errorhandler(500)
def page_not_found(e):
    return flask.render_template('404.html')


if __name__ == '__main__':
   app.run(debug = True)
