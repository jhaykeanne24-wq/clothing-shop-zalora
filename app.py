from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import MySQLdb.cursors
import re
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'clothing_shop')
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

mysql = MySQL(app)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Home Page
@app.route('/')
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM products LIMIT 12')
    products = cursor.fetchall()
    cursor.close()
    return render_template('index.html', products=products)

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9_]{5,}', username):
            msg = 'Username must be at least 5 characters and contain only letters, numbers, and underscores!'
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                         (username, email, hashed_password))
            mysql.connection.commit()
            msg = 'Successfully registered! Please log in.'
        cursor.close()
    
    return render_template('register.html', msg=msg)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        cursor.close()
        
        if account and check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect username or password!'
    
    return render_template('login.html', msg=msg)

# Dashboard (Profile)
@app.route('/dashboard')
@login_required
def dashboard():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
    user = cursor.fetchone()
    cursor.close()
    return render_template('dashboard.html', user=user)

# Update Profile
@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    email = request.form.get('email')
    phone = request.form.get('phone', '')
    address = request.form.get('address', '')
    
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        return jsonify({'success': False, 'msg': 'Invalid email!'})
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE users SET email = %s, phone = %s, address = %s WHERE id = %s',
                 (email, phone, address, session['id']))
    mysql.connection.commit()
    cursor.close()
    
    return jsonify({'success': True, 'msg': 'Profile updated successfully!'})

# Products Listing
@app.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '', type=str)
    search = request.args.get('search', '', type=str)
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    query = 'SELECT * FROM products WHERE 1=1'
    params = []
    
    if category:
        query += ' AND category = %s'
        params.append(category)
    
    if search:
        query += ' AND (name LIKE %s OR description LIKE %s)'
        params.extend([f'%{search}%', f'%{search}%'])
    
    query += ' LIMIT %s OFFSET %s'
    params.extend([12, (page - 1) * 12])
    
    cursor.execute(query, params)
    products_list = cursor.fetchall()
    cursor.close()
    
    return render_template('products.html', products=products_list, page=page)

# Product Detail
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
    product = cursor.fetchone()
    cursor.close()
    
    if not product:
        return redirect(url_for('products'))
    
    return render_template('product_detail.html', product=product)

# Shopping Cart
@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    products_list = []
    total_price = 0
    
    for item in cart_items:
        cursor.execute('SELECT * FROM products WHERE id = %s', (item['product_id'],))
        product = cursor.fetchone()
        if product:
            product['quantity'] = item['quantity']
            product['subtotal'] = product['price'] * item['quantity']
            products_list.append(product)
            total_price += product['subtotal']
    
    cursor.close()
    return render_template('cart.html', cart_items=products_list, total=total_price)

# Add to Cart (AJAX)
@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    existing_item = next((item for item in cart if item['product_id'] == product_id), None)
    
    if existing_item:
        existing_item['quantity'] += quantity
    else:
        cart.append({'product_id': product_id, 'quantity': quantity})
    
    session['cart'] = cart
    session.modified = True
    
    return jsonify({'success': True, 'msg': 'Added to cart!', 'cart_count': len(cart)})

# Remove from Cart
@app.route('/remove-from-cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['product_id'] != product_id]
        session.modified = True
    return jsonify({'success': True})

# Checkout
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        cart_items = session.get('cart', [])
        if not cart_items:
            return jsonify({'success': False, 'msg': 'Cart is empty!'})
        
        total_price = 0
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        for item in cart_items:
            cursor.execute('SELECT price FROM products WHERE id = %s', (item['product_id'],))
            product = cursor.fetchone()
            if product:
                total_price += product['price'] * item['quantity']
        
        # Create order
        cursor.execute('INSERT INTO orders (user_id, total_price, status) VALUES (%s, %s, %s)',
                     (session['id'], total_price, 'pending'))
        mysql.connection.commit()
        order_id = cursor.lastrowid
        
        # Add order items
        for item in cart_items:
            cursor.execute('INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)',
                         (order_id, item['product_id'], item['quantity']))
        mysql.connection.commit()
        cursor.close()
        
        session['cart'] = []
        session.modified = True
        
        return jsonify({'success': True, 'msg': 'Order placed successfully!', 'order_id': order_id})
    
    return render_template('checkout.html')

# Orders History
@app.route('/orders')
@login_required
def orders():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC', (session['id'],))
    user_orders = cursor.fetchall()
    cursor.close()
    return render_template('orders.html', orders=user_orders)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
