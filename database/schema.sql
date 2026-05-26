-- Inventory Operations API - PostgreSQL Schema

-- Dimension tables for status tracking
CREATE TABLE IF NOT EXISTS order_statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

INSERT INTO order_statuses (id, name, description) VALUES
    (1, 'pending', 'Order received, awaiting processing'),
    (2, 'processing', 'Order is being prepared'),
    (3, 'shipped', 'Order has been shipped'),
    (4, 'delivered', 'Order delivered to buyer'),
    (5, 'cancelled', 'Order was cancelled'),
    (6, 'returned', 'Order was returned');

CREATE TABLE IF NOT EXISTS warehouse_statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO warehouse_statuses (id, name) VALUES
    (1, 'in_stock'),
    (2, 'picked'),
    (3, 'packed'),
    (4, 'shipped');

CREATE TABLE IF NOT EXISTS payment_statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO payment_statuses (id, name) VALUES
    (1, 'pending'),
    (2, 'completed'),
    (3, 'refunded');

-- Core tables
CREATE TABLE IF NOT EXISTS physical_items (
    lpn VARCHAR(50) PRIMARY KEY,
    asin VARCHAR(20),
    amazon_description TEXT,
    image_urls TEXT,
    scraped_price DECIMAL(10, 2),
    sale_price DECIMAL(10, 2),
    condition VARCHAR(30),
    available BOOLEAN NOT NULL DEFAULT TRUE,
    truckload_id VARCHAR(50),
    scraping_attempts INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_items_asin ON physical_items(asin);
CREATE INDEX idx_items_condition ON physical_items(condition);
CREATE INDEX idx_items_available ON physical_items(available);
CREATE INDEX idx_items_truckload ON physical_items(truckload_id);

CREATE TABLE IF NOT EXISTS orders (
    request_id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50),
    buyer_name VARCHAR(200),
    buyer_hash VARCHAR(64),
    buyer_country VARCHAR(5),
    order_date DATE,
    due_date DATE,
    status_id INTEGER NOT NULL DEFAULT 1 REFERENCES order_statuses(id),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    shipping_code VARCHAR(100),
    shipping_company_id INTEGER,
    notes TEXT,
    buyer_address TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_orders_status ON orders(status_id);
CREATE INDEX idx_orders_account ON orders(account_id);
CREATE INDEX idx_orders_date ON orders(order_date);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(50) NOT NULL REFERENCES orders(request_id) ON DELETE CASCADE,
    lpn VARCHAR(50) NOT NULL REFERENCES physical_items(lpn),
    price DECIMAL(10, 2) NOT NULL DEFAULT 0,
    web_url TEXT,
    warehouse_status_id INTEGER REFERENCES warehouse_statuses(id)
);

CREATE INDEX idx_order_items_request ON order_items(request_id);
CREATE INDEX idx_order_items_lpn ON order_items(lpn);

CREATE TABLE IF NOT EXISTS listings (
    lpn VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50),
    product_id VARCHAR(100),
    title VARCHAR(500),
    description TEXT,
    sale_price DECIMAL(10, 2),
    category_id INTEGER,
    is_reserved BOOLEAN NOT NULL DEFAULT FALSE,
    is_sold BOOLEAN NOT NULL DEFAULT FALSE,
    is_banned BOOLEAN NOT NULL DEFAULT FALSE,
    conversations_count INTEGER NOT NULL DEFAULT 0,
    favorites_count INTEGER NOT NULL DEFAULT 0,
    views_count INTEGER NOT NULL DEFAULT 0,
    platform VARCHAR(50)
);

CREATE INDEX idx_listings_platform ON listings(platform);
CREATE INDEX idx_listings_account ON listings(account_id);

CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    lpn VARCHAR(50) NOT NULL REFERENCES physical_items(lpn),
    account_id VARCHAR(50),
    final_price DECIMAL(10, 2) NOT NULL DEFAULT 0,
    shipping_cost DECIMAL(10, 2) NOT NULL DEFAULT 0,
    platform_fee DECIMAL(10, 2) NOT NULL DEFAULT 0,
    sale_date TIMESTAMP,
    buyer_info TEXT,
    payment_status_id INTEGER NOT NULL DEFAULT 1 REFERENCES payment_statuses(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sales_lpn ON sales(lpn);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_items_updated_at
    BEFORE UPDATE ON physical_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
