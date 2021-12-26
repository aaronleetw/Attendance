from functions import *
from manage.homeroom import homeroom
from manage.student import student
from manage.admin import admin
from manage.group import group
manage = Blueprint('manage', __name__)
manage.register_blueprint(homeroom)
manage.register_blueprint(student)
manage.register_blueprint(admin)
manage.register_blueprint(group)

@manage.route('/manage', methods=['GET'])
def manageRoot():
    return manageProcess("", "")

@homeroom.route('/manage/date/<date>', methods=['GET'])
def manage_date(date):
    return manageProcess("date", date)

@manage.route('/manage/admin/<g>/<r>/<date>', methods=['GET'])
def manage_admin(g, r, date):
    data = [
        g + '^' + r,
        date
    ]
    return manageProcess("admin", data)


def manageProcess(fCommand, fData):
    if (check_login_status()):
        return redirect('/logout')
    refresh_token()
    if 'user_type' in session and session['user_type'] == 'student':
        return redirect('/student')
    pl = session['subuser_type']
    if pl == 'admin':
        db = refresh_db()
        cursor = db.cursor()
        cursor.execute("SELECT grade, class_ FROM homerooms ORDER BY grade ASC, class_ ASC")
        homeroomsSQL = cursor.fetchall()
        homerooms = {}
        for h in homeroomsSQL:
            if h[0] in homerooms:
                homerooms[h[0]].append(h[1])
            else:
                homerooms[h[0]] = [h[1]]
        currRoom = []
        if fCommand == "admin":
            currRoom = fData[0].split("^")
        else:
            currRoom = [homeroomsSQL[0][0], homeroomsSQL[0][1]]
        cursor = db.cursor()
        cursor.execute("SELECT num,name,ename,classes FROM students WHERE grade=%s AND class_=%s ORDER BY num ASC", (currRoom[0], currRoom[1]))
        students = cursor.fetchall()
        studGP = {}
        for s in students:
            studGP[s[0]] = json.loads(s[3])
        cursor = db.cursor()
        cursor.execute("SELECT date FROM dates ORDER BY date ASC")
        dates = cursor.fetchall()
        currDate = ""
        if fCommand != "":
            currDate = fData[1]
        else:
            for i in dates:
                currDate = i[0]
                if i[0] >= datetime.now(tz).strftime("%Y-%m-%d"):
                    break
        cursor = db.cursor()
        cursor.execute("SELECT dow FROM dates WHERE date=%s", (currDate, ))
        dow = cursor.fetchone()[0]
        cursor = db.cursor()
        cursor.execute("SELECT period, subject, teacher FROM schedule WHERE grade=%s AND class_=%s AND dow=%s", (currRoom[0], currRoom[1], dow))
        scheduleSQL = cursor.fetchall()
        schedule = {}
        for i in scheduleSQL:
            schedule[i[0]] = {
                "subject": i[1],
                "teacher": i[2],
            }
        cursor = db.cursor()
        cursor.execute("SELECT period, subject, teacher FROM specschedule WHERE grade=%s AND class_=%s AND date=%s", (currRoom[0], currRoom[1], currDate))
        specScheduleSQL = cursor.fetchall()
        for i in specScheduleSQL:
            schedule[i[0]] = {
                "subject": i[1],
                "teacher": i[2],
                "special": True
            }
        cursor = db.cursor()
        cursor.execute("SELECT period, signature, notes, ds1,ds2,ds3,ds4,ds5,ds6,ds7 FROM submission WHERE grade=%s AND class_=%s AND date=%s", (currRoom[0], currRoom[1], currDate))
        submissionSQL = cursor.fetchall()
        submission = {}
        cursor = db.cursor()
        cursor.execute("SELECT period, num, note FROM ds WHERE grade=%s AND class_=%s AND date=%s", (currRoom[0], currRoom[1], currDate))
        idvDSSQL = cursor.fetchall()
        idvDS = {}
        for i in idvDSSQL:
            if i[0] not in idvDS:
                idvDS[i[0]] = {}
            idvDS[i[0]][i[1]]= i[2]
        for i in submissionSQL:
            if i[0] == 'c':
                submission[i[0]] = {
                    "signature": i[1],
                    "notes": i[2]
                }
            elif schedule[i[0]]["subject"] == "GP":
                submission[i[0]] = OrderedDict()
                signatures = json.loads(i[1])
                for j in signatures:
                    submission[i[0]][j] = {
                        "signature": signatures[j],
                    }
                submission[i[0]]["notes"] = i[2]
            else:
                submission[i[0]] = {
                    "signature": i[1],
                    "notes": i[2],
                    "ds1": i[3],
                    "ds2": i[4],
                    "ds3": i[5],
                    "ds4": i[6],
                    "ds5": i[7],
                    "ds6": i[8],
                    "ds7": i[9]
                }
        cursor = db.cursor()
        cursor.execute("SELECT period, num, status, note FROM absent WHERE grade=%s AND class_=%s AND date=%s", (currRoom[0], currRoom[1], currDate))
        absentDataSQL = cursor.fetchall()
        absentData = {}
        for p in ['m', '1', '2', '3', '4', 'n', '5', '6', '7', '8', '9']:
            absentData[p] = {}
        for i in absentDataSQL:
            absentData[i[0]][i[1]] = i[2]
        for i in absentDataSQL:
            absentData[i[0]][i[1]] = {
                'status': i[2],
                'note': i[3],
            }
        return render_template('admin.html', homerooms=homerooms, currRoom=currRoom, students=students, currDate=currDate, schedule=schedule, submission=submission, studGP=studGP, idvDS=idvDS,
                                dates=dates, absentData=absentData, periods=['m', '1', '2', '3', '4', 'n', '5', '6', '7', '8', '9'], showUpload=session['showUpload'], dsboard=DSBOARD, dstext=DSTEXT, dsoffenses=DSOFFENSES)
                                                                                                            #  'n', '5', '6', '7', '8', '9'], showUpload=session['showUpload'])
    elif pl == 'group':
        db = refresh_db()
        cursor = db.cursor()
        cursor.execute("SELECT category, subclass FROM gpclasses WHERE accs LIKE %s", ('%'+session['oldUsername']+'%',))
        gpclasses = cursor.fetchall()
        data = {}
        currDate = ""
        dow = ""
        cursor = db.cursor()
        cursor.execute("SELECT date FROM dates ORDER BY date ASC")
        dates = cursor.fetchall()
        if fCommand != "":
            currDate = fData
        else:
            for i in dates:
                currDate = i[0]
                if i[0] >= datetime.now(tz).strftime("%Y-%m-%d"):
                    break
        cursor = db.cursor()
        cursor.execute("SELECT dow FROM dates WHERE date=%s", (currDate, ))
        dow = cursor.fetchone()[0]

        for c in gpclasses:
            cursor.execute("SELECT about FROM gpclasses WHERE subclass=%s AND category=%s", 
                            (c[1], c[0]))
            cclass = {
                "name": cursor.fetchone()[0],
                "category": c[0],
                "class_id": c[1]
            }
            data[cclass['category'] + ' ' + cclass['class_id']] = {
                "cdata": cclass,
            }
            # get student list
            cursor.execute("SELECT grade,class_,num,name,ename FROM students WHERE classes LIKE " + '\'%\"'+ cclass['category'] + '\": \"' + cclass['class_id'] +'\"%\'' + " ORDER BY grade ASC,class_ ASC,num ASC")
            students = cursor.fetchall()
            # get student homerooms
            homerooms = []
            for x in students:
                if (str(x[0]) + '^' + str(x[1])) not in homerooms:
                    homerooms.append(str(x[0]) + '^' + str(x[1]))
            # get periods
            for h in homerooms:
                hs = h.split('^')
                cursor.execute("SELECT period FROM schedule WHERE grade=%s AND class_=%s AND dow=%s AND teacher=%s", (hs[0], hs[1], dow, cclass['category']))
                scheduleSQL = cursor.fetchall()
                cursor.execute("SELECT period FROM specschedule WHERE grade=%s AND class_=%s AND date=%s AND teacher=%s", (hs[0], hs[1], currDate, cclass['category']))
                specNTPSQL = cursor.fetchall()
                for s in specNTPSQL:
                    scheduleSQL.append(s)
                cursor.execute("SELECT period FROM specschedule WHERE grade=%s AND class_=%s AND date=%s AND teacher!=%s", (hs[0], hs[1], currDate, cclass['category']))
                specNTDSQL = cursor.fetchall()
                specNTD = {}
                for i in specNTDSQL:
                    specNTD[i[0]] = True
                print(h, specNTD, scheduleSQL)
                for p in scheduleSQL:
                    if p[0] in specNTD and specNTD[p[0]] == True:
                        continue
                    if p[0] not in data[cclass['category'] + ' ' + cclass['class_id']]:
                        data[cclass['category'] + ' ' + cclass['class_id']][p[0]] = {}
                    if (h not in data[cclass['category'] + ' ' + cclass['class_id']][p[0]]):
                        data[cclass['category'] + ' ' + cclass['class_id']][p[0]][h] = {}
                    cursor = db.cursor()
                    cursor.execute("SELECT signature, dscfrm FROM submission WHERE grade=%s AND class_=%s AND date=%s AND period=%s", (hs[0], hs[1], currDate, p[0]))
                    submissionSQL = cursor.fetchone()
                    submitted = False
                    try:
                        signatures = json.loads(submissionSQL[0])
                        if cclass['class_id'] in signatures:
                            submitted = True
                    except:
                        pass
                    hrCfrm = False
                    if not submitted:
                        cursor = db.cursor()
                        cursor.execute("SELECT signature FROM submission WHERE grade=%s AND class_=%s AND date=%s AND period='c'", (hs[0], hs[1], currDate))
                        hrCfrm = True if cursor.fetchone() != None else submitted
                    cursor = db.cursor()
                    cursor.execute("SELECT num, status, note FROM absent WHERE grade=%s AND class_=%s AND date=%s AND period=%s", (hs[0], hs[1], currDate, p[0]))
                    absentDataSQL = cursor.fetchall()
                    for x in students:
                        if (str(x[0])==hs[0] and str(x[1])==hs[1]):
                            studStatus = [item for item in absentDataSQL if item[0] == x[2]]
                            status = ""
                            if submitted:
                                if studStatus == []:
                                    status = 'present'
                                else:
                                    status = studStatus[0][1]
                            else:
                                if studStatus == []:
                                    if hrCfrm:
                                        status = '--'
                                    else:
                                        status = 'na'
                                else:
                                    status = studStatus[0][1]
                            data[cclass['category'] + ' ' + cclass['class_id']][p[0]][h][x[2]] = {
                                "name": x[3],
                                "ename": x[4],
                                "status": status,
                                "note": '' if studStatus == [] else studStatus[0][2],
                                "needDS": False if hrCfrm != True and submissionSQL[1] != None and cclass['class_id'] in json.loads(submissionSQL[1]) else True
                            }
            return render_template('group_teach.html', dates=dates, currDate=currDate, data=data, dsoffenses=DSOFFENSES)
    elif pl == 'homeroom':
        db = refresh_db()
        times = OrderedDict({
            'm': '00:00',
            '1': '08:15',
            '2': '09:10',
            '3': '10:05',
            '4': '11:00',
            'n': '11:55',
            '5': '13:10',
            '6': '14:05',
            '7': '15:00',
            '8': '15:53',
            '9': '16:43',
            'ph': '23:59'
        })
        currPeriod = ""
        currTime = datetime.now(tz).strftime("%H:%M")
        for i in times:
            if (times[i] <= currTime and
                    currTime <= times[next_item(times, i)]):
                currPeriod = i
                break
        currRoom = session['homeroom'].split('^')
        cursor = db.cursor()
        cursor.execute("SELECT num,name,ename,classes FROM students WHERE grade=%s AND class_=%s ORDER BY num ASC", (currRoom[0], currRoom[1]))
        students = cursor.fetchall()
        studGP = {}
        for s in students:
            studGP[s[0]] = json.loads(s[3])
        cursor = db.cursor()
        cursor.execute("SELECT date FROM dates ORDER BY date ASC")
        dates = cursor.fetchall()
        currDate = ""
        if fCommand != "":
            currDate = fData
        else:
            for i in dates:
                currDate = i[0]
                if i[0] >= datetime.now(tz).strftime("%Y-%m-%d"):
                    break
        cursor = db.cursor()
        cursor.execute("SELECT dow FROM dates WHERE date=%s", (currDate, ))
        dow = cursor.fetchone()[0]
        cursor = db.cursor()
        cursor.execute("SELECT period, subject, teacher FROM schedule WHERE grade=%s AND class_=%s AND dow=%s", (currRoom[0], currRoom[1], dow))
        scheduleSQL = cursor.fetchall()
        schedule = {}
        for i in scheduleSQL:
            schedule[i[0]] = {
                "subject": i[1],
                "teacher": i[2],
            }
        cursor = db.cursor()
        cursor.execute("SELECT period, subject, teacher FROM specschedule WHERE grade=%s AND class_=%s AND date=%s", (currRoom[0], currRoom[1], currDate))
        specScheduleSQL = cursor.fetchall()
        for i in specScheduleSQL:
            schedule[i[0]] = {
                "subject": i[1],
                "teacher": i[2],
                "special": True
            }
        cursor = db.cursor()
        cursor.execute("SELECT period, signature, notes, ds1,ds2,ds3,ds4,ds5,ds6,ds7, dscfrm FROM submission WHERE grade=%s AND class_=%s AND date=%s", (currRoom[0], currRoom[1], currDate))
        submissionSQL = cursor.fetchall()
        cursor = db.cursor()
        cursor.execute("SELECT period, num, note FROM ds WHERE grade=%s AND class_=%s AND date=%s", (currRoom[0], currRoom[1], currDate))
        idvDSSQL = cursor.fetchall()
        idvDS = {}
        for i in idvDSSQL:
            if i[0] not in idvDS:
                idvDS[i[0]] = {}
            idvDS[i[0]][i[1]]= i[2]
        submission = {}
        for i in submissionSQL:
            if i[0] == 'c':
                submission[i[0]] = {
                    "signature": i[1],
                    "notes": i[2]
                }
            elif schedule[i[0]]["subject"] == "GP":
                submission[i[0]] = OrderedDict()
                signatures = json.loads(i[1])
                for j in signatures:
                    submission[i[0]][j] = {
                        "signature": signatures[j],
                    }
                submission[i[0]]["notes"] = i[2]
            else:
                submission[i[0]] = {
                    "signature": i[1],
                    "notes": i[2],
                    "ds1": i[3],
                    "ds2": i[4],
                    "ds3": i[5],
                    "ds4": i[6],
                    "ds5": i[7],
                    "ds6": i[8],
                    "ds7": i[9],
                }
                if i[10] == 'yes':
                    submission[i[0]]["dscfrm"] = True
        cursor = db.cursor()
        cursor.execute("SELECT period, num, status, note FROM absent WHERE grade=%s AND class_=%s AND date=%s", (currRoom[0], currRoom[1], currDate))
        absentDataSQL = cursor.fetchall()
        absentData = {}
        for p in ['m', '1', '2', '3', '4', 'n', '5', '6', '7', '8', '9']:
            absentData[p] = {}
        for i in absentDataSQL:
            absentData[i[0]][i[1]] = {
                'status': i[2],
                'note': i[3],
            }
        return render_template('homeroom.html', currRoom=currRoom, students=students, currDate=currDate, schedule=schedule, submission=submission, currPeriod=currPeriod, studGP=studGP,
                                dates=dates, absentData=absentData, periods=['m', '1', '2', '3', '4', 'n', '5', '6', '7', '8', '9'], dsboard=DSBOARD, dstext=DSTEXT, dsoffenses=DSOFFENSES, idvDS=idvDS)
    else:
        return redirect('/logout')