from flask import Blueprint, render_template, url_for, request, session, redirect
import bcrypt

from database_connection import database_connection



admin_app_page = Blueprint('admin_app_page', __name__,
                        template_folder='templates')



@admin_app_page.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username or password'