from functions import *
from manage.manage import manage
from upload import upload
from login import login
load_dotenv()
app = Flask(__name__)
babel = Babel(app)
app.register_blueprint(manage)
app.register_blueprint(upload)
app.register_blueprint(login)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+os.environ.get('MYSQL_USER')+':'+os.environ.get('MYSQL_PASSWORD')+'@'+os.environ.get('MYSQL_HOST')+'/attendance'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_TW'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
sdb = SQLAlchemy(app)

class DefaultModelView(ModelView):
    restricted = True
    def __init__(self, model, session, restricted=True, name=None, category=None, endpoint=None, url=None, **kwargs):
        self.restricted = restricted
        self.column_default_sort = ('id', True)
        for k, v in kwargs.items():
            setattr(self, k, v)
        setattr(self, 'can_export', True)
        super(DefaultModelView, self).__init__(model, session, name=name, category=category, endpoint=endpoint, url=url)
    def is_accessible(self):
        if self.restricted == True:
            return ((not check_login_status()) and is_admin() and check_permission())
        return ((not check_login_status()) and is_admin())
    def inaccessible_callback(self, name, **kwargs):
        return redirect('/')
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return ((not check_login_status()) and is_admin())
    def inaccessible_callback(self, name, **kwargs):
        return redirect('/')

admin = Admin(
        app,
        name='Attendance 點名系統 後台管理',
        template_mode='bootstrap3',
        index_view=MyAdminIndexView(),
    )
class Users(sdb.Model):
    id = sdb.Column(sdb.INT, primary_key=True)
    email = sdb.Column(sdb.Text)
    name = sdb.Column(sdb.Text)
    oldUsername = sdb.Column(sdb.Text)
    role = sdb.Column(sdb.CHAR)
    password = sdb.Column(sdb.Text)
class Students(sdb.Model):
    id = sdb.Column(sdb.INT, primary_key=True)
    email = sdb.Column(sdb.INT)
    grade = sdb.Column(sdb.INT)
    class_ = sdb.Column(sdb.INT)
    num = sdb.Column(sdb.INT)
    name = sdb.Column(sdb.Text)
    ename = sdb.Column(sdb.Text)
    classes = sdb.Column(sdb.Text)
    password = sdb.Column(sdb.Text)
class Schedule(sdb.Model):
    id = sdb.Column(sdb.INT, primary_key=True)
    grade = sdb.Column(sdb.INT)
    class_ = sdb.Column(sdb.INT)
    dow = sdb.Column(sdb.INT)
    period = sdb.Column(sdb.CHAR)
    subject = sdb.Column(sdb.Text)
    teacher = sdb.Column(sdb.Text)
class SpecSchedule(sdb.Model):
    __tablename__ = 'specschedule'
    id = sdb.Column(sdb.INT, primary_key=True)
    grade = sdb.Column(sdb.INT)
    class_ = sdb.Column(sdb.INT)
    date = sdb.Column(sdb.VARCHAR(11))
    period = sdb.Column(sdb.CHAR)
    subject = sdb.Column(sdb.Text)
    teacher = sdb.Column(sdb.Text)
class GPClasses(sdb.Model):
    __tablename__ = 'gpclasses'
    id = sdb.Column(sdb.INT, primary_key=True)
    category = sdb.Column(sdb.Text)
    subclass = sdb.Column(sdb.Text)
    about = sdb.Column(sdb.Text)
    accs = sdb.Column(sdb.Text)
class Homerooms(sdb.Model):
    id = sdb.Column(sdb.INT, primary_key=True)
    grade = sdb.Column(sdb.INT)
    class_ = sdb.Column(sdb.INT)
    accs = sdb.Column(sdb.Text)
