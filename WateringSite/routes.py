from WateringSite import app
from flask import render_template


@app.route('/')
@app.route('/home')
def home():
    user = {'username':'Kevin'}
    return render_template('index.html',title='Home',user = user)