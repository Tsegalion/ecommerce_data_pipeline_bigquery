-- Create schema
CREATE SCHEMA IF NOT EXISTS raw;

-- Create table for product dataset
CREATE TABLE IF NOT EXISTS raw.products (
    product_id VARCHAR(255) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name_length INT,
    product_description_length INT,
    product_photos_qty INT,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT
);

-- Copy product dataset
COPY raw.products(product_id, product_category_name, product_name_length,
                            product_description_length, product_photos_qty, product_weight_g,
                            product_length_cm, product_height_cm, product_width_cm)
FROM '/data/olist_products_dataset.csv' DELIMITER ',' CSV HEADER;

-- Create table for order dataset
CREATE TABLE IF NOT EXISTS raw.orders (
    order_id VARCHAR(255) PRIMARY KEY,
    customer_id VARCHAR(255),
    order_status VARCHAR(100),
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

-- Copy order dataset
COPY raw.orders(order_id, customer_id, order_status, order_purchase_timestamp,
                            order_approved_at, order_delivered_carrier_date, order_delivered_customer_date,
                            order_estimated_delivery_date)
FROM '/data/olist_orders_dataset.csv' DELIMITER ',' CSV HEADER;

-- Create table for customer dataset
CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id VARCHAR(255) PRIMARY KEY,
    customer_unique_id VARCHAR(255),
    customer_zip_code_prefix INT,
    customer_city VARCHAR(100),
    customer_state VARCHAR(100)
);

-- Copy customer dataset
COPY raw.customers(customer_id, customer_unique_id, customer_zip_code_prefix,
                            customer_city, customer_state)
FROM '/data/olist_customers_dataset.csv' DELIMITER ',' CSV HEADER;

-- Create table for order items dataset
CREATE TABLE IF NOT EXISTS raw.order_items (
    order_id VARCHAR(255),
    order_item_id INT,
    product_id VARCHAR(255),
    seller_id VARCHAR(255),
    shipping_limit_date TIMESTAMP,
    price FLOAT,
    freight_value FLOAT,
    PRIMARY KEY (order_id, order_item_id)
);

-- Copy order items dataset
COPY raw.order_items(order_id, order_item_id, product_id, seller_id,
                            shipping_limit_date, price, freight_value)
FROM '/data/olist_order_items_dataset.csv' DELIMITER ',' CSV HEADER;

-- Create table for sellers dataset
CREATE TABLE IF NOT EXISTS raw.sellers (
    seller_id VARCHAR(255) PRIMARY KEY,
    seller_zip_code_prefix INT,
    seller_city VARCHAR(100),
    seller_state VARCHAR(100)
);

-- Copy sellers dataset
COPY raw.sellers(seller_id, seller_zip_code_prefix, seller_city, seller_state)
FROM '/data/olist_sellers_dataset.csv' DELIMITER ',' CSV HEADER;

-- Create table for product category dataset
CREATE TABLE IF NOT EXISTS raw.product_category_name_translation (
    product_category_name VARCHAR(255) PRIMARY KEY,
    product_category_name_english VARCHAR(100)
);

-- Copy product category dataset
COPY raw.product_category_name_translation(product_category_name, product_category_name_english)
FROM '/data/product_category_name_translation.csv' DELIMITER ',' CSV HEADER;

-- Create table for geolocation dataset
CREATE TABLE IF NOT EXISTS raw.geolocation (
    geolocation_zip_code_prefix INT,
    geolocation_lat FLOAT,
    geolocation_lng FLOAT,
    geolocation_city VARCHAR(100),
    geolocation_state VARCHAR(100)
);

-- Copy geolocation dataset
COPY raw.geolocation(geolocation_zip_code_prefix, geolocation_lat, geolocation_lng,
                            geolocation_city, geolocation_state)
FROM '/data/olist_geolocation_dataset.csv' DELIMITER ',' CSV HEADER;

-- Create table for order reviews dataset
CREATE TABLE IF NOT EXISTS raw.order_reviews (
    review_id VARCHAR(255),
    order_id VARCHAR(255),
    review_score INT,
    review_comment_title VARCHAR(100),
    review_comment_message VARCHAR(255),
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP,
    PRIMARY KEY (review_id, order_id)
);


-- Copy order reviews dataset
COPY raw.order_reviews(review_id, order_id, review_score, review_comment_title,
                            review_comment_message, review_creation_date, review_answer_timestamp)
FROM '/data/olist_order_reviews_dataset.csv' DELIMITER ',' CSV HEADER;

-- Create table for payment dataset
CREATE TABLE IF NOT EXISTS raw.order_payments (
    order_id VARCHAR(255),
    payment_sequential INT,
    payment_type VARCHAR(100),
    payment_installments INT,
    payment_value FLOAT,
    PRIMARY KEY (order_id, payment_sequential)
);

-- Copy payment dataset
COPY raw.order_payments(order_id, payment_sequential, payment_type, payment_installments, payment_value)
FROM '/data/olist_order_payments_dataset.csv' DELIMITER ',' CSV HEADER;