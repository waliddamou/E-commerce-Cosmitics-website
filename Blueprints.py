from flask import Blueprint , render_template, request, current_app, flash, redirect, url_for,send_file,send_from_directory,Response,jsonify
from werkzeug.utils import secure_filename
import os
from flask_login import login_required, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt
import uuid
from .models import Userr, Category, SubCategory, Product, Order, Apperence, Type, db,Notification
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import json
import datetime
from fpdf import FPDF
import logging
from pywebpush import webpush, WebPushException
from bs4 import BeautifulSoup as bs
import re

Blueprints=Blueprint('Blueprints',__name__,template_folder='templates',static_folder='static')
UPLOAD_FOLDER = 'static/Uploaded_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
Bcrypt=Bcrypt()

DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH = os.path.join(os.getcwd(),"private_key.txt")
DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH = os.path.join(os.getcwd(),"public_key.txt")

VAPID_PRIVATE_KEY = open(DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH, "r+").readline().strip("\n")
VAPID_PUBLIC_KEY = open(DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH, "r+").read().strip("\n")

VAPID_CLAIMS = {
"sub": "mailto:develop@raturi.in"
}

def send_web_push(subscription_information, message_body):
    return webpush(
        subscription_info=subscription_information,
        data=message_body,
        vapid_private_key=VAPID_PRIVATE_KEY,
        vapid_claims=VAPID_CLAIMS
    )

def sniper():
    message="Une nouvelle Commande !"
    tokens=Notification.query.all()
    if tokens:
        for i in tokens:
            send_web_push(json.loads(i.body), message)
    return "SENDED"
    



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def getall():
    Orders=Order.query.all()
    return Orders
class PDF(FPDF):
    def header(self):
        # Logo
        self.image('static/img/logo_kbc.jpg', 7, 5, 25)
        
        self.set_font('Times', 'B', 15)
        self.cell(130)
        self.cell(10, 10, 'FACTURE')
        self.set_font('Times', '', 10)
        # Title
        self.cell(-110)
        self.cell(10, 10, 'Num: ')
        self.cell(1)
        self.cell(8, 10, '0560 60 00 13')
        self.cell(70)
        self.ln(4)
        self.cell(30)
        self.cell(10, 10, 'E-mail: elmakitha@gmail.com ')
        self.cell(90)
        self.cell(10, 10, 'Numéro de la facture :')
        self.cell(30)
        self.ln(4)
        self.cell(30)
        self.cell(10, 10, 'Site: www.KBC-shop.com')
        self.cell(90)
        self.cell(10, 10, 'Date de facturation: '+str(datetime.datetime.today()))
        self.line(1, 31, 255, 30)
        self.ln(20)
        # second section
        self.cell(10)
        
 
    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Times', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/1', 0, 0, 'C')

def generate_bill(qte,products_detailes,price,total,id,first_name,last_name,address):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Times', 'B', 13)
    pdf.cell(10, 10, 'FACTURER A :')
    pdf.cell(110)
    pdf.ln(7)
    pdf.cell(10)
    pdf.cell(10, 10, first_name+" "+last_name)
    pdf.cell(110)
    pdf.ln(5)
    pdf.set_font('Times', '', 10)
    pdf.cell(10)
    pdf.cell(10, 10, address)
    epw = pdf.w - 2*pdf.l_margin
    pdf.ln(5)
    # Set column width to 1/4 of effective page width to distribute content 
    # evenly across table and page
    col_width = epw/4

    # Since we do not need to draw lines anymore, there is no need to separate
    # headers from data matrix.
    pdf.set_fill_color(225, 224, 230)

    data = [['IDENTIFICATEUR','Qte','PRIX UNIT']]
    for i in products_detailes:
        data.append(i)
    th = pdf.font_size

    # Line break equivalent to 4 lines
    pdf.ln(4) 
    pdf.ln(0.5)
    pdf.set_font('Times', 'B', 13)
    
    for row in data[0]:
        pdf.cell(col_width, 2*th, str(row), border=1,fill=True)
    pdf.ln(2*th)
    keys=['name','count','price']
    for i in products_detailes:
        for k in keys:
            pdf.cell(col_width, col_width*2, str(i[k]) , border=1,align='C')
        pdf.ln()
    pdf.cell(10)
    pdf.cell(10, 10," Totale :"+str(total)+"DA")
    pdf.output('bill.pdf', 'F')


