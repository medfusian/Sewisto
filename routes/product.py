import psycopg2
from flask import render_template, redirect, request, url_for, session, g, flash, abort
from . import product_bp


@product_bp.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    # Проверяем, что пользователь аутентифицирован как администратор
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        article = request.form['article']
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        supplier = request.form['supplier']
        season = request.form['season']
        color = request.form['color']
        price = request.form['price']

        # Добавляем новый продукт в таблицу "product"
        g.cursor.execute("INSERT INTO product (article, name, description, category, supplier, season, color, price)"
                         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                         (article, name, description, category, supplier, season, color, price))

        flash('Product added successfully')
        return redirect(url_for('product.admin_products'))

    return render_template('admin/add_product.html')


@product_bp.route('/admin/products')
def admin_products():
    # Проверяем, что пользователь аутентифицирован как администратор
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    g.cursor.execute("SELECT * FROM product")
    products = g.cursor.fetchall()
    return render_template('admin/admin_products.html', products=products)


@product_bp.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    # Получаем товар по его идентификатору
    g.cursor.close()
    with g.connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute('SELECT * FROM product WHERE article = %s', (product_id,))
        product = cursor.fetchone()

    # Проверяем, что пользователь аутентифицирован как администратор
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    # Если товар не найден, возвращаем ошибку 404
    if not product:
        abort(404)

    # Обработка GET запроса
    if request.method == 'GET':
        # Отображаем форму для редактирования товара
        return render_template('admin/edit_product.html', product=product)

    # Обработка POST запроса
    if request.method == 'POST':
        # Обновляем информацию о товаре в базе данных
        article = request.form['article']
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        supplier = request.form['supplier']
        season = request.form['season']
        color = request.form['color']
        price = request.form['price']
        with g.connect.cursor() as cursor:
            cursor.execute(
                'UPDATE product SET article=%s, name=%s, description=%s, category=%s, supplier=%s, season=%s, color=%s, price=%s WHERE article=%s',
                (article, name, description, category, supplier, season, color, price, product_id))

        # Перенаправляем пользователя на страницу с товарами
        return redirect(url_for('product.admin_products'))


@product_bp.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    # Проверяем, что пользователь аутентифицирован как администратор
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    try:
        # Удаляем товар из таблицы product
        g.cursor.execute("DELETE FROM product WHERE article=%s", (product_id,))

        # Возвращаемся на страницу со списком товаров
        flash('Товар успешно удален', 'success')
        return redirect(url_for('product.admin_products'))

    except:
        # В случае ошибки откатываем изменения
        g.connect.rollback()
        flash('Ошибка удаления товара', 'error')
        return redirect(url_for('product.admin_products'))