import psycopg2
from flask import Flask, render_template, request
import os
import urllib.parse
import json
import requests as req

urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
conn = psycopg2.connect(database=url.path[1:],user=url.username,password=url.password,host=url.hostname,port=url.port)
cur = conn.cursor()

## WARNING: RUNNING THIS CODE WILL DELETE ALL EXISTING USER ACCOUNTS AND CONNECTED DATA!
cur.execute("""DROP TABLE IF EXISTS students CASCADE;
               DROP TABLE IF EXISTS students_game CASCADE;
               DROP TABLE IF EXISTS professor CASCADE;
               DROP TABLE IF EXISTS game CASCADE;
               DROP TABLE IF EXISTS character CASCADE;
               DROP TABLE IF EXISTS professor_game CASCADE;
               DROP TABLE IF EXISTS student_character CASCADE;
               DROP TABLE IF EXISTS game_assignments CASCADE;
               DROP TABLE IF EXISTS assignments CASCADE;
               DROP TABLE IF EXISTS student_submissions CASCADE;
               DROP TABLE IF EXISTS submissions CASCADE;
               DROP TABLE IF EXISTS gametype CASCADE;
               DROP TABLE IF EXISTS assignments_submissions CASCADE;
               DROP TABLE IF EXISTS students_chargame CASCADE;""")
print("TABLES DELETED")

## CREATE NEW TABLES
cur.execute("""CREATE TABLE students (sid int unique, name varchar(300), email varchar(200) unique, hashpswd varchar(200));""")
cur.execute("""CREATE TABLE professor (pid int unique, name varchar(300), email varchar(200) unique, hashpswd varchar(200));""")
cur.execute("""CREATE TABLE gametype (gtid int unique, title varchar(200));""")
cur.execute("""CREATE TABLE game (gid int unique, title varchar(200) unique, gtid int, FOREIGN KEY (gtid) references gametype(gtid));""")
cur.execute("""CREATE TABLE students_game (sid int, gid int, FOREIGN KEY (sid) references students(sid), FOREIGN KEY (gid) references game(gid));""")
cur.execute("""CREATE TABLE professor_game (pid int, gid int, FOREIGN KEY (pid) references professor(pid), FOREIGN KEY (gid) references game(gid));""")
cur.execute("""CREATE TABLE character (cid int unique, name varchar(200), descriptionURL text, imageURL text, gtid int, FOREIGN KEY (gtid) references gametype(gtid));""")
cur.execute("""CREATE TABLE student_character (sid int, cid int, FOREIGN KEY (sid) references students(sid), FOREIGN KEY (cid) references character(cid));""")

cur.execute("""CREATE TABLE students_chargame (sid int, cid int, gid int, FOREIGN KEY (sid) references students(sid), FOREIGN KEY (cid) references character(cid), FOREIGN KEY (gid) references game(gid));""")

## V2 beta
cur.execute("""CREATE TABLE assignments (aid int unique, title varchar(200), due timestamp);""")
cur.execute("""CREATE TABLE submissions (subid int unique, link varchar(300), uploadTime timestamp);""")
cur.execute("""CREATE table game_assignments (gid int, aid int, FOREIGN KEY (gid) references game(gid), FOREIGN KEY (aid) references assignments(aid));""")
cur.execute("""CREATE TABLE student_submissions (sid int, subid int, FOREIGN KEY (sid) references students(sid), FOREIGN KEY (subid) references submissions(subid));""")
cur.execute("""CREATE TABLE assignments_submissions (aid int, subid int, FOREIGN KEY (aid) references assignments(aid), FOREIGN KEY (subid) references submissions(subid));""")



# NEW ROLLOUT v3 alpha
# cur.execute("""CREATE TABLE newspaper (nid serial unique, url text, uploaddate date);""")

# cur.execute("""CREATE TABLE documents (did serial unique, url text, uploaddate date, )""")
# cur.execute("""CREATE TABLE professor_game (pid int, gid int, FOREIGN KEY (pid) references professor(pid), FOREIGN KEY (gid) references game(gid));""")
# cur.execute("""CREATE TABLE game_character (gid int, cid int, FOREIGN KEY (gid) references game(gid), FOREIGN KEY (cid) references character(cid));""")
conn.commit()
print("TABLES CREATED")

cur.execute("""INSERT INTO gametype (gtid, title) VALUES ((SELECT floor(random()*(2034343003-43434+1))+10), '2002 French Presidential Election')""")
conn.commit()
print("GAMETYPE POPULATED")

cur.execute("""INSERT INTO character (cid, name, descriptionURL, imageURL, gtid) VALUES ((SELECT floor(random()*(2034343003-43434+1))+10),'Jacques Chirac', 'https://docs.google.com/document/d/1WOYKuY6ZFRR6s_3Wt2aurdLk_mO7RWhX1KxJ83kbaHI/pub?embedded=true', 'https://upload.wikimedia.org/wikipedia/commons/7/73/Jacques_Chirac_2.jpg', (SELECT gtid from gametype where title = '2002 French Presidential Election'));""")
cur.execute("""INSERT INTO character (cid, name, descriptionURL, imageURL, gtid) VALUES ((SELECT floor(random()*(2034343003-43434+1))+10), 'Arlette Laguiller', 'https://www.dropbox.com/s/4gedlbi2sddnyjz/Arlette%20Laguiller.docx?dl=0', 'https://upload.wikimedia.org/wikipedia/commons/8/8e/Arlette_Laguiller.jpg', (SELECT gtid from gametype where title = '2002 French Presidential Election'));""")
cur.execute("""INSERT INTO character (cid, name, descriptionURL, imageURL, gtid) VALUES ((SELECT floor(random()*(2034343003-43434+1))+10), 'Christiana Taubira', 'https://www.dropbox.com/s/zmp3gk4vj3we5qc/Christiana%20Taubira.docx?dl=0', 'https://upload.wikimedia.org/wikipedia/commons/1/1e/Christiane_Taubira_par_Claude_Truong-Ngoc_juin_2013.jpg', (SELECT gtid from gametype where title = '2002 French Presidential Election'));""")
cur.execute("""INSERT INTO character (cid, name, descriptionURL, imageURL, gtid) VALUES ((SELECT floor(random()*(2034343003-43434+1))+10), 'Noel Mamère', 'https://www.dropbox.com/s/at1mspxgwtwjeiq/Noel%20Mam%C3%A8re.docx?dl=0', 'https://upload.wikimedia.org/wikipedia/commons/1/1a/Noel.Mamere2006.JPG', (SELECT gtid from gametype where title = '2002 French Presidential Election'));""")
conn.commit()
print("POPULATED TABLE CHARACTER")
