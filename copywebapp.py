from flask import Flask, render_template, url_for, flash, redirect, session , request
from flask_sqlalchemy import SQLAlchemy 
from forms import RegistrationForm, LoginForm
import pyodbc as pyodbc
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from forms import RegistrationForm, LoginForm
import urllib.request
import os
import secrets
from PIL import Image



app = Flask(__name__)
app.config['SECRET_KEY'] = '06fc067623bd8dbeeb198d9eb53625b8'



posts = [
    {
        'author': 'ADMIN',
        'title': 'Registration steps',
        'content': 'New users are requested to upload personal and vehicle details for registration',
        'date_posted': 'March 20, 2023'
    }
]
cnxn = pyodbc.connect(driver='{SQL Server}', server='DESKTOP-9KO479H\SQLEXPRESS', database='facerecognition',trusted_connection='yes')
cursor = cnxn.cursor()

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'Static/profile_pictures', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    o_string = picture_path.replace('\\', '/')
    output_string = o_string.replace('/', '//')

    return output_string

@app.route("/register", methods=['GET', 'POST'])
def register():

    form = RegistrationForm()
    if form.validate_on_submit():
        picture_file = save_picture(form.picture.data)

        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (form.username.data, form.email.data ))
        user = cursor.fetchone()
        if user:
            form.username.data = user[1]
            form.email.data = user[2]
            flash('Account already exists!', 'Failed')
        else:    
            cursor.execute('INSERT INTO users (username, email, password) VALUES (? , ? , ?)', (form.username.data, form.email.data, form.password.data))
            query = f"insert into driverDetails (dName,dAge,dphoneNumber,dImage) SELECT  ?, ?, ? , BulkColumn FROM OPENROWSET (Bulk N'"+ picture_file +"' , SINGLE_BLOB) AS varBinaryData" 
            print(query)
            cursor.execute(query, ('r1aaam', 19, '+100'))
            cnxn.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

    
@app.route("/login", methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (form.email.data, form.password.data ))
        user = cursor.fetchone()
        if user:
            form.email.data = user[2]
            form.password.data = user[3]
            session['loggedin'] = True
            #login_user(user, remember=form.remember.data)
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False)



