from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import SelectField

from app.shop import db
from datetime import datetime
import random
from flask_admin.contrib.sqla import ModelView
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_login import UserMixin

class User(db.Model, UserMixin):  # 继承 UserMixin
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}  # 允许重新定义

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    mobile = db.Column(db.String(11), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # 存储明文密码
    weixin = db.Column(db.String(200), nullable=False)
    xuehao = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    def verify_password(self, password):
        return self.password == password  # 直接比较明文密码

    @property
    def is_active(self):
        return True  # 返回 True，表示用户是激活的

    @property
    def is_authenticated(self):
        return True  # 返回 True，表示用户已认证

    @property
    def is_anonymous(self):
        return False  # 返回 False，表示用户不是匿名用户

    def get_id(self):
        return self.id  # 返回用户的唯一标识符

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Category {self.name}>'



class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 商品名称
    price = db.Column(db.Float, nullable=False)  # 商品价格
    image_url = db.Column(db.String(200))  # 商品图片链接
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 发布用户，关联到User表
    status = db.Column(db.String(20), nullable=False, default='售卖中')  # 商品状态，默认为售卖中
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)  # 关联到Category表的外键
    description = db.Column(db.Text)  # 商品描述字段

    # 与User建立关系，使用 user_id 关联到 User 表
    user = db.relationship('User', backref=db.backref('products', lazy=True))
    # 与Category建立关系，使用 category_id 关联到 Category 表
    category = db.relationship('Category', backref=db.backref('products', lazy=True))

    def __repr__(self):
        return f'<Product {self.name}>'




class ProductAdmin(ModelView):
    # 指定要显示的列
    form_columns = ['name', 'category', 'price', 'image_url', 'user', 'status', 'description']



def generate_order_number():
    # 生成一个与交易时间有关的订单号，使用当前时间加上随机数
    now = datetime.now()
    order_number = now.strftime("%Y%m%d%H%M%S") + str(random.randint(1000, 9999))
    return order_number

class Transaction(db.Model):
    __tablename__ = 'transaction'
    order_number = db.Column(db.String(20), primary_key=True, default=generate_order_number)  # 订单号，使用生成函数
    transaction_time = db.Column(db.DateTime, default=datetime.utcnow)  # 交易时间
    location = db.Column(db.String(200), nullable=False)  # 交易地点，用户填写
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 购买用户，关联到User表
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # 交易商品，关联到Product表

    # 与User和Product建立关系
    buyer = db.relationship('User', backref=db.backref('transactions', lazy=True))
    product = db.relationship('Product', backref=db.backref('transactions', lazy=True))

    def __repr__(self):
        return f'<Transaction {self.order_number}>'

