from flask import Flask, render_template, url_for, flash, redirect, session , request
from flask_sqlalchemy import SQLAlchemy 
from forms import RegistrationForm, LoginForm, AccountForm
from driver_authentication import authenticateDriver
from vehicle_authentication import authenticateVehicle
import pyodbc as pyodbc
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
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
    
    i = Image.open(form_picture)
    i.save(picture_path)
    o_string = picture_path.replace('\\', '/')
    output_string = o_string.replace('/', '//')

    return output_string

@app.route("/register", methods=['GET', 'POST'])
def register():

    form = RegistrationForm()
    if form.validate_on_submit():
        picture_file = save_picture(form.picture.data)

        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (form.email.data, form.password.data ))
        user = cursor.fetchone()
        if user:
            form.email.data = user[2]
            form.password.data = user[3]
            flash('Account already exists!', 'Failed')
        else:    
            cursor.execute('INSERT INTO users (username, email, password) VALUES (? , ? , ?)', (form.firstName.data, form.email.data, form.password.data))
            query_driver = f"insert into driverDetails (dFirstName ,dLastName ,dAge,dAddress ,dNumber ,dEmail ,dImage) SELECT  ?, ?, ?, ?, ?, ? , BulkColumn FROM OPENROWSET (Bulk N'"+ picture_file +"' , SINGLE_BLOB) AS varBinaryData" 
            query_vehicle = f"insert into vehicleDetails  (vNum  ,vEmail  ,vDetails ) VALUES (? , ? , ?)" 
            print(query_driver)
            print(query_vehicle)
            cursor.execute(query_driver, (form.firstName.data,form.lastName.data,form.age.data,form.address.data,form.phoneNumber.data,form.email.data))
            cursor.execute(query_vehicle, (form.vehicleNumber.data,form.email.data,form.vehicleModeldetails.data))
           
            cnxn.commit()
            flash(f'Account created for {form.firstName.data}!', 'success')
        return redirect(url_for('login'))
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
            return redirect(url_for('account'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/account', methods=['GET', 'POST'])
def account():
    form = AccountForm()
    if form.validate_on_submit():
        driverPicture = save_picture(form.driverPicture.data)
        vehiclePicture = save_picture(form.vehiclePicture.data)
        cursor.execute('SELECT ISNULL(max(authentication_id),0) FROM dr_vh_auth')
        user = cursor.fetchone()
        authentication_id = user[0] + 1
        query_driver = f"INSERT INTO dr_vh_auth (authentication_id, dAuthImage ) SELECT ? , BulkColumn FROM OPENROWSET (Bulk N'"+ driverPicture +"' , SINGLE_BLOB) AS varBinaryData"
        query_vehicle = f"UPDATE dr_vh_auth set vAuthImage = BulkColumn FROM OPENROWSET (Bulk N'"+ vehiclePicture +"' , SINGLE_BLOB) AS varBinaryData where authentication_id = ?"
        cursor.execute(query_driver, (authentication_id))
        cursor.execute(query_vehicle, (authentication_id))
        cnxn.commit()
        flash(f'Driver and Vehicle data uploaded sucessfully', 'success')
        driverdetails = authenticateDriver(authentication_id)
        driver_name =  driverdetails[1] +' ' + driverdetails[2]
        driver_id = str(driverdetails[0])
        vehicledetails = authenticateVehicle(authentication_id)
        flash(f'Driver authenticated. Driver id is: '+ driver_id +'  and Driver name is: '+ driver_name, 'success')
        flash(f'vehicle authenticated. vehicle number is: '+ vehicledetails, 'success')
        flash(f'Please proceed with drowsyness monitoring', 'success')


    return render_template('account.html', title='account', form=form)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False)



