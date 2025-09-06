from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

# Define the base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Define and create the instance folder path
instance_path = os.path.join(basedir, 'instance')
app.instance_path = instance_path
os.makedirs(app.instance_path, exist_ok=True)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'store.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)


if __name__ == '__main__':
    app.run(debug=True)


# Import models here to avoid circular import issues and make them known to the CLI
from .models import User, Product, Order

@app.cli.command('init-db')
def init_db_command():
    """Clears the existing data, creates new tables, and seeds with sample data."""
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
