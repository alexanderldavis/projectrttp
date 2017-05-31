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
               DROP TABLE IF EXISTS professor CASCADE;
               DROP TABLE IF EXISTS game CASCADE;
               DROP TABLE IF EXISTS character CASCADE;
               DROP TABLE IF EXISTS professor_game CASCADE;
               DROP TABLE IF EXISTS game_character CASCADE;""")
print("TABLES DELETED")

# Create new tables here
cur.execute("""CREATE TABLE students (uid serial unique, email varchar(200) unique, name varchar(200), charid varchar(200), gid varchar(100), characterid varchar(100));""")
cur.execute("""CREATE TABLE professor (pid serial unique, email varchar(200) unique, hashpswd varchar(200));""")
cur.execute("""CREATE TABLE game (gid serial unique, title varchar(200) unique);""")
cur.execute("""CREATE TABLE character (cid serial unique, name varchar(200), imageurl varchar(200), description text, objectives text, strategy text, topsecret text);""")
cur.execute("""CREATE TABLE professor_game (pid int, gid int, FOREIGN KEY (pid) references professor(pid), FOREIGN KEY (gid) references game(gid));""")
cur.execute("""CREATE TABLE game_character (gid int, cid int, FOREIGN KEY (gid) references game(gid), FOREIGN KEY (cid) references character(cid));""")
conn.commit()
print("TABLES CREATED")


# cur.execite("""INSERT INTO character (name, imageurl, description, objectives, strategy, topsecret) VALUES ('Test', 'TestUrl', 'testdescription', 'teststrategy', 'testtest', 'testtopsecret');""")
# cur.execute("""INSERT INTO character """)


original = open("charactersheet.txt", "r")

intro = 0
objectives = 0
responsibilities = 0
strategy = 0
topsecret = 0

namestr = ""
introstr = ""
objectivesstr = ""
responsibilitiesstr = ""
strategystr = ""
topsecretstr = ""

for line in original:
	if line == "Introduction\n":
		intro = 1
	if line == "Objectives\n":
		intro = 0
		objectives = 1
	if line == "Responsibilities\n":
		objectives = 0
		responsibilities = 1
	if line == "Strategy/Relationships\n":
		responsibilities = 0
		strategy = 1
	if line == "--TOP SECRET--\n":
		strategy = 0
		topsecret = 1

	if intro == 0:
		if line != "\n":
			namestr += line
	if intro == 1:
		if line != "\n":
			introstr += line
	if objectives == 1:
		if line != "\n":
			objectivesstr += line
	if responsibilities == 1:
		if line != "\n":
			responsibilitiesstr += line
	if strategy == 1:
		if line != "\n":
			strategystr += line
	if topsecret == 1:
		if line != "\n":
			topsecretstr += line

cur.execute("""INSERT INTO character (name, imageurl, description, objectives, strategy, topsecret) VALUES (%s, %s, %s, %s, %s, %s)""", (namestr, introstr, objectivesstr, responsibilitiesstr, strategystr, topsecretstr))
conn.commit()
print("POPULATED TABLE CHARACTER")
# str = ([introstr],[objectivesstr],[responsibilitiesstr],[strategystr],[topsecretstr])
