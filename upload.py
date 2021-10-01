from flask import *
import pyrebase
from datetime import datetime
import pytz
import csv
import os
import pandas as pd
from dotenv import load_dotenv
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
                with open(filepath) as file:
                    csv_dict = csv.DictReader(file)
                    for row in csv_dict:
                        if row['number'] == 'password':
                            auth.create_user_with_email_and_password(
                                gradec + classc + "@group-attendance.fhjh.tp.edu.tw", row['name'])
                            user = auth.sign_in_with_email_and_password(
                                gradec + classc + "@group-attendance.fhjh.tp.edu.tw", row['name'])
                            db.child("Users").child(user['localId']).update({
                                "permission": 'homeroom',
                                "username": gradec + classc,
                                "homeroom": gradec + classc
                            })
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
                for i in range(category_cnt):
                    tmp_csv = csv_dict[csv_dict.columns[i+1]].tolist()
                    for j in range(len(tmp_csv)):
                        if type(tmp_csv[j]) == float:
                            break
                        if j % 5 == 0:
                            db.child("Classes").child("GP_Class").child(csv_dict.columns[i+1]).child("Class").child(
                                tmp_csv[j]).child("name").set(tmp_csv[j+1] + " : " + tmp_csv[j+2] + " (" + tmp_csv[j+3] + ")", session['token'])
                            auth.create_user_with_email_and_password(
                                tmp_csv[j] + "@group-attendance.fhjh.tp.edu.tw", tmp_csv[j+4])
                            user = auth.sign_in_with_email_and_password(
                                tmp_csv[j] + "@group-attendance.fhjh.tp.edu.tw", tmp_csv[j+4])
                            db.child("Users").child(user['localId']).update({
                                "permission": 'group',
                                "username": tmp_csv[j],
                                "class": {
                                    csv_dict.columns[i+1]: tmp_csv[j],
                                }
                            }, session['token'])
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
