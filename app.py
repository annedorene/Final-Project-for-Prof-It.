""" IMPORT LIBRARIES """
# Import Libraries
from flask import Flask, render_template, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from os.path import join, abspath, dirname
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, EqualTo
from datetime import date, datetime

""" INSTANTIATE FLASK MAIN APP"""
app = Flask(__name__)

""" CONSTANTS """
BASEDIR = abspath(dirname(__file__))

""" CONFIGURATIONS """
# 256-bit WEP Keys for security
app.config['SECRET_KEY'] = "AC3C3B653E9B3641F5D56B3F6332E"
# Flask SQLAlchemy will use SQLITE as its database
# app.config['SQLALCHEMY_DATABASE_URI'] =\
    # 'sqlite:///' + join(BASEDIR, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:useruser@localhost/users'
# OPTIONAL: use less memory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

""" INSTANTIATE DATABASE AND LOGIN_MANAGER """
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

""" CLASSES """
# Forms


class ConfirmForm(FlaskForm):
    back = SubmitField('Back')
    submit = SubmitField('Confirm')


class LoginForm(FlaskForm):
    """
    All fields must be field: DataRequired()
    Email must be in email format
    """
    email = StringField('Email',
                        validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    surname = StringField('Surname')
    first_name = StringField('First name')
    age = IntegerField('Age')
    birth_date = DateField('Birth Date')
    school = StringField('School')
    year_college = SelectField('Year of College', choices=[
        (1, '1st'),
        (2, '2nd'),
        (3, '3rd'),
        (4, '4th'),
        (5, '5th')
    ])
    course = StringField('Course')
    email = StringField('Email',
                        validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('password2', message="Passwords must match.")])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

# Models


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(64))
    first_name = db.Column(db.String(64))
    age = db.Column(db.Integer)
    birth_date = db.Column(db.Date)
    school = db.Column(db.String(64))
    year_college = db.Column(db.Integer)
    course = db.Column(db.String(64))

    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))


""" ROUTES """
# MAIN PAGES


@app.route('/')  # Home Page
def index():
    return render_template('main/index.html')


@app.route('/about')  # About Us Page
def about():
    return render_template('main/about.html')


@app.route('/book_it')  # Book It Page
@login_required
def book_it():
    return render_template('main/book_it.html')


@app.route('/faq')  # FAQ Page
@login_required
def faq():
    return render_template('main/faq.html')

### ERROR PAGES ###
# Optional error pages with Bootstrap to make them look good


@app.errorhandler(403)  # Forbidden Page
def forbidden(e):
    return render_template('errors/403.html'), 403


@app.errorhandler(404)  # Page Not Found
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)  # Internal Server Error Page
def internal_server_error(e):
    return render_template('errors/500.html'), 500


### AUTH PAGES ###


@app.route('/logout')  # Logout Page
@login_required
def logout():  # Logout Page
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])  # Login Page
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and (user.password == form.password.data):
            login_user(user)
            return redirect(url_for("index"))
        flash('Invalid email or password.')
    return render_template('auth/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])  # Register Page
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first() is None:
            session['form'] = {
                'surname': form.surname.data,
                'first_name': form.first_name.data,
                'age': form.age.data,
                'birth_date': form.birth_date.data,
                'school': form.school.data,
                'year_college': form.year_college.data,
                'course': form.course.data,
                'email': form.email.data,
                'password': form.password.data
            }
            return redirect(url_for('confirm'))
        flash("Email is already been used. Kindly use another email")
    return render_template('auth/register.html', form=form)


@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    form = session.get('form')
    submit = ConfirmForm()
    if submit.validate_on_submit():
        if submit.submit.data:
            bday = form["birth_date"].split()
            bday = date(
                year=int(bday[3]),
                month=datetime.strptime(bday[2], "%b").month,
                day=int(bday[1])
            )
            user = User(surname=form['surname'],
                        first_name=form['first_name'],
                        age=form['age'],
                        birth_date=bday,
                        school=form['school'],
                        year_college=form['year_college'],
                        course=form['course'],
                        email=form['email'],
                        password=form['password']
                        )
            db.session.add(user)
            db.session.commit()
            flash('You can now login.')
            return redirect(url_for('login'))
        else:
            return redirect(url_for('register'))
    return render_template('auth/confirm.html', form=form, submit_button=submit)


@app.route('/users')
@login_required
def users():
    users = User.query.all()
    index = []
    surname = []
    first_name = []
    email = []
    birth_date = []
    school = []
    course = []
    arr_len = len(users)

    for idx, user in enumerate(users):
        index.append(idx+1)
        email.append(user.email)
        surname.append(user.surname)
        first_name.append(user.first_name)
        birth_date.append(user.birth_date)
        school.append(user.school)
        course.append(user.course)

    query = {
        'id': index,
        'email': email,
        'surname': surname,
        'first_name': first_name,
        'birth_date': birth_date,
        'school': school,
        'course': course,
    }

    return render_template('main/users.html', query=query, arr_len=arr_len)


""" USER LOADER """


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


""" FLASK SHELL"""


@app.shell_context_processor
def make_shell_context():
    # for flask shell session auto var creation
    # import into a dict
    return dict(db=db, User=User)
