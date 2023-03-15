from flask import render_template, session, g
from . import main_bp


@main_bp.route('/')
def index():
    # Получаем все записи из таблицы "product"
    g.cursor.execute("SELECT * FROM product")
    products = g.cursor.fetchall()

    # Получаем информацию о текущем пользователе, если он залогинен
    current_user = None
    user = None
    admin = False

    if 'user_id' in session:
        g.cursor.execute("SELECT * FROM public.user WHERE id = %s", (session['user_id'],))
        current_user = g.cursor.fetchone()
        user = current_user[3]
        current_user = current_user[1]
        admin = False
    elif 'admin_id' in session:
        admin = True

    return render_template('index.html', products=products, user=user, current_user=current_user, admin=admin)


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/catalog')
def catalog():
    return render_template('catalog.html')


@main_bp.route('/contacts')
def contacts():
    return render_template('contacts.html')
