from functions import *
from export import *
admin = Blueprint('admin', __name__)

@admin.route('/manage/admin/mark', methods=['GET', 'POST'])
def mark_absent():
    if (check_login_status() or session['subuser_type'] != 'admin'):
        return redirect('/logout')
    refresh_token()
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            periods = [i[7] for i in data if i.startswith('period-')]
            db = refresh_db()
            cursor = db.cursor()
            for p in periods:
                cursor.execute("INSERT INTO absent (grade, class_, date, period, num, status, note) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                    (data['grade'], data['class'], data['date'], p, data['num'], data['type'], data['notes'] if 'notes' in data else ''))
            db.commit()
        except Exception as e:
            flash(e)
        else:
            flash("`成功！ (" + data['grade'] + data['class'] + "班" + data['num'] + "號, 日期: " + data['date'] + ", 總計 " + str(len(periods)) + "堂課)")
        return redirect('/manage/admin/mark')
    db = refresh_db()
    cursor = db.cursor()
    cursor.execute("SELECT grade, class_, num, name FROM students ORDER BY grade,class_,num ASC")
    sql = cursor.fetchall()
    students = {}
    for i in sql:
        if i[0] not in students:
            students[i[0]] = {}
        if i[1] not in students[i[0]]:
            students[i[0]][i[1]] = {}
        students[i[0]][i[1]][i[2]] = i[3]
    cursor.execute("SELECT date,period,grade,class_,num,status,note FROM absent ORDER BY id DESC LIMIT 10")
    records = cursor.fetchall()
    return render_template("admin_mark.html", students=students, periods=['m', '1', '2', '3', '4', 'n', '5', '6', '7', '8', '9'], records=records, hideSel=True)

@admin.route('/manage/admin/export', methods=['GET'])
def admin_export():
    if (check_login_status() or session['subuser_type'] != 'admin'):
        return redirect('/logout')
    refresh_token()
    return render_template("admin_export.html", hideSel=True)

@admin.route('/manage/admin/export/homeroom_period', methods=['POST'])
def admin_export_homeroom_period():
    if (check_login_status() or session['subuser_type'] != 'admin'):
        return redirect('/logout')
    refresh_token()
    workbook = Workbook()
    workbook.remove_sheet(workbook.get_sheet_by_name('Sheet'))
    workbook = create_period_sheets(workbook, [request.form['grade'], request.form['class']])
    excel_stream = io.BytesIO()
    workbook.save(excel_stream)
    excel_stream.seek(0)
    return send_file(excel_stream, attachment_filename='homeroom_period_' + request.form['grade'] + request.form['class'] +'.xlsx', as_attachment=True)

@admin.route('/manage/admin/export/homeroom_period/all', methods=['GET'])
def admin_export_homeroom_period_all():
    if (check_login_status() or session['subuser_type'] != 'admin'):
        return redirect('/logout')
    refresh_token()
    db = refresh_db()
    cursor = db.cursor()
    cursor.execute("SELECT grade,class_ FROM homerooms")
    homerooms = cursor.fetchall()
    workbook = Workbook()
    workbook.remove_sheet(workbook.get_sheet_by_name('Sheet'))
    for i in homerooms:
        workbook = create_period_sheets(workbook, [str(i[0]), str(i[1])])
    excel_stream = io.BytesIO()
    workbook.save(excel_stream)
    excel_stream.seek(0)
    return send_file(excel_stream, attachment_filename='homeroom_period_all.xlsx', as_attachment=True)


@admin.route('/manage/admin/export/student_list', methods=['POST'])
def admin_export_student_list():
    if (check_login_status() or session['subuser_type'] != 'admin'):
        return redirect('/logout')
    refresh_token()
    workbook = Workbook()
    workbook.remove_sheet(workbook.get_sheet_by_name('Sheet'))
    workbook = create_student_list(workbook, [request.form['grade'], request.form['class']])
    excel_stream = io.BytesIO()
    workbook.save(excel_stream)
    excel_stream.seek(0)
    return send_file(excel_stream, attachment_filename='student_list_' + request.form['grade'] + request.form['class'] +'.xlsx', as_attachment=True)

@admin.route("/manage/admin/export/student_list/all", methods=['GET'])
def admin_export_student_list_all():
    if (check_login_status() or session['subuser_type'] != 'admin'):
        return redirect('/logout')
    refresh_token()
    db = refresh_db()
    cursor = db.cursor()
    cursor.execute("SELECT grade,class_ FROM homerooms")
    homerooms = cursor.fetchall()
    workbook = Workbook()
    workbook.remove_sheet(workbook.get_sheet_by_name('Sheet'))
    for i in homerooms:
        workbook = create_student_list(workbook, [str(i[0]), str(i[1])])
    excel_stream = io.BytesIO()
    workbook.save(excel_stream)
    excel_stream.seek(0)
    return send_file(excel_stream, attachment_filename='student_list_all.xlsx', as_attachment=True)

@admin.route('/manage/admin/export/teacher_period', methods=['POST'])
def admin_export_teacher_period():
    if (check_login_status() or session['subuser_type'] != 'admin'):
        return redirect('/logout')
    refresh_token()
    workbook = Workbook()
    workbook.remove_sheet(workbook.get_sheet_by_name('Sheet'))
    workbook = create_teacher_periods(workbook, request.form['name'], request.form['orig_username'])
    excel_stream = io.BytesIO()
    workbook.save(excel_stream)
    excel_stream.seek(0)
    return send_file(excel_stream, attachment_filename='teacher_period_' + request.form['name'] + '_' + ('' if 'orig_username' not in request.form else request.form['orig_username']) +'.xlsx', as_attachment=True)

@admin.route('/manage/admin/export/teacher_period/all', methods=['GET'])
def admin_export_teacher_period_all():
    if (check_login_status() or session['subuser_type'] != 'admin'):
        return redirect('/logout')
    refresh_token()
    db = refresh_db()
    cursor = db.cursor()
    cursor.execute("SELECT name,oldUsername FROM users")
    teachers = cursor.fetchall()
    workbook = Workbook()
    workbook.remove_sheet(workbook.get_sheet_by_name('Sheet'))
    for i in teachers:
        workbook = create_teacher_periods(workbook, i[0], i[1])
    excel_stream = io.BytesIO()
    workbook.save(excel_stream)
    excel_stream.seek(0)
    return send_file(excel_stream, attachment_filename='teacher_period_all.xlsx', as_attachment=True)