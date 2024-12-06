from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791728bb0b18ce0c676dfde280ba245'


services = [
    {
        'title' : 'Cleaning House',
        'service_providor' : 'Shakib',
        'description' : 'Deep cleaning of the whole house',
        'date_posted' : 'April 25, 2024'
    },
    {
        'title' : 'Washing Toilet',
        'service_providor' : 'Tamim',
        'description' : 'Deep cleaning of the toilet',
        'date_posted' : 'May 12, 2024'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', services=services)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@yahoo.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(debug=True)