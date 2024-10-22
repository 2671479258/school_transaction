from flask import render_template, redirect, current_app, session

from app.shop import db
from . import api_bp
from app.shop.model import Product,Category,Transaction,generate_order_number
from flask import render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
import os

from .form import ProductForm,LoginForm
from .model import User
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, login_manager, current_user


@api_bp.route('/')
def index():
    products = Product.query.filter_by(status='售卖中').all()
    categories = Category.query.all()
    return render_template('index.html', products=products, categories=categories)


@api_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)






@api_bp.route('/product/new', methods=['GET', 'POST'])
@login_required
def create_product():
    form = ProductForm()

    # 动态获取类别选项
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        # 获取表单数据
        name = form.name.data
        price = form.price.data
        category_id = form.category.data
        description = form.description.data
        user_id = current_user.id  # 假设使用 Flask-Login 并且用户已登录
        print(user_id)

        # 处理上传的图片
        image_file = form.image.data
        image_url = None
        if image_file:
            filename = form.name.data + str(user_id)+str(price)+'.png'
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_url = url_for('static', filename='images/' + filename, _external=True)
            print(image_url)


        # 创建新商品
        new_product = Product(
            name=name,
            price=price,
            category_id=category_id,
            user_id=user_id,
            image_url=image_url,
            description=description
        )
        db.session.add(new_product)
        db.session.commit()

        flash('商品发布成功！', 'success')
        return redirect(url_for('shop.index'))

    return render_template('create_product.html', form=form)




@api_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # 获取用户输入的手机号或学号
        identifier = form.identifier.data
        password = form.password.data
        # 查询数据库，检查手机号或学号是否存在
        user = User.query.filter((User.mobile == identifier) | (User.xuehao == identifier)).first()
        if user and user.verify_password(password):  # 验证密码
            login_user(user, remember=form.remember_me.data)
            print('成功')
            flash('登录成功！', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('shop.index'))
        else:
            flash('无效的手机号、学号或密码', 'danger')
    return render_template('login.html', form=form)


@api_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已经退出登录', 'info')
    return redirect(url_for('shop.index'))

@api_bp.route('/checkout/<int:product_id>', methods=['GET', 'POST'])
@login_required
def checkout(product_id):
    # 获取商品和卖家信息
    product = Product.query.get_or_404(product_id)
    seller = User.query.get(product.user_id)
    if request.method == 'POST':
        location = request.form.get('location')
        if not location:
            flash('请填写交易地点！', 'warning')
            return render_template('checkout.html', product=product, seller=seller)
        session['location'] = location
        return redirect(url_for('shop.order_confirmation', product_id=product_id))
    return render_template('checkout.html', product=product, seller=seller)


@api_bp.route('/order-confirmation/<int:product_id>', methods=['GET'])
@login_required
def order_confirmation(product_id):
    # 获取商品和卖家信息
    product = Product.query.get_or_404(product_id)
    seller = User.query.get_or_404(product.user_id)
    if product.status != '售卖中':
        flash('该商品已被购买或不再售卖。', 'warning')
        return redirect(url_for('shop.index'))
    location = session.get('location')
    if not location:
        flash('交易地点信息缺失，请重新填写。', 'warning')
        return redirect(url_for('shop.checkout', product_id=product_id))


    order_number = generate_order_number()
    transaction = Transaction(
        order_number=order_number,
        location=location,  # 使用在 checkout 中填写的交易地点
        buyer_id=current_user.id,
        product_id=product.id
    )

    product.status = '已售出'

    db.session.add(transaction)
    db.session.commit()

    flash('订单已生成，等待卖家确认！', 'success')
    return render_template('order_confirmation.html', product=product, seller=seller, order_number=order_number,
                           location=location)


@api_bp.route('/my-transactions', methods=['GET'])
@login_required
def my_transactions():
    # 获取当前用户的所有交易记录
    transactions = Transaction.query.filter_by(buyer_id=current_user.id).all()

    return render_template('my_transactions.html', transactions=transactions)