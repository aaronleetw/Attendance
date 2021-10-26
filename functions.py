from flask import *
from typing import OrderedDict
from flask import *
import pyrebase
from datetime import datetime
import pytz
import os
import base64
import csv
import os
import pandas as pd
from random import randint
from dotenv import load_dotenv
load_dotenv()

config = {
    "apiKey": os.environ.get('apiKey'),
    "authDomain": os.environ.get('authDomain'),
    "databaseURL": os.environ.get('databaseURL'),
    "storageBucket": os.environ.get('storageBucket'),
    "serviceAccount": os.environ.get('serviceAccount'),
    "messagingSenderId": os.environ.get('messagingSenderId'),
    "appId": os.environ.get('appId'),
    "measurementId": os.environ.get('measurementId'),
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()
storage = firebase.storage()
tz = pytz.timezone('Asia/Taipei')


def refresh_token():
    user = auth.refresh(session['refreshToken'])
    session['is_logged_in'] = True
    session['token'] = user['idToken']
    session['refreshToken'] = user['refreshToken']
    session['loginTime'] = datetime.now(tz)


def next_item(odic, key):
    return list(odic)[list(odic.keys()).index(key) + 1]


def check_login_status():
    return ('is_logged_in' not in session or
            session['is_logged_in'] == False or
            (datetime.now(tz) - session['loginTime']).total_seconds() > 3600)

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


def check_permission():
    return (db.child('Users').child(session['uid']).child('permission').get(session['token']).val() == 'admin' and
            db.child("Users").child(session['uid']).child("showUpload").get(session['token']).val() == '1')


def addZeroesUntil(str, number):
    if len(str) >= number:
        return str
    else:
        str = str + '0'
        return addZeroesUntil(str, number)


# MANAGE
def removeprefix(s, prefix):
    if s.startswith(prefix):
        return s[len(prefix):]
    return s
