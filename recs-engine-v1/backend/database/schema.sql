-- =============================================================================
-- BenefitMe Recommendation System — Database Schema
-- Matches production column names from db-schema/csv/ exports.
-- Target DB: MySQL 8+ / MariaDB 10.5+
-- Run: mysql -u <user> -p < schema.sql
-- =============================================================================
CREATE DATABASE IF NOT EXISTS findme_rs_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE findme_rs_db;
SET FOREIGN_KEY_CHECKS = 0;
-- -----------------------------------------------------------------------------
-- 1. employees
--    Employee master table — the primary RS actors.
--    Source: employees CSV export (employees_YYYYMMDD.csv).
--    Only RS-relevant columns are included; auth tokens, payroll, attendance
--    scan flags, political/party/NSSF fields, and HR-internal placeholders
--    (x, x2, decimal…) are intentionally omitted.
--
--    Key RS fields:
--      client_id                 — which company this employee belongs to
--      latitude / longitude      — employee's registered location (geo RS feature)
--      birthday / join_date      — age-group and tenure cold-start features
--      nationality               — demographic cold-start feature
--      education_level           — IN ('high_school','vocational','bachelor','master')
--      employee_level_id         — seniority tier (1=junior, 2=mid, 3=senior)
--      employee_category_type_id — employee type taxonomy
--
--    Product assignments are tracked in employee_products (M2M junction).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS employees (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    client_id INT UNSIGNED NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) DEFAULT NULL,
    phone VARCHAR(30) DEFAULT NULL,
    gender VARCHAR(10) DEFAULT NULL,
    address TEXT DEFAULT NULL,
    latitude DECIMAL(10, 8) DEFAULT NULL,
    longitude DECIMAL(11, 8) DEFAULT NULL,
    birthday DATE DEFAULT NULL,
    join_date DATE DEFAULT NULL,
    nationality VARCHAR(100) DEFAULT NULL,
    education_level VARCHAR(20) DEFAULT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    media_id INT UNSIGNED DEFAULT NULL,
    position_id INT UNSIGNED DEFAULT NULL,
    branch_id INT UNSIGNED DEFAULT NULL,
    employee_category_type_id INT UNSIGNED DEFAULT NULL,
    employee_level_id INT UNSIGNED DEFAULT NULL,
    deleted_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_emp_client (client_id),
    KEY idx_emp_is_active (is_active),
    KEY idx_emp_cat_type (employee_category_type_id),
    KEY idx_emp_level (employee_level_id),
    KEY idx_emp_lat_lng (latitude, longitude)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 2. benefit_me_page_types
