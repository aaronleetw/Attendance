from flask import *
import pyrebase
from datetime import datetime
import pytz
import csv
import os
import pandas as pd
import base64
from random import randint
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
storage = firebase.storage()
tz = pytz.timezone('Asia/Taipei')


def check_login_status():
    return ('is_logged_in' not in session or
            session['is_logged_in'] == False or
            (datetime.now(tz) - session['loginTime']).total_seconds() > 3600)


def manageProcess(fCommand, fData):
    if (check_login_status()):
        return redirect('/logout')
    # this is to fix a bug where pyrebase doesnt load the first request
    db.child("Users").child(
        session['uid']).child("permission").get().val()
    # end bug fix
    pl = db.child("Users").child(
        session['uid']).child("permission").get().val()
    if pl == 'admin':
        homerooms = db.child("Homerooms").get().val()
        currRoom = []
        if fCommand == "admin":
            currRoom = fData[0].split("^")
        else:
            for i in homerooms:
                currRoom.append(i)
                for j in homerooms[i]:
                    currRoom.append(j)
                    break
                break
        homeroomData = homerooms[currRoom[0]][currRoom[1]]
        absData = homeroomData["Absent"]
        homeroomData.pop('Absent')
        homeroomData.pop('placeholder')
        currDate = ""
        if fCommand != "":
            currDate = fData[1]
        else:
            for i in absData:
                currDate = i
                if i >= datetime.now(tz).strftime("%Y-%m-%d"):
                    break
        return render_template('admin.html', homerooms=homerooms, absData=absData, homeroomCode=currRoom, homeroomData=homeroomData, currDate=currDate, periods=['m', '1', '2', '3', '4', 'n', '5', '6', '7', '8', '9'])
    elif pl == 'group':
        classes = db.child("Users").child(
            session['uid']).child("class").get().val()
        cclass = {}
        cateData = {}
        for i in classes:
            cateData = db.child("Classes").child(
                "GP_Class").child(i).get().val()
            cclass = {
                "name": cateData['Class'][classes[i]]['name'],
                "teacher": cateData['Class'][classes[i]]['teacher'],
                "classroom": cateData['Class'][classes[i]]['classroom'],
                "category": i,
                "class_id": classes[i]
            }
        print("got class")
        homerooms = cateData['Homerooms']
        currDate = ""
        confirmed = []
        absData = {}
        for h in homerooms:
            h = h.split('^')
            print(h)
            hrData = db.child("Homerooms").child(h[0]).child(h[1]).get().val()
            tmpAbsData = hrData['Absent']
            hrData.pop('Absent')
            hrData.pop('placeholder')
            periods = []
            dow = ""
            if currDate == "":
                if fCommand == 'date':
                    currDate = fData
                    for j in tmpAbsData[currDate]:
                        if j == "dow":
                            dow = tmpAbsData[currDate][j]
                            continue
                        elif j == "confirm":
                            confirmed.append([h[0], h[1]])
                            continue
                        if (tmpAbsData[currDate][j]['name'] == 'GP' and
                                tmpAbsData[currDate][j]['teacher'] == cclass['category']):
                            periods.append(j)

                else:
                    for i in tmpAbsData:
                        currDate = i
                        if i >= datetime.now(tz).strftime("%Y-%m-%d"):
                            tmp = False
                            for j in tmpAbsData[i]:
                                if j == "dow":
                                    dow = tmpAbsData[i][j]
                                    continue
                                elif j == "confirm":
                                    confirmed.append([h[0], h[1]])
                                    continue
                                if (tmpAbsData[i][j]['name'] == 'GP' and
                                        tmpAbsData[i][j]['teacher'] == cclass['category']):
                                    periods.append(j)
                                    tmp = True
                            if tmp == True:
                                break
            else:
                for j in tmpAbsData[currDate]:
                    if j == "dow":
                        dow = tmpAbsData[currDate][j]
                        continue
                    elif j == "confirm":
                        confirmed.append([h[0], h[1]])
                        continue
                    if (tmpAbsData[currDate][j]['name'] == 'GP' and
                            tmpAbsData[currDate][j]['teacher'] == cclass['category']):
                        periods.append(j)
            for p in periods:
                if not p in absData:
                    absData[p] = {}
            for p in periods:
                if not h[0] in absData[p]:
                    absData[p][h[0]] = {}
                absData[p][h[0]][h[1]] = {}
            for num in hrData:
                if (cclass['category'] in hrData[num]['GP_Class'] and
                        hrData[num]['GP_Class'][cclass['category']] == cclass['class_id']):
                    for p in periods:
                        absData[p][h[0]][h[1]][num] = {
                            "name": hrData[num]['name'],
                            "eng_name": hrData[num]['eng_name'],
                            "alr_fill": ('signature' in tmpAbsData[currDate][p] and
                                         cclass['class_id'] in tmpAbsData[currDate][p]['signature']),
                            "absent": num in tmpAbsData[currDate][p]
                        }
            print(absData)
        return render_template('group_teach.html', cclass=cclass, absData=absData, dow=dow, currDate=currDate, tmpAbsData=tmpAbsData, confirmed=confirmed)
    elif pl == 'homeroom':
        homeroom = db.child("Users").child(
            session['uid']).child("homeroom").get().val().split('^')
        homeroomData = db.child("Homerooms").child(homeroom[0]).child(
            homeroom[1]).get().val()
        absData = homeroomData["Absent"]
        homeroomData.pop('Absent')
        homeroomData.pop('placeholder')
        currDate = ""
        if fCommand == 'date':
            currDate = fData
        else:
            for i in absData:
                currDate = i
                if i >= datetime.now(tz).strftime("%Y-%m-%d"):
                    break
        return render_template('homeroom.html', absData=absData, homeroomCode=homeroom, homeroomData=homeroomData, currDate=currDate, periods=['m', '1', '2', '3', '4', 'n', '5', '6', '7', '8', '9'])
    else:
        return redirect('/logout')


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