class Submission(sdb.Model):
    id = sdb.Column(sdb.INT, primary_key=True)
    grade = sdb.Column(sdb.INT)
    class_ = sdb.Column(sdb.INT)
    date = sdb.Column(sdb.VARCHAR(11))
    period = sdb.Column(sdb.CHAR)
    signature = sdb.Column(sdb.Text)
    ds1 = sdb.Column(sdb.INT)
    ds2 = sdb.Column(sdb.INT)
    ds3 = sdb.Column(sdb.INT)
    ds4 = sdb.Column(sdb.INT)
    ds5 = sdb.Column(sdb.INT)
    ds6 = sdb.Column(sdb.INT)
    ds7 = sdb.Column(sdb.INT)
    notes = sdb.Column(sdb.Text)
class DS(sdb.Model):
    id = sdb.Column(sdb.INT, primary_key=True)
    grade = sdb.Column(sdb.INT)
    class_ = sdb.Column(sdb.INT)
    num = sdb.Column(sdb.INT)
    date = sdb.Column(sdb.VARCHAR(11))
    period = sdb.Column(sdb.CHAR)
    note = sdb.Column(sdb.Text)
    status = sdb.Column(sdb.CHAR, default='X')
class Dates(sdb.Model):
    id = sdb.Column(sdb.INT, primary_key=True)
    date = sdb.Column(sdb.VARCHAR(11))
    dow = sdb.Column(sdb.INT)
class Absent(sdb.Model):
    id = sdb.Column(sdb.INT, primary_key=True)
    grade = sdb.Column(sdb.INT)
    class_ = sdb.Column(sdb.INT)
    num = sdb.Column(sdb.INT)
    date = sdb.Column(sdb.VARCHAR(11))
    period = sdb.Column(sdb.CHAR)
    status = sdb.Column(sdb.CHAR)
    note = sdb.Column(sdb.Text)
class Forgot(sdb.Model):
    id = sdb.Column(sdb.INT, primary_key=True)
    resetID = sdb.Column(sdb.VARCHAR(11))
    email = sdb.Column(sdb.Text)
    reqTime = sdb.Column(sdb.VARCHAR(20))
admin.add_view(DefaultModelView(Users, sdb.session, restricted=False, column_exclude_list = ['password'], column_searchable_list = ['name', 'email', 'role']))
admin.add_view(DefaultModelView(Students, sdb.session, restricted=False, column_exclude_list = ['password'], column_searchable_list = ['grade', 'class_', 'num', 'email','name', 'ename', 'classes']))
admin.add_view(DefaultModelView(Schedule, sdb.session, column_searchable_list = ['grade', 'class_', 'dow', 'period', 'subject', 'teacher']))
admin.add_view(DefaultModelView(SpecSchedule, sdb.session, restricted=False, column_searchable_list = ['grade', 'class_', 'date', 'period', 'subject', 'teacher']))
admin.add_view(DefaultModelView(GPClasses, sdb.session, column_searchable_list = ['category', 'subclass', 'about', 'accs']))
admin.add_view(DefaultModelView(Homerooms, sdb.session, column_searchable_list = ['grade', 'class_', 'accs']))
admin.add_view(DefaultModelView(Submission, sdb.session, column_exclude_list=['signature'], column_searchable_list = ['grade', 'class_', 'date', 'period', 'notes']))
admin.add_view(DefaultModelView(DS, sdb.session, restricted=False, column_searchable_list = ['grade', 'class_', 'date', 'period', 'num', 'note', 'status']))
admin.add_view(DefaultModelView(Dates, sdb.session, column_searchable_list = ['date', 'dow']))
admin.add_view(DefaultModelView(Absent, sdb.session, restricted=False, column_searchable_list = ['grade', 'class_', 'date', 'period', 'num', 'status', 'note']))
admin.add_view(DefaultModelView(Forgot, sdb.session, column_searchable_list = ['resetID', 'email', 'reqTime']))
admin.add_link(MenuLink(name='Back to Home 返回一般管理', category='', url='/manage'))
admin.add_link(MenuLink(name='Logout 登出', category='', url='/logout'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
