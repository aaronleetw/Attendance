from functions import *

manage = Blueprint('manage', __name__)


def manageProcess(fCommand, fData):
    if (check_login_status()):
        return redirect('/logout')
    # this is to fix a bug where pyrebase doesnt load the first request
    db.child("Users").child(
        session['uid']).child("permission").get(session['token']).val()
    # end bug fix
    refresh_token()
    pl = session['subuser_type']
    if pl == 'admin':
        homerooms = db.child("Homerooms").get(session['token']).val()
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
        if 'placeholder' in homeroomData:
            homeroomData.pop('placeholder')
        currDate = ""
        if fCommand != "":
            currDate = fData[1]
        else:
            for i in absData:
                currDate = i
                if i >= datetime.now(tz).strftime("%Y-%m-%d"):
                    break
        return render_template('admin.html', homerooms=homerooms, absData=absData,
                               homeroomCode=currRoom, homeroomData=homeroomData, currDate=currDate, periods=['m', '1', '2', '3', '4',
                                                                                                             'n', '5', '6', '7', '8', '9'], showUpload=session['showUpload'])
    elif pl == 'group':
        cateData = db.child("Classes").child(
            "GP_Class").child(session['category']).get(session['token']).val()
        cclass = {
            "name": cateData['Class'][session['class']]['name'],
            "category": session['category'],
            "class_id": session['class']
        }
        homerooms = cateData['Homerooms']
        currDate = ""
        confirmed = []
        absData = {}
        for h in homerooms:
            h = h.split('^')
            hrData = db.child("Homerooms").child(
                h[0]).child(h[1]).get(session['token']).val()
            tmpAbsData = hrData['Absent']
            hrData.pop('Absent')
            if 'placeholder' in hrData:
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
                        elif j == "notes":
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
                                elif j == 'notes':
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
                    elif j == "notes":
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
                if 'notes' in tmpAbsData[currDate][p]:
                    absData[p][h[0]][h[1]
                                     ]['notes'] = tmpAbsData[currDate][p]['notes']
            for num in hrData:
                if (cclass['category'] in hrData[num]['GP_Class'] and
                        hrData[num]['GP_Class'][cclass['category']] == cclass['class_id']):
                    for p in periods:
                        absData[p][h[0]][h[1]][num] = {
                            "name": hrData[num]['name'],
                            "eng_name": hrData[num]['eng_name'],
                            "alr_fill": (('signature' in tmpAbsData[currDate][p]) and
                                         (cclass['class_id'] in tmpAbsData[currDate][p]['signature'] or 'STUD_AFFAIR_OFFICE' in tmpAbsData[currDate][p]['signature'])),
                            "absent": False if not num in tmpAbsData[currDate][p] else tmpAbsData[currDate][p][num]
                        }
        return render_template('group_teach.html', dateKeys=sorted(tmpAbsData.keys()), cclass=cclass, absData=absData, dow=dow, currDate=currDate, tmpAbsData=tmpAbsData, confirmed=confirmed)
    elif pl == 'homeroom':
        homeroom = session['homeroom'].split('^')
        homeroomData = db.child("Homerooms").child(homeroom[0]).child(
            homeroom[1]).get(session['token']).val()
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
        absData = homeroomData["Absent"]
        homeroomData.pop('Absent')
        if 'placeholder' in homeroomData:
            homeroomData.pop('placeholder')
        currDate = ""
        if fCommand == 'date':
            currDate = fData
        else:
            for i in absData:
                currDate = i
                if i >= datetime.now(tz).strftime("%Y-%m-%d"):
                    break
        return render_template('homeroom.html', absData=absData, homeroomCode=homeroom, homeroomData=homeroomData,
                               currDate=currDate, dateKeys=sorted(absData.keys()), periods=['m', '1', '2', '3', '4', 'n', '5', '6', '7', '8', '9'], currPeriod=currPeriod)
    else:
        return redirect('/logout')


@manage.route('/manage', methods=['GET'])
def manageRoot():
    return manageProcess("", "")


@manage.route('/manage/date/<date>', methods=['GET'])
def manage_date(date):
    return manageProcess("date", date)


@manage.route('/manage/admin/<g>/<r>/<date>', methods=['GET'])
def manage_admin(g, r, date):
    data = [
        g + '^' + r,
        date
    ]
    return manageProcess("admin", data)