@ app.route('/manage', methods=['GET'])
def manage():
    return manageProcess("", "")


@ app.route('/manage/date', methods=['POST'])
def manage_date():
    return manageProcess("date", request.form['date'])


@app.route('/manage/admin', methods=['POST'])
def manage_admin():
    data = [
        request.form['grade'] + '^' + request.form['room'],
        request.form['date']
    ]
    return manageProcess("admin", data)


@ app.route('/manage/group_teach_publish', methods=['POST'])
def group_teach_publish():
    if (check_login_status()):
        return redirect('/logout')
    classes = db.child("Users").child(
        session['uid']).child("class").get().val()
    cclass = {}
    for i in classes:
        cclass = {
            "name": db.child("Classes").child(i).child(
                "Class").child(classes[i]).child("name").get().val(),
            "category": i,
            "class_id": classes[i],
            "homerooms": db.child("Classes").child(
                "GP_Class").child(i).child("Homerooms").get().val()
        }
    print("got class")
    date = request.form['date']
    period = request.form['period']
    signature = request.form['signatureData']
    signature = signature.removeprefix('data:image/png;base64,')
    signature = bytes(signature, 'utf-8')
    rand = str(randint(100000000000000, 999999999999999))
    rand += ".png"
    with open(os.path.join('temp', rand), "wb") as fh:
        fh.write(base64.decodebytes(signature))
    storage.child(os.path.join('signatures', rand)
                  ).put(os.path.join('temp', rand))

    formData = request.form.to_dict()
    formData.pop('signatureData')
    formData.pop('date')
    formData.pop('period')
    for i in formData:
        i = i.split('^')
        db.child("Homerooms").child(i[0]).child(i[1]).child(
            "Absent").child(date).child(period).update({i[2]: 0})
    for h in cclass['homerooms']:
        h = h.split('^')
        db.child("Homerooms").child(h[0]).child(h[1]).child(
            "Absent").child(date).child(period).child("signature").update({cclass['class_id']: str(storage.child(os.path.join('signatures', rand)).get_url(None))})
    os.remove(os.path.join('temp', rand))
    return redirect('/manage')


@ app.route('/manage/homeroom_abs', methods=['POST'])
def homeroom_abs_publish():
    if (check_login_status()):
        return redirect('/logout')

    date = request.form['date']
    homeroom = request.form['homeroom'].split('^')
    period = request.form['period']
    signature = request.form['signatureData']
    signature = signature.removeprefix('data:image/png;base64,')
    signature = bytes(signature, 'utf-8')
    rand = str(randint(100000000000000, 999999999999999))
    rand += ".png"
    with open(os.path.join('temp', rand), "wb") as fh:
        fh.write(base64.decodebytes(signature))
    storage.child(os.path.join('signatures', rand)
                  ).put(os.path.join('temp', rand))
    formData = request.form.to_dict()
    formData.pop('signatureData')
    formData.pop('date')
    formData.pop('homeroom')
    formData.pop('period')
    for i in formData:
        db.child("Homerooms").child(homeroom[0]).child(
            homeroom[1]).child("Absent").child(date).child(period).update({i: 0})
    db.child("Homerooms").child(homeroom[0]).child(homeroom[1]).child(
        "Absent").child(date).child(period).update({'signature': str(storage.child(os.path.join('signatures', rand)).get_url(None))})
    os.remove(os.path.join('temp', rand))
    return redirect('/manage')


