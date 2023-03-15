from flask import render_template, redirect, url_for, session
from . import admin_bp


@admin_bp.route('/admin')
def admin_panel():
    # Проверяем, что пользователь аутентифицирован как администратор
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    admin = True
    return render_template('admin/admin.html', admin=admin)

