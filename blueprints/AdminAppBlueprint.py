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
    current_app.logger.info("Tyring Logging into application")
    if request.method == 'POST':
        admins = current_app.db.Admins
        login_user = admins.find_one({'name': request.form['username']})

        if login_user:
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user[
                'password']:
                session['userName'] = request.form['username']
                flash('You were successfully logged in')
                current_app.logger.info("Successfully Logged in into application")
                return redirect(url_for('.admin_data'))

        error = 'Invalid username or password. Please try again!'
    return render_template('auth/login.html', error=error, title='Login')



@admin_app_page.route('/register', methods=['POST', 'GET'])
def register():
    """
    Route function to register a new user as admin , should not have this function later
    """
    error = None
    if request.method == 'POST':
        current_app.logger.info("Tyring to register admin into application")
        admins = current_app.db.Admins
        existing_admin = admins.find_one({'name': request.form['username']})

        if existing_admin is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            entitled = "all"   # can switch this variable
            admins.insert({'name': request.form['username'], 'password': hashpass, 'entitled':entitled})
            current_app.logger.info(" Admin registered : %s ")
            return redirect(url_for('.login'))
        error = 'Username already exists!'
    return render_template('auth/register.html', error=error, title='Register')

@admin_app_page.route('/logout', methods=['POST', 'GET'])
def logout():
    current_app.logger.info("logged out : %s ",session["userName"])
    session.clear()
    return redirect(url_for('.login'))

@admin_app_page.route('/admin-data')
def admin_data():
    if('userName' not in session.keys()):
        return redirect(url_for('.login'))

    try:
        current_app.logger.info(" Trying to show data for : %s ", session["userName"])
        admin = current_app.db.Admins.find_one({"name":session['userName']})
        if(not admin ):
            return redirect(url_for('.login'))
        entitled = admin["entitled"]
        admin_data = current_app.db.AdminPageData
        session["entitled"] = entitled
        data = admin_data.find_one({"entitled": session["entitled"]})
        return render_template('admin_app/admin_page.html', data=data, title='Admin PAge')
    except:
        current_app.logger.exception("message")


@admin_app_page.route('/delete-user/<userId>' , methods=['PUT'])
def delete_user(userId):
    """
    Function to mark the status of user as deleted . The user will be deleted later in a batch process
    """
    if ('userName' not in session.keys()):
        return redirect(url_for('.login'))

    if current_app.db.Admins.find({"name": session['userName']}).count() < 1:
        return redirect(url_for('.login'))
    try:
        current_app.logger.info(" Trying to delete user : %s ", str(userId))
        users = current_app.db.Users
        users.update_one({"userID": userId}, {"$set": {"status": "delete"}})
        admin_data = current_app.db.AdminPageData
        reported_users = admin_data.find_one({"entitled":"all"})["reportedUsers"]
        del reported_users[userId]
        admin_data.update_one({"entitled": "all"}, {"$set": {"reportedUsers": reported_users}})

        current_app.logger.info(" User marked for deletion : %s", str(userId))
        return "User is marked for deletion"
    except:
        current_app.logger.exception("message")
#     # return redirect(url_for('.admin_data'))
#     # add admin page with the row removed



@admin_app_page.route('/delete-post/<postId>',methods=['PUT'])
def delete_post(postId):
    """
    Function to mark the status of post as deleted . The post will be deleted later in a batch process
    """

    if ('userName' not in session.keys()):
        return redirect(url_for('.login'))

    if current_app.db.Admins.find({"name": session['userName']}).count() < 1:
        return redirect(url_for('.login'))
    try:
        current_app.logger.info(" Trying to delete post : %s", str(postId))
        posts = current_app.db.Posts
        posts.update_one({"postID": postId}, {"$set": {"status": "delete"}})
        admin_data = current_app.db.AdminPageData
        reported_posts = admin_data.find_one({"entitled": "all"})["reportedPosts"]
        del reported_posts[postId]
        current_app.db.ReportedPosts.delete_many({"postID":postId})
        admin_data.update_one({"entitled": "all"}, {"$set": {"reportedPosts": reported_posts}})
    except:
        current_app.logger.exception("message")
    # return redirect(url_for('.admin_data'))
    #add admin page with the row removed


@admin_app_page.route('/update-admin-data')
def update_admin_data():
    """function will update all the application data
        It will delete the users marked for deletion
        It will delete posts marked for deletion
        It will update recommendation for users
        It will update data seen by admin on the CRM page
    """
    if ('userName' not in session.keys()):
        return redirect(url_for('.login'))

    if current_app.db.Admins.find({"name": session['userName']}).count() < 1:
        return redirect(url_for('.login'))

    try:
        current_app.logger.info("Update started")
        admin_page_data = AdminPageData.AdminPageData()
        admin_page_data.delete_posts()
        admin_page_data.delete_users()
        admin_page_data.update_most_active_users()
        admin_page_data.update_top_rated_posts()
        admin_page_data.update_users_count_data()
        admin_page_data.update_users_recommendation()
        admin_page_data.update_reported_posts_and_users()
        admin_page_data = current_app.db.AdminPageData
    except:
        current_app.logger.exception("message")
    return redirect(url_for('.admin_data'))
