import os
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import secrets
import json

from flask import Flask, request, jsonify, session, make_response, send_from_directory
from flask_cors import CORS
import jwt
import pymysql

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'car-shop-flask-secret-2024')
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'car-shop-secret-key-2024')
ALGORITHM = "HS256"

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'car_shop',
    'charset': 'utf8mb4'
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

def init_database():
    conn = pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        charset='utf8mb4'
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS car_shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
    finally:
        conn.close()

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(50) PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(64) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    role VARCHAR(20) DEFAULT 'user',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cars (
                    id VARCHAR(50) PRIMARY KEY,
                    brand VARCHAR(50) NOT NULL,
                    model VARCHAR(50) NOT NULL,
                    year INT,
                    price DECIMAL(12, 2) NOT NULL,
                    category VARCHAR(50),
                    color VARCHAR(30),
                    image TEXT,
                    description TEXT,
                    specs JSON,
                    features JSON,
                    stock INT DEFAULT 0,
                    sales INT DEFAULT 0
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(50) NOT NULL,
                    car_id VARCHAR(50) NOT NULL,
                    quantity INT DEFAULT 1,
                    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_user_car (user_id, car_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id VARCHAR(50) PRIMARY KEY,
                    user_id VARCHAR(50) NOT NULL,
                    items JSON NOT NULL,
                    total DECIMAL(12, 2) NOT NULL,
                    status VARCHAR(30) DEFAULT 'pending_payment',
                    payment_method VARCHAR(30) DEFAULT 'wechat',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    paid_at DATETIME
                )
            """)
        conn.commit()
    finally:
        conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def generate_token(user_id, username, role='user'):
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        if token.startswith('Bearer '):
            token = token[7:]
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
        request.user = payload
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        if token.startswith('Bearer '):
            token = token[7:]
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
        if payload.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        request.user = payload
        return f(*args, **kwargs)
    return decorated

def init_sample_data():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM cars")
            if cursor.fetchone()['count'] == 0:
                cars = [
                    {"id": "car001", "brand": "特斯拉", "model": "Model 3", "year": 2024, "price": 249900, "category": "电动车", "color": "黑色", "image": "https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=800", "description": "特斯拉Model 3是一款高性能纯电动轿车，拥有出色的续航里程和加速性能。", "specs": {"engine": "纯电动", "horsepower": "283马力", "torque": "404牛·米", "battery": "60kWh", "range": "556km", "0_100": "5.6秒", "transmission": "单速变速箱", "drive": "后驱"}, "features": ["自动驾驶", "全景天窗", "智能召唤", "OTA升级", "15寸中控屏"], "stock": 10, "sales": 156},
                    {"id": "car002", "brand": "特斯拉", "model": "Model Y", "year": 2024, "price": 299900, "category": "电动车", "color": "白色", "image": "https://images.unsplash.com/photo-1619767886558-efdc259cde1a?w=800", "description": "特斯拉Model Y是一款全能纯电动SUV，空间宽敞，性能卓越。", "specs": {"engine": "纯电动", "horsepower": "384马力", "torque": "510牛·米", "battery": "75kWh", "range": "615km", "0_100": "5.0秒", "transmission": "单速变速箱", "drive": "四驱"}, "features": ["七座布局", "自动驾驶", "全景天窗", "电动尾门", "OTA升级"], "stock": 8, "sales": 98},
                    {"id": "car003", "brand": "宝马", "model": "BMW i4", "year": 2024, "price": 369900, "category": "电动车", "color": "蓝色", "image": "https://images.unsplash.com/photo-1617788138017-80ad40651399?w=800", "description": "宝马i4是一款纯电动轿跑，将运动性能与豪华品质完美结合。", "specs": {"engine": "纯电动", "horsepower": "340马力", "torque": "430牛·米", "battery": "83.9kWh", "range": "625km", "0_100": "5.7秒", "transmission": "单速变速箱", "drive": "后驱"}, "features": ["运动座椅", "哈曼卡顿音响", "自动驾驶辅助", "无线充电", "手势控制"], "stock": 5, "sales": 42},
                    {"id": "car004", "brand": "奔驰", "model": "EQE", "year": 2024, "price": 479900, "category": "电动车", "color": "银色", "image": "https://images.unsplash.com/photo-1619043354140-9d697274b24c?w=800", "description": "奔驰EQE是纯电动豪华轿车，提供卓越的舒适性和先进的科技配置。", "specs": {"engine": "纯电动", "horsepower": "292马力", "torque": "565牛·米", "battery": "96.1kWh", "range": "717km", "0_100": "6.5秒", "transmission": "单速变速箱", "drive": "后驱"}, "features": ["柏林之声", "空气悬挂", "全景天窗", "智能驾驶", "后轮转向"], "stock": 3, "sales": 28},
                    {"id": "car005", "brand": "比亚迪", "model": "汉EV", "year": 2024, "price": 229900, "category": "电动车", "color": "红色", "image": "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?w=800", "description": "比亚迪汉EV是国产高端纯电动轿车，性价比极高。", "specs": {"engine": "纯电动", "horsepower": "222马力", "torque": "330牛·米", "battery": "76.9kWh", "range": "605km", "0_100": "7.9秒", "transmission": "单速变速箱", "drive": "前驱"}, "features": ["智能旋转屏", "DiLink系统", "全景影像", "自动泊车", "远程控制"], "stock": 15, "sales": 234},
                    {"id": "car006", "brand": "奥迪", "model": "e-tron GT", "year": 2024, "price": 999900, "category": "电动车", "color": "黑色", "image": "https://images.unsplash.com/photo-1614200179396-23677285d59d?w=800", "description": "奥迪e-tron GT是高性能纯电动轿跑，源自保时捷Taycan平台。", "specs": {"engine": "纯电动", "horsepower": "476马力", "torque": "630牛·米", "battery": "93.4kWh", "range": "488km", "0_100": "4.1秒", "transmission": "单速变速箱", "drive": "四驱"}, "features": ["矩阵LED", "空气悬挂", "激光大灯", "Bang & Olufsen音响", "碳纤维车顶"], "stock": 2, "sales": 15},
                    {"id": "car007", "brand": "理想", "model": "L9", "year": 2024, "price": 459900, "category": "混动", "color": "银色", "image": "https://images.unsplash.com/photo-1633511090164-b43840ea1607?w=800", "description": "理想L9是一款大型增程式SUV，家庭出行首选。", "specs": {"engine": "1.5T增程器+双电机", "horsepower": "449马力", "torque": "620牛·米", "battery": "44.5kWh", "range": "1315km", "0_100": "5.3秒", "transmission": "单速变速箱", "drive": "四驱"}, "features": ["六座布局", "后排娱乐屏", "空气悬挂", "NOA导航辅助", "冰箱"], "stock": 6, "sales": 187},
                    {"id": "car008", "brand": "蔚来", "model": "ET7", "year": 2024, "price": 428000, "category": "电动车", "color": "白色", "image": "https://images.unsplash.com/photo-1669633935986-1c2a34223e05?w=800", "description": "蔚来ET7是纯电动中大型轿车，支持电池租赁和换电服务。", "specs": {"engine": "纯电动", "horsepower": "653马力", "torque": "850牛·米", "battery": "100kWh", "range": "700km", "0_100": "3.8秒", "transmission": "单速变速箱", "drive": "四驱"}, "features": ["NOMI助手", "换电服务", "空气悬挂", "蔚来自动驾驶", "全景天窗"], "stock": 7, "sales": 89}
                ]
                for car in cars:
                    cursor.execute("""
                        INSERT INTO cars (id, brand, model, year, price, category, color, image, description, specs, features, stock, sales)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (car['id'], car['brand'], car['model'], car['year'], car['price'], car['category'],
                          car['color'], car['image'], car['description'], json.dumps(car['specs'], ensure_ascii=False),
                          json.dumps(car['features'], ensure_ascii=False), car['stock'], car['sales']))

            cursor.execute("SELECT COUNT(*) as count FROM users")
            if cursor.fetchone()['count'] == 0:
                cursor.execute("""
                    INSERT INTO users (id, username, password, email, role, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, ('admin001', 'admin', hash_password('admin123'), 'admin@carstore.com', 'admin', datetime.now()))
        conn.commit()
    finally:
        conn.close()

init_database()
init_sample_data()

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@app.route('/api/cars', methods=['GET'])
def get_cars():
    brand = request.args.get('brand')
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    search = request.args.get('search')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM cars WHERE 1=1"
            params = []
            if brand:
                sql += " AND brand = %s"
                params.append(brand)
            if category:
                sql += " AND category = %s"
                params.append(category)
            if min_price:
                sql += " AND price >= %s"
                params.append(min_price)
            if max_price:
                sql += " AND price <= %s"
                params.append(max_price)
            if search:
                sql += " AND (brand LIKE %s OR model LIKE %s OR description LIKE %s)"
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern, search_pattern])

            cursor.execute(sql, params)
            cars = cursor.fetchall()
            for car in cars:
                if car.get('specs') and isinstance(car['specs'], str):
                    car['specs'] = json.loads(car['specs'])
                if car.get('features') and isinstance(car['features'], str):
                    car['features'] = json.loads(car['features'])
            return jsonify(cars)
    finally:
        conn.close()

@app.route('/api/cars/<car_id>', methods=['GET'])
def get_car(car_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM cars WHERE id = %s", (car_id,))
            car = cursor.fetchone()
            if not car:
                return jsonify({'error': 'Car not found'}), 404
            if car.get('specs') and isinstance(car['specs'], str):
                car['specs'] = json.loads(car['specs'])
            if car.get('features') and isinstance(car['features'], str):
                car['features'] = json.loads(car['features'])
            return jsonify(car)
    finally:
        conn.close()

@app.route('/api/brands', methods=['GET'])
def get_brands():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT brand FROM cars ORDER BY brand")
            brands = [row['brand'] for row in cursor.fetchall()]
            return jsonify(brands)
    finally:
        conn.close()

@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT category FROM cars ORDER BY category")
            categories = [row['category'] for row in cursor.fetchall()]
            return jsonify(categories)
    finally:
        conn.close()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return jsonify({'error': 'Username already exists'}), 400

            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({'error': 'Email already exists'}), 400

            cursor.execute("SELECT COUNT(*) as count FROM users")
            user_count = cursor.fetchone()['count']
            new_user_id = f'user{user_count + 1:03d}'

            cursor.execute("""
                INSERT INTO users (id, username, password, email, role, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (new_user_id, username, hash_password(password), email, 'user', datetime.now()))
        conn.commit()

        token = generate_token(new_user_id, username, 'user')
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': {
                'id': new_user_id,
                'username': username,
                'email': email,
                'role': 'user'
            }
        })
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if not user or not verify_password(password, user.get('password', '')):
                return jsonify({'error': 'Invalid username or password'}), 401

            token = generate_token(user['id'], user['username'], user['role'])
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role']
                }
            })
    finally:
        conn.close()

