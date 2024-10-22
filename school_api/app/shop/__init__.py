from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy


api_bp = Blueprint('shop', __name__)
db = SQLAlchemy()
from . import view