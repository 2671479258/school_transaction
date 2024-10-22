from app.shop import db
from app.shop.model import User
from werkzeug.security import generate_password_hash

users = User.query.all()

for user in users:
    # 假设用户密码是以明文存储的，现将其转换为哈希存储
    if user.password and not user.password_hash:  # 只对之前明文存储的密码进行哈希
        user.password_hash = generate_password_hash(user.password)
        user.password = None  # 清空明文密码字段

# 提交更改
db.session.commit()