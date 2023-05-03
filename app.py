import psycopg2
import secrets
from config import host, user, password, db_name
from flask import Flask, request, g
from routes import admin_bp, product_bp, user_bp, main_bp, auth_bp, cart_bp

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
dsn = f"dbname={db_name} user={user} password={password} host={host}"

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(product_bp)
app.register_blueprint(user_bp)
app.register_blueprint(cart_bp)


@app.before_request
def before_request():
    """Открывает соединение с БД"""
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


if __name__ == "__main__":
    app.run()