from functions import *
homeroom = Blueprint('homeroom', __name__)

@homeroom.route('/manage/abs', methods=['GET'])
def showAllAbs():
    if (check_login_status()):
        return redirect('/logout')
    refresh_token()
    currRoom = session['homeroom'].split('^')
    db = refresh_db()
    cursor = db.cursor()
    cursor.execute("SELECT num,name,ename FROM students WHERE grade=%s AND class_=%s ORDER BY num ASC", (currRoom[0], currRoom[1]))
    studentsSQL = cursor.fetchall()
    students = {}
    for st in studentsSQL:
        students[st[0]] = {
            'name': st[1],
            'ename': st[2],
        }
    cursor = db.cursor()
    cursor.execute("SELECT date, period, num, status, note FROM absent WHERE grade=%s AND class_=%s ORDER BY date DESC, FIND_IN_SET(period, 'm,1,2,3,4,n,5,6,7,8,9') DESC, num ASC", (currRoom[0], currRoom[1]))
    absentDataSQL = cursor.fetchall()
    return render_template("list.html", title="Absent List | 缺勤紀錄", mode='ABS', students=students, data=absentDataSQL, currRoom=currRoom)

@homeroom.route('/manage/ds', methods=['GET'])
def showAllDS():
    if (check_login_status()):
        return redirect('/logout')
    refresh_token()
    currRoom = session['homeroom'].split('^')
    db = refresh_db()
    cursor = db.cursor()
    cursor.execute("SELECT num,name,ename FROM students WHERE grade=%s AND class_=%s ORDER BY num ASC", (currRoom[0], currRoom[1]))
    studentsSQL = cursor.fetchall()
    students = {}
    for st in studentsSQL:
        students[st[0]] = {
            'name': st[1],
            'ename': st[2],
        }
    cursor = db.cursor()
    cursor.execute("SELECT date, period, num, note FROM ds WHERE grade=%s AND class_=%s ORDER BY date DESC, FIND_IN_SET(period, 'm,1,2,3,4,n,5,6,7,8,9') DESC, num ASC", (currRoom[0], currRoom[1]))
    dsDataSQL = cursor.fetchall()
    return render_template("list.html", title="DS List | 定心紀錄", mode='DS', students=students, data=dsDataSQL, currRoom=currRoom)

@homeroom.route('/manage/homeroom_abs', methods=['POST'])
def homeroom_abs_publish():
    if (check_login_status()):
        return redirect('/logout')
    refresh_token()
    db = refresh_db()
    data = request.form.to_dict()
    date = data.pop('date')
    period = data.pop('period')
    signature = data.pop('signatureData')
    notes = data.pop('notes')
    homeroom = data.pop('homeroom').split('^')
    absentData = {}
    for x in data:
        xt = x.split('^')
        if (xt[0] == 'note'):
            if xt[2] not in absentData:
                absentData[xt[2]] = {}
            absentData[xt[2]]['note'] = data[x]
        else:
            if xt[1] not in absentData:
                absentData[xt[1]] = {}
            absentData[xt[1]]['status'] = 'L' if x[0] == '2' else 'K'
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO submission
        (grade, class_, date, period, signature, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (homeroom[0], homeroom[1], date, period, signature, notes))
    for x in absentData:
        cursor.execute("""
            INSERT INTO absent
            (grade, class_, date, period, num, status, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (homeroom[0], homeroom[1], date, period, x, absentData[x]['status'], absentData[x]['note'] if 'note' in absentData[x] else ''))
    db.commit()
    return redirect('/manage')

@homeroom.route('/manage/homeroom_ds', methods=['POST'])
def homeroom_ds_publish():
    if (check_login_status()):
        return redirect('/logout')
    refresh_token()
    db = refresh_db()
    cursor = db.cursor()
    data = request.form.to_dict()
    print(data)
    date = data.pop('date')
    period = data.pop('period')
    notes = ';' + data.pop('notes')
    homeroom = data.pop('homeroom').split('^')
    dsidv = {}
    ds1 = data.pop('ds^1')
    ds2 = data.pop('ds^2')
    ds3 = data.pop('ds^3')
    ds4 = data.pop('ds^4')
    ds5 = data.pop('ds^5')
    ds6 = data.pop('ds^6')
    ds7 = data.pop('ds^7')
    cursor.execute("""
        UPDATE submission
        SET ds1=%s,ds2=%s,ds3=%s,ds4=%s,ds5=%s,ds6=%s,ds7=%s,notes=concat(ifnull(notes,""), %s),dscfrm='yes'
        WHERE grade=%s AND class_=%s AND date=%s AND period=%s
    """, (ds1, ds2, ds3, ds4, ds5, ds6, ds7, notes, homeroom[0], homeroom[1], date, period))
    for x in data:
        xt = x.split('^')
        if (xt[0] == 'dsidv'):
            dsidv[xt[1]] = data[x]
    for x in dsidv:
        cursor.execute("""
            INSERT INTO ds
            (grade, class_, date, period, num, note)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (homeroom[0], homeroom[1], date, period, x, dsidv[x]))
    db.commit()
    return redirect('/manage')

@homeroom.route('/manage/homeroom_confirm', methods=['POST'])
def homeroom_confirm():
    if (check_login_status()):
        return redirect('/logout')
    refresh_token()
    data = request.form.to_dict()
    homeroom = data.pop('homeroom').split('^')
    date = data.pop('date')
    signature = data.pop('signatureData')
    notes = data.pop('notes')
    db = refresh_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO submission
        (grade, class_, date, period, signature, notes)
        VALUES (%s, %s, %s, 'c', %s, %s)
    """, (homeroom[0], homeroom[1], date, signature, notes))
    db.commit()
    return redirect('/manage')
