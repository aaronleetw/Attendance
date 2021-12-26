from functions import *
student = Blueprint('student', __name__)

@student.route('/student', methods=['GET'])
def showStudentAbs():
    if (check_login_status()):
        return redirect('/logout')
    refresh_token()
    if not ('user_type' in session and session['user_type'] == 'student'):
        return redirect('/')
    db = refresh_db()
    cursor = db.cursor()
    cursor.execute("SELECT date, period, num, status, note FROM absent WHERE grade=%s AND class_=%s AND num=%s ORDER BY date DESC, FIND_IN_SET(period, 'm,1,2,3,4,n,5,6,7,8,9') DESC, num ASC", (session['grade'], session['class'], session['num']))
    absentDataSQL = cursor.fetchall()
    return render_template("list.html", title="Student Absent List | 學生缺勤紀錄", mode='STUDABS', data=absentDataSQL, currRoom=[session['grade'],session['class']], name=session['name'], num=session['num'])

@student.route('/student/ds', methods=['GET'])
def showStudentDS():
    if (check_login_status()):
        return redirect('/logout')
    refresh_token()
    if not ('user_type' in session and session['user_type'] == 'student'):
        return redirect('/')
    db = refresh_db()
    cursor = db.cursor()
    cursor.execute("SELECT date, period, num, note FROM ds WHERE grade=%s AND class_=%s AND num=%s ORDER BY date DESC, FIND_IN_SET(period, 'm,1,2,3,4,n,5,6,7,8,9') DESC, num ASC", (session['grade'], session['class'], session['num']))
    dsDataSQL = cursor.fetchall()
    print(dsDataSQL)
    return render_template("list.html", title="Student DS List | 學生定心紀錄", mode='STUDDS', data=dsDataSQL, currRoom=[session['grade'],session['class']], name=session['name'], num=session['num'])

