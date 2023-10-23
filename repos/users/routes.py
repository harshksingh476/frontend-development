from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import current_user, logout_user, login_user
from repos.modules import User, Project
from flask_bcrypt import Bcrypt

users = Blueprint('users', __name__)


@users.route('/')
@users.route('/login', methods=['POST', 'GET'])
def login():
    bcrypt = Bcrypt()
    password = "password".encode('utf-8')
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    if current_user.is_authenticated:
        if 'PROJECT_IDS' not in session:
            logout()
    if request.method == "POST":
        data = request.form
        user = User.query.filter_by(useremail=data['user_email']).first()
        password = data['user_password']
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember='True')
            next_page = request.args.get('next')
            project_id = Project.query.with_entities(Project.id).filter_by(parent_project_name=user.project_name).all()
            project_ids = [item[0] for item in project_id]
            session['PROJECT_IDS'] = project_ids
            session['COMPANY_NAME'] =  user.project_name
            flash('You have been loggen in!', 'success')
            if user.project_name == 'AAVANA':
                return redirect(next_page) if next_page else redirect(url_for('aavana.aavana_home'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash("Login Unsuccessful. Please try with correct email and password", 'danger')
    return render_template('login.html')


@users.route('/logout')
def logout():
    logout_user()
    session.pop('PROJECT_IDS', None)
    session.pop('COMPANY_NAME', None)
    return redirect(url_for('users.login'))