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
               DROP TABLE IF EXISTS game_character CASCADE;
               DROP TABLE IF EXISTS student_character CASCADE;
               DROP TABLE IF EXISTS game_character CASCADE;
               DROP TABLE IF EXISTS documents CASCADE;""")
print("TABLES DELETED")

## CREATE NEW TABLES
cur.execute("""CREATE TABLE students (sid int unique, name varchar(300), email varchar(200) unique, hashpswd varchar(200));""")
cur.execute("""CREATE TABLE professor (pid int unique, email varchar(200) unique, hashpswd varchar(200));""")
cur.execute("""CREATE TABLE game (gid serial unique, title varchar(200) unique);""")
cur.execute("""CREATE TABLE students_game (sid int, gid int, FOREIGN KEY (sid) references students(sid), FOREIGN KEY (gid) references game(gid));""")
cur.execute("""CREATE TABLE professor_game (pid int, gid int, FOREIGN KEY (pid) references professor(pid), FOREIGN KEY (gid) references game(gid));""")
cur.execute("""CREATE TABLE character (cid serial unique, name varchar(200), descriptionURL text, imageURL text);""")
cur.execute("""CREATE TABLE student_character (sid int, cid int, FOREIGN KEY (sid) references students(sid), FOREIGN KEY (cid) references character(cid));""")
cur.execute("""CREATE TABLE game_character (gid int, cid int, FOREIGN KEY (gid) references game(gid), FOREIGN KEY (cid) references character (cid));""")

# NEW ROLLOUT v2
# cur.execute("""CREATE TABLE newspaper (nid serial unique, url text, uploaddate date);""")

# cur.execute("""CREATE TABLE documents (did serial unique, url text, uploaddate date, )""")
# cur.execute("""CREATE TABLE professor_game (pid int, gid int, FOREIGN KEY (pid) references professor(pid), FOREIGN KEY (gid) references game(gid));""")
# cur.execute("""CREATE TABLE game_character (gid int, cid int, FOREIGN KEY (gid) references game(gid), FOREIGN KEY (cid) references character(cid));""")
conn.commit()
print("TABLES CREATED")


# cur.execite("""INSERT INTO character (name, imageurl, description, objectives, strategy, topsecret) VALUES ('Test', 'TestUrl', 'testdescription', 'teststrategy', 'testtest', 'testtopsecret');""")
# cur.execute("""INSERT INTO character """)

cur.execute("""INSERT INTO character (name, descriptionURL, imageURL) VALUES ('Jacques Chirac', 'https://docs.google.com/document/d/1WOYKuY6ZFRR6s_3Wt2aurdLk_mO7RWhX1KxJ83kbaHI/pub?embedded=true', 'https://upload.wikimedia.org/wikipedia/commons/7/73/Jacques_Chirac_2.jpg');""")
conn.commit()
print("POPULATED TABLE CHARACTER")

print("POPULATED TABLE GAME_CHARACTER")
# str = ([introstr],[objectivesstr],[responsibilitiesstr],[strategystr],[topsecretstr])
