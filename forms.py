from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired ,ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired

class RegistrationForm(FlaskForm):
    firstName = StringField('firstName',
                           validators=[DataRequired(), Length(min=2, max=20)])
    lastName = StringField('lastName',
                           validators=[DataRequired(), Length(min=2, max=20)])
    age = StringField('age',
                           validators=[DataRequired(), Length(min=2, max=2)])
    address = StringField('address',
                           validators=[DataRequired(), Length(min=10, max=200)])
    phoneNumber = StringField('phoneNumber',
                           validators=[DataRequired(), Length(min=10, max=12)])
    vehicleNumber = StringField('vehicleNumber',
                           validators=[DataRequired(), Length(min=6, max=20)])
    vehicleModeldetails = StringField('vehicleModeldetails',
                           validators=[DataRequired(), Length(min=10, max=200)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])

    picture = FileField('Upload Picture', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'gif']), FileRequired()])
    
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class AccountForm(FlaskForm):
    driverPicture = FileField('Upload Driver Picture', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'gif']), FileRequired()])
    vehiclePicture = FileField('Upload Vehicle Picture with number plate', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'gif']), FileRequired()])
    
    submit = SubmitField('Authenticate User')