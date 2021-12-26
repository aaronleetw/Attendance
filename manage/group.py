from functions import *
group = Blueprint('group', __name__)

@group.route('/manage/group_teach_publish', methods=['POST'])
def group_teach_publish():
    if (check_login_status()):
        return redirect('/logout')
    refresh_token()
    data = request.form.to_dict()
    cclass = {
        "category": data.pop('category'),
        "class_id": data.pop('class_id')
    }
    db = refresh_db()
    cursor = db.cursor()
    cursor.execute("SELECT about FROM gpclasses WHERE category=%s AND subclass=%s", 
                    (cclass['category'], cclass['class_id']))
    cclass["name"] = cursor.fetchone()[0]
    cursor.execute("SELECT grade,class_,num,name,ename FROM students WHERE classes LIKE " + '\'%\"'+ cclass['category'] + '\": \"' + cclass['class_id'] +'\"%\'' + " ORDER BY grade ASC,class_ ASC,num ASC")
    students = cursor.fetchall()
    homerooms = []
    for x in students:
        if (str(x[0]) + '^' + str(x[1])) not in homerooms:
            homerooms.append(str(x[0]) + '^' + str(x[1]))
    data.pop('dsnumbers')
    data.pop('dsoffense')
    data.pop('dsoffenseother')
    date = data.pop('date')
    period = data.pop('period')
    signature = data.pop('signatureData')
    notes = data.pop('notes')
    submissionType = data.pop('submissionType')
    if (submissionType == 'newAbsent'):
        absentData = []
        for x in data:
            xs = x.split('^')
            if xs[0] == 'note':
                continue
            else:
                absentData.append([xs[1], xs[2], xs[3], 'K' if xs[0] == '1' else 'L', data['note^'+xs[1]+'^'+xs[2]+'^'+xs[3]]])
        for h in homerooms:
            h = h.split('^')
            cursor = db.cursor()
            cursor.execute("""
                SELECT signature, notes FROM submission WHERE grade=%s AND class_=%s AND date=%s AND period=%s
            """, (h[0], h[1], date, period))
            one = cursor.fetchone()
            if one is None:
                jSignature = json.dumps({cclass['class_id']: signature})
                cursor.execute("""
                    INSERT INTO submission (grade, class_, date, period, signature, notes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (h[0], h[1], date, period, jSignature, notes))
                db.commit()
            else:
                jSignature = json.loads(one[0])
                if cclass['class_id'] in jSignature:
                    continue
                jSignature[cclass['class_id']] = signature
                note = one[1] + '; ' + notes
                cursor.execute("""
                    UPDATE submission SET signature=%s, notes=%s WHERE grade=%s AND class_=%s AND date=%s AND period=%s
                """, (json.dumps(jSignature), note, h[0], h[1], date, period))
                db.commit()
        for a in absentData:
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO absent (grade, class_, num, date, period, status, note)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (a[0], a[1], a[2], date, period, a[3], a[4]))
            db.commit()
    elif (submissionType == 'dsSubmit'):
        dsData = []
        for x in data:
            xs = x.split('^')
            if xs[0] == 'note':
                continue
            elif xs[0] == 'ds':
                dsData.append([xs[1], xs[2].split('-')[0], xs[2].split('-')[1], data[x]])
        for h in homerooms:
            h = h.split('^')
            cursor = db.cursor()
            cursor.execute("""
                SELECT dscfrm, notes FROM submission WHERE grade=%s AND class_=%s AND date=%s AND period=%s
            """, (h[0], h[1], date, period))
            one = cursor.fetchone()
            dsCfrm = [] if one[0] == None else json.loads(one[0])
            if cclass['class_id'] in dsCfrm:
                continue
            dsCfrm.append(cclass['class_id'])
            note = one[1] + '; ' + notes
            cursor.execute("""
                UPDATE submission SET dsCfrm=%s, notes=%s WHERE grade=%s AND class_=%s AND date=%s AND period=%s
            """, (json.dumps(dsCfrm), note, h[0], h[1], date, period))
        for d in dsData:
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO ds (grade, class_, num, date, period, note)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (d[0], d[1], d[2], date, period, d[3]))
            db.commit()
    return redirect('/manage')