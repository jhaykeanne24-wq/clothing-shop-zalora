CREATE DATABASE IF NOT EXISTS clothing_shop;
USE clothing_shop;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    profile_photo VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL,
    image_url VARCHAR(255),
    brand VARCHAR(100),
    sizes VARCHAR(255),
    colors VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    shipping_address TEXT,
    payment_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Insert sample products
INSERT INTO products (name, category, description, price, stock, image_url, brand, sizes, colors) VALUES
('Classic White T-Shirt', 'Tops', 'Comfortable and versatile white t-shirt', 25.99, 50, '/static/images/product1.jpg', 'BasicWear', 'XS,S,M,L,XL', 'White'),
('Blue Denim Jeans', 'Bottoms', 'Stylish and durable denim jeans', 59.99, 30, '/static/images/product2.jpg', 'DenimCo', '28,30,32,34,36', 'Blue'),
('Black Leather Jacket', 'Outerwear', 'Premium black leather jacket', 199.99, 15, '/static/images/product3.jpg', 'LeatherLux', 'S,M,L,XL', 'Black'),
('Summer Floral Dress', 'Dresses', 'Beautiful floral pattern summer dress', 49.99, 25, '/static/images/product4.jpg', 'FashionFlow', 'XS,S,M,L,XL', 'Multicolor'),
('Running Sneakers', 'Shoes', 'Comfortable running shoes with cushioning', 89.99, 40, '/static/images/product5.jpg', 'SportZone', '5,6,7,8,9,10,11,12', 'Black'),
('Wool Sweater', 'Tops', 'Warm and cozy wool sweater', 79.99, 20, '/static/images/product6.jpg', 'WarmKnits', 'S,M,L,XL', 'Gray,Navy,Beige'),
('Chino Pants', 'Bottoms', 'Casual chino pants for everyday wear', 54.99, 35, '/static/images/product7.jpg', 'CasualStyle', '28,30,32,34,36', 'Khaki'),
('Striped Polo Shirt', 'Tops', 'Classic striped polo shirt', 39.99, 45, '/static/images/product8.jpg', 'PoloWear', 'S,M,L,XL,XXL', 'Blue,Red,White'),
('Yoga Pants', 'Bottoms', 'Flexible yoga pants for active lifestyle', 69.99, 30, '/static/images/product9.jpg', 'YogaLife', 'XS,S,M,L,XL', 'Black'),
('Bomber Jacket', 'Outerwear', 'Trendy bomber jacket', 89.99, 25, '/static/images/product10.jpg', 'UrbanWear', 'S,M,L,XL', 'Green'),
('Casual Sneakers', 'Shoes', 'Casual and comfortable sneakers', 64.99, 50, '/static/images/product11.jpg', 'SneakerHub', '5,6,7,8,9,10,11,12', 'White'),
('Maxi Skirt', 'Bottoms', 'Elegant maxi skirt', 59.99, 20, '/static/images/product12.jpg', 'ElegantWear', 'XS,S,M,L,XL', 'Black');
