import psycopg2
import psycopg2.extras
import secrets
from config import host, user, password, db_name
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, abort
from routes import admin_bp, product_bp, user_bp

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
dsn = f"dbname={db_name} user={user} password={password} host={host}"

# app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(product_bp)
app.register_blueprint(user_bp)


@app.before_request
def before_request():
    db = getattr(g, 'connect', None)
    if db is None and request.endpoint not in ['static']:
        g.connect = psycopg2.connect(dsn)
        g.connect.autocommit = True
        g.cursor = g.connect.cursor()


@app.teardown_appcontext
def close_connection(exception):
    """Закрывает соединение с БД"""
    if hasattr(g, 'cursor'):
        g.cursor.close()
    if hasattr(g, 'connect'):
        g.connect.close()


@app.route('/')
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


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/catalog')
def catalog():
    return render_template('catalog.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']

        # Проверяем, что email и пароль соответствуют пользователю в таблице "admin"
        g.cursor.execute("SELECT * FROM admin WHERE email = %s AND password = %s", (email, password))
        admin = g.cursor.fetchone()

        if admin:
            # Устанавливаем переменную сессии "admin_id" в значение admin.id
            session['admin_id'] = admin[0]
            flash('Logged in as admin')
            return redirect(url_for('admin.admin_panel'))

        # Проверяем, что email и пароль соответствуют пользователю в таблице "user"
        g.cursor.execute("SELECT * FROM public.user WHERE email = %s AND password = %s", (email, password))
        user = g.cursor.fetchone()

        if user:
            # Устанавливаем переменную сессии "user_id" в значение user.id
            session['user_id'] = user[0]
            flash('Logged in successfully')
            return redirect(url_for('index'))

        flash('Email or password is incorrect')

    return render_template('auth/login.html')


