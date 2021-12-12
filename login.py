from functions import *
login = Blueprint('login', __name__)
@login.after_request
def add_header(response):
    response.headers['SameSite'] = "Strict"
    return response


@login.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if check_login_status():
            return render_template('login.html')
        return redirect('/select')
    elif request.method == 'POST':
        email = request.form['username']
        if check_login_status():
            try:
                if (verify_recaptcha("")):
                    if request.form['user_type'] == 'teacher':
                        db = refresh_db()
                        cursor = db.cursor(buffered=True)
                        cursor.execute("SELECT name, role, oldUsername, password FROM users WHERE email = %s", (email,))
                        user = cursor.fetchone()
                        cursor.close()
                        if user == None or not verifyPassword(request.form['password'], user[3]):
                            raise Exception('Invalid Login')
                        usrRole = user[1]
                        if (usrRole == 'R'):
                            print("RealPerson Login SUCC:", email, flush=True)
                            session['is_logged_in'] = True
                            session['email'] = email
                            session['name'] = user[0]
                            session['oldUsername'] = user[2]
                            session['loginTime'] = datetime.now(tz)
                            return redirect('/select')
                        if (usrRole == 'A' or usrRole == 'S'):
                            print("Admin Login SUCC:", email, flush=True)
                            session['subuser_type'] = 'admin'
                            session['is_logged_in'] = True
                            session['email'] = email
                            session['oldUsername'] = user[2]
                            session['loginTime'] = datetime.now(tz)
                            session['showUpload'] = True if usrRole == 'S' else False
                            return redirect('/manage')
                        raise Exception("not real person or admin")
                    elif request.form['user_type'] == 'student':
                        db = refresh_db()
                        cursor = db.cursor(buffered=True)
                        cursor.execute("SELECT password, grade, class_, num, name FROM students WHERE email = %s", (email,))
                        user = cursor.fetchone()
                        cursor.close()
                        if user == None or not verifyPassword(request.form['password'], user[0]):
                            raise Exception('Invalid Login')
                        print("Student Login SUCC:", email, flush=True)
                        session['is_logged_in'] = True
                        session['email'] = email
                        session['loginTime'] = datetime.now(tz)
                        session['user_type'] = 'student'
                        session['name'] = user[4]
                        session['grade'] = user[1]
                        session['class'] = user[2]
                        session['num'] = user[3]
                        return redirect('/manage')
                else:
                    print("ReC Error:", email, flush=True)
                    flash(
                        'reCAPTCHA 錯誤，請稍後再試一次<br>reCAPTCHA Failed. Please try again later.')
                    return redirect('/')
            except Exception as e:
                print("Error*Login:", email, str(e), flush=True)
                flash(
                    '帳號或密碼錯誤，請重新輸入<br>Incorrect username or password')
                return redirect('/')
        else:
            return redirect('/select')


@login.route('/select', methods=['GET', 'POST'])
def selSubUser():
    if check_login_status():
        session.clear()
        flash("Timeout. 遇時，請重新登入")
        return redirect('/')
    refresh_token()
    if 'subuser_type' in session and session['subuser_type'] == 'admin' or 'user_type' in session and session['user_type'] == 'student':
        return redirect('/manage')
    if request.method == 'GET':
        db = refresh_db()
        cursor = db.cursor(buffered=True)
        cursor.execute("SELECT category, subclass FROM gpclasses WHERE accs LIKE %s LIMIT 1", ('%'+session['oldUsername']+'%',))
        classes = cursor.fetchone()
        cursor.close()
        hasGroup = False
        if classes != None:
            hasGroup = True
        db = refresh_db()
        cursor = db.cursor(buffered=True)
        cursor.execute("SELECT grade, class_ FROM homerooms WHERE accs LIKE %s", ('%'+session['oldUsername']+'%',))
        homerooms = cursor.fetchall()
        cursor.close()
        hrC = {}
        for h in homerooms:
            hrC[h[0]] = []
            hrC[h[0]].append(h[1])
        return render_template('selSubUser.html', group=hasGroup, homeroom=hrC, name=session['name'])
    else:
        data = request.form['subuser_sel'].split('^')
        if data == []:
            return redirect('/select')
        try:
            if (verify_recaptcha("")):
                if (data[0] == 'homeroom'):
                    session['homeroom'] = data[1] + '^' + data[2]
                    session['subuser_type'] = 'homeroom'
                elif (data[0] == 'group'):
                    session['subuser_type'] = 'group'
                return redirect('/manage')
            else:
                print("ReC Error:", data, flush=True)
                flash(
                    'reCAPTCHA 錯誤，請稍後再試一次<br>reCAPTCHA Failed. Please try again later.')
                return redirect('/select')
        except Exception as e:
            print("Error*select:", session['email'], str(e), flush=True)
            flash(str(e))
            return redirect('/select')