@manage.route('/manage/group_teach_publish', methods=['POST'])
def group_teach_publish():
    if (check_login_status()):
        return redirect('/logout')
    refresh_token()
    cclass = {
        "name": db.child("Classes").child("GP_Class").child(session['category']).child(
            "Class").child(session['class']).child("name").get(session['token']).val(),
        "category": session['category'],
        "class_id": session['class'],
        "homerooms": db.child("Classes").child(
            "GP_Class").child(session['category']).child("Homerooms").get(session['token']).val()
    }
    date = request.form['date']
    period = request.form['period']
    signature = request.form['signatureData']
    formData = request.form.to_dict()
    notes = ""
    if 'notes' in request.form:
        notes = request.form['notes']
        formData.pop('notes')
    signature = removeprefix(signature, 'data:image/png;base64,')
    signature = bytes(signature, 'utf-8')
    rand = str(date + '^' + cclass['category'] +
               '^' + cclass['class_id'] + '^' + period)
    rand += ".png"
    with open(os.path.join('temp', rand), "wb") as fh:
        fh.write(base64.decodebytes(signature))
    storage.child(os.path.join('signatures', rand)
                  ).put(os.path.join('temp', rand), session['token'])
    formData.pop('signatureData')
    formData.pop('date')
    formData.pop('period')
    for i in formData:
        i = i.split('^')
        db.child("Homerooms").child(i[1]).child(i[2]).child(
            "Absent").child(date).child(period).update({i[3]: int(i[0])}, session['token'])
    for h in cclass['homerooms']:
        h = h.split('^')
        if "confirm" in db.child("Homerooms").child(h[0]).child(h[1]).child("Absent").child(date).get(session['token']).val():
            continue
        db.child("Homerooms").child(h[0]).child(h[1]).child(
            "Absent").child(date).child(period).child("signature").update({cclass['class_id']: str(storage.child(os.path.join('signatures', rand)).get_url(None))}, session['token'])
        db.child("Homerooms").child(h[0]).child(h[1]).child(
            "Absent").child(date).child(period).child("names").child(cclass['class_id']).set(cclass['name'], session['token'])
        currPeriodData = db.child("Homerooms").child(h[0]).child(h[1]).child(
            "Absent").child(date).child(period).get(session['token']).val()
        if 'notes' in currPeriodData:
            db.child("Homerooms").child(h[0]).child(h[1]).child(
                "Absent").child(date).child(period).update({'notes': currPeriodData['notes']+'; '+notes}, session['token'])
        else:
            db.child("Homerooms").child(h[0]).child(h[1]).child(
                "Absent").child(date).child(period).update({'notes': notes}, session['token'])
    os.remove(os.path.join('temp', rand))
    return redirect('/manage')


@manage.route('/manage/homeroom_abs', methods=['POST'])
def homeroom_abs_publish():
    if (check_login_status()):
        return redirect('/logout')
    refresh_token()
    date = request.form['date']
    homeroom = request.form['homeroom'].split('^')
    period = request.form['period']
    signature = request.form['signatureData']
    formData = request.form.to_dict()
    notes = ""
    if "confirm" in db.child("Homerooms").child(homeroom[0]).child(homeroom[1]).child("Absent").child(date).get(session['token']).val():
        return redirect('/manage')
    if 'notes' in request.form:
        notes = request.form['notes']
        formData.pop('notes')
    signature = removeprefix(signature, 'data:image/png;base64,')
    signature = bytes(signature, 'utf-8')
    rand = str(date + '^' + homeroom[0] + '^' + homeroom[1] + '^' + period)
    rand += ".png"
    with open(os.path.join('temp', rand), "wb") as fh:
        fh.write(base64.decodebytes(signature))
    storage.child(os.path.join('signatures', rand)
                  ).put(os.path.join('temp', rand), session['token'])
    formData.pop('signatureData')
    formData.pop('date')
    formData.pop('homeroom')
    formData.pop('period')
    formData.pop('stype')
    for i in formData:
        i = i.split('^')
        db.child("Homerooms").child(homeroom[0]).child(
            homeroom[1]).child("Absent").child(date).child(period).update({i[1]: int(i[0])}, session['token'])
    db.child("Homerooms").child(homeroom[0]).child(homeroom[1]).child(
        "Absent").child(date).child(period).update({'signature': str(storage.child(os.path.join('signatures', rand)).get_url(None))}, session['token'])
    db.child("Homerooms").child(homeroom[0]).child(homeroom[1]).child(
        "Absent").child(date).child(period).update({'notes': notes}, session['token'])
    os.remove(os.path.join('temp', rand))
    return redirect('/manage')


