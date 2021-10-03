from flask import *
import pyrebase
from datetime import datetime
import pytz
import csv
import os
import pandas as pd
from dotenv import load_dotenv
from random import randint
load_dotenv()

upload = Blueprint('upload', __name__)
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
tz = pytz.timezone('Asia/Taipei')


def check_login_status():
    return ('is_logged_in' not in session or
            session['is_logged_in'] == False or
            (datetime.now(tz) - session['loginTime']).total_seconds() > 3600)


def check_permission():
    return (db.child('Users').child(session['uid']).child('permission').get(session['token']).val() == 'admin' and
            db.child("Users").child(session['uid']).child("showUpload").get(session['token']).val() == '1')


def addZeroesUntil(str, number):
    if len(str) >= number:
        return str
    else:
        str = str + '0'
        return addZeroesUntil(str, number)


@upload.route('/upload/users', methods=['GET', 'POST'])
def upload_users():
    if ((not check_login_status()) and check_permission()):
        if request.method == 'GET':
            return render_template('uploadcsv.html', title="All Indiviual Users", url="/upload/users")
        elif request.method == 'POST':
            try:
                csv_file = request.files['csv']
                filepath = os.path.join('./temp', csv_file.filename)
                csv_file.save(filepath)
                with open(filepath) as file:
                    csv_dict = csv.DictReader(file)
                    for row in csv_dict:
                        pwd = addZeroesUntil(row['password'], 6)
                        user = auth.create_user_with_email_and_password(
                            row['username'] + "@group-attendance.fhjh.tp.edu.tw", pwd)
                        db.child("Users").child(user['localId']).set({
                            'permission': 'realPerson',
                            'name': row['name'],
                            'origUsername': row['username'],
                        }, session['token'])
                os.remove(filepath)
            except Exception as e:
                os.remove(filepath)
                return "Error. Please try again\n("+str(e)+")"
            return "Successfully uploaded users"
    else:
        return redirect('/logout')


@upload.route('/upload/1', methods=['GET', 'POST'])
def upload_homeroom():
    if ((not check_login_status()) and check_permission()):
        if request.method == 'GET':
            return render_template('uploadcsv.html', title="Homeroom List", url="/upload/1")
        elif request.method == 'POST':
            try:
                # get csv
                gradec = request.form['gradeCode']
                classc = request.form['classcode']
                csv_file = request.files['csv']
                filepath = os.path.join('./temp', csv_file.filename)
                csv_file.save(filepath)
                allUsers = db.child("Users").get(session['token']).val()
                with open(filepath) as file:
                    csv_dict = csv.DictReader(file)
                    for row in csv_dict:
                        if row['number'] == 'teacher' or row['number'] == 'Teacher':
                            accs = row['name'].split(',')
                            for key in allUsers:
                                if accs == []:
                                    break
                                if (allUsers[key]['origUsername'] in accs):
                                    db.child("Users").child(key).child("accounts").child("homeroom^"+gradec+classc+'^'+str(randint(10000, 99999))).update({
                                        "homeroom": gradec + '^' + classc,
                                        "type": 'homeroom'
                                    }, session['token'])
                                    accs.remove(allUsers[key]['origUsername'])
                        else:
                            db.child("Homerooms").child(gradec).child(
                                classc).child(row['number']).set(row, session['token'])
                # row['class'] row['number'] row['name'] row['eng_name']
                os.remove(filepath)
            except Exception as e:
                os.remove(filepath)
                return "Error. Please try again\n("+str(e)+")"
            return "Successfully uploaded " + gradec + "-" + classc
    else:
        return redirect('/logout')


@upload.route('/upload/2', methods=['GET', 'POST'])
def upload_gp_classes():
    if ((not check_login_status()) and check_permission()):
        if request.method == 'GET':
            return render_template('uploadcsv.html', title="Group Classes", url="/upload/2")
        elif request.method == 'POST':
            try:
                csv_file = request.files['csv']
                filepath = os.path.join('./temp', csv_file.filename)
                csv_file.save(filepath)
                csv_dict = pd.read_csv(filepath)
                category_cnt = csv_dict.shape[1] - 1
                allUsers = db.child("Users").get(session['token']).val()
                for i in range(category_cnt):
                    tmp_csv = csv_dict[csv_dict.columns[i+1]].tolist()
                    for j in range(len(tmp_csv)):
                        if type(tmp_csv[j]) == float:
                            break
                        if j % 5 == 0:
                            db.child("Classes").child("GP_Class").child(csv_dict.columns[i+1]).child("Class").child(
                                tmp_csv[j]).child("name").set(tmp_csv[j+1] + " : " + tmp_csv[j+2] + " (" + tmp_csv[j+3] + ")", session['token'])
                            accs = tmp_csv[j+4].split(',')
                            for key in allUsers:
                                if accs == []:
                                    break
                                if (allUsers[key]['origUsername'] in accs):
                                    db.child("Users").child(key).child("accounts").child("GP_Class^"+csv_dict.columns[i+1]+'^'+str(randint(10000, 99999))).update({
                                        csv_dict.columns[i+1]: tmp_csv[j],
                                        "type": 'group'
                                    }, session['token'])
                                    accs.remove(allUsers[key]['origUsername'])
                os.remove(filepath)
            except Exception as e:
                os.remove(filepath)
                return "Error. Please try again\n("+str(e)+")"
            return "Successfully uploaded"
    else:
        return redirect('/logout')


