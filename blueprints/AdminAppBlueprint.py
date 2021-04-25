"""
The admin crm  page Blueprint
"""
from analytics_algorithms import AdminPageData
from flask import Blueprint, render_template, url_for, request, session, redirect
import bcrypt
from flask import current_app ,flash

template_dir = "../frontend/templates/"

admin_app_page = Blueprint('admin_app_page', __name__,
                        template_folder=template_dir)

#TODO restrict access only to logged in users

@admin_app_page.route('/login', methods=['POST', 'GET'])
def login():
    """
    Route function of login page .
    Takes two types of HTTP methods
    POST and GET
    GET: renders the login html page
    POST: takes the user information , validates it and logins user to it's entitled view of data
    """
    error = None
    current_app.logger.info("herer")
    if request.method == 'POST':
        admins = current_app.db.Admins
        login_user = admins.find_one({'name': request.form['username']})

        if login_user:
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user[
                'password']:
                session['username'] = request.form['username']
                flash('You were successfully logged in')
                return redirect(url_for('.admin_data'))

        error = 'Invalid username or password. Please try again!'
    return render_template('auth/login.html', error=error)



@admin_app_page.route('/register', methods=['POST', 'GET'])
def register():
    """
    Route function to register a new user as admin
    """
    if request.method == 'POST':
        admins = current_app.db.Admins
        existing_admin = admins.find_one({'name': request.form['username']})

        if existing_admin is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            entitled = "all"   # can switch this variable
            admins.insert({'name': request.form['username'], 'password': hashpass, 'entitled':entitled})
            return redirect(url_for('index'))

        return 'That username already exists!'
    return render_template('auth/register.html')

@admin_app_page.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('index'))

@admin_app_page.route('/admin_data')
def admin_data():
    if('username' not in session.keys()):
        return redirect(url_for('index'))
    
    admin_data = current_app.db.AdminPageData
    data = admin_data.find_one({"entitled":session["entitled"]})

    return render_template('admin_app/admin_page.html', data=data)

@admin_app_page.route('/delete_user<userId>' , methods=['DELETE'])
def delete_user(userId):
    """
    Function to mark the status of user as deleted . The user will be deleted later in a batch process
    """
    if ('username' not in session.keys()):
        return redirect(url_for('index'))
    users = current_app.db.Users
    users.update_one({"userID": userId}, {"$set": {"status": "deleted"}})

@admin_app_page.route('/delete_post<postId>',methods=['DELETE'])
def delete_post(postId):
    """
    Function to mark the status of post as deleted . The post will be deleted later in a batch process
    """
    if ('username' not in session.keys()):
        return redirect(url_for('index'))
    posts = current_app.db.Posts
    posts.update_one({"postID": postId}, {"$set": {"status": "deleted"}})


@admin_app_page.route('/update_admin_data')
def update_admin_data():
    """function will update all the application data
        It will delete the users marked for deletion
        It will delete posts marked for deletion
        It will update recommendation for users
        It will update data seen by admin on the CRM page
    """

    admin_data = AdminPageData.AdminPageData()
    admin_data.delete_posts()
    admin_data.delete_users()
    admin_data.update_most_active_users()
    admin_data.update_top_rated_posts()
    admin_data.update_users_count_data()
    admin_data.update_users_recommendation()
    admin_data = current_app.db.AdminPageData
    data = admin_data.find()

    return render_template('admin_app/admin_page.html', data=data)

