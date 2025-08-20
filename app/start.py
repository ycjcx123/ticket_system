from flask import Flask
from login import login_bp
from movie import movie_bp
from order import order_bp
from create_schedule import cs_bp
from admin import admin_bp

import os

app = Flask(__name__,
            template_folder=os.path.join('..', 'web', 'templates'),  # 指向web/templates
            static_folder=os.path.join('..', 'web', 'static'),      # 指向web/static
            static_url_path='/static')


app.secret_key = '123456'

app.register_blueprint(login_bp)
app.register_blueprint(movie_bp)
app.register_blueprint(order_bp)
app.register_blueprint(cs_bp)
app.register_blueprint(admin_bp)


if __name__ == '__main__':
    app.run(debug=True)

