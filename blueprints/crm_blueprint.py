from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

crm_page = Blueprint('crm_page', __name__,
                        template_folder='templates')

@crm_page.route('/crm')
def show():
    return "<h1>Welcome to crm server !!</h1>"