@upload.route('/upload/3', methods=['GET', 'POST'])
def upload_stud_in_group():
    if ((not check_login_status()) and check_permission()):
        if request.method == 'GET':
            return render_template('uploadcsv.html', title="Student in Group List", url="/upload/3")
        elif request.method == 'POST':
            try:
                gradec = request.form['gradeCode']
                classc = request.form['classcode']
                csv_file = request.files['csv']
                filepath = os.path.join('./temp', csv_file.filename)
                csv_file.save(filepath)
                with open(filepath) as file:
                    csv_dict = csv.DictReader(file)
                    headers = csv_dict.fieldnames
                    headers = headers[1:]
                    for h in headers:
                        db.child("Classes").child("GP_Class").child(
                            h).child("Homerooms").update({gradec+'^'+classc: 0}, session['token'])
                    for row in csv_dict:
                        for h in headers:
                            db.child("Homerooms").child(gradec).child(classc).child(
                                row[str(gradec+classc)]).child("GP_Class").update({h: row[h]}, session['token'])
                os.remove(filepath)
            except Exception as e:
                os.remove(filepath)
                return "Error. Please try again\n("+str(e)+")"
            return "Successfully uploaded " + gradec + "-" + classc
    else:
        return redirect('/logout')


@upload.route('/upload/4', methods=['GET', 'POST'])
def upload_period_list():
    if ((not check_login_status()) and check_permission()):
        if request.method == 'GET':
            return render_template('uploadcsv.html', title="Period List", url="/upload/4")
        elif request.method == 'POST':
            try:
                # get csv
                gradec = request.form['gradeCode']
                classc = request.form['classcode']
                csv_file = request.files['csv']
                filepath = os.path.join('./temp', csv_file.filename)
                csv_file.save(filepath)
                csv_dict = pd.read_csv(filepath)
                periodCodes = csv_dict['Period Day'].tolist()
                for i in range(5):
                    tmp_csv = csv_dict[str(i+1)].tolist()
                    for j in range(len(tmp_csv)):
                        if not (periodCodes[j].endswith('-t')):
                            if type(tmp_csv[j]) == float:
                                db.child("Classes").child("Homeroom").child(gradec).child(classc).child(
                                    str(i+1)).child(periodCodes[j]).update({'name': '--'}, session['token'])
                            else:
                                db.child("Classes").child("Homeroom").child(gradec).child(classc).child(
                                    str(i+1)).child(periodCodes[j]).update({'name': tmp_csv[j]}, session['token'])
                                if not(periodCodes[j] == 'm' or periodCodes[j] == 'n'):
                                    j += 1
                                    db.child("Classes").child("Homeroom").child(gradec).child(classc).child(
                                        str(i+1)).child(periodCodes[j-1]).update({'teacher': tmp_csv[j]}, session['token'])
                os.remove(filepath)
            except Exception as e:
                os.remove(filepath)
                return "Error. Please try again\n("+str(e)+")"
            return "Successfully uploaded " + gradec + "-" + classc
    else:
        return redirect('/logout')


@upload.route('/upload/dates', methods=['GET', 'POST'])
def upload_dates():
    if ((not check_login_status()) and check_permission()):
        if request.method == 'GET':
            return render_template('uploadcsv.html', title="School Days", url="/upload/dates")
        elif request.method == 'POST':
            try:
                csv_file = request.files['csv']
                filepath = os.path.join('./temp', csv_file.filename)
                csv_file.save(filepath)
                with open(filepath) as file:
                    csv_dict = csv.DictReader(file)
                    headers = csv_dict.fieldnames
                    temp = db.child("Homerooms").get(session['token']).val()
                    for row in csv_dict:
                        for h in headers:
                            h = h.replace('/', '-')
                            for t in temp:
                                for i in temp[t]:
                                    periodData = db.child("Classes").child(
                                        "Homeroom").child(t).child(i).get(session['token']).val()
                                    db.child("Homerooms").child(t).child(i).child(
                                        "Absent").child(h).update({"dow": row[h.replace('-', '/')]}, session['token'])
                                    db.child("Homerooms").child(t).child(i).child(
                                        "Absent").child(h).update(periodData[int(row[h.replace('-', '/')])], session['token'])
                os.remove(filepath)
            except Exception as e:
                os.remove(filepath)
                return "Error. Please try again\n("+str(e)+")"
            return "Successfully uploaded dates"
    else:
        return redirect('/logout')


@upload.route('/upload/admin_acc', methods=['GET', 'POST'])
def upload_admin_acc():
    if ((not check_login_status()) and check_permission()):
        if request.method == 'GET':
            return render_template('uploadcsv.html', title="Admin Accounts", url="/upload/admin_acc")
        elif request.method == 'POST':
            try:
                csv_file = request.files['csv']
                filepath = os.path.join('./temp', csv_file.filename)
                csv_file.save(filepath)
                with open(filepath) as file:
                    csv_dict = csv.DictReader(file)
                    for row in csv_dict:
                        auth.create_user_with_email_and_password(
                            row['username'] + '@group-attendance.fhjh.tp.edu.tw', row['password'])
                        user = auth.sign_in_with_email_and_password(
                            row['username'] + '@group-attendance.fhjh.tp.edu.tw', row['password'])
                        db.child("Users").child(user['localId']).update({
                            'permission': 'admin',
                            'username': row['username'],
                            'showUpload': row['permission']
                        }, session['token'])
                os.remove(filepath)
            except Exception as e:
                os.remove(filepath)
                return "Error. Please try again\n("+str(e)+")"
            return "Successfully uploaded admin accounts"
    else:
        return redirect('/logout')
