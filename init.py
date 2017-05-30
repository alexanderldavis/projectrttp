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

cur.execute("""DROP TABLE IF EXISTS user CASCADE;
               DROP TABLE IF EXISTS professor CASCADE;
               DROP TABLE IF EXISTS game CASCADE;
               DROP TABLE IF EXISTS character CASCADE;""")
print("TABLES DELETED")
cur.execute("""CREATE TABLE user (uid serial unique, email varchar(200), name varchar(200), hashpswd varchar(200), gid varchar(100));""")
cur.execute("""CREATE TABLE professor (pid serial unique, email varchar(200), hashpswd varchar(200);""")
cur.execute("""CREATE TABLE game (gid serial unique, title varchar(200), name varchar(200), hashpswd varchar(200), gid varchar(100));""")
cur.execute("""CREATE TABLE character (cid serial unique, name varchar(200), imageurl varchar(200), description text, objectives text, strategy text, topsecret text);""")
conn.commit()
print("TABLES CREATED")
