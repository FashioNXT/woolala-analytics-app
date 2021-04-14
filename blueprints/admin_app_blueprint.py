from flask import Blueprint, render_template, abort

admin_app_page = Blueprint('admin_app_page', __name__,
                        template_folder='templates')

@admin_app_page.route('/admin_app')
def show():
    return "<h1>Welcome to admin server !!</h1>"