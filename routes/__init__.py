from flask import Blueprint

# main_bp = Blueprint('main_bp', __name__)
admin_bp = Blueprint('admin', __name__)
product_bp = Blueprint('product', __name__)
user_bp = Blueprint('user', __name__)

from . import admin, product, user