@Blueprints.route("/notification/subscription/", methods=["GET", "POST"])
def subscription():
    """
        POST creates a subscription
        GET returns vapid public key which clients uses to send around push notification
    """

    if request.method == "GET":
        return Response(response=json.dumps({"public_key": VAPID_PUBLIC_KEY}),
            headers={"Access-Control-Allow-Origin": "*"}, content_type="application/json")

    subscription_token = request.get_json("subscription_token")
    return Response(status=201, mimetype="application/json")


@Blueprints.route("/notification/storetoken", methods=['POST'])
def storetoen():
    data=request.json.get('sub_token')
    old=db.session.query(Notification).delete()
    db.session.commit()
    newNotification=Notification(body=data)
    db.session.add(newNotification)
    db.session.commit()
    return jsonify({'success':1})


@Blueprints.route('/',methods=['GET','POST'])
def index():
    Categories=Category.query.all()
    SubCategories=SubCategory.query.all()
    types=Type.query.all()
    Apperences=Apperence.query.all()
    topsales=Product.query.all()[:8]
    if topsales:
        topsales.reverse()
    if Apperences:
        Apperences.reverse()
        Apperences=Apperences[0]
    if Apperences and topsales:
        return render_template('index.html',topsales=topsales,apperences=Apperences, Categories=Categories,SubCategories=SubCategories,types=types)
    if Apperences and not topsales:
        return render_template('index.html',apperences=Apperences, Categories=Categories,SubCategories=SubCategories,types=types)
    if topsales and not Apperences:
        return render_template('index.html',topsales=topsales, Categories=Categories,SubCategories=SubCategories,types=types)

    return render_template('index.html', Categories=Categories,SubCategories=SubCategories,types=types)

@Blueprints.route('/Dashboard/import',methods=['GET','POST'])
def importe():
    if request.method=="POST":
        file=request.files["upload"].read().decode('utf-8')
        content1 = re.sub('D�signation','Designation', file)
        content2 = re.sub('%=', '=', content1)
        content3 = re.sub('VENUS DEO 200ml N�1.2.3.4','VENUS DEO 200ml N 1.2.3.4',content2)
        content4 = re.sub('�','e',content3)
        soup = bs(content4, 'lxml')
        for i in soup.findAll("row"):
            name = i["designation"]
            prix_achat = i["prix_achat"]
            prix_vente = i["tarif_01"]
            valeur_stock = i["valeur_stock"]
            stock = i["stock"]
            if ',' in valeur_stock:
                valeur_stock=''.join(valeur_stock.split(','))
            if 'TRESemm� DUO SHP+MASQ KERATIN ' == name:
                pass
            if not str(stock).isdigit():
                stock=0
            products=Product(Name=name,Description=name,Photos="download.jpeg",BuyPrice=prix_achat,SellPrice=prix_vente,Qte=stock,QteAlert=valeur_stock,AddedBy=current_user.id,categorie_id=8,sub_categorie_id=7,type_id=11)
            db.session.add(products)
        db.session.commit()
    return render_template('import.html')


