import psycopg2.extras
from flask import render_template, redirect, request, url_for, session, g, flash, abort
from . import cart_bp


@cart_bp.context_processor
def inject_user():
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

    return dict(current_user=current_user, user=user, admin=admin)


@cart_bp.route('/cart')
def cart():
    g.cursor.execute("SELECT * FROM cart")
    cart = g.cursor.fetchall()

    # Проверяем, что пользователь аутентифицирован
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    return render_template('cart.html', cart=cart)


@cart_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    # Проверяем, что пользователь аутентифицирован
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    g.cursor.execute("SELECT * FROM product WHERE article=%s", (product_id,))
    product = g.cursor.fetchone()
    if not product:
        flash('Товар не найден', 'error')
        return redirect(url_for('main.index'))

    g.cursor.execute("SELECT * FROM cart")
    cart = g.cursor.fetchall()
    is_on_cart = False
    for c in cart:
        if c[1] == product[0]:
            is_on_cart = True
            cart_id = c[0]

    if is_on_cart:
        g.cursor.execute('UPDATE cart SET count=count+1 WHERE id=%s', (cart_id,))
    else:
        g.cursor.execute("INSERT INTO cart (article, name, price, count) VALUES (%s, %s, %s, %s)",
                        (product[0], product[1], product[7], 1))

    flash(f'Товар "{product[1]}" добавлен в корзину', 'success')
    return redirect(url_for('cart.cart'))


@cart_bp.route('/edit_cart/<int:cart_id>', methods=['GET', 'POST'])
def update_count(cart_id):
    # Получаем товар по его идентификатору
    with g.connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute('SELECT * FROM cart WHERE id = %s', (cart_id,))
        cart = cursor.fetchone()

    # Если товар не найден, возвращаем ошибку 404
    if not cart:
        abort(404)

    # Обработка GET запроса
    if request.method == 'GET':
        # Отображаем форму для редактирования товара
        return render_template('edit_cart.html', product=cart)

    # Обработка POST запроса
    if request.method == 'POST':
        # Обновляем информацию о товаре в базе данных
        count = request.form['count']

    with g.connect.cursor() as cursor:
        cursor.execute(
            'UPDATE cart SET count=%s WHERE id=%s', (count, cart_id))

    # Перенаправляем пользователя на страницу с корзиной
    return redirect(url_for('cart.cart'))


@cart_bp.route('/delete_cart/<int:cart_id>', methods=['POST'])
def delete_product(cart_id):
    # Удаляем товар из таблицы product
    g.cursor.execute("DELETE FROM cart WHERE id=%s", (cart_id,))

    # Возвращаемся на страницу со списком товаров
    flash('Товар успешно удален', 'success')
    return redirect(url_for('cart.cart'))