from flask import Blueprint, render_template, url_for, request, session, redirect
import bcrypt
from flask import current_app ,flash
from database_connection import database_connection

template_dir = "../frontend/templates/"

admin_app_page = Blueprint('admin_app_page', __name__,
                        template_folder=template_dir)



@admin_app_page.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        admins = current_app.db.Admins
        login_user = admins.find_one({'name': request.form['username']})

        if login_user:
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
                session['username'] = request.form['username']
                flash('You were successfully logged in')
                return redirect(url_for('.all_users_data'))

        error = 'Invalid username or password. Please try again!'
    return render_template('auth/login.html',error = error)



@admin_app_page.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        admins = current_app.db.Admins
        existing_admin = admins.find_one({'name': request.form['username']})

        if existing_admin is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            admins.insert({'name': request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return 'That username already exists!'
    return render_template('auth/register.html')


@admin_app_page.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('index'))


def delete(userId):
    filter = {"userId":userId}
    current_app.db.Users.remove(filter)

@admin_app_page.route('/all_users_data')
def all_users_data():
    users = current_app.db.Users
    users = users.find()
    return render_template('admin_app/admin_page.html',users = users)
