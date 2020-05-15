from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from energyapp.blueprints.page.models import Newsletter
from energyapp.extensions import db


page = Blueprint('page', __name__, template_folder='templates')

@page.route('/', methods=('GET','POST'))
def home():
    if request.method == 'POST':
        emailaddress = request.form['emailaddress']
        email= Newsletter(email=emailaddress)
        signup = Newsletter.query.filter_by(email=emailaddress).first()
        if not signup:
            db.session.add(email)
            db.session.commit()
            flash('Registration has been successful', 'success')
        else:
            flash('Email address already exists', 'error')

        
    return render_template('page/home.html')
