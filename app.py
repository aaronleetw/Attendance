from flask import *
import pyrebase
from datetime import datetime
import time
import pytz
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import csv
import os
from dotenv import load_dotenv
from pprint import pprint
load_dotenv()
app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
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


def manageProcess(fCommand, fData):
    # this is to fix a bug where pyrebase doesnt load the first request
    db.child("Users").child(
        session['uid']).child("permission").get().val()
    # end bug fix
    pl = db.child("Users").child(
        session['uid']).child("permission").get().val()
    print(pl)
    print(db.child("Users").child(
        'DRZqqSSpg3OkPSCuWkv417dv0vh1').child("permission").get().val())
    print(fCommand, fData, session['uid'], pl)
    if pl == 'admin':
        return pl
    elif pl == 'group':
        classes = db.child("Users").child(
            session['uid']).child("class").get().val()
        cclass = {}
        for i in classes:
            cclass = {
                "name": db.child("Classes").child(i).child(
                    "Class").child(classes[i]).child("name").get().val(),
                "category": i,
                "class_id": classes[i]
            }
        print("got class")
        students = db.child("Classes").child(cclass['category']).child(
            "Class").child(cclass['class_id']).child("Students").get().val()
        print(students['9']['11'])
        all_stud_list = {}
        for grade in students:
            print(grade)
            all_stud_list[grade] = {}
            print(type(students[grade]))
            for homeroom in students[grade]:
                print(homeroom)
                roomData = db.child("Homerooms").child(
                    grade).child(homeroom).get().val()
                all_stud_list[grade][homeroom] = {}
                if type(students[grade][homeroom]) == list:
                    i = 0
                    for student in students[grade][homeroom]:
                        if student == 0:
                            all_stud_list[grade][homeroom][i] = {
                                "name": roomData[str(i)]["name"],
                                "eng_name": roomData[str(i)]["eng_name"]
                            }
                        i += 1
                else:
                    for student in students[grade][homeroom]:
                        print(student)
                        all_stud_list[grade][homeroom][student] = {
                            "name": roomData[student]["name"],
                            "eng_name": roomData[student]["eng_name"]
                        }
        print("got students")
        dates = db.child("Classes").child(
            cclass['category']).child("Dates").get().val()
        status = 0
        attendance = {}

        if fCommand == 'date':
            currDate = fData
            if cclass['class_id'] in dates[currDate]:
                status = 1
                for grade in dates[currDate]['Absent']:
                    attendance[grade] = {}
                    for homeroom in dates[currDate]['Absent'][grade]:
                        attendance[grade][homeroom] = {}
                        for student in dates[currDate]['Absent'][grade][homeroom]:
                            attendance[grade][homeroom][student] = 0
        else:
            for i in dates:
                if i >= datetime.now(tz).strftime("%Y-%m-%d"):
                    currDate = i
                    if cclass['class_id'] in dates[currDate]:
                        status = 1
                        for grade in dates[currDate]['Absent']:
                            attendance[grade] = {}
                            for homeroom in dates[currDate]['Absent'][grade]:
                                attendance[grade][homeroom] = {}
                                for student in dates[currDate]['Absent'][grade][homeroom]:
                                    attendance[grade][homeroom][student] = 0
                    break
                dates[i].pop('placeholder')
        print("got dates")
        return render_template('group_teach.html', cclass=cclass, all_stud_list=all_stud_list, dates=dates, currDate=currDate, status=status, attendance=attendance)
    elif pl == 'homeroom':
        homeroom = db.child("Users").child(
            session['uid']).child("homeroom").get().val()
        homeroomCode = homeroom.split('^')
        homeroom = db.child("Homerooms").child(
            homeroomCode[0]).child(homeroomCode[1]).get().val()
        categories = homeroom['Categories'].split('^')
        currCategory = categories[0]
        currDate = ""
        gpClasses = db.child("Classes").child(currCategory).get().val()
        dates = gpClasses['Dates']
        confirmedClasses = []
        status = 0

        if fCommand == 'date':
            currDate = fData
            tmp1 = 0
            tmp2 = 0
            for k in gpClasses['Class']:
                if k in dates[currDate]:
                    confirmedClasses.append(k)
                    tmp2 += 1
                tmp1 += 1
            if tmp1 == tmp2:
                status = 1
        else:
            for i in dates:
                if i >= datetime.now(tz).strftime("%Y-%m-%d"):
                    currDate = i
                    tmp1 = 0
                    tmp2 = 0
                    for k in gpClasses['Class']:
                        if k in dates[currDate]:
                            confirmedClasses.append(k)
                            tmp2 += 1
                        tmp1 += 1
                    if tmp1 == tmp2:
                        status = 1
                    break
        print("got dates")
        db.child("Classes").child(currCategory).child("Dates")
        homeroom.pop('Categories')
        all_stud_list = {}
        for i in homeroom:
            all_stud_list[i] = {}
            all_stud_list[i]['name'] = homeroom[i]['name']
            all_stud_list[i]['eng_name'] = homeroom[i]['eng_name']
            all_stud_list[i]['gpClass'] = homeroom[i]['Classes'][currCategory]
            if all_stud_list[i]['gpClass'] in confirmedClasses:
                if (homeroomCode[0] in gpClasses['Dates'][currDate]['Absent'] and
                        homeroomCode[1] in gpClasses['Dates'][currDate]['Absent'][homeroomCode[0]] and
                        i in gpClasses['Dates'][currDate]['Absent'][homeroomCode[0]][homeroomCode[1]]):
                    # confirmed by teacher and absent
                    all_stud_list[i]['status'] = 2
                else:
                    # confirmed by teacher and not absent
                    all_stud_list[i]['status'] = 1
            else:
                all_stud_list[i]['status'] = 0  # not yet confirmed by teacher
        return render_template('homeroom.html', all_stud_list=all_stud_list, currDate=currDate, dates=dates, gpClasses=gpClasses, confirmedClasses=confirmedClasses,
                               currCategory=currCategory, categories=categories, homeroomCode=homeroomCode, status=status)

    else:
        return redirect('/')


