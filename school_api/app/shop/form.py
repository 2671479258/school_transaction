

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, FileField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    identifier = StringField('手机号或学号', validators=[DataRequired(), Length(1, 200)])  # 允许手机号或学号
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')


class ProductForm(FlaskForm):
    name = StringField('商品名称', validators=[DataRequired()])
    price = FloatField('价格', validators=[DataRequired()])
    category = SelectField('类别', choices=[], coerce=int, validators=[DataRequired()])  # 动态填充类别
    image = FileField('商品图片')
    description = StringField('商品描述', validators=[DataRequired()])


