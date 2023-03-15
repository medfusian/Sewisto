from flask import render_template, redirect, url_for, request, session, g, flash
from . import auth_bp


@auth_bp.route('/login', methods=['GET', 'POST'])
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
            return redirect(url_for('main.index'))

        flash('Email or password is incorrect')

    return render_template('auth/login.html')


@auth_bp.route('/password')
def password():
    return render_template('auth/password.html')


@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('admin_id', None)
    flash('Logged out successfully')
    return redirect(url_for('main.index'))
