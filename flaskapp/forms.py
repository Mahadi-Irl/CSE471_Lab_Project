from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from flaskapp.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
            


class ReviewForm(FlaskForm):
    rate = IntegerField('Rate', validators=[DataRequired(), NumberRange(min=1, max=5)])
    review = TextAreaField('Review', validators=[DataRequired()])
    submit = SubmitField('Submit Review')


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Add Category')

class SubcategoryForm(FlaskForm):
    name = StringField('Subcategory Name', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Subcategory')

class DeleteCategoryForm(FlaskForm):
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Delete Category')

class DeleteSubcategoryForm(FlaskForm):
    subcategory = SelectField('Subcategory', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Delete Subcategory')