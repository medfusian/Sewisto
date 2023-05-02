from flask import render_template, session, g, request, redirect, url_for, Response, flash
from PIL import Image
from io import BytesIO
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
    return render_template('info/about.html')


@main_bp.route('/catalog')
def catalog():
    g.cursor.execute("SELECT article, name FROM product;")
    products = g.cursor.fetchall()
    return render_template('catalog.html', products=products)


@main_bp.route('/category')
def category():
    g.cursor.execute("SELECT id, category.category FROM category;")
    categories = g.cursor.fetchall()
    return render_template('category.html', categories=categories)


@main_bp.route('/delivery')
def delivery():
    return render_template('info/delivery.html')


@main_bp.route('/contacts')
def contacts():
    return render_template('info/contacts.html')


@main_bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        # Проверяем, что пользователь аутентифицирован
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        name = request.form['name']
        text = request.form['text']

        # Добавляем новый продукт в таблицу "product"
        g.cursor.execute("INSERT INTO feedback (name, text)"
                         "VALUES (%s, %s)",
                         (name, text))

        return redirect(url_for('main.feedback'))

    g.cursor.execute("SELECT * FROM feedback")
    feedbacks = g.cursor.fetchall()
    return render_template('info/feedback.html', feedbacks=feedbacks)


@main_bp.route('/cart')
def cart():
    g.cursor.execute("SELECT * FROM cart")
    cart = g.cursor.fetchall()
    return render_template('cart.html', cart=cart)


@main_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    g.cursor.execute("SELECT * FROM product WHERE article=%s", (product_id,))
    products = g.cursor.fetchall()
    if not products:
        flash('Товар не найден', 'error')
        return redirect(url_for('main.index'))

    g.cursor.execute("INSERT INTO cart (article, name, price, count, summary) VALUES (%s, %s, %s, %s, %s)",
                     (products[0], products[1], products[7], 1, products[7]))

    flash(f'Товар "{products[1]}" добавлен в корзину', 'success')
    return redirect(url_for('cart'))


@main_bp.route('/image_cat/<int:category_id>')
def get_image(category_id):
    # Получение данных изображения категории из базы данных
    g.cursor.execute("SELECT image FROM category WHERE id=%s", (category_id,))
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


@main_bp.route('/category/<int:category_id>')
def get_category(category_id):
    g.cursor.execute("SELECT p.article, p.name, c.category FROM product p "
                     "JOIN category c ON c.id = p.category "
                     "WHERE p.category=%s", (category_id,))
    products = g.cursor.fetchall()
    return render_template('category_sort.html', products=products)
