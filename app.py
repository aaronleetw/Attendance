from functions import *
from manage import manage
from upload import upload
load_dotenv()
app = Flask(__name__)
app.register_blueprint(manage)
app.register_blueprint(upload)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


@app.after_request
def add_header(response):
    response.headers['SameSite'] = "Strict"
    return response


@ app.route('/', methods=['GET', 'POST'])
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
                    user = auth.sign_in_with_email_and_password(
                        email, request.form['password'])
                    usrData = db.child("Users").child(user['localId']).child("permission").get(
                        user['idToken']).val()
                    if (usrData == 'realPerson'):
                        print("RealPerson Login SUCC:", email, flush=True)
                        session['is_logged_in'] = True
                        session['email'] = user['email']
                        session['uid'] = user['localId']
                        session['token'] = user['idToken']
                        session['refreshToken'] = user['refreshToken']
                        session['loginTime'] = datetime.now(tz)
                        return redirect('/select')
                    if (usrData == 'admin'):
                        print("Admin Login SUCC:", email, flush=True)
                        session['subuser_type'] = 'admin'
                        session['is_logged_in'] = True
                        session['email'] = user['email']
                        session['uid'] = user['localId']
                        session['token'] = user['idToken']
                        session['refreshToken'] = user['refreshToken']
                        session['loginTime'] = datetime.now(tz)
                        session['showUpload'] = db.child("Users").child(
                            session['uid']).child("showUpload").get(session['token']).val()
                        return redirect('/manage')
                    raise Exception("not real person or admin")
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


@app.route('/select', methods=['GET', 'POST'])
def selSubUser():
    if check_login_status():
        session.clear()
        flash("Timeout. 遇時，請重新登入")
        return redirect('/')
    refresh_token()
    if 'subuser_type' in session and session['subuser_type'] == 'admin':
        return redirect('/manage')
    if request.method == 'GET':
        usrData = db.child("Users").child(session['uid']).get(
            session['token']).val()
        session['subuser_type'] = ''
        return render_template('selSubUser.html', data=usrData['accounts'], name=usrData['name'])
    else:
        data = request.form['subuser_sel'].split('^')
        try:
            if (verify_recaptcha("")):
                if (data[0] == 'homeroom'):
                    session['homeroom'] = data[1] + '^' + data[2]
                    session['subuser_type'] = 'homeroom'
                elif (data[0] == 'group'):
                    session['category'] = data[1]
                    session['class'] = data[2]
                    session['subuser_type'] = 'group'
                return redirect('/manage')
            else:
                print("ReC Error:", data, flush=True)
                flash(
                    'reCAPTCHA 錯誤，請稍後再試一次<br>reCAPTCHA Failed. Please try again later.')
                return redirect('/select')
        except Exception as e:
            print("Error*select:", session['email'], str(json.loads(e.args[1])[
                  'error']['message']), flush=True)
            flash(str(json.loads(e.args[1])[
                  'error']['message']))
            return redirect('/select')


@app.route('/chgPassword', methods=['POST', 'GET'])
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
        delUser = False
        if not check_login_status():
            refresh_token()
            try:
                if (verify_recaptcha("")):
                    oldUsr = auth.sign_in_with_email_and_password(
                        oldEmail, request.form['password'])
                    print("chgPwd oldUser:", oldEmail, flush=True)
                    old = {}
                    old['uid'] = oldUsr['localId']
                    old['token'] = oldUsr['idToken']
                    data = db.child("Users").child(
                        oldUsr['localId']).get(oldUsr['idToken']).val()

                    auth.delete_user_account(oldUsr['idToken'])
                    delUser = True

                    newUsr = auth.create_user_with_email_and_password(
                        request.form['new_username'], request.form['new_password'])
                    db.child("Users").child(newUsr['localId']).set(
                        data, newUsr['idToken'])
                    db.child("Users").child(oldUsr['localId']).remove(oldUsr['idToken'])
                    session.clear()
                    flash(
                        '修改密碼成功，請重新登入<br>Password changed successfully. Please login again.')
                    return redirect('/')
                else:
                    print("ReC Error:", oldEmail, flush=True)
                    flash(
                        'reCAPTCHA 錯誤，請稍後再試一次<br>reCAPTCHA Failed. Please try again later.')
                    return redirect('/chgPassword')
            except Exception as e:
                if delUser:
                    try:
                        usr = auth.create_user_with_email_and_password(
                            oldEmail, request.form['password'])
                        db.child("Users").child(usr['localId']).set(
                            data, usr['idToken'])
                    except:
                        pass
                print("Error*chgPassword:", oldEmail, str(json.loads(e.args[1])[
                    'error']['message']), flush=True)
                flash(str(json.loads(e.args[1])[
                    'error']['message']))
                return redirect('/chgPassword')


@app.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'GET':
        return render_template('forgotPassword.html')
    elif request.method == 'POST':
        email = request.form['username']
        try:
            if (verify_recaptcha("")):
                auth.send_password_reset_email(email)
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
            print("Error*forgotPassword:", email, str(json.loads(e.args[1])[
                  'error']['message']), flush=True)
            flash(str(json.loads(e.args[1])[
                  'error']['message']))
            return redirect('/forgotPassword')


@app.route('/resetPassword', methods=['GET', 'POST'])
def resetPassword():
    if request.args.get('oobCode') is None:
        return abort(404)
    if request.method == 'GET':
        return render_template('verifiedChgPassword.html', oobCode=request.args.get('oobCode'))
    else:
        try:
            if (verify_recaptcha("")):
                auth.verify_password_reset_code(
                    request.args.get('oobCode'), request.form['password'])
                print("resetPassword success:", flush=True)
                session.clear()
                flash('重置密碼成功，請重新登入<br>Password reset success. Please login again.')
                return redirect('/')
            else:
                print("ReC Error:", flush=True)
                flash(
                    'reCAPTCHA 錯誤，請稍後再試一次<br>reCAPTCHA Failed. Please try again later.')
                return redirect('/resetPassword')
        except Exception as e:
            print("Error*resetPassword:", request.args.get('oobCode'), str(json.loads(e.args[1])[
                  'error']['message']), flush=True)
            flash(str(json.loads(e.args[1])[
                  'error']['message']))
            return redirect('/resetPassword?mode=resetPassword&oobCode=' + request.args.get('oobCode'))


@ app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