@Blueprints.route('/ProductView/<int:id>',methods=['GET','POST'])
def ProductView(id):
    Categories=Category.query.all()
    SubCategories=SubCategory.query.all()
    types=Type.query.all()
    product=Product.query.filter_by(id=id).first()
    if request.method=="POST":
        name=request.form["name"]
        lastname=request.form["lastname"]
        phone=request.form["phone"]
        qte=request.form["qte"]
        wilaya = request.form["wilaya"]
        commune = request.form["Commune"]
        adress = request.form["adress"]
        string_data=[{"productname": product.Name , "name": product.id , "price": product.SellPrice, "count": qte }]
        finaldata=json.dumps(string_data)
        new_order=Order(FirstName=name,LastName=lastname,Address=adress,Phone=phone,Qte=0,products_detailes=finaldata,wilaya=wilaya,commune=commune)
        db.session.add(new_order)
        db.session.commit()
        sniper()
    return render_template('ProductView.html', product=product,Categories=Categories,SubCategories=SubCategories,types=types)


@Blueprints.route('/ViewCategoryProducts/<string:category>/',methods=['GET','POST'])
def ViewCategoryProducts(category):
    Categories=Category.query.all()
    SubCategories=SubCategory.query.all()
    types=Type.query.all()
    ProductCategorie=Category.query.filter_by(Name=category).first()
    product=Product.query.filter_by(categorie_id=ProductCategorie.id).all()

    return render_template('ViewCategoryProducts.html',product=product,Categories=Categories,SubCategories=SubCategories,types=types)


@Blueprints.route('/ViewSubCategoryProducts/<string:category>/<string:subcategory>/',methods=['GET','POST'])
def ViewSubCategoryProducts(category,subcategory):
    ProductCategorie=Category.query.filter_by(Name=category).first()
    ProductSubCategorie=SubCategory.query.filter_by(Name=subcategory).first()
    types=Type.query.all()
    product=Product.query.filter_by(categorie_id=ProductCategorie.id , sub_categorie_id=ProductSubCategorie.id).first()
    Categories=Category.query.all()
    SubCategories=SubCategory.query.all()
    return render_template('ViewSubCategoryProducts.html', product=product,Categories=Categories,SubCategories=SubCategories,types=types)

@Blueprints.route('/ViewTypeProducts/<string:category>/<string:subcategory>/<string:types>/<int:x>',methods=['GET','POST'])
def ViewTypeProducts(category,subcategory,types,x):
    ProductCategorie=Category.query.filter_by(Name=category).first()
    ProductSubCategorie=SubCategory.query.filter_by(Name=subcategory).first()
    ProductTypes=Type.query.filter_by(Name=types).first()
    products=Product.query.filter_by(categorie_id=ProductCategorie.id , sub_categorie_id=ProductSubCategorie.id,type_id=ProductTypes.id)[30*(x-1):30*x]
    Categories=Category.query.all()
    SubCategories=SubCategory.query.all()
    types=Type.query.all()
    if request.method=="POST":
        firstname = request.form["name"]
        lastname = request.form["lastname"]
        phone = request.form["phone"]
        wilaya = request.form["wilaya"]
        commune = request.form["Commune"]
        adress = request.form["adress"]
        data = request.form["test"]
        sniper()
        new_order = Order(FirstName=firstname,LastName=lastname,wilaya=wilaya,commune=commune,Address=adress,Phone=phone,Qte=0,products_detailes=data)
        db.session.add(new_order)
        db.session.commit()
        
    return render_template('ViewTYpeProducts.html', products=products,Categories=Categories,SubCategories=SubCategories,types=types)



@Blueprints.route('/Dashboard')
@login_required
def Dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    ord=getall()
    categories=Category.query.all()
    products=Product.query.all()
    subcategories=SubCategory.query.all()
    orders=Order.query.filter_by(Status="En attente").all()
    types=Type.query.all()
    users=Userr.query.all()
    print(current_user.Role)
    return render_template('Dashboard.html',ord=ord,orders=len(orders),products=len(products),categories=len(categories),subcategories=len(subcategories),types=len(types),users=len(users))


@Blueprints.route('/Dashboard/AddProduct',methods=['GET','POST'])
@login_required
def AddProduct():
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    
    user_id=current_user.id
    categories=Category.query.all()
    subcategories=SubCategory.query.all()
    types=Type.query.all()
    if not categories or not types or not subcategories:
        flash(f'Veuillez verifier les catégories ou les sous catégories ou bien les types SVP!', 'warning')
        return redirect(url_for('.Dashboard'))
    if request.method=='POST':
        name=request.form["name"]
        description=request.form["description"]
        buyprice=request.form["buyprice"]
        sellprice=request.form["sellprice"]
        qte=request.form["qte"]
        qtealert=request.form["qtealert"]
        category=request.form.get("category")
        subcategory=request.form.get("subcategory")
        types=request.form.get("types")
        if request.files:
            photos=request.files['files']
            if photos.filename == '':
                product=Product(Name=name, Description=description, BuyPrice=buyprice, SellPrice=sellprice, categorie_id=int(category), sub_categorie_id=int(subcategory),type_id=int(types), Qte=qte, QteAlert=qtealert, AddedBy=str(user_id))
                db.session.add(product)
                db.session.commit()
                flash(f"Le Produit a été Ajouté mais sans photos. ", "success")
                return redirect(url_for('.AddProduct'))
            if photos.filename != '':
                photos_list=''
                for i in request.files.getlist('files'):
                    verifying = secure_filename(i.filename)
                    if verifying:
                        filename_extention = i.filename.split('.')[1]
                        if filename_extention not in ALLOWED_EXTENSIONS:
                            flash(f"produit n'a pas été ajouté à la base de donnée ,format de fichier unsuportable",'danger')
                            return redirect(url_for('.AddProduct'))
                        else:
                            unique_filename=uuid.uuid4()
                            i.filename =str(unique_filename)+'.'+filename_extention
                            photos_list=photos_list+str(i.filename)
                            new_photo_list=photos_list.split(',')
                            i.save(os.path.join(UPLOAD_FOLDER, i.filename))
                
                product=Product(Name=name, Description=description, BuyPrice=buyprice, SellPrice=sellprice, categorie_id=int(category), sub_categorie_id=int(subcategory), type_id=int(types) ,Qte=qte, QteAlert=qtealert, Photos=photos_list, AddedBy=str(user_id))
                db.session.add(product)
                db.session.commit()
                flash(f"Le Produit a été Ajouté ", "success")
                return redirect(url_for('.AllProducts'))
    return render_template('add_product.html',categories=categories,subcategories=subcategories,types=types)


@Blueprints.route('/Dashboard/all_products/<int:id>')
@login_required
def AllProducts(id):
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    
    products=Product.query.all()[30*(id-1):30*id]

    
    return render_template('all_products.html',AllProducts=products)

@Blueprints.route('/Dashboard/EditProduct/<int:id>',methods=['GET','POST'])
@login_required
def EditProduct(id):
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    
    product=Product.query.filter_by(id=int(id)).first()
    categories=Category.query.all()
    subcategories=SubCategory.query.all()
    types=Type.query.all()
    if request.method=='POST':
        name=request.form["name"]
        description=request.form["description"]
        buyprice=request.form["buyprice"]
        sellprice=request.form["sellprice"]
        qte=request.form["qte"]
        qtealert=request.form["qtealert"]
        category=request.form.get("category")
        subcategory=request.form.get("subcategory")
        types=request.form.get("types")
        photos=request.files['files']
        if photos.filename != '':
            photos_list=''
            for i in request.files.getlist('files'):
                verifying = secure_filename(i.filename)
                if verifying:
                    filename_extention = i.filename.split('.')[1]
                    if filename_extention not in ALLOWED_EXTENSIONS:
                        flash(f"produit n'a pas été ajouté à la base de donnée ,format de fichier unsuportable",'danger')
                        return redirect(url_for('.AddProduct'))
                    else:
                        unique_filename=uuid.uuid4()
                        i.filename =str(unique_filename)+'.'+filename_extention
                        photos_list=photos_list+str(i.filename)+';'
                        i.save(os.path.join(UPLOAD_FOLDER, i.filename))
            product.Name=name
            product.Description=description
            product.BuyPrice=buyprice
            product.SellPrice=sellprice
            product.Qte=qte
            product.QteAlert=qtealert
            product.categorie_id=int(category)
            product.sub_categorie_id=int(subcategory)
            product.type_id=int(types)
            product.Photos=photos_list    
            db.session.commit()
            flash(f"Le Produit a été Modifier ", "warning")
            return redirect(url_for('.EditProduct',id=id))
    
    return render_template('edit_product.html',product=product,categories=categories,subcategories=subcategories,types=types)


@Blueprints.route('/Dashboard/EditProduct/DeleteProduct/<int:id>',methods=['GET','POST'])
@login_required
def DeleteProduct(id):
    product=Product.query.filter_by(id=id).first()
    if request.method=="POST":
        db.session.delete(product)
        db.session.commit()
        flash(f'le produit a été supprimer','warning')
        return redirect(url_for('.AllProducts'))
    return render_template("DeleteProduct.html",product=product)


@Blueprints.route('/Dashboard/Stats')
@login_required
def Stats():
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    
    
    return render_template('stats.html')

@Blueprints.route('/Dashboard/Orders', methods=['GET','POST'])
@login_required
def Orders():
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    Orders=Order.query.filter_by(Status='En attente').all()
    if request.method == "POST" and 'valider' in request.form:
        id_cmd=request.form.get('valider')
        order=Order.query.filter_by(id=int(id_cmd)).first()
        order.Status='Livré'
        db.session.add(order)
        db.session.commit()
        return redirect(url_for('.Orders'))
    return render_template('Orders.html',Orders=Orders)

@Blueprints.route('/Dashboard/OldOrder', methods=['GET','POST'])
@login_required
def OldOrder():
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    old = Order.query.filter_by(Status='Livré').all()

    return render_template('OldOrder.html',old=old)


@Blueprints.route('/Dashboard/Orders/ViewOrder/<int:id>',methods=['GET','POST'])
@login_required
def ViewOrder(id):
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    
    Orders=Order.query.filter_by(id=id).first()
    jsonstring=json.loads(Orders.products_detailes)
    jsonstring2=json.dumps(jsonstring)
    ProductList=list()
    qte='0'
    price='0'
    total=0
    my_product="test"
    address=Orders.Address
    date=Orders.Created_at
    for i in jsonstring:
        ProductList.append(Product.query.filter_by(id=int(i["name"])).first())
        price=i["price"]
        count=i["count"]
        total=total+(float(price)*float(count))
    if 'bill' in request.form and request.method=='POST':
        generate_bill(qte,jsonstring,price,total,id,Orders.FirstName,Orders.LastName,address)
        f = open('bill.pdf', 'rb')
        return send_file(f, attachment_filename='bill.pdf')
    return render_template('ViewOrder.html',Orders=Orders,ProductDetailes=jsonstring,ProductList=ProductList)

@Blueprints.route('/Dashboard/DeleteOrders/<int:id>',methods=['GET','POST'])
@login_required
def DeleteOrders(id):
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    order=Order.query.filter_by(id=id).first()
    if request.method =="POST":
        db.session.delete(order)
        db.session.commit()
        flash(f'la commande a été supprimmer avec success','success')
        return redirect(url_for('.Orders'))
    return render_template('DeleteOrders.html' , order=order)

@Blueprints.route('/Dashboard/AddCategory',methods=['GET','POST'])
@login_required
def AddCategory():
    
    if request.method == "POST":
        categoryName=request.form["name"]
        category=Category(Name=categoryName)
        db.session.add(category)
        db.session.commit()
        flash(f"La catégorie a été ajoutée avec succès", "success")
        return redirect(url_for('.ManageCategories'))
    
    return render_template('add_category.html')

@Blueprints.route('/Dashboard/ManageCategories',methods=['GET','POST'])
@login_required
def ManageCategories():
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    
    Categories=Category.query.all()
    
    return render_template('ManageCategories.html',Categories=Categories)


@Blueprints.route('/Dashboard/EditCategories/<int:id>',methods=['GET','POST'])
@login_required
def EditCategories(id):
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    
    Categories=Category.query.filter_by(id=id).first()
    if request.method=="POST":
        name=request.form["name"]
        Categories.Name=name
        db.session.commit()
        flash(f"Le Produit a été Modifier ", "warning")
        
    
    return render_template('EditCategories.html',Categories=Categories)

@Blueprints.route('/Dashboard/DeleteCategories/<int:id>',methods=['GET','POST'])
@login_required
def DeleteCategories(id):
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    
    Categories=Category.query.filter_by(id=id).first()
    if request.method=="POST":
        db.session.query(Category).filter_by(id=int(id)).delete(synchronize_session='fetch')
        db.session.commit()
        flash(f"La Catégorie a été supprimé ", "success")
        return redirect(url_for('.ManageCategories'))
        
    
    return render_template('DeleteCategories.html',Categories=Categories)



@Blueprints.route('/Dashboard/AddSubCategory',methods=['GET','POST'])
@login_required
def AddSubCategory():
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    
    categories=Category.query.all()
    if request.method == "POST":
        subCategorieName=request.form["name"]
        category = request.form.get("category")
        subCategorie=SubCategory(Name=subCategorieName,CategoryId=int(category))
        db.session.add(subCategorie)
        db.session.commit()
        flash(f"La sous catégorie a été ajoutée avec succès", "success")
        return redirect(url_for('.ManageSubCategories'))
    return render_template('add_sub_category.html',Categories=categories)



@Blueprints.route('/Dashboard/ManageSubCategories',methods=['GET','POST'])
@login_required
def ManageSubCategories():
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    
    SubCategories=SubCategory.query.all()
    Categories=Category.query.all()
    
    return render_template('ManageSubCategories.html', SubCategories=SubCategories,Categories=Categories)


@Blueprints.route('/Dashboard/EditSubCategories/<int:id>',methods=['GET','POST'])
@login_required
def EditSubCategories(id):
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    
    SubCategories=SubCategory.query.filter_by(id=id).first()
    Categories=Category.query.all()
    if request.method == "POST":
        name=request.form["name"]
        category=request.form["category"]
        SubCategories.Name=name
        SubCategories.CategoryId=int(category)
        db.session.commit()
        flash(f"La sous catégorie a été Modifier avec succès", "warning")
        return redirect(url_for('.ManageSubCategories'))
    
    return render_template('EditSubCategories.html',SubCategories=SubCategories,Categories=Categories)



@Blueprints.route('/Dashboard/DeleteSubCategories/<int:id>',methods=['GET','POST'])
@login_required
def DeleteSubCategories(id):
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    
    SubCategories=SubCategory.query.filter_by(id=id).first()
    if request.method=="POST":
        #db.session.query(SubCategory).filter_by(id=int(id)).delete(synchronize_session='fetch')
        db.session.delete(SubCategories)
        db.session.commit()
        flash(f"La Sous Catégorie a été supprimé ", "danger")
        return redirect(url_for('.ManageSubCategories'))
        
    
    return render_template('DeleteSubCategories.html',SubCategories=SubCategories)


@Blueprints.route('/Dashboard/AddType',methods=['GET','POST'])
@login_required
def AddType():
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    
    categories=Category.query.all()
    subcategories=SubCategory.query.all()
    if request.method == "POST":
        TypeName=request.form["name"]
        category = request.form.get("category")
        subcategory=request.form.get("subcategory")        
        Types=Type(Name=TypeName,CategoryId=int(category),SubCategoryId=int(subcategory))
        db.session.add(Types)
        db.session.commit()
        flash(f"Le Type a été ajoutée avec succès", "success")
        return redirect(url_for('.ManageTypes'))
        
    return render_template('AddType.html', Categories=categories,SubCategories=subcategories)

@Blueprints.route('/Dashboard/ManageTypes',methods=['GET','POST'])
@login_required
def ManageTypes():
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    
    types=Type.query.all()
    SubCategories=SubCategory.query.all()
    Categories=Category.query.all()
    
    return render_template('ManageTypes.html',types=types,SubCategories=SubCategories,Categories=Categories)


@Blueprints.route('/Dashboard/EditTypes/<int:id>',methods=['GET','POST'])
@login_required
def EditTypes(id):
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    types=Type.query.filter_by(id=id).first()
    SubCategories=SubCategory.query.all()
    Categories=Category.query.all()
    if request.method=="POST":
        name=request.form["name"]
        category=request.form["category"]
        subcategory=request.form["subcategory"]
        types.Name=name
        types.CategoryId=int(category)
        types.SubCategoryId=int(subcategory)
        db.session.commit()
        flash(f"Le Type a été Modifier avec succès", "warning")
        return redirect(url_for('.ManageTypes'))

    return render_template('EditTypes.html',types=types,SubCategories=SubCategories,Categories=Categories)



@Blueprints.route('/Dashboard/DeleteType/<int:id>',methods=['GET','POST'])
@login_required
def DeleteType(id):
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    types=Type.query.filter_by(id=id).first()
    if request.method=="POST":
        db.session.query(Type).filter_by(id=int(id)).delete(synchronize_session='fetch')
        db.session.commit()
        flash(f"Le Type a été supprimé ", "success")
        
    return render_template('DeleteType.html',types=types)

@Blueprints.route('/Dashboard/AddUser',methods=['GET', 'POST'])
@login_required
def AddUser():
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    users=Userr.query.all()
    if request.method == 'POST':
        First_name=request.form["firstname"]
        Last_name=request.form["lastname"]
        Email=request.form["email"]
        for i in users:
            if i.Mail==Email:
                flash(f"l'email éxiste déja dans la Base de Donnée veuillez reessayer!",'warning')
                return redirect(url_for('.AddUser'))
        Password=request.form["password"].encode('utf-8')
        Phone=request.form["telephone"]
        Role=request.form["role"]
        salt=bcrypt.gensalt()
        hashed = bcrypt.hashpw(Password, salt)
        if request.files:
            photo=request.files['photo']
            if photo.filename == '':
                user=Userr(FirstName=First_name, LastName=Last_name, Mail=Email, Password=hashed, Phone=Phone)
                db.session.add(user)
                db.session.commit()
                flash(f"L'utilisateur a été Ajouté ", "success")
                return redirect(url_for('.AddUser'))
                
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(UPLOAD_FOLDER, filename))
                user=Userr(FirstName=First_name, LastName=Last_name, Mail=Email, Password=hashed, Phone=Phone,Photo=filename)
                db.session.add(user)
                db.session.commit()
                flash(f"L'utilisateur a été Ajouté ", "success")
                return redirect(url_for('.AddUser'))
                
    return render_template('AddUser.html')

@Blueprints.route('/Dashboard/ManageUsers',methods=['GET', 'POST'])
@login_required
def ManageUsers():
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    users=Userr.query.all()
    return render_template('ManageUsers.html',users=users)


