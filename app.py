from flask import *
import pyrebase
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv
import requests
from manage import manage
from upload import upload
load_dotenv()
app = Flask(__name__)
app.register_blueprint(manage)
app.register_blueprint(upload)

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
auth = firebase.auth()
tz = pytz.timezone('Asia/Taipei')


def check_login_status():
    return ('is_logged_in' not in session or
            session['is_logged_in'] == False or
            (datetime.now(tz) - session['loginTime']).total_seconds() > 3600)


def verify_recaptcha(response):
    data = {
        'secret': os.environ.get('RECAPTCHA_SECRET'),
        'response': response,
        'remoteip': request.remote_addr
    }
    r = requests.post(
        'https://www.google.com/recaptcha/api/siteverify', data=data)
    return r.json()['success']


@ app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if check_login_status():
            return render_template('login.html')
        return redirect('/manage')
    elif request.method == 'POST':
        email = request.form['username'] + "@group-attendance.fhjh.tp.edu.tw"
        if check_login_status():
            try:
                if (verify_recaptcha(request.form['g-recaptcha-response'])):
                    user = auth.sign_in_with_email_and_password(
                        email, request.form['password'])
                    print("Login SUCC:", email, flush=True)
                    session['is_logged_in'] = True
                    session['email'] = user['email']
                    session['uid'] = user['localId']
                    session['token'] = user['idToken']
                    session['refreshToken'] = user['refreshToken']
                    session['loginTime'] = datetime.now(tz)
                    return redirect('/manage')
                else:
                    print("ReC Error:", email, flush=True)
                    flash(
                        'reCAPTCHA 錯誤，請稍後再試一次<br>reCAPTCHA Failed. Please try again later.')
                    return redirect('/')
            except Exception as e:
              print("Error:", email, str(e), flush=True)
              flash(
                    '帳號或密碼錯誤，請重新輸入<br>Incorrect username or password')
              return redirect('/')
        else:
            return redirect('/manage')


@ app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
