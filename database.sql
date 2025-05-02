-- PostgreSQL Schema for PVC Pipe Manufacturing Company

-- Create Categories and Subcategories Table
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    parent_category_id INTEGER NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    image_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_parent_category FOREIGN KEY (parent_category_id) REFERENCES categories(category_id) ON DELETE SET NULL
);

-- Add index on parent_category_id
CREATE INDEX idx_categories_parent ON categories(parent_category_id);

-- Create Users and Customers Table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    company_name VARCHAR(100),
    business_type VARCHAR(50),
    tax_id VARCHAR(30),
    shipping_address TEXT,
    billing_address TEXT,
    user_type VARCHAR(20) NOT NULL DEFAULT 'customer' CHECK (user_type IN ('customer', 'distributor', 'administrator', 'employee')),
    credit_limit DECIMAL(12,2) DEFAULT 0.00,
    payment_terms VARCHAR(50),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Add indexes for Users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_user_type ON users(user_type);

-- Create Products Catalog Table
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    regular_price DECIMAL(10,2) NOT NULL,
    sale_price DECIMAL(10,2),
    diameter VARCHAR(20),
    length DECIMAL(10,2),
    wall_thickness DECIMAL(6,2),
    pressure_rating VARCHAR(20),
    material_type VARCHAR(50),
    brand VARCHAR(50),
    unit_of_measure VARCHAR(30) NOT NULL,
    image_url VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'out_of_stock', 'by_order', 'discontinued')),
    category_id INTEGER,
    subcategory_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
    CONSTRAINT fk_product_subcategory FOREIGN KEY (subcategory_id) REFERENCES categories(category_id) ON DELETE SET NULL
);

-- Add indexes for Products table
CREATE INDEX idx_products_product_code ON products(product_code);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_category ON products(category_id);

-- Create Suppliers Table
CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    supplier_type VARCHAR(50),
    payment_terms VARCHAR(50),
    lead_time INTEGER, -- Lead time in days
    quality_rating DECIMAL(3,1),
    active_status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add index on supplier_name
CREATE INDEX idx_suppliers_name ON suppliers(supplier_name);

-- Create Inventory Table
CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    available_quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    minimum_stock_level INTEGER DEFAULT 0,
    maximum_stock_level INTEGER,
    warehouse_location VARCHAR(50),
    warehouse_id INTEGER,
    last_restock_date DATE,
    last_count_date DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_inventory_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- Add index on product_id for inventory
CREATE INDEX idx_inventory_product ON inventory(product_id);

