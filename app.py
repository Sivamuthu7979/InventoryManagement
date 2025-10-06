from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Product(db.Model):
    product_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
class Location(db.Model):
    location_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
class ProductMovement(db.Model):
    movement_id = db.Column(db.String, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    from_location = db.Column(db.String, db.ForeignKey('location.location_id'), nullable=True)
    to_location = db.Column(db.String, db.ForeignKey('location.location_id'), nullable=True)
    product_id = db.Column(db.String, db.ForeignKey('product.product_id'))
    qty = db.Column(db.Integer, nullable=False)
@app.route('/')
def index():
    return redirect(url_for('products'))
@app.route('/products')
def products():
    items = Product.query.order_by(Product.name).all()
    return render_template('products.html', products=items)
@app.route('/products/add', methods=['GET','POST'])
def add_product():
    if request.method == 'POST':
        pid = request.form['product_id'].strip()
        name = request.form['name'].strip()
        if pid and name:
            db.session.add(Product(product_id=pid, name=name))
            db.session.commit()
            return redirect(url_for('products'))
    return render_template('product_form.html', action='Add', product=None)
@app.route('/products/<product_id>/edit', methods=['GET','POST'])
def edit_product(product_id):
    p = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        p.name = request.form['name'].strip()
        db.session.commit()
        return redirect(url_for('products'))
    return render_template('product_form.html', action='Edit', product=p)
@app.route('/locations')
def locations():
    items = Location.query.order_by(Location.name).all()
    return render_template('locations.html', locations=items)
@app.route('/locations/add', methods=['GET','POST'])
def add_location():
    if request.method == 'POST':
        lid = request.form['location_id'].strip()
        name = request.form['name'].strip()
        if lid and name:
            db.session.add(Location(location_id=lid, name=name))
            db.session.commit()
            return redirect(url_for('locations'))
    return render_template('location_form.html', action='Add', location=None)
@app.route('/locations/<location_id>/edit', methods=['GET','POST'])
def edit_location(location_id):
    l = Location.query.get_or_404(location_id)
    if request.method == 'POST':
        l.name = request.form['name'].strip()
        db.session.commit()
        return redirect(url_for('locations'))
    return render_template('location_form.html', action='Edit', location=l)
@app.route('/movements')
def movements():
    items = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
    products = Product.query.order_by(Product.name).all()
    locations = Location.query.order_by(Location.name).all()
    return render_template('movements.html', movements=items, products=products, locations=locations)
@app.route('/movements/add', methods=['GET','POST'])
def add_movement():
    products = Product.query.order_by(Product.name).all()
    locations = Location.query.order_by(Location.name).all()
    if request.method == 'POST':
        mid = request.form['movement_id'].strip()
        pid = request.form['product_id']
        qty = int(request.form['qty'])
        from_loc = request.form.get('from_location') or None
        to_loc = request.form.get('to_location') or None
        if mid and pid and qty:
            db.session.add(ProductMovement(movement_id=mid, product_id=pid, qty=qty, from_location=from_loc, to_location=to_loc))
            db.session.commit()
            return redirect(url_for('movements'))
    return render_template('movement_form.html', products=products, locations=locations)
@app.route('/report')
def report():
    products = Product.query.order_by(Product.name).all()
    locations = Location.query.order_by(Location.name).all()
    rows = []
    for p in products:
        for l in locations:
            incoming = db.session.query(db.func.coalesce(db.func.sum(ProductMovement.qty),0)).filter(ProductMovement.product_id==p.product_id, ProductMovement.to_location==l.location_id).scalar() or 0
            outgoing = db.session.query(db.func.coalesce(db.func.sum(ProductMovement.qty),0)).filter(ProductMovement.product_id==p.product_id, ProductMovement.from_location==l.location_id).scalar() or 0
            balance = incoming - outgoing
            if balance != 0:
                rows.append((p.name, l.name, balance))
    return render_template('report.html', rows=rows)
if __name__ == '__main__':
    app.run(debug=True)