@login.route('/chgPassword', methods=['POST', 'GET'])
def chgPassword():
    data = {}
    if request.method == 'GET':
        if not check_login_status():
            refresh_token()
            return render_template('chgPassword.html')
        else:
            return abort(404)
    elif request.method == 'POST':
        oldEmail = session['email']
        if not check_login_status():
            refresh_token()
            try:
                if (verify_recaptcha("")):
                    db = refresh_db()
                    cursor = db.cursor(buffered=True)
                    if ('user_type' in session and session['user_type'] == 'student'):
                        cursor.execute("SELECT password FROM students WHERE email = %s", (oldEmail,))
                    else:
                        cursor.execute("SELECT password FROM users WHERE email = %s", (oldEmail,))
                    user = cursor.fetchone()
                    cursor.close()
                    if user == None or not verifyPassword(request.form['password'], user[0]):
                        raise Exception('Invalid Login')
                    if len(request.form['new_password']) < 6:
                        raise Exception('密碼長度不足<br>Password not long enough')
                    db = refresh_db()
                    cursor = db.cursor(buffered=True)
                    if (request.form['new_username'] != oldEmail and request.form['new_username'] != ''):
                        if ('user_type' in session and session['user_type'] == 'student'):
                            cursor.execute("SELECT * FROM students WHERE email = %s", (request.form['new_username'],))
                        else:
                            cursor.execute("SELECT * FROM users WHERE email = %s", (request.form['new_username'],))
                        user = cursor.fetchone()
                        cursor.close()
                        if user != None:
                            raise Exception('帳號已被使用<br>Username already used')
                    db = refresh_db()
                    cursor = db.cursor(buffered=True)
                    if ('user_type' in session and session['user_type'] == 'student'):
                        cursor.execute("UPDATE students SET password = %s WHERE email = %s", (genHash(request.form['new_password']), oldEmail))
                        if (request.form['new_username'] != oldEmail and request.form['new_username'] != ''):
                            cursor.execute("UPDATE students SET email = %s WHERE email = %s", (request.form['new_username'], oldEmail))
                    else:
                        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (
                            genHash(request.form['new_password']), oldEmail))
                        if (request.form['new_username'] != oldEmail and request.form['new_username'] != ''):
                            cursor.execute("UPDATE users SET email = %s WHERE email = %s", (request.form['new_username'], oldEmail))
                    db.commit()
                    cursor.close()
                    session.clear()
                    if (request.form['new_username'] != oldEmail and request.form['new_username'] != ''):
                        send_email(oldEmail, "Email Changed 信箱已更改",
                        """<hr>
                        Your email was changed at %s to %s.<br>
                        If you did not change your email, please contact the student affair's office immediately.
                        <hr>
                        你的信箱已在 %s 更改為 %s。 <br>
                        如果你沒有更改信箱，請立即聯絡學務處。
                        <hr>
                        <small>This email was sent automatically. Please do not reply.<br>
                        這個郵件是自動發送的，請不要回覆。</small>
                        """ % (str(datetime.now(tz)), request.form['new_username'], str(datetime.now(tz)), request.form['new_username']))
                    flash(
                        '修改密碼成功，請重新登入<br>Password changed successfully. Please login again.')
                    return redirect('/')
                else:
                    print("ReC Error:", oldEmail, flush=True)
                    flash(
                        'reCAPTCHA 錯誤，請稍後再試一次<br>reCAPTCHA Failed. Please try again later.')
                    return redirect('/chgPassword')
            except Exception as e:
                flash(str(e))
                return redirect('/chgPassword')


