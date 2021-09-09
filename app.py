from flask import *
import pyrebase
from datetime import datetime
import pytz
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import csv
import os
# from dotenv import load_dotenv
# from pprint import pprint
# load_dotenv()
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
    pl = db.child("Users").child(
        session['uid']).child("permission").get().val()
    print(pl)
    s = str(pl)
    if pl == 'admin':
        return s
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
        all_stud_list = {}
        for homeroom in students:
            print(homeroom)
            all_stud_list[homeroom] = {}
            if type(students[homeroom]) == list:
                i = 0
                for student in students[homeroom]:
                    if student == 0:
                        # print(i)
                        # print(db.child("Homerooms").child(
                        # homeroom).child(i).child("name").get().val())
                        all_stud_list[homeroom][i] = {
                            "name": db.child("Homerooms").child(homeroom).child(i).child("name").get().val(),
                            "eng_name": db.child("Homerooms").child(homeroom).child(i).child("eng_name").get().val(),
                        }
                    i += 1
            else:
                for student in students[homeroom]:
                    all_stud_list[homeroom][student] = {
                        "name": db.child("Homerooms").child(homeroom).child(student).child("name").get().val(),
                        "eng_name": db.child("Homerooms").child(homeroom).child(student).child("eng_name").get().val(),
                    }

        print("got students")
        # for homeroom in all_stud_list:
        #     for student in all_stud_list[homeroom]:
        #         print("homeroom: ", homeroom)
        #         print("student: ", student)
        #         print("all_stud_list['homeroom']['student']['name']: ",
        #               all_stud_list['homeroom']['student']['name'])
        #         print("all_stud_list['homeroom']['student']['eng_name']: ",
        #               all_stud_list['homeroom']['student']['eng_name'])
        # get dates
        dates = db.child("Classes").child(
            cclass['category']).child("Dates").get().val()
        for i in dates:
            dates[i].pop('placeholder')
            if i >= datetime.now(tz).strftime("%Y-%m-%d"):
                currDate = i
                break
        print("got dates")
        return render_template('group_teach.html', cclass=cclass, all_stud_list=all_stud_list, dates=dates, currDate=currDate)
    elif pl == 'homeroom':
        homeroom = db.child("Users").child(
            session['uid']).child("homeroom").get().val()
        s += " " + homeroom  # 912
        return s
    else:
        return "no permission"


@ app.route('/upload/homeroom', methods=['GET', 'POST'])
def upload_homeroom():
    if request.method == 'GET':
        return render_template('uploadcsv.html', title="Homeroom List", url="/upload/homeroom")
    elif request.method == 'POST':
        try:
            # get csv
            classc = request.form['classcode']
            csv_file = request.files['csv']
            filepath = os.path.join('./temp', csv_file.filename)
            csv_file.save(filepath)
            with open(filepath) as file:
                csv_dict = csv.DictReader(file)
                for row in csv_dict:
                    db.child("Homerooms").child(
                        classc).child(row['number']).set(row)
            # row['class'] row['number'] row['name'] row['eng_name']
            os.remove(filepath)
        except Exception as e:
            os.remove(filepath)
            return "Error. Please try again\n("+str(e)+")"
        return "Successfully uploaded " + classc


@ app.route('/upload/stud_in_group', methods=['GET', 'POST'])
def upload_stud_in_group():
    if request.method == 'GET':
        return render_template('uploadcsv.html', title="Student in Group List", url="/upload/stud_in_group")
    elif request.method == 'POST':
        try:
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
                        db.child("Homerooms").child(classc).child(
                            row['number']).child("Classes").child(h).set(row[h])
                        db.child("Classes").child(h).child("Class").child(row[h]).child(
                            "Students").child(classc).update({str(row['number']): 0})

            os.remove(filepath)
        except Exception as e:
            os.remove(filepath)
            return "Error. Please try again\n("+str(e)+")"
        return "Successfully uploaded " + classc


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


# if __name__ == '__main__':
#     app.run(debug=True)
