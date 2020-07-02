from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin , current_user
import datetime
import time
from datetime import datetime as dt
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView

db = SQLAlchemy()
class Userr(UserMixin,db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(255), nullable=False)
    LastName = db.Column(db.String(255), nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    Mail = db.Column(db.String(255), unique=True, nullable=True)
    Phone = db.Column(db.String(255), unique=True,nullable=False)
    Photo = db.Column(db.Text, nullable=True)
    Role = db.Column(db.String(255), default='Admin')
    
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)

    def __repr__(self):
        return '<Message {}>'.format(self.body)


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer , primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    products = db.relationship('Product', backref='category')
    subCategories = db.relationship('SubCategory', backref='Category', lazy=True)

class SubCategory(db.Model):
    __tablename__ = 'sub_categories'

    id = db.Column(db.Integer , primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    products = db.relationship('Product', backref='subCategory')
    CategoryId = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

class Type(db.Model):
    __tablename__ = 'types'
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    CategoryId = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    SubCategoryId = db.Column(db.Integer, db.ForeignKey('sub_categories.id'), nullable=False)


    

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer , primary_key=True)
    FirstName = db.Column(db.String(255), nullable=False)
    LastName = db.Column(db.String(255), nullable=False)
    Address = db.Column(db.String(255), nullable=False)
    Phone = db.Column(db.String(255), nullable=False)
    Qte = db.Column(db.Integer, nullable=True)
    products_detailes = db.Column(db.Text, nullable=False)
    wilaya = db.Column(db.String(255),nullable=False)
    commune = db.Column(db.String(255),nullable=False)
    Ordered_at = db.Column(db.DateTime,nullable=False,default=datetime.date.today())
    Status = db.Column(db.String(255),nullable=False, default='En attente')
    Shipped_by = db.Column(db.Integer, default=-1, nullable=True)
    Created_at = db.Column(db.DateTime,nullable=False,default=datetime.date.today())
    Edited_at = db.Column(db.DateTime,nullable=False,default=datetime.date.today())
    
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer , primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    Description = db.Column(db.Text , nullable=True)
    Photo = db.Column(db.String(255), nullable=True)
    BuyPrice = db.Column(db.String(255), nullable=False)
    SellPrice = db.Column(db.String(255), nullable=False)
    Qte = db.Column(db.Integer)
    QteAlert = db.Column(db.Integer)
    Photos = db.Column(db.Text, nullable=True)
    AddedBy = db.Column(db.String(255), nullable=False)
    Created_at = db.Column(db.DateTime,nullable=False,default=datetime.date.today())
    Edited_at = db.Column(db.DateTime,nullable=False,default=datetime.date.today())
    categorie_id = db.Column(db.Integer, db.ForeignKey(Category.id))
    sub_categorie_id = db.Column(db.Integer, db.ForeignKey(SubCategory.id))
    type_id = db.Column(db.Integer, db.ForeignKey(Type.id))
    sales= db.Column(db.Integer, default=0)

class Apperence(db.Model):
    __tablename__= 'apperences'
    id = db.Column(db.Integer, primary_key=True)
    SlidePhoto= db.Column(db.Text, nullable=True)
    Title= db.Column(db.String(255) , nullable=True)
    Description= db.Column(db.String(255), nullable=True)
    TopSales = db.Column(db.Text, nullable=True)
    

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated