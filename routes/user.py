import psycopg2.extras
from flask import render_template, redirect, request, url_for, session, g, flash, abort
from . import user_bp


@user_bp.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
    # Проверяем, что пользователь аутентифицирован как администратор
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        id = request.form['id']
        email = request.form['email']
        password = request.form['password']
        login = request.form['login']

        # Добавляем новый продукт в таблицу "product"
        g.cursor.execute("INSERT INTO public.user (id, email, password, login)"
                         "VALUES (%s, %s, %s, %s)",
                         (id, email, password, login))

        flash('User added successfully')
        return redirect(url_for('user.admin_users'))

    return render_template('admin/add_user.html')


@user_bp.route('/admin/users')
def admin_users():
    # Проверяем, что пользователь аутентифицирован как администратор
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    g.cursor.execute("SELECT * FROM public.user")
    users = g.cursor.fetchall()
    return render_template('admin/admin_users.html', users=users)


@user_bp.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    # Получаем пользователя по его идентификатору
    g.cursor.close()
    with g.connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute('SELECT * FROM public.user WHERE id = %s', (user_id,))
        user = cursor.fetchone()

    # Проверяем, что пользователь аутентифицирован как администратор
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    # Если товар не найден, возвращаем ошибку 404
    if not user:
        abort(404)

    # Обработка GET запроса
    if request.method == 'GET':
        # Отображаем форму для редактирования товара
        return render_template('admin/edit_user.html', user=user)

    # Обработка POST запроса
    if request.method == 'POST':
        # Обновляем информацию о товаре в базе данных
        id = request.form['id']
        email = request.form['email']
        password = request.form['password']
        login = request.form['login']
        with g.connect.cursor() as cursor:
            cursor.execute(
                'UPDATE public.user SET id=%s, email=%s, password=%s, login=%s WHERE id=%s',
                (id, email, password, login, user_id))

        # Перенаправляем пользователя на страницу с информацией о товаре
        return redirect(url_for('user.admin_users'))


@user_bp.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # Проверяем, что пользователь аутентифицирован как администратор
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    try:
        # Удаляем пользователя из таблицы user
        g.cursor.execute("DELETE FROM public.user WHERE id=%s", (user_id,))

        # Возвращаемся на страницу со списком пользователей
        flash('Пользователь успешно удален', 'success')
        return redirect(url_for('user.admin_users'))

    except:
        # В случае ошибки откатываем изменения
        g.connect.rollback()
        flash('Ошибка удаления пользователя', 'error')
        return redirect(url_for('user.admin_users'))