@app.route('/password')
def password():
    return render_template('auth/password.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('admin_id', None)
    flash('Logged out successfully')
    return redirect(url_for('index'))


# @app.route('/admin')
# def admin_panel():
#     # Проверяем, что пользователь аутентифицирован как администратор
#     if 'admin_id' not in session:
#         return redirect(url_for('login'))
#     admin = True
#     return render_template('admin/admin.html', admin=admin)


# @app.route('/admin/add_product', methods=['GET', 'POST'])
# def add_product():
#     # Проверяем, что пользователь аутентифицирован как администратор
#     if 'admin_id' not in session:
#         return redirect(url_for('login'))
#
#     if request.method == 'POST':
#         article = request.form['article']
#         name = request.form['name']
#         description = request.form['description']
#         category = request.form['category']
#         supplier = request.form['supplier']
#         season = request.form['season']
#         color = request.form['color']
#         price = request.form['price']
#
#         # Добавляем новый продукт в таблицу "product"
#         g.cursor.execute("INSERT INTO product (article, name, description, category, supplier, season, color, price)"
#                          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
#                          (article, name, description, category, supplier, season, color, price))
#
#         flash('Product added successfully')
#         return redirect(url_for('admin_products'))
#
#     return render_template('admin/add_product.html')
#
#
# @app.route('/admin/products')
# def admin_products():
#     # Проверяем, что пользователь аутентифицирован как администратор
#     if 'admin_id' not in session:
#         return redirect(url_for('login'))
#
#     g.cursor.execute("SELECT * FROM product")
#     products = g.cursor.fetchall()
#     return render_template('admin/admin_products.html', products=products)
#
#
# @app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
# def edit_product(product_id):
#     # Получаем товар по его идентификатору
#     g.cursor.close()
#     with g.connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
#         cursor.execute('SELECT * FROM product WHERE article = %s', (product_id,))
#         product = cursor.fetchone()
#
#     # Проверяем, что пользователь аутентифицирован как администратор
#     if 'admin_id' not in session:
#         return redirect(url_for('login'))
#
#     # Если товар не найден, возвращаем ошибку 404
#     if not product:
#         abort(404)
#
#     # Обработка GET запроса
#     if request.method == 'GET':
#         # Отображаем форму для редактирования товара
#         return render_template('admin/edit_product.html', product=product)
#
#     # Обработка POST запроса
#     if request.method == 'POST':
#         # Обновляем информацию о товаре в базе данных
#         article = request.form['article']
#         name = request.form['name']
#         description = request.form['description']
#         category = request.form['category']
#         supplier = request.form['supplier']
#         season = request.form['season']
#         color = request.form['color']
#         price = request.form['price']
#         with g.connect.cursor() as cursor:
#             cursor.execute(
#                 'UPDATE product SET article=%s, name=%s, description=%s, category=%s, supplier=%s, season=%s, color=%s, price=%s WHERE article=%s',
#                 (article, name, description, category, supplier, season, color, price, product_id))
#
#         # Перенаправляем пользователя на страницу с товарами
#         return redirect(url_for('admin_products'))
#
#
# @app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
# def delete_product(product_id):
#     # Проверяем, что пользователь аутентифицирован как администратор
#     if 'admin_id' not in session:
#         return redirect(url_for('login'))
#
#     try:
#         # Удаляем товар из таблицы product
#         g.cursor.execute("DELETE FROM product WHERE article=%s", (product_id,))
#
#         # Возвращаемся на страницу со списком товаров
#         flash('Товар успешно удален', 'success')
#         return redirect(url_for('admin_products'))
#
#     except:
#         # В случае ошибки откатываем изменения
#         g.connect.rollback()
#         flash('Ошибка удаления товара', 'error')
#         return redirect(url_for('admin_products'))



# @app.route('/admin/add_user', methods=['GET', 'POST'])
# def add_user():
#     # Проверяем, что пользователь аутентифицирован как администратор
#     if 'admin_id' not in session:
#         return redirect(url_for('login'))
#
#     if request.method == 'POST':
#         id = request.form['id']
#         email = request.form['email']
#         password = request.form['password']
#         login = request.form['login']
#
#         # Добавляем новый продукт в таблицу "product"
#         g.cursor.execute("INSERT INTO public.user (id, email, password, login)"
#                          "VALUES (%s, %s, %s, %s)",
#                          (id, email, password, login))
#
#         flash('User added successfully')
#         return redirect(url_for('admin_users'))
#
#     return render_template('admin/add_user.html')
#
#
# @app.route('/admin/users')
# def admin_users():
#     # Проверяем, что пользователь аутентифицирован как администратор
#     if 'admin_id' not in session:
#         return redirect(url_for('login'))
#
#     g.cursor.execute("SELECT * FROM public.user")
#     users = g.cursor.fetchall()
#     return render_template('admin/admin_users.html', users=users)
#
#
# @app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
# def edit_user(user_id):
#     # Получаем пользователя по его идентификатору
#     g.cursor.close()
#     with g.connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
#         cursor.execute('SELECT * FROM public.user WHERE id = %s', (user_id,))
#         user = cursor.fetchone()
#
#     # Проверяем, что пользователь аутентифицирован как администратор
#     if 'admin_id' not in session:
#         return redirect(url_for('login'))
#
#     # Если товар не найден, возвращаем ошибку 404
#     if not user:
#         abort(404)
#
#     # Обработка GET запроса
#     if request.method == 'GET':
#         # Отображаем форму для редактирования товара
#         return render_template('admin/edit_user.html', user=user)
#
#     # Обработка POST запроса
#     if request.method == 'POST':
#         # Обновляем информацию о товаре в базе данных
#         id = request.form['id']
#         email = request.form['email']
#         password = request.form['password']
#         login = request.form['login']
#         with g.connect.cursor() as cursor:
#             cursor.execute(
#                 'UPDATE public.user SET id=%s, email=%s, password=%s, login=%s WHERE id=%s',
#                 (id, email, password, login, user_id))
#
#         # Перенаправляем пользователя на страницу с информацией о товаре
#         return redirect(url_for('admin_users'))
#
#
# @app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
# def delete_user(user_id):
#     # Проверяем, что пользователь аутентифицирован как администратор
#     if 'admin_id' not in session:
#         return redirect(url_for('login'))
#
#     try:
#         # Удаляем пользователя из таблицы user
#         g.cursor.execute("DELETE FROM public.user WHERE id=%s", (user_id,))
#
#         # Возвращаемся на страницу со списком пользователей
#         flash('Пользователь успешно удален', 'success')
#         return redirect(url_for('admin_users'))
#
#     except:
#         # В случае ошибки откатываем изменения
#         g.connect.rollback()
#         flash('Ошибка удаления пользователя', 'error')
#         return redirect(url_for('admin_users'))


if __name__ == "__main__":
    app.run()
