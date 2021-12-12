from flask import *
from typing import OrderedDict
from flask import *
from datetime import datetime
import pytz
import os
import base64
import csv
import os
import pandas as pd
from random import randint, choices
import string
from dotenv import load_dotenv
from passlib.hash import sha256_crypt
import mysql.connector
import requests
from pprint import pprint
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_babelex import Babel
load_dotenv()

tz = pytz.timezone('Asia/Taipei')

DSBOARD = [
    "上課前秩序",
    "上課前禮貌",
    "課間秩序",
    "板擦清潔",
    "講桌乾淨",
    "地板整齊",
    "桌椅整齊"
]
DSTEXT = [
    "",
    "定",
    "心",
    "",
    "專",
    "案",
    ""
]
DSOFFENSES = {
    'A': "把玩物品、不專心聽講",
    'B': "書寫或傳遞紙條、物品", 
    'C': "自言自語或與同學交談",
    'D': "接話、大聲笑、起哄、發出怪聲",
    'E': "亂動、逗弄同學、影響教學情境",
    'F': "閱讀與該堂課無關之書籍",
    'G': "不敬師長、態度傲慢",
    'H': "其他經任教老師糾正、制止之行為",
    'Z': "上課睡覺"
}

def refresh_db():
    return mysql.connector.connect(user=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PASSWORD'),
                                   host=os.environ.get('MYSQL_HOST'),
                                   database='attendance')

def genHash(password):
    return sha256_crypt.hash(password)

def verifyPassword(password, hash):
    return sha256_crypt.verify(password, hash)

def refresh_token():
    session['is_logged_in'] = True
    session['loginTime'] = datetime.now(tz)


def next_item(odic, key):
    return list(odic)[list(odic.keys()).index(key) + 1]


def check_login_status():
    return ('is_logged_in' not in session or
            session['is_logged_in'] == False or
            (datetime.now(tz) - session['loginTime']).total_seconds() > 3600)

def send_email(to, subject, text):
    return requests.post(
        "https://api.mailgun.net/v3/mg.aaronlee.tech/messages",
        auth=("api", os.environ.get("MG_APIKEY")),
        data={"from": "Attendance 點名系統 <attendance@mg.aaronlee.tech>",
              "to": [to],
              "subject": subject,
              "html": text})

def getName(grade, class_, number):
    db = refresh_db()
    cursor = db.cursor()
    print(grade, class_, number)
    cursor.execute("SELECT name FROM students WHERE grade=%s AND class=%s AND number=%s", (grade, class_, number))
    name = cursor.fetchone()
    cursor.close()
    db.close()
    return name[0]

# LOGIN


def verify_recaptcha(response):
    return True
    data = {
        'secret': os.environ.get('RECAPTCHA_SECRET'),
        'response': response,
        'remoteip': request.remote_addr
    }
    r = requests.post(
        'https://www.google.com/recaptcha/api/siteverify', data=data)
    print(r.json())
    return r.json()['success']

# UPLOAD
def is_admin():
    return 'subuser_type' in session and session['subuser_type'] == 'admin'

def check_permission():
    if 'subuser_type' in session and session['subuser_type'] == 'admin':
        return session['showUpload']
    else:
        return False

# MANAGE
def removeprefix(s, prefix):
    if s.startswith(prefix):
        return s[len(prefix):]
    return s
