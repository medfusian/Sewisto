import psycopg2.extras
from flask import render_template, redirect, request, url_for, session, g, flash, abort, Response
from PIL import Image
from io import BytesIO
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
        image = request.files['image'].read()

        # Добавляем новый продукт в таблицу "product"
        g.cursor.execute(
            "INSERT INTO product (article, name, description, category, supplier, season, color, price, image)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (article, name, description, category, supplier, season, color, price, image))

        flash('Product added successfully')
        return redirect(url_for('product.admin_products'))

    return render_template('admin/add_product.html')


@product_bp.route('/admin/products')
def admin_products():
    # Проверяем, что пользователь аутентифицирован как администратор
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    g.cursor.execute(
        " SELECT p.article, p.name, p.description, c.category, s.supplier, p.season, p.color, p.price"
        " FROM product p"
        " LEFT JOIN category c ON p.category = c.id"
        " LEFT JOIN supplier s ON p.supplier = s.id;")
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
        # image_file = request.files.get('image')
        # image = image_file.read()
        image = request.files['image'].read()

        with g.connect.cursor() as cursor:
            cursor.execute(
                'UPDATE product SET article=%s, name=%s, description=%s, category=%s, supplier=%s, season=%s, color=%s, price=%s, image=%s WHERE article=%s',
                (article, name, description, category, supplier, season, color, price, image, product_id))

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


@product_bp.route('/image_prod/<int:product_id>')
def get_image(product_id):
    # Получение данных изображения продукта из базы данных
    g.cursor.execute("SELECT image FROM product WHERE article=%s", (product_id,))
    image = g.cursor.fetchone()[0]

    # Открытие изображения с помощью PIL
    img = Image.open(BytesIO(image))

    # Изменение размера изображения
    img = img.resize((250, 250))

    # Конвертация изображения в формат JPEG
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    image = buffer.getvalue()

    # Отправка изображения в ответе
    return Response(image, mimetype='image/jpeg')