@Blueprints.route('/Dashboard/EditUser/<int:id>',methods=['GET', 'POST'])
@login_required
def EditUser(id):
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    users=Userr.query.filter_by(id=id).first_or_404()
    if request.method == 'POST':
        First_name=request.form["firstname"]
        Last_name=request.form["lastname"]
        Email=request.form["email"]
        Password=request.form["password"].encode('utf-8')
        Phone=request.form["telephone"]
        Role=request.form["role"]
        salt=bcrypt.gensalt()
        hashed = bcrypt.hashpw(Password, salt)
        if request.files:
            photo=request.files['photo']
            if photo.filename == '':
                users.FirstName=First_name
                users.LastName=Last_name
                users.Mail=Email
                users.Password=hashed
                users.Phone=Phone
                users.Role=Role
                db.session.add(users)
                db.session.commit()
                flash(f"L'utilisateur a été Modifié ", "warning")
                return redirect(url_for('.ManageUsers'))
                
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(UPLOAD_FOLDER, filename))
                users.FirstName=First_name
                users.LastName=Last_name
                users.Mail=Email
                users.Password=hashed
                users.Phone=Phone
                users.Role=Role
                users.Photo=filename
                db.session.add(users)
                db.session.commit()
                flash(f"L'utilisateur a été Modifié ", "warning")
                return redirect(url_for('.ManageUsers'))
    

    return render_template('EditUser.html',users=users)

@Blueprints.route('/Dashboard/DeleteUser/<int:id>',methods=['GET', 'POST'])
@login_required
def DeleteUser(id):
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    users=Userr.query.filter_by(id=id).first_or_404()
    if request.method=="POST":
        db.session.delete(users)
        db.session.commit()
        flash(f"l'utilisateur' a été supprimer",'warning')
        return redirect(url_for('.ManageUsers'))

    

    return render_template('DeleteUser.html',users=users)


@Blueprints.route('/Dashboard/Apperences',methods=['GET', 'POST'])
@login_required
def Apperences():
    apps=Apperence.query.first()
    if not current_user.is_authenticated:
        return redirect(url_for('.Connexion'))
    if request.method=="POST":
        title=request.form["title"]
        description=request.form["description"]         
        photos_list=''
        topsalesphotos_list=''
        if request.files:
            for i in request.files.getlist('files'):
                verifying = secure_filename(i.filename)
                if verifying:
                    filename_extention = i.filename.split('.')[1]
                    unique_filename=uuid.uuid4()
                    i.filename =str(unique_filename)+'.'+filename_extention
                    photos_list=photos_list+str(i.filename)+';'
                    new_photo_list=photos_list.split(',')
                    i.save(os.path.join(UPLOAD_FOLDER, i.filename))
            for i in request.form.getlist('slide'):
                
                verifying = secure_filename(i)
                if verifying:
                    filename_extention = i.split('.')[1]
                    unique_filename=uuid.uuid4()
                    i=str(unique_filename)+'.'+filename_extention
                    topsalesphotos_list=topsalesphotos_list+str(i)+';'
                    new_photo_list=photos_list.split(',')
            apperences=Apperence(Title=title,Description=description,SlidePhoto=photos_list,TopSales=topsalesphotos_list)
            db.session.add(apperences)
            db.session.commit()
            flash(f"La page d'acceuille a été mise a jour","warning")
            return redirect(url_for('.Apperences'))
    
    
    return render_template('Apperence.html',slidephotos=os.listdir(UPLOAD_FOLDER))

@Blueprints.route('/<string:category>/<string:subcategory>')
def Products(category,subcategory):
    categories=Category.query.filter_by(Name=category).first()
    sub_categories=SubCategory.query.filter_by(Name=subcategory).first()
    products=Product.query.filter_by(categorie_id=category.id,sub_categorie_id=sub_categories.id).all()
    if products:
        return render_template('Products.html', products=products)
    else:
        return render_template('Products.html')


@Blueprints.route('/Connexion',methods=['GET','POST'])
def Connexion():
    if current_user.is_authenticated:
        return redirect(url_for('.Dashboard'))
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]
        userr=Userr.query.filter_by(Mail=email).first()
        if userr and Bcrypt.check_password_hash(userr.Password, password):
            login_user(userr)
            return redirect(url_for('.Dashboard'))
        else:
            flash(f"L'email ou le mot de passe est incorrect'", "danger")
            return redirect(url_for('.Connexion'))
    return render_template('login.html')


@Blueprints.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))