@login.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'GET':
        return render_template('forgotPassword.html')
    elif request.method == 'POST':
        email = request.form['username']
        try:
            if (verify_recaptcha("")):
                db = refresh_db()
                cursor = db.cursor(buffered=True)
                if (request.form['user_type'] == 'student'):
                    cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
                elif (request.form['user_type'] == 'teacher'):
                    cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                cursor.close()
                if user == None:
                    raise Exception('無此 Email<br>Invalid Email')
                exists = True
                while exists:
                    resetID = ''.join(choices(string.ascii_lowercase + string.digits, k=10))
                    cursor = db.cursor(buffered=True)
                    cursor.execute("SELECT * FROM forgot WHERE resetID = %s", (resetID,))
                    user = cursor.fetchone()
                    cursor.close()
                    exists = (user != None)
                db = refresh_db()
                cursor = db.cursor(buffered=True)
                cursor.execute("""
                    INSERT INTO forgot (resetID, email, reqTime, userType)
                    VALUES (%s, %s, %s, %s)
                """, (resetID, email, datetime.strftime(datetime.now(tz), '%Y-%m-%d %H:%M:%S'), 'T' if request.form['user_type'] == 'teacher' else 'S'))
                db.commit()
                cursor.close()
                send_email(email, "Password Reset 重置密碼",
                """<hr>
                Please go to the following link to reset your password:<br>
                https://abs.aaronlee.tech/resetPassword?resetCode=%s<br>
                If you did not request a password reset, please ignore this email.
                <hr>
                請點選以下連結重置密碼：<br>
                https://abs.aaronlee.tech/resetPassword?resetCode=%s<br>
                如果您沒有要求重置密碼，請忽略此郵件。
                <hr>
                <small>This email was sent automatically. Please do not reply.<br>
                這個郵件是自動發送的，請不要回覆。</small>
                """ % (resetID, resetID))
                print("forgotPassword email sent:", email, flush=True)
                flash(
                    '重置密碼信件已寄出，請至信箱收取<br>Password reset email has been sent to your email. Please check your email.')
                return redirect('/')
            else:
                print("ReC Error:", email, flush=True)
                flash(
                    'reCAPTCHA 錯誤，請稍後再試一次<br>reCAPTCHA Failed. Please try again later.')
                return redirect('/forgotPassword')
        except Exception as e:
            print("Error*forgotPassword:", email, str(escape), flush=True)
            flash(str(e))
            return redirect('/forgotPassword')


@login.route('/resetPassword', methods=['GET', 'POST'])
def resetPassword():
    if request.args.get('resetCode') is None:
        return abort(404)
    if request.method == 'GET':
        return render_template('verifiedChgPassword.html', resetCode=request.args.get('resetCode'))
    else:
        try:
            if (verify_recaptcha("")):
                db = refresh_db()
                cursor = db.cursor(buffered=True)
                cursor.execute("""
                    SELECT resetID, email, reqTime, userType
                    FROM forgot
                    WHERE resetID = %s
                """, (request.args.get('resetCode'),))
                user = cursor.fetchone()
                cursor.close()
                if user == None:
                    raise Exception('無此重置密碼代碼<br>Invalid reset password code')
                if (datetime.now(tz) - datetime.strptime(user[2], '%Y-%m-%d %H:%M:%S')).seconds > 3600:
                    cursor.execute("DELETE FROM forgot WHERE resetID = %s", (user[0],))
                    db.commit()
                    cursor.close()
                    raise Exception('重置密碼代碼已過期<br>Reset password code expired')
                if len(request.form['password']) < 6:
                    raise Exception('密碼長度不足<br>Password not long enough')
                db = refresh_db()
                cursor = db.cursor(buffered=True)
                if (user[3] == 'T'):
                    cursor.execute("UPDATE users SET password = %s WHERE email = %s", (
                        genHash(request.form['password']), user[1]))
                elif (user[3] == 'S'):
                    cursor.execute("UPDATE students SET password = %s WHERE email = %s", (
                        genHash(request.form['password']), user[1]))
                db.commit()
                cursor.close()
                db = refresh_db()
                cursor = db.cursor(buffered=True)
                cursor.execute("DELETE FROM forgot WHERE resetID = %s", (user[0],))
                db.commit()
                cursor.close()
                session.clear()
                flash(
                    '重置密碼成功，請重新登入<br>Password changed successfully. Please login again.')
                return redirect('/')
            else:
                print("ReC Error:", flush=True)
                flash(
                    'reCAPTCHA 錯誤，請稍後再試一次<br>reCAPTCHA Failed. Please try again later.')
                return redirect('/resetPassword')
        except Exception as e:
            print("Error*resetPassword:", request.args.get('resetCode'), str(e), flush=True)
            flash(str(e))
            return redirect('/resetPassword?resetCode=' + request.args.get('resetCode'))


@login.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')