@manage.route('/manage/edit_abs', methods=['POST'])
def edit_abs():
    if (check_login_status() or not check_permission()):
        return redirect('/logout')
    refresh_token()
    date = request.form['date']
    homeroom = request.form['homeroom'].split('^')
    period = request.form['period']
    signature = "https://firebasestorage.googleapis.com/v0/b/attendance-be176.appspot.com/o/stud_affairs.png?alt=media"
    formData = request.form.to_dict()
    notes = ""
    oldData = list(db.child("Homerooms").child(homeroom[0]).child(homeroom[1]).child(
        "Absent").child(date).child(period).shallow().get(session['token']).val())
    for k in oldData:
        if k == 'name' or k == 'teacher':
            continue
        db.child("Homerooms").child(homeroom[0]).child(homeroom[1]).child(
            "Absent").child(date).child(period).child(k).remove(session['token'])
    cfrmstatus = db.child("Homerooms").child(homeroom[0]).child(
        homeroom[1]).child("Absent").child(date).get(session['token']).val()
    if "confirm" in cfrmstatus:
        db.child("Homerooms").child(homeroom[0]).child(homeroom[1]).child(
            "Absent").child(date).update({'notes': cfrmstatus['notes'] + '; (???????????????????????????)'}, session['token'])
    if 'notes' in request.form:
        notes = request.form['notes']
        formData.pop('notes')
    formData.pop('date')
    formData.pop('homeroom')
    formData.pop('period')
    for i in formData:
        i = i.split('^')
        db.child("Homerooms").child(homeroom[0]).child(
            homeroom[1]).child("Absent").child(date).child(period).update({i[1]: int(i[0])}, session['token'])
    db.child("Homerooms").child(homeroom[0]).child(homeroom[1]).child(
        "Absent").child(date).child(period).update({'notes': notes}, session['token'])
    if cfrmstatus[period]['name'] == 'GP':
        db.child("Homerooms").child(homeroom[0]).child(
            homeroom[1]).child("Absent").child(date).child(period).child("signature").set({'STUD_AFFAIR_OFFICE': signature}, session['token'])
        db.child("Homerooms").child(homeroom[0]).child(
            homeroom[1]).child("Absent").child(date).child(period).child("names").set({'STUD_AFFAIR_OFFICE': "??????????????????"}, session['token'])
    else:
        db.child("Homerooms").child(homeroom[0]).child(
            homeroom[1]).child("Absent").child(date).child(period).child("signature").set(signature, session['token'])
    return redirect('/manage/admin/'+homeroom[0]+'/'+homeroom[1]+'/'+date)


@manage.route('/manage/homeroom_confirm', methods=['POST'])
def homeroom_confirm():
    if (check_login_status()):
        return redirect('/logout')
    refresh_token()
    homeroom = request.form['homeroom'].split('^')
    date = request.form['date']
    if 'notes' in request.form:
        notes = request.form['notes']
        db.child("Homerooms").child(homeroom[0]).child(homeroom[1]).child(
            "Absent").child(date).update({"notes": notes}, session['token'])

    signature = request.form['signatureData']
    signature = removeprefix(signature, 'data:image/png;base64,')
    signature = bytes(signature, 'utf-8')
    rand = str(date + '^' + homeroom[0] + '^' + homeroom[1] + '^' + 'hrCfrm')
    rand += ".png"
    with open(os.path.join('temp', rand), "wb") as fh:
        fh.write(base64.decodebytes(signature))
    storage.child(os.path.join('signatures', rand)
                  ).put(os.path.join('temp', rand), session['token'])
    db.child("Homerooms").child(homeroom[0]).child(homeroom[1]).child("Absent").child(date).update(
        {"confirm": str(storage.child(os.path.join('signatures', rand)).get_url(None))}, session['token'])
    os.remove(os.path.join('temp', rand))
    return redirect('/manage')