--    Top-level taxonomy: food | service | store
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS benefit_me_page_types (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_page_type_name (name)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 3. benefit_me_categories
--    Second-level taxonomy, belongs to a page_type.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS benefit_me_categories (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    page_type_id INT UNSIGNED NOT NULL,
    media_id INT UNSIGNED DEFAULT NULL,
    name VARCHAR(100) NOT NULL,
    deleted_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_bm_cat_page_type (page_type_id),
    CONSTRAINT fk_bm_cat_page_type FOREIGN KEY (page_type_id) REFERENCES benefit_me_page_types (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 4. crm_products
--    Product master — the primary item set for the recommender.
--    product_type IN ('food','service','store','crm_product')
--    review_status IN ('pending','approved','rejected')
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crm_products (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    client_id INT UNSIGNED NOT NULL,
    benefit_me_category_id INT UNSIGNED DEFAULT NULL,
    name VARCHAR(255) NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    crm_product_image_id INT UNSIGNED DEFAULT NULL,
    product_type VARCHAR(50) DEFAULT NULL,
    product_code VARCHAR(50) DEFAULT NULL,
    discount_price DECIMAL(12, 2) DEFAULT NULL,
    after_discount_price DECIMAL(12, 2) DEFAULT NULL,
    discount_percentage DECIMAL(6, 2) DEFAULT NULL,
    description TEXT DEFAULT NULL,
    custom_description TEXT DEFAULT NULL,
    expired_at DATETIME DEFAULT NULL,
    is_expired TINYINT(1) NOT NULL DEFAULT 0,
    review_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    video_link VARCHAR(500) DEFAULT NULL,
    total_views INT UNSIGNED NOT NULL DEFAULT 0,
    deleted_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_crm_products_client (client_id),
    KEY idx_crm_products_category (benefit_me_category_id),
    KEY idx_crm_products_type (product_type),
    KEY idx_crm_products_review_active (review_status, is_active, is_expired),
    KEY idx_crm_products_total_views (total_views),
    CONSTRAINT fk_crm_products_category FOREIGN KEY (benefit_me_category_id) REFERENCES benefit_me_categories (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 5. crm_benefit_promotions
--    Promotional campaigns created by clients.
--    review_status IN ('pending','approved','rejected')
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crm_benefit_promotions (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    page_type_id INT UNSIGNED DEFAULT NULL,
    client_id INT UNSIGNED NOT NULL,
    benefit_me_category_id INT UNSIGNED DEFAULT NULL,
    media_id INT UNSIGNED DEFAULT NULL,
    name_location VARCHAR(255) NOT NULL,
    title VARCHAR(255) DEFAULT NULL,
    description TEXT DEFAULT NULL,
    discount_price DECIMAL(12, 2) DEFAULT NULL,
    phone VARCHAR(30) DEFAULT NULL,
    facebook_link VARCHAR(500) DEFAULT NULL,
    map_location_link VARCHAR(1000) DEFAULT NULL,
    latitude DECIMAL(10, 8) DEFAULT NULL,
    longitude DECIMAL(11, 8) DEFAULT NULL,
    business_type VARCHAR(100) DEFAULT NULL,
    category VARCHAR(100) DEFAULT NULL,
    review_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    approved_at DATETIME DEFAULT NULL,
    expired_at DATETIME DEFAULT NULL,
    deleted_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_crm_promo_client (client_id),
    KEY idx_crm_promo_category (benefit_me_category_id),
    KEY idx_crm_promo_status (review_status),
    CONSTRAINT fk_crm_promo_page_type FOREIGN KEY (page_type_id) REFERENCES benefit_me_page_types (id),
    CONSTRAINT fk_crm_promo_category FOREIGN KEY (benefit_me_category_id) REFERENCES benefit_me_categories (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 6. crm_benefit_promotion_categories
--    Many-to-many: promotions ↔ categories
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crm_benefit_promotion_categories (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    benefit_me_category_id INT UNSIGNED NOT NULL,
    crm_benefit_promotion_id INT UNSIGNED NOT NULL,
    created_at DATETIME DEFAULT NULL,
    updated_at DATETIME DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_promo_cat (benefit_me_category_id, crm_benefit_promotion_id),
    CONSTRAINT fk_promo_cat_category FOREIGN KEY (benefit_me_category_id) REFERENCES benefit_me_categories (id),
    CONSTRAINT fk_promo_cat_promotion FOREIGN KEY (crm_benefit_promotion_id) REFERENCES crm_benefit_promotions (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 7. crm_benefit_promotion_employee_favourites
--    Explicit promotion favourites saved by employees.
--    RS weight: explicit positive signal (weight=4).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crm_benefit_promotion_employee_favourites (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    client_id INT UNSIGNED NOT NULL,
    employee_id INT UNSIGNED NOT NULL,
    crm_benefit_promotion_id INT UNSIGNED NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_fav_client (client_id),
    KEY idx_fav_employee (employee_id),
    KEY idx_fav_promotion (crm_benefit_promotion_id),
    CONSTRAINT fk_fav_promotion FOREIGN KEY (crm_benefit_promotion_id) REFERENCES crm_benefit_promotions (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 8. crm_product_views
--    Raw per-session view events.  RS weight: view=1.
--    One row per view session (not deduplicated).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crm_product_views (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    client_id INT UNSIGNED NOT NULL,
    employee_id INT UNSIGNED NOT NULL,
    crm_product_id INT UNSIGNED NOT NULL,
    total_views INT UNSIGNED NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_pv_client (client_id),
    KEY idx_pv_employee (employee_id),
    KEY idx_pv_product (crm_product_id),
    KEY idx_pv_created (created_at),
    CONSTRAINT fk_pv_product FOREIGN KEY (crm_product_id) REFERENCES crm_products (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 9. benefit_me_reach_products
--    Aggregated per-user/per-product engagement counter (pre-computed).
--    Faster than scanning raw crm_product_views for popularity scoring.
--    RS weight: aggregated view=1, used for fast affinity lookup.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS benefit_me_reach_products (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    client_id INT UNSIGNED NOT NULL,
    employee_id INT UNSIGNED NOT NULL,
    crm_product_id INT UNSIGNED NOT NULL,
    total_views INT UNSIGNED NOT NULL DEFAULT 0,
    viewed_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_rp_client (client_id),
    KEY idx_rp_employee (employee_id),
    KEY idx_rp_product (crm_product_id),
    KEY idx_rp_viewed (viewed_at),
    CONSTRAINT fk_rp_product FOREIGN KEY (crm_product_id) REFERENCES crm_products (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 10. benefit_me_engagements
--     Product interaction events triggered from the BenefitMe app.
--     action_type IN ('Call Me Later','Just Exploring','Buy in telegram')
--     RS weights: Just Exploring=1, Call Me Later=4, Buy in telegram=8
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS benefit_me_engagements (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    client_id INT UNSIGNED NOT NULL,
    employee_id INT UNSIGNED NOT NULL,
    crm_contact_id INT UNSIGNED NOT NULL,
    product_id INT UNSIGNED NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    telephone VARCHAR(30) DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_eng_client (client_id),
    KEY idx_eng_employee (employee_id),
    KEY idx_eng_product (product_id),
    KEY idx_eng_action (action_type),
    KEY idx_eng_created (created_at),
    CONSTRAINT fk_eng_product FOREIGN KEY (product_id) REFERENCES crm_products (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 11. benefit_me_search_histories
--     Search query log. The `search` column stores a JSON blob:
--     {"search": "<query>", "created_at": "<ISO timestamp>"}
--     RS use: keyword-aware re-ranking; term frequency → category affinity.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS benefit_me_search_histories (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    client_id INT UNSIGNED NOT NULL,
    employee_id INT UNSIGNED NOT NULL,
    search JSON DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_sh_client (client_id),
    KEY idx_sh_employee (employee_id),
    KEY idx_sh_created (created_at)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 12. crm_benefit_more_info_archives
--     Older product interaction log (pre-BenefitMe-app era).
--     action_type IN ('Call Me Later','Buy in telegram','Just Exploring')
--     RS weight: same scale as benefit_me_engagements.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crm_benefit_more_info_archives (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    client_id INT UNSIGNED NOT NULL,
    employee_customer_id INT UNSIGNED NOT NULL,
    product_id INT UNSIGNED NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    upgraded_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_mia_client (client_id),
    KEY idx_mia_employee (employee_customer_id),
    KEY idx_mia_product (product_id),
    KEY idx_mia_created (created_at),
    CONSTRAINT fk_mia_product FOREIGN KEY (product_id) REFERENCES crm_products (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 13. crm_benefit_sold_products
--     Buy/claim signal — the strongest interaction weight (8).
--     One row per deal line item.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crm_benefit_sold_products (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    client_id INT UNSIGNED NOT NULL,
    crm_deal_id INT UNSIGNED NOT NULL,
    crm_product_id INT UNSIGNED NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL DEFAULT 1.00,
    deleted_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_sp_client (client_id),
    KEY idx_sp_deal (crm_deal_id),
    KEY idx_sp_product (crm_product_id),
    KEY idx_sp_created (created_at),
    CONSTRAINT fk_sp_product FOREIGN KEY (crm_product_id) REFERENCES crm_products (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 14. employee_products
--     Many-to-many junction: which crm_products each employee is assigned to
--     target / sell. One row per (employee, product) pair.
--     RS use: cold-start affinity signal — products an employee is explicitly
--     assigned to are boosted in their personalised homepage feed.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS employee_products (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    employee_id INT UNSIGNED NOT NULL,
    crm_product_id INT UNSIGNED NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_emp_product (employee_id, crm_product_id),
    KEY idx_ep_employee (employee_id),
    KEY idx_ep_product (crm_product_id),
    CONSTRAINT fk_ep_employee FOREIGN KEY (employee_id) REFERENCES employees (id),
    CONSTRAINT fk_ep_product FOREIGN KEY (crm_product_id) REFERENCES crm_products (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 16. benefit_me_payment_histories
--     Client plan payment ledger.
--     item IN ('start','pro','business')
--     type IN ('upgrade','renewal')
--     Confirms buy signal end-to-end; used for client plan-tier feature.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS benefit_me_payment_histories (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    client_id INT UNSIGNED NOT NULL,
    erp_invoice_id INT UNSIGNED DEFAULT NULL,
    payment_id INT UNSIGNED NOT NULL,
    remaining_duration INT DEFAULT NULL,
    item VARCHAR(20) NOT NULL,
    `type` VARCHAR(20) NOT NULL,
    `old` DATE DEFAULT NULL,
    `new` DATE DEFAULT NULL,
    unit_price DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    `value` DECIMAL(12, 2) NOT NULL DEFAULT 1.00,
    sub_total DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    grand_total DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    description TEXT DEFAULT NULL,
    start_at DATETIME DEFAULT NULL,
    end_at DATETIME DEFAULT NULL,
    duration INT DEFAULT NULL,
    created_by_id INT UNSIGNED DEFAULT NULL,
    created_by_type VARCHAR(100) DEFAULT NULL,
    updated_by_id INT UNSIGNED DEFAULT NULL,
    updated_by_type VARCHAR(100) DEFAULT NULL,
    deleted_by_id INT UNSIGNED DEFAULT NULL,
    deleted_by_type VARCHAR(100) DEFAULT NULL,
    deleted_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_ph_client (client_id),
    KEY idx_ph_payment (payment_id),
    KEY idx_ph_item_type (item, `type`),
    KEY idx_ph_created (created_at)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 17. crm_product_restaurants
--     Type-specific detail for food/restaurant products.
--     One row per crm_products row where product_type = 'food'.
--     Holds merchant contact, geo, and operating-hours metadata.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crm_product_restaurants (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    crm_product_id INT UNSIGNED NOT NULL,
    phone VARCHAR(30) DEFAULT NULL,
    address TEXT DEFAULT NULL,
    map_location_url VARCHAR(1000) DEFAULT NULL,
    facebook_url VARCHAR(500) DEFAULT NULL,
    opening_hours VARCHAR(255) DEFAULT NULL,
    latitude DECIMAL(10, 8) DEFAULT NULL,
    longitude DECIMAL(11, 8) DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_restaurant_product (crm_product_id),
    KEY idx_rest_lat_lng (latitude, longitude),
    CONSTRAINT fk_rest_product FOREIGN KEY (crm_product_id) REFERENCES crm_products (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 18. crm_product_stores
--     Type-specific detail for store-type products.
--     One row per crm_products row where product_type = 'store'.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crm_product_stores (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    crm_product_id INT UNSIGNED NOT NULL,
    phone VARCHAR(30) DEFAULT NULL,
    address TEXT DEFAULT NULL,
    map_location_url VARCHAR(1000) DEFAULT NULL,
    facebook_url VARCHAR(500) DEFAULT NULL,
    opening_hours VARCHAR(255) DEFAULT NULL,
    latitude DECIMAL(10, 8) DEFAULT NULL,
    longitude DECIMAL(11, 8) DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_store_product (crm_product_id),
    KEY idx_store_lat_lng (latitude, longitude),
    CONSTRAINT fk_store_product FOREIGN KEY (crm_product_id) REFERENCES crm_products (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- -----------------------------------------------------------------------------
-- 19. crm_product_services
--     Type-specific detail for service-type products.
--     One row per crm_products row where product_type = 'service'.
--     selling_price stores the billing model label (e.g. "Per Session",
--     "Monthly", "Annual", "Fixed Price", "Per Hour").
--     start_price / end_price bound the variable price range for the service.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crm_product_services (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    crm_product_id INT UNSIGNED NOT NULL,
    selling_price VARCHAR(100) DEFAULT NULL,
    start_price DECIMAL(12, 2) DEFAULT NULL,
    end_price DECIMAL(12, 2) DEFAULT NULL,
    phone VARCHAR(30) DEFAULT NULL,
    facebook_url VARCHAR(500) DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_service_product (crm_product_id),
    KEY idx_svc_selling_price (selling_price),
    CONSTRAINT fk_svc_product FOREIGN KEY (crm_product_id) REFERENCES crm_products (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
SET FOREIGN_KEY_CHECKS = 1;