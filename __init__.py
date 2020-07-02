from flask import app, Flask, render_template, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os
from flask_login import LoginManager
from .Blueprints import Blueprints,Bcrypt, login_required, UPLOAD_FOLDER
from .models import db, Userr, Category, SubCategory, Order, Product ,Type, MyAdminIndexView, MyModelView
from flask_migrate import Migrate, MigrateCommand
#, index_view=MyAdminIndexView()
admin = Admin(name='Damou walid', template_mode='bootstrap3')
migrate = Migrate()
def create_app():
    app=Flask(__name__)
    app.register_blueprint(Blueprints)
    app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:test@localhost/BodyCare'
    app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER 
    app.config['SECRET_KEY']='123456789'
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    app.register_blueprint(Blueprints)
    with app.app_context():
        db.init_app(app)
        db.create_all()
        migrate.init_app(app, db)
        login_manager=LoginManager()
        login_manager.init_app(app)
        login_manager.session_protection = "strong"
        Bcrypt.init_app(app)
        admin.init_app(app)
        admin.add_view(ModelView(Userr, db.session))
        admin.add_view(ModelView(Product, db.session))
        admin.add_view(ModelView(Category, db.session))
        admin.add_view(ModelView(SubCategory, db.session))
        admin.add_view(ModelView(Type, db.session))
        admin.add_view(ModelView(Order, db.session))
        login_manager.login_view = ".Connexion"

    @login_manager.user_loader
    def load_user(user_id):
        return Userr.query.get(user_id)    



    return app
    