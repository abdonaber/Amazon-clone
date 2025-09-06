import os
from flask import Flask, render_template, url_for, flash, redirect, request
from .extensions import db, login_manager
from flask_login import login_user, current_user, logout_user
from .models import User, Product, Order
from .forms import RegistrationForm, LoginForm


app = Flask(__name__)

# --- App Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')
app.instance_path = instance_path
os.makedirs(app.instance_path, exist_ok=True)
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


# --- Routes ---
@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)


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


# --- CLI Commands ---
@app.cli.command('init-db')
def init_db_command():
    """Clears the existing data, creates new tables, and seeds with sample data."""
    with app.app_context():
        db.drop_all()
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
        print('Initialized the database and seeded with sample products.')


if __name__ == '__main__':
    app.run(debug=True)