@app.route('/manage/homeroom_confirm', methods=['POST'])
def homeroom_confirm():
    if (check_login_status()):
        return redirect('/logout')
    date = request.form['date']
    homeroom = request.form['homeroom'].split('^')
    signature = request.form['signatureData']
    signature = signature.removeprefix('data:image/png;base64,')
    signature = bytes(signature, 'utf-8')
    rand = str(randint(100000000000000, 999999999999999))
    rand += ".png"
    with open(os.path.join('temp', rand), "wb") as fh:
        fh.write(base64.decodebytes(signature))
    storage.child(os.path.join('signatures', rand)
                  ).put(os.path.join('temp', rand))
    db.child("Homerooms").child(homeroom[0]).child(homeroom[1]).child("Absent").child(date).update(
        {"confirm": str(storage.child(os.path.join('signatures', rand)).get_url(None))})
    os.remove(os.path.join('temp', rand))
    return redirect('/manage')


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


@ app.route('/upload/gp_classes', methods=['GET', 'POST'])
def upload_gp_classes():
    if request.method == 'GET':
        return render_template('uploadcsv.html', title="Group Classes", url="/upload/gp_classes")
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
                    if j % 4 == 0:
                        db.child("Classes").child("GP_Class").child(csv_dict.columns[i+1]).child("Class").child(
                            tmp_csv[j]).child("name").set(tmp_csv[j+1])
                        db.child("Classes").child("GP_Class").child(csv_dict.columns[i+1]).child("Class").child(
                            tmp_csv[j]).child("teacher").set(tmp_csv[j+2])
                        db.child("Classes").child("GP_Class").child(csv_dict.columns[i+1]).child("Class").child(
                            tmp_csv[j]).child("classroom").set(tmp_csv[j+3])
            os.remove(filepath)
        except Exception as e:
            os.remove(filepath)
            return "Error. Please try again\n("+str(e)+")"
        return "Successfully uploaded"


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
                for h in headers:
                    db.child("Classes").child("GP_Class").child(
                        h).child("Homerooms").update({gradec+'^'+classc: 0})
                for row in csv_dict:
                    for h in headers:
                        db.child("Homerooms").child(gradec).child(classc).child(
                            row['number']).child("GP_Class").update({h: row[h]})
            os.remove(filepath)
        except Exception as e:
            os.remove(filepath)
            return "Error. Please try again\n("+str(e)+")"
        return "Successfully uploaded " + gradec + "-" + classc


@ app.route('/upload/period_list', methods=['GET', 'POST'])
def upload_period_list():
    if request.method == 'GET':
        return render_template('uploadcsv.html', title="Period List", url="/upload/period_list")
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
                print(tmp_csv)
                for j in range(len(tmp_csv)):
                    if not (periodCodes[j].endswith('-t')):
                        if type(tmp_csv[j]) == float:
                            db.child("Classes").child("Homeroom").child(gradec).child(classc).child(
                                str(i+1)).child(periodCodes[j]).update({'name': '--'})
                        else:
                            db.child("Classes").child("Homeroom").child(gradec).child(classc).child(
                                str(i+1)).child(periodCodes[j]).update({'name': tmp_csv[j]})
                            if not(periodCodes[j] == 'm' or periodCodes[j] == 'n'):
                                j += 1
                                db.child("Classes").child("Homeroom").child(gradec).child(classc).child(
                                    str(i+1)).child(periodCodes[j-1]).update({'teacher': tmp_csv[j]})
            os.remove(filepath)
        except Exception as e:
            os.remove(filepath)
            return "Error. Please try again\n("+str(e)+")"
        return "Successfully uploaded " + gradec + "-" + classc


@ app.route('/upload/dates', methods=['GET', 'POST'])
def upload_dates():
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
                temp = db.child("Homerooms").get().val()
                for row in csv_dict:
                    for h in headers:
                        for t in temp:
                            for i in temp[t]:
                                periodData = db.child("Classes").child(
                                    "Homeroom").child(t).child(i).get().val()
                                print(type(t), t)
                                print(type(i), i)
                                db.child("Homerooms").child(t).child(i).child(
                                    "Absent").child(h).update({"dow": row[h]})
                                db.child("Homerooms").child(t).child(i).child(
                                    "Absent").child(h).update(
                                    periodData[int(row[h])]
                                )
            os.remove(filepath)
        except Exception as e:
            os.remove(filepath)
            return "Error. Please try again\n("+str(e)+")"
        return "Successfully uploaded dates"


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


@ app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
