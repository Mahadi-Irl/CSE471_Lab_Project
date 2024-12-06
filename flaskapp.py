from flask import Flask, render_template, url_for
app = Flask(__name__)

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


if __name__ == '__main__':
    app.run(debug=True)