@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_profile():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, username, email, role, created_at FROM users WHERE id = %s", (request.user['user_id'],))
            user = cursor.fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            return jsonify(user)
    finally:
        conn.close()

@app.route('/api/user/cart', methods=['GET'])
@token_required
def get_cart():
    user_id = request.user['user_id']
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT c.id as car_id, c.brand, c.model, c.price, c.image, c.specs, c.features, ca.quantity, ca.added_at
                FROM carts ca
                JOIN cars c ON ca.car_id = c.id
                WHERE ca.user_id = %s
            """, (user_id,))
            rows = cursor.fetchall()
            items = []
            total = 0
            for row in rows:
                specs = row.get('specs')
                if specs and isinstance(specs, str):
                    specs = json.loads(specs)
                features = row.get('features')
                if features and isinstance(features, str):
                    features = json.loads(features)
                item = {
                    'car_id': row['car_id'],
                    'car': {
                        'id': row['car_id'],
                        'brand': row['brand'],
                        'model': row['model'],
                        'price': float(row['price']),
                        'image': row.get('image'),
                        'specs': specs,
                        'features': features
                    },
                    'quantity': row['quantity'],
                    'added_at': row['added_at'].isoformat() if row.get('added_at') else None
                }
                items.append(item)
                total += float(row['price']) * row['quantity']
            return jsonify({'items': items, 'total': total})
    finally:
        conn.close()

@app.route('/api/user/cart', methods=['POST'])
@token_required
def add_to_cart():
    user_id = request.user['user_id']
    data = request.get_json()
    car_id = data.get('car_id')
    quantity = data.get('quantity', 1)

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM cars WHERE id = %s", (car_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Car not found'}), 404

            cursor.execute("SELECT * FROM carts WHERE user_id = %s AND car_id = %s", (user_id, car_id))
            existing = cursor.fetchone()

            if existing:
                cursor.execute("UPDATE carts SET quantity = quantity + %s WHERE user_id = %s AND car_id = %s",
                              (quantity, user_id, car_id))
            else:
                cursor.execute("INSERT INTO carts (user_id, car_id, quantity) VALUES (%s, %s, %s)",
                             (user_id, car_id, quantity))
        conn.commit()
        return jsonify({'message': 'Added to cart successfully'})
    finally:
        conn.close()

@app.route('/api/user/cart/<car_id>', methods=['DELETE'])
@token_required
def remove_from_cart(car_id):
    user_id = request.user['user_id']
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM carts WHERE user_id = %s AND car_id = %s", (user_id, car_id))
        conn.commit()
        return jsonify({'message': 'Item removed from cart'})
    finally:
        conn.close()

@app.route('/api/user/cart', methods=['DELETE'])
@token_required
def clear_cart():
    user_id = request.user['user_id']
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM carts WHERE user_id = %s", (user_id,))
        conn.commit()
        return jsonify({'message': 'Cart cleared'})
    finally:
        conn.close()

@app.route('/api/orders', methods=['POST'])
@token_required
def create_order():
    user_id = request.user['user_id']
    data = request.get_json()

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT c.*, ca.quantity FROM carts ca JOIN cars c ON ca.car_id = c.id WHERE ca.user_id = %s", (user_id,))
            cart_items = cursor.fetchall()

            if not cart_items:
                return jsonify({'error': 'Cart is empty'}), 400

            order_items = []
            total = 0
            for item in cart_items:
                if item.get('stock', 0) < item.get('quantity', 1):
                    return jsonify({'error': f'{item["brand"]} {item["model"]} stock insufficient'}), 400
                order_items.append({
                    'car_id': item['id'],
                    'car': {
                        'brand': item['brand'],
                        'model': item['model'],
                        'price': float(item['price']),
                        'image': item.get('image')
                    },
                    'quantity': item.get('quantity', 1)
                })
                total += float(item['price']) * item.get('quantity', 1)

            order_id = f'ORD{datetime.now().strftime("%Y%m%d%H%M%S")}{secrets.token_hex(2).upper()}'
            cursor.execute("""
                INSERT INTO orders (id, user_id, items, total, status, payment_method, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (order_id, user_id, json.dumps(order_items, ensure_ascii=False), float(total),
                  'pending_payment', data.get('payment_method', 'wechat'), datetime.now(), datetime.now()))

            cursor.execute("DELETE FROM carts WHERE user_id = %s", (user_id,))
        conn.commit()
        return jsonify({
            'message': 'Order created successfully',
            'order': {'id': order_id, 'items': order_items, 'total': total, 'status': 'pending_payment'}
        })
    finally:
        conn.close()

