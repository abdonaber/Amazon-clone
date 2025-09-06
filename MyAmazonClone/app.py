import os
from flask import Flask, render_template, url_for, flash, redirect, request, session
from .extensions import db, login_manager
from flask_login import login_user, current_user, logout_user, login_required
from .models import User, Product, Order
from .forms import RegistrationForm, LoginForm


app = Flask(__name__)

# --- App Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')
app.instance_path = instance_path
# Create instance folder with specific permissions if it doesn't exist
os.makedirs(app.instance_path, mode=0o755, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'store.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'a_super_secret_key_for_development'


# --- Initialize Extensions ---
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Database Initialization on Startup ---
with app.app_context():
    db_file_path = os.path.join(app.instance_path, 'store.db')
    # This check is to prevent re-seeding on every app restart in a real environment
    if not os.path.exists(db_file_path):
        print("--- Database not found, creating and seeding... ---")
        db.create_all()
        # Add sample products
        products = [
            Product(name='Laptop', description='A powerful laptop for all your needs.', price=1200.50, image_url='https://placehold.co/600x400/EEE/31343C?text=Laptop', stock_quantity=10),
            Product(name='Smartphone', description='A smart and sleek phone.', price=800.00, image_url='https://placehold.co/600x400/EEE/31343C?text=Smartphone', stock_quantity=25),
            Product(name='Headphones', description='Noise-cancelling headphones.', price=150.75, image_url='https://placehold.co/600x400/EEE/31343C?text=Headphones', stock_quantity=50),
            Product(name='Coffee Maker', description='Brews the perfect cup of coffee.', price=89.99, image_url='https://placehold.co/600x400/EEE/31343C?text=Coffee+Maker', stock_quantity=30)
        ]
        db.session.add_all(products)
        db.session.commit()
        # Explicitly set permissions to be writable
        os.chmod(db_file_path, 0o666)
        print("--- Database created and seeded. ---")


# --- Routes ---
@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/contact")
def contact():
    return render_template('contact.html', title='Contact')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/add_to_cart/<int:product_id>", methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    cart[product_id_str] = cart.get(product_id_str, 0) + 1
    session['cart'] = cart
    flash(f'"{product.name}" has been added to your cart!', "success")
    return redirect(request.referrer or url_for('home'))


@app.route("/cart")
def cart():
    cart = session.get('cart', {})
    cart_items = []
    total_price = 0
    if cart:
        product_ids = [int(pid) for pid in cart.keys()]
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        product_map = {product.id: product for product in products}
        for product_id, quantity in cart.items():
            product = product_map.get(int(product_id))
            if product:
                subtotal = product.price * quantity
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
                total_price += subtotal
    return render_template('cart.html', title='Shopping Cart', cart_items=cart_items, total_price=total_price)


@app.route("/update_cart/<int:product_id>", methods=['POST'])
def update_cart(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    try:
        quantity = int(request.form['quantity'])
    except (ValueError, KeyError):
        flash('Invalid quantity specified.', 'danger')
        return redirect(url_for('cart'))
    if product_id_str in cart:
        if quantity > 0:
            cart[product_id_str] = quantity
            flash('Cart updated successfully.', 'success')
        else:
            del cart[product_id_str]
            flash('Item removed from cart.', 'success')
    session['cart'] = cart
    return redirect(url_for('cart'))


@app.route("/remove_from_cart/<int:product_id>", methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        cart.pop(product_id_str, None)
        flash('Item removed from your cart.', 'success')
    session['cart'] = cart
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty. Nothing to checkout.', 'info')
        return redirect(url_for('cart'))
    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    product_map = {product.id: product for product in products}
    for product_id, quantity in cart.items():
        product = product_map.get(int(product_id))
        if product:
            total_price = product.price * quantity
            order = Order(
                user_id=current_user.id,
                product_id=product.id,
                quantity=quantity,
                total_price=total_price
            )
            db.session.add(order)
    db.session.commit()
    session.pop('cart', None)
    flash('Thank you for your order! It has been placed successfully.', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
