from datetime import timedelta

from flask import Flask
from flask_admin.contrib.sqla import ModelView  # 导入用于SQLAlchemy模型管理的类
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash

from app.shop import db
from flask_admin import Admin
from app.shop.model import User, Product, Transaction, ProductAdmin,Category
from flask_login import LoginManager, current_user


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@my_mysql/school'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'yug'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['UPLOAD_FOLDER'] = 'app/static/images'

    login_manager = LoginManager()
    login_manager.init_app(app)
    db.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

        db.session.commit()







    from app.shop import api_bp
    app.register_blueprint(api_bp, url_prefix='/shop')


    admin = Admin(app, name='MyApp Admin', template_mode='bootstrap3')
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ProductAdmin(Product, db.session))
    admin.add_view(ModelView(Category, db.session))


    admin.add_view(ModelView(Transaction, db.session))  # 添加Transaction模型到Admin面板




    return app