-- Create Promotions and Offers Table
CREATE TABLE promotions (
    promotion_id SERIAL PRIMARY KEY,
    product_id INTEGER NULL,
    category_id INTEGER NULL,
    promotion_name VARCHAR(100) NOT NULL,
    promotion_type VARCHAR(20) NOT NULL CHECK (promotion_type IN ('percentage', 'fixed_amount', 'bundle')),
    discount_percentage DECIMAL(5,2),
    discount_amount DECIMAL(10,2),
    minimum_purchase DECIMAL(10,2),
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    status VARCHAR(10) DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_promotion_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    CONSTRAINT fk_promotion_category FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

-- Add indexes for Promotions table
CREATE INDEX idx_promotions_dates ON promotions(start_date, end_date);
CREATE INDEX idx_promotions_status ON promotions(status);

-- Create Orders Table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    order_status VARCHAR(20) DEFAULT 'pending' CHECK (order_status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')),
    payment_method VARCHAR(50),
    order_total DECIMAL(12,2) NOT NULL,
    tax_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    shipping_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    shipping_address TEXT,
    billing_address TEXT,
    delivery_date DATE,
    tracking_number VARCHAR(50),
    notes TEXT,
    CONSTRAINT fk_order_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT
);

-- Add indexes for Orders table
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_orders_date ON orders(order_date);

-- Create Order Details Table
CREATE TABLE order_details (
    order_detail_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    discount_applied DECIMAL(10,2) DEFAULT 0.00,
    CONSTRAINT fk_order_detail_order FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_order_detail_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);

-- Add index on order_id for order_details
CREATE INDEX idx_order_details_order ON order_details(order_id);

-- Create Raw Materials Inventory Table
CREATE TABLE raw_materials_inventory (
    material_id SERIAL PRIMARY KEY,
    material_name VARCHAR(100) NOT NULL,
    material_type VARCHAR(50) NOT NULL,
    supplier_id INTEGER,
    quantity_available DECIMAL(12,3) NOT NULL DEFAULT 0,
    unit_of_measure VARCHAR(30) NOT NULL,
    minimum_stock_level DECIMAL(12,3) DEFAULT 0,
    cost_per_unit DECIMAL(10,2) NOT NULL,
    location VARCHAR(50),
    last_purchase_date DATE,
    expiration_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_raw_material_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE SET NULL
);

-- Add index on material_type
CREATE INDEX idx_raw_materials_type ON raw_materials_inventory(material_type);

-- Create Manufacturing Machines Table
CREATE TABLE manufacturing_machines (
    machine_id SERIAL PRIMARY KEY,
    machine_name VARCHAR(100) NOT NULL,
    machine_type VARCHAR(50) NOT NULL,
    purchase_date DATE,
    maintenance_schedule TEXT,
    last_maintenance_date DATE,
    operational_status VARCHAR(20) DEFAULT 'operational' CHECK (operational_status IN ('operational', 'maintenance', 'repair', 'offline')),
    production_capacity VARCHAR(100),
    notes TEXT
);

-- Add index on operational_status
CREATE INDEX idx_machines_status ON manufacturing_machines(operational_status);

-- Create Production Batches Table
CREATE TABLE production_batches (
    batch_id SERIAL PRIMARY KEY,
    production_date DATE NOT NULL,
    product_id INTEGER NOT NULL,
    quantity_produced INTEGER NOT NULL,
    material_used TEXT,
    operator_id INTEGER,
    machine_id INTEGER,
    quality_check_status VARCHAR(10) DEFAULT 'pending' CHECK (quality_check_status IN ('pending', 'passed', 'failed')),
    production_cost DECIMAL(12,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_production_batch_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
    CONSTRAINT fk_production_batch_operator FOREIGN KEY (operator_id) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_production_batch_machine FOREIGN KEY (machine_id) REFERENCES manufacturing_machines(machine_id) ON DELETE SET NULL
);

-- Add indexes for Production Batches table
CREATE INDEX idx_production_batches_product ON production_batches(product_id);
CREATE INDEX idx_production_batches_date ON production_batches(production_date);

-- Create Quality Control Table
CREATE TABLE quality_control (
    quality_check_id SERIAL PRIMARY KEY,
    batch_id INTEGER NOT NULL,
    inspector_id INTEGER,
    check_date DATE NOT NULL,
    pressure_test_result VARCHAR(50),
    dimensional_check_result VARCHAR(50),
    visual_inspection_result VARCHAR(50),
    status VARCHAR(10) NOT NULL CHECK (status IN ('passed', 'failed')),
    rejection_reason TEXT,
    notes TEXT,
    CONSTRAINT fk_quality_control_batch FOREIGN KEY (batch_id) REFERENCES production_batches(batch_id) ON DELETE CASCADE,
    CONSTRAINT fk_quality_control_inspector FOREIGN KEY (inspector_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Add indexes for Quality Control table
CREATE INDEX idx_quality_control_batch ON quality_control(batch_id);
CREATE INDEX idx_quality_control_status ON quality_control(status);

-- Create Invoicing and Payments Table
CREATE TABLE invoice_payments (
    invoice_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    tax_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    payment_method VARCHAR(50),
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('paid', 'partially_paid', 'pending', 'overdue')),
    payment_date DATE,
    notes TEXT,
    CONSTRAINT fk_invoice_order FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE RESTRICT
);

-- Add indexes for Invoice Payments table
CREATE INDEX idx_invoice_payments_number ON invoice_payments(invoice_number);
CREATE INDEX idx_invoice_payments_status ON invoice_payments(payment_status);

-- Create Shipping and Delivery Table
CREATE TABLE shipping_delivery (
    shipping_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    shipping_date DATE,
    carrier_name VARCHAR(100),
    tracking_number VARCHAR(100),
    estimated_delivery_date DATE,
    actual_delivery_date DATE,
    shipping_cost DECIMAL(10,2) DEFAULT 0.00,
    shipping_status VARCHAR(20) DEFAULT 'processing' CHECK (shipping_status IN ('processing', 'shipped', 'in_transit', 'delivered', 'failed')),
    receiver_name VARCHAR(100),
    delivery_notes TEXT,
    CONSTRAINT fk_shipping_order FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- Add indexes for Shipping and Delivery table
CREATE INDEX idx_shipping_order ON shipping_delivery(order_id);
CREATE INDEX idx_shipping_status ON shipping_delivery(shipping_status);

-- Create Technical Specifications Table
CREATE TABLE technical_specifications (
    spec_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    standard_compliance VARCHAR(100),
    certification_details TEXT,
    usage_recommendations TEXT,
    installation_guidelines TEXT,
    technical_drawing_url VARCHAR(255),
    safety_information TEXT,
    CONSTRAINT fk_technical_spec_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- Add index on product_id for technical specifications
CREATE INDEX idx_technical_specs_product ON technical_specifications(product_id);

-- Create Customer Returns Table
CREATE TABLE customer_returns (
    return_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    return_date DATE NOT NULL,
    quantity_returned INTEGER NOT NULL,
    return_reason TEXT,
    inspection_result TEXT,
    refund_amount DECIMAL(10,2),
    status VARCHAR(10) DEFAULT 'pending' CHECK (status IN ('pending', 'processed', 'rejected')),
    notes TEXT,
    CONSTRAINT fk_return_order FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE RESTRICT,
    CONSTRAINT fk_return_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);

-- Add indexes for Customer Returns table
CREATE INDEX idx_customer_returns_order ON customer_returns(order_id);
CREATE INDEX idx_customer_returns_status ON customer_returns(status);

-- Add update_timestamp function for automatic updated_at columns
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for tables with updated_at columns
CREATE TRIGGER update_categories_timestamp BEFORE UPDATE ON categories
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_products_timestamp BEFORE UPDATE ON products
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_suppliers_timestamp BEFORE UPDATE ON suppliers
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_inventory_timestamp BEFORE UPDATE ON inventory
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_promotions_timestamp BEFORE UPDATE ON promotions
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_raw_materials_timestamp BEFORE UPDATE ON raw_materials_inventory
FOR EACH ROW EXECUTE FUNCTION update_timestamp();