@app.route('/api/orders', methods=['GET'])
@token_required
def get_orders():
    user_id = request.user['user_id']
    role = request.user.get('role')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if role == 'admin':
                cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
            else:
                cursor.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
            orders = cursor.fetchall()
            for order in orders:
                order['total'] = float(order['total']) if order.get('total') else 0
                if order.get('created_at'):
                    order['created_at'] = order['created_at'].isoformat()
                if order.get('updated_at'):
                    order['updated_at'] = order['updated_at'].isoformat()
                if order.get('paid_at'):
                    order['paid_at'] = order['paid_at'].isoformat()
                if order.get('items') and isinstance(order['items'], str):
                    order['items'] = json.loads(order['items'])
            return jsonify(orders)
    finally:
        conn.close()

@app.route('/api/orders/<order_id>', methods=['GET'])
@token_required
def get_order(order_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order = cursor.fetchone()

            if not order:
                return jsonify({'error': 'Order not found'}), 404

            user_id = request.user['user_id']
            role = request.user.get('role')

            if order.get('user_id') != user_id and role != 'admin':
                return jsonify({'error': 'Unauthorized'}), 403

            order['total'] = float(order['total']) if order.get('total') else 0
            if order.get('created_at'):
                order['created_at'] = order['created_at'].isoformat()
            if order.get('updated_at'):
                order['updated_at'] = order['updated_at'].isoformat()
            if order.get('paid_at'):
                order['paid_at'] = order['paid_at'].isoformat()
            if order.get('items') and isinstance(order['items'], str):
                order['items'] = json.loads(order['items'])

            return jsonify(order)
    finally:
        conn.close()

@app.route('/api/orders/<order_id>', methods=['PUT'])
@token_required
def update_order_status(order_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order = cursor.fetchone()

            if not order:
                return jsonify({'error': 'Order not found'}), 404

            user_id = request.user['user_id']
            role = request.user.get('role')

            if order.get('user_id') != user_id and role != 'admin':
                return jsonify({'error': 'Unauthorized'}), 403

            data = request.get_json()
            if 'status' in data:
                cursor.execute("UPDATE orders SET status = %s, updated_at = %s WHERE id = %s",
                             (data['status'], datetime.now(), order_id))
        conn.commit()

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order = cursor.fetchone()
            order['total'] = float(order['total']) if order.get('total') else 0
            if order.get('created_at'):
                order['created_at'] = order['created_at'].isoformat()
            if order.get('updated_at'):
                order['updated_at'] = order['updated_at'].isoformat()
            if order.get('paid_at'):
                order['paid_at'] = order['paid_at'].isoformat()
            if order.get('items') and isinstance(order['items'], str):
                order['items'] = json.loads(order['items'])
        return jsonify({'message': 'Order updated successfully', 'order': order})
    finally:
        conn.close()

@app.route('/api/payment/create/<order_id>', methods=['POST'])
@token_required
def create_payment(order_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order = cursor.fetchone()

            if not order:
                return jsonify({'error': 'Order not found'}), 404

            user_id = request.user['user_id']
            if order.get('user_id') != user_id:
                return jsonify({'error': 'Unauthorized'}), 403

            payment_data = {
                'order_id': order_id,
                'amount': float(order['total']),
                'payment_method': order.get('payment_method', 'wechat'),
                'status': 'pending',
                'qr_code_url': f'/payment/qrcode.html?order_id={order_id}&amount={order["total"]}',
                'created_at': order['created_at'].isoformat() if order.get('created_at') else datetime.now().isoformat()
            }
            return jsonify(payment_data)
    finally:
        conn.close()

@app.route('/api/payment/status/<order_id>', methods=['GET'])
@token_required
def get_payment_status(order_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, status, total FROM orders WHERE id = %s", (order_id,))
            order = cursor.fetchone()

            if not order:
                return jsonify({'error': 'Order not found'}), 404

            return jsonify({
                'order_id': order_id,
                'status': order.get('status', 'unknown'),
                'total': float(order['total'])
            })
    finally:
        conn.close()

@app.route('/api/payment/simulate/<order_id>', methods=['POST'])
@token_required
def simulate_payment(order_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order = cursor.fetchone()

            if not order:
                return jsonify({'error': 'Order not found'}), 404

            user_id = request.user['user_id']
            if order.get('user_id') != user_id:
                return jsonify({'error': 'Unauthorized'}), 403

            cursor.execute("UPDATE orders SET status = 'paid', paid_at = %s, updated_at = %s WHERE id = %s",
                          (datetime.now(), datetime.now(), order_id))

            items = json.loads(order['items']) if isinstance(order['items'], str) else order['items']
            for item in items:
                cursor.execute("UPDATE cars SET stock = stock - %s, sales = sales + %s WHERE id = %s",
                             (item.get('quantity', 1), item.get('quantity', 1), item['car_id']))
        conn.commit()
        return jsonify({'message': 'Payment successful', 'order': order})
    finally:
        conn.close()

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_stats():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT SUM(total) as total_sales FROM orders WHERE status = 'paid'")
            total_sales = cursor.fetchone()['total_sales'] or 0

            cursor.execute("SELECT COUNT(*) as total_orders FROM orders")
            total_orders = cursor.fetchone()['total_orders']

            cursor.execute("SELECT COUNT(*) as paid_orders FROM orders WHERE status = 'paid'")
            paid_orders = cursor.fetchone()['paid_orders']

            cursor.execute("SELECT COUNT(*) as total_users FROM users")
            total_users = cursor.fetchone()['total_users']

            cursor.execute("SELECT * FROM cars ORDER BY sales DESC LIMIT 5")
            top_cars = cursor.fetchall()
            for car in top_cars:
                if car.get('specs') and isinstance(car['specs'], str):
                    car['specs'] = json.loads(car['specs'])
                if car.get('features') and isinstance(car['features'], str):
                    car['features'] = json.loads(car['features'])

            cursor.execute("SELECT * FROM orders WHERE status = 'paid'")
            paid_orders_data = cursor.fetchall()

            sales_by_brand = {}
            for order in paid_orders_data:
                items = json.loads(order['items']) if isinstance(order['items'], str) else order['items']
                for item in items:
                    brand = item.get('car', {}).get('brand', 'Unknown')
                    sales_by_brand[brand] = sales_by_brand.get(brand, 0) + item.get('quantity', 0)

            monthly_sales = {}
            for order in paid_orders_data:
                if order.get('paid_at'):
                    month = order['paid_at'].strftime('%Y-%m')
                    monthly_sales[month] = monthly_sales.get(month, 0) + float(order['total'])

            return jsonify({
                'total_sales': float(total_sales),
                'total_orders': total_orders,
                'paid_orders': paid_orders,
                'total_users': total_users,
                'sales_by_brand': sales_by_brand,
                'top_cars': top_cars,
                'monthly_sales': monthly_sales
            })
    finally:
        conn.close()

@app.route('/api/admin/cars', methods=['GET'])
@admin_required
def get_all_cars():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM cars ORDER BY id")
            cars = cursor.fetchall()
            for car in cars:
                if car.get('specs') and isinstance(car['specs'], str):
                    car['specs'] = json.loads(car['specs'])
                if car.get('features') and isinstance(car['features'], str):
                    car['features'] = json.loads(car['features'])
            return jsonify(cars)
    finally:
        conn.close()

@app.route('/api/admin/cars', methods=['POST'])
@admin_required
def add_car():
    data = request.get_json()
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM cars")
            car_count = cursor.fetchone()['count']
            new_car_id = f'car{car_count + 1:03d}'

            cursor.execute("""
                INSERT INTO cars (id, brand, model, year, price, category, color, image, description, specs, features, stock, sales)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (new_car_id, data.get('brand'), data.get('model'), data.get('year'), data.get('price'),
                  data.get('category'), data.get('color'), data.get('image'), data.get('description'),
                  json.dumps(data.get('specs', {}), ensure_ascii=False),
                  json.dumps(data.get('features', []), ensure_ascii=False),
                  data.get('stock', 0), 0))
        conn.commit()
        return jsonify({'message': 'Car added successfully', 'car': {'id': new_car_id, **data}})
    finally:
        conn.close()

@app.route('/api/admin/cars/<car_id>', methods=['PUT'])
@admin_required
def update_car(car_id):
    data = request.get_json()
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM cars WHERE id = %s", (car_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Car not found'}), 404

            updates = []
            params = []
            for key in ['brand', 'model', 'year', 'price', 'category', 'color', 'image', 'description', 'specs', 'features', 'stock']:
                if key in data:
                    if key in ['specs', 'features']:
                        updates.append(f"{key} = %s")
                        params.append(json.dumps(data[key], ensure_ascii=False))
                    else:
                        updates.append(f"{key} = %s")
                        params.append(data[key])

            if updates:
                params.append(car_id)
                cursor.execute(f"UPDATE cars SET {', '.join(updates)} WHERE id = %s", params)
        conn.commit()

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM cars WHERE id = %s", (car_id,))
            car = cursor.fetchone()
            if car.get('specs') and isinstance(car['specs'], str):
                car['specs'] = json.loads(car['specs'])
            if car.get('features') and isinstance(car['features'], str):
                car['features'] = json.loads(car['features'])
        return jsonify({'message': 'Car updated successfully', 'car': car})
    finally:
        conn.close()

@app.route('/api/admin/cars/<car_id>', methods=['DELETE'])
@admin_required
def delete_car(car_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM cars WHERE id = %s", (car_id,))
        conn.commit()
        return jsonify({'message': 'Car deleted successfully'})
    finally:
        conn.close()

@app.route('/api/admin/orders', methods=['GET'])
@admin_required
def get_all_orders():
    status = request.args.get('status')
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if status:
                cursor.execute("""
                    SELECT o.*, u.username
                    FROM orders o
                    LEFT JOIN users u ON o.user_id = u.id
                    WHERE o.status = %s
                    ORDER BY o.created_at DESC
                """, (status,))
            else:
                cursor.execute("""
                    SELECT o.*, u.username
                    FROM orders o
                    LEFT JOIN users u ON o.user_id = u.id
                    ORDER BY o.created_at DESC
                """)
            orders = cursor.fetchall()
            for order in orders:
                order['total'] = float(order['total']) if order.get('total') else 0
                order['username'] = order.get('username', order['user_id'])
                if order.get('created_at'):
                    order['created_at'] = order['created_at'].isoformat()
                if order.get('updated_at'):
                    order['updated_at'] = order['updated_at'].isoformat()
                if order.get('paid_at'):
                    order['paid_at'] = order['paid_at'].isoformat()
                if order.get('items') and isinstance(order['items'], str):
                    order['items'] = json.loads(order['items'])
            return jsonify(orders)
    finally:
        conn.close()

@app.route('/api/admin/orders/<order_id>', methods=['PUT'])
@admin_required
def update_order(order_id):
    data = request.get_json()
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Order not found'}), 404

            if 'status' in data:
                cursor.execute("UPDATE orders SET status = %s, updated_at = %s WHERE id = %s",
                             (data['status'], datetime.now(), order_id))
        conn.commit()

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order = cursor.fetchone()
        return jsonify({'message': 'Order updated successfully', 'order': order})
    finally:
        conn.close()

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.username, u.email, u.role, u.created_at,
                       COUNT(CASE WHEN o.status = 'paid' THEN 1 END) as paid_orders,
                       COALESCE(SUM(CASE WHEN o.status = 'paid' THEN o.total ELSE 0 END), 0) as total_spent
                FROM users u
                LEFT JOIN orders o ON u.id = o.user_id
                GROUP BY u.id, u.username, u.email, u.role, u.created_at
                ORDER BY u.created_at DESC
            """)
            users = cursor.fetchall()
            for user in users:
                if user.get('created_at'):
                    user['created_at'] = user['created_at'].isoformat()
                user['total_spent'] = float(user['total_spent']) if user.get('total_spent') else 0
            return jsonify(users)
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)