@ app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if check_login_status():
            return render_template('login.html', error=False)
        return redirect('/manage')
    elif request.method == 'POST':
        if check_login_status():
            try:
                user = auth.sign_in_with_email_and_password(
                    request.form['username'] + "@group-attendence.fhjh.tp.edu.tw", request.form['password'])
                session['is_logged_in'] = True
                session['email'] = user['email']
                session['uid'] = user['localId']
                session['token'] = user['idToken']
                session['refreshToken'] = user['refreshToken']
                session['loginTime'] = datetime.now(tz)
                return redirect('/manage')
            except Exception as e:
                return render_template('login.html', error=True)
        else:
            return redirect('/manage')


@app.route('/manage', methods=['GET'])
def manage():
    return manageProcess("", "")


@app.route('/manage/date', methods=['POST'])
def manage_date():
    return manageProcess("date", request.form['date'])


@app.route('/manage/group_teach_publish', methods=['POST'])
def group_teach_publish():
    classes = db.child("Users").child(
        session['uid']).child("class").get().val()
    cclass = {}
    for i in classes:
        cclass = {
            "name": db.child("Classes").child(i).child(
                "Class").child(classes[i]).child("name").get().val(),
            "category": i,
            "class_id": classes[i]
        }
    print("got class")
    cDate = ""
    for key in request.form.keys():
        print(type(key), key)
        if key == 'date':
            print('here')
            cDate = request.form[key]
            db.child("Classes").child(cclass['category']).child(
                "Dates").child(request.form[key]).update({'confirmed': 0})
            db.child("Classes").child(cclass['category']).child(
                "Dates").child(request.form[key]).update({cclass['class_id']: request.form['signatureData']})
        elif key == 'signatureData':
            pass
        else:
            # spilt string
            id = key.split('^')
            print(id)
            db.child("Classes").child(cclass['category']).child("Dates").child(
                cDate).child("Absent").child(id[0]).child(id[1]).update({id[2]: 1})
    return "Success!"


@ app.route('/upload/homeroom', methods=['GET', 'POST'])
def upload_homeroom():
    if request.method == 'GET':
        return render_template('uploadcsv.html', title="Homeroom List", url="/upload/homeroom")
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
                    db.child("Homerooms").child(gradec).child(
                        classc).child(row['number']).set(row)
            # row['class'] row['number'] row['name'] row['eng_name']
            os.remove(filepath)
        except Exception as e:
            os.remove(filepath)
            return "Error. Please try again\n("+str(e)+")"
        return "Successfully uploaded " + gradec + "-" + classc


@ app.route('/upload/stud_in_group', methods=['GET', 'POST'])
def upload_stud_in_group():
    if request.method == 'GET':
        return render_template('uploadcsv.html', title="Student in Group List", url="/upload/stud_in_group")
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
                for row in csv_dict:
                    for h in headers:
                        db.child("Homerooms").child(gradec).child(classc).child(
                            row['number']).child("Classes").child(h).set(row[h])
                        db.child("Classes").child(h).child("Class").child(row[h]).child(
                            "Students").child(gradec).child(classc).update({str(row['number']): 0})

            os.remove(filepath)
        except Exception as e:
            os.remove(filepath)
            return "Error. Please try again\n("+str(e)+")"
        return "Successfully uploaded " + gradec + "-" + classc


# @ app.route('/upload/rm_all_data_of_class', methods=['GET', "POST"])
# def rm_all_data_of_class():
#     if request.method == 'GET':
#         return render_template('uploadcsv.html', title="Remove all data of class", url="/upload/rm_all_data_of_class")
#     elif request.method == 'POST':
#         try:
#             classc = request.form['classcode']
#             db.child("Homerooms").child(classc).remove()
#         except Exception as e:
#             return "Error. Please try again\n("+str(e)+")"
#         return "Successfully removed " + classc


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
