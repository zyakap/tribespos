# TRIBESPOS — COMPLETE SYSTEM BLUEPRINT
> **For:** Claude Code Implementation  
> **Client:** Harhurum.com.pg — Papua New Guinea  
> **Stack:** Django 4.2 LTS · MySQL 8 · Material Design (MDB5) · Django REST Framework · Celery · Redis · Django Channels · WeasyPrint  
> **Version:** 2.0 — Definitive

---

## TABLE OF CONTENTS

1. [System Identity & Overview](#1-system-identity--overview)
2. [The Five Modules](#2-the-five-modules)
3. [Architecture](#3-architecture)
4. [Technology Stack](#4-technology-stack)
5. [Database Schema](#5-database-schema)
6. [Module 1 — TribesCoffeeClub Restaurant POS](#6-module-1--tribescoffeeclub-restaurant-pos)
7. [Module 2 — TribesSuppliers Inventory](#7-module-2--tribessuppliers-inventory)
8. [Module 3 — ParadiseTailoring](#8-module-3--paradisetailoring)
9. [Module 4 — Accounting Dashboard](#9-module-4--accounting-dashboard)
10. [Module 5 — SuperAdmin Dashboard (MD)](#10-module-5--superadmin-dashboard-md)
11. [IRC PNG Tax Compliance Engine](#11-irc-png-tax-compliance-engine)
12. [Shared Accounting Engine](#12-shared-accounting-engine)
13. [User Roles & Access Control](#13-user-roles--access-control)
14. [API Endpoints](#14-api-endpoints)
15. [Django Project Structure](#15-django-project-structure)
16. [Settings & Configuration](#16-settings--configuration)
17. [UI/UX Guidelines](#17-uiux-guidelines)
18. [Deployment](#18-deployment)
19. [Implementation Phases](#19-implementation-phases)
20. [Claude Code Instructions](#20-claude-code-instructions)

---

## 1. SYSTEM IDENTITY & OVERVIEW

### Name
**TribesPOS** — a unified, multi-module Point of Sale and Accounting platform built for Papua New Guinea.

### Purpose
Replace HikePOS and Xero with a single, self-contained system that covers:
- Restaurant & café sales
- Supplier-to-warehouse inventory management
- Custom tailoring order tracking
- Full double-entry accounting with PNG IRC tax compliance
- A single Managing Director super dashboard across everything

### Key Principles
- **One codebase, five modules** — all share the same database, accounting engine, and user system
- **Every transaction posts a journal entry automatically** — no manual bookkeeping
- **IRC-compliant** — GST, SWT, CIT and WHT returns generated automatically
- **Role-locked dashboards** — each login type lands on exactly what they need, nothing more
- **Offline-capable POS** — service worker + IndexedDB on POS terminals
- **PNG context** — currency PGK, GST 10%, fiscal year Jan–Dec

---

## 2. THE FIVE MODULES

| # | Module | Business Unit | Primary Users |
|---|---|---|---|
| 1 | **TribesCoffeeClub Restaurant POS** | Café + Restaurant | Cashier, Waiter, Barista, Manager |
| 2 | **TribesSuppliers Inventory** | Warehouse / Supply Chain | Inventory Staff, Receiver, Packer, Dispatcher, Inventory Manager |
| 3 | **ParadiseTailoring** | Tailoring Shop | Tailor Staff, Salesperson, Admin |
| 4 | **Accounting** | Finance | Accountant |
| 5 | **SuperAdmin** | Entire system | Managing Director |

All five modules connect to a **single shared accounting ledger**. Every sale, purchase, payroll, or adjustment posts a double-entry journal automatically.

---

## 3. ARCHITECTURE

```
╔══════════════════════════════════════════════════════════════════════╗
║                         T R I B E S P O S                           ║
╠══════════════════╦══════════════════╦══════════════════════════════╣
║ MODULE 1         ║ MODULE 2         ║ MODULE 3                     ║
║ TribesCoffeeClub ║ TribesSuppliers  ║ ParadiseTailoring            ║
║ Restaurant POS   ║ Inventory        ║ Orders & Dispatch            ║
╠══════════════════╩══════════════════╩══════════════════════════════╣
║ MODULE 4: Accounting Dashboard    MODULE 5: SuperAdmin (MD)        ║
╠══════════════════════════════════════════════════════════════════════╣
║            SHARED CORE SERVICES                                      ║
║  Double-Entry Accounting  │  IRC Tax Engine  │  Products & Stock    ║
║  Customers & Suppliers    │  User / RBAC     │  Reporting & Export  ║
╠══════════════════════════════════════════════════════════════════════╣
║         Django 4.2  ·  DRF  ·  Channels  ·  Celery  ·  Redis       ║
╠══════════════════════════════════════════════════════════════════════╣
║                        MySQL 8.0                                     ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Login → Dashboard Routing
```
User logs in
    │
    ├── cashier / barista / waiter  →  TribesCoffeeClub POS Terminal
    ├── coffee_manager              →  TribesCoffeeClub Manager Dashboard
    ├── inventory_staff             →  TribesSuppliers Inventory View
    ├── inventory_manager           →  TribesSuppliers Manager Dashboard
    ├── tailor_staff                →  ParadiseTailoring Staff View
    ├── tailoring_admin             →  ParadiseTailoring Admin Dashboard
    ├── accountant                  →  Accounting Dashboard
    └── superadmin                  →  SuperAdmin MD Dashboard
```

---

## 4. TECHNOLOGY STACK

| Layer | Technology | Purpose |
|---|---|---|
| Framework | Django 4.2 LTS | Core application |
| Database | MySQL 8.0 | Primary data store |
| REST API | Django REST Framework 3.15 | POS terminal API + mobile |
| Auth | Django Auth + SimpleJWT | Web + API authentication |
| Async/Queue | Celery 5.4 + Redis 7 | Background tasks, tax return generation |
| Real-time | Django Channels 4 + Redis | Kitchen display WebSocket |
| Frontend | MDB5 (Material Design Bootstrap 5) | All templates |
| Charts | Chart.js 4 | Dashboard visualisations |
| PDF | WeasyPrint 62 | Tax returns, receipts, invoices |
| Excel | openpyxl 3.1 | Report exports |
| Barcodes | python-barcode + ZPL | Product labels |
| Offline POS | Service Worker + IndexedDB | Café/Restaurant offline capability |
| Container | Docker + docker-compose | Development + production |
| Web server | Nginx + Gunicorn + Daphne | Production serving |

---

## 5. DATABASE SCHEMA

### 5.1 Users & Roles

```sql
-- Django default auth_user table is used.

CREATE TABLE staff_profile (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    user_id             INT UNIQUE NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    module              ENUM(
                            'coffeeclub',       -- Module 1
                            'suppliers',        -- Module 2
                            'tailoring',        -- Module 3
                            'accounting',       -- Module 4
                            'superadmin'        -- Module 5
                        ) NOT NULL,
    role                ENUM(
                            -- Module 1
                            'cashier',
                            'barista',
                            'waiter',
                            'coffee_manager',
                            -- Module 2
                            'inventory_staff',
                            'receiver',
                            'packer',
                            'dispatcher',
                            'inventory_manager',
                            -- Module 3
                            'tailor_staff',
                            'tailor_salesperson',
                            'tailoring_admin',
                            -- Module 4
                            'accountant',
                            -- Module 5
                            'superadmin'
                        ) NOT NULL,
    pin                 VARCHAR(6),              -- quick POS PIN login
    phone               VARCHAR(30),
    is_active           BOOL DEFAULT TRUE,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 5.2 Customers

```sql
CREATE TABLE customer (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    code                VARCHAR(20) UNIQUE,
    name                VARCHAR(150) NOT NULL,
    phone               VARCHAR(30),
    email               VARCHAR(150),
    address             TEXT,
    customer_type       ENUM('walk_in','account','wholesale','vip') DEFAULT 'walk_in',
    loyalty_points      INT DEFAULT 0,
    credit_limit        DECIMAL(12,2) DEFAULT 0.00,
    outstanding_balance DECIMAL(12,2) DEFAULT 0.00,
    module_source       ENUM('coffeeclub','suppliers','tailoring') NOT NULL,
    notes               TEXT,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 5.3 Suppliers

```sql
CREATE TABLE supplier (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    code                VARCHAR(20) UNIQUE NOT NULL,
    name                VARCHAR(150) NOT NULL,
    contact_person      VARCHAR(100),
    phone               VARCHAR(30),
    email               VARCHAR(150),
    address             TEXT,
    payment_terms_days  INT DEFAULT 30,
    currency            VARCHAR(3) DEFAULT 'PGK',
    gst_registered      BOOL DEFAULT TRUE,
    tax_invoice_number  VARCHAR(50),
    is_active           BOOL DEFAULT TRUE,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 5.4 Products & Inventory

```sql
CREATE TABLE category (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    parent_id   INT REFERENCES category(id),
    name        VARCHAR(100) NOT NULL,
    module      ENUM('coffeeclub','suppliers','tailoring','shared'),
    sort_order  INT DEFAULT 0
);

CREATE TABLE unit_of_measure (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(30) NOT NULL,   -- Kilogram, Litre, Piece, Metre
    abbreviation    VARCHAR(10) NOT NULL    -- kg, L, pcs, m
);

CREATE TABLE product (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    sku             VARCHAR(50) UNIQUE NOT NULL,
    barcode         VARCHAR(50),
    name            VARCHAR(200) NOT NULL,
    category_id     INT REFERENCES category(id),
    uom_id          INT REFERENCES unit_of_measure(id),
    module          ENUM('coffeeclub','suppliers','tailoring','shared') NOT NULL,
    product_type    ENUM('goods','service','composite','fabric','packaging') NOT NULL,
    cost_price      DECIMAL(12,4) DEFAULT 0.0000,
    sell_price      DECIMAL(12,2) DEFAULT 0.00,
    sell_price_wholesale DECIMAL(12,2),
    gst_type        ENUM('taxable','zero_rated','exempt') DEFAULT 'taxable',
    tax_inclusive   BOOL DEFAULT TRUE,
    track_inventory BOOL DEFAULT TRUE,
    min_stock_level DECIMAL(12,3) DEFAULT 0.000,
    reorder_qty     DECIMAL(12,3) DEFAULT 0.000,
    image           VARCHAR(255),
    description     TEXT,
    is_active       BOOL DEFAULT TRUE,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE product_variant (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    product_id      INT NOT NULL REFERENCES product(id),
    sku_suffix      VARCHAR(20),
    attributes_json JSON,               -- {"size":"XL","colour":"Red"}
    barcode         VARCHAR(50),
    cost_price      DECIMAL(12,4),
    sell_price      DECIMAL(12,2),
    is_active       BOOL DEFAULT TRUE
);

-- Bill of Materials (for café composite menu items)
CREATE TABLE bom_item (
    id                      INT PRIMARY KEY AUTO_INCREMENT,
    parent_product_id       INT NOT NULL REFERENCES product(id),
    component_product_id    INT NOT NULL REFERENCES product(id),
    quantity                DECIMAL(12,4) NOT NULL
);
```

### 5.5 Warehouses & Stock

```sql
CREATE TABLE warehouse (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(100) NOT NULL,
    module          ENUM('coffeeclub','suppliers','tailoring','shared'),
    location_type   ENUM('main','cold_room','bar','kitchen','fabric_store','packaging') DEFAULT 'main',
    is_active       BOOL DEFAULT TRUE
);

-- Bin-level locations (used by TribesSuppliers for precise tracking)
CREATE TABLE warehouse_location (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    warehouse_id    INT NOT NULL REFERENCES warehouse(id),
    aisle           VARCHAR(10),
    rack            VARCHAR(10),
    shelf           VARCHAR(10),
    bin             VARCHAR(10),
    location_code   VARCHAR(30) GENERATED ALWAYS AS (
                        CONCAT_WS('-', aisle, rack, shelf, bin)
                    ) STORED UNIQUE,
    is_active       BOOL DEFAULT TRUE
);

CREATE TABLE stock_location (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    product_id      INT NOT NULL REFERENCES product(id),
    variant_id      INT REFERENCES product_variant(id),
    warehouse_id    INT NOT NULL REFERENCES warehouse(id),
    bin_location_id INT REFERENCES warehouse_location(id),
    batch_number    VARCHAR(50),
    expiry_date     DATE,
    qty_on_hand     DECIMAL(12,3) DEFAULT 0.000,
    qty_reserved    DECIMAL(12,3) DEFAULT 0.000,
    qty_available   DECIMAL(12,3) AS (qty_on_hand - qty_reserved) STORED,
    last_updated    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_stock (product_id, variant_id, warehouse_id, bin_location_id, batch_number)
);

-- Full audit trail of every stock movement
CREATE TABLE stock_movement (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    product_id      INT NOT NULL REFERENCES product(id),
    variant_id      INT REFERENCES product_variant(id),
    warehouse_id    INT NOT NULL REFERENCES warehouse(id),
    movement_type   ENUM('purchase','sale','adjustment','transfer_in','transfer_out',
                         'production','waste','return','pack_consumption','dispatch') NOT NULL,
    reference_type  VARCHAR(50),    -- PurchaseOrder, SaleOrder, TailoringOrder, etc.
    reference_id    INT,
    qty             DECIMAL(12,3) NOT NULL,     -- positive=in, negative=out
    unit_cost       DECIMAL(12,4),
    total_cost      DECIMAL(14,4),
    notes           TEXT,
    created_by_id   INT REFERENCES auth_user(id),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 5.6 Procurement (TribesSuppliers)

```sql
CREATE TABLE purchase_order (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    po_number           VARCHAR(30) UNIQUE NOT NULL,    -- PO-2025-0001
    supplier_id         INT NOT NULL REFERENCES supplier(id),
    warehouse_id        INT NOT NULL REFERENCES warehouse(id),
    status              ENUM('draft','pending_approval','approved','sent',
                             'partial','received','cancelled') DEFAULT 'draft',
    approval_status     ENUM('pending','approved','rejected') DEFAULT 'pending',
    approved_by_id      INT REFERENCES auth_user(id),
    approved_at         DATETIME,
    order_date          DATE NOT NULL,
    expected_date       DATE,
    received_date       DATE,
    subtotal            DECIMAL(14,2) DEFAULT 0.00,
    tax_total           DECIMAL(14,2) DEFAULT 0.00,
    total               DECIMAL(14,2) DEFAULT 0.00,
    notes               TEXT,
    created_by_id       INT REFERENCES auth_user(id),
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE purchase_order_line (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    po_id           INT NOT NULL REFERENCES purchase_order(id),
    product_id      INT NOT NULL REFERENCES product(id),
    variant_id      INT REFERENCES product_variant(id),
    qty_ordered     DECIMAL(12,3) NOT NULL,
    qty_received    DECIMAL(12,3) DEFAULT 0.000,
    unit_cost       DECIMAL(12,4) NOT NULL,
    tax_rate        DECIMAL(5,2) DEFAULT 10.00,
    line_total      DECIMAL(14,2)
);

CREATE TABLE goods_received_note (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    grn_number      VARCHAR(30) UNIQUE NOT NULL,    -- GRN-2025-0001
    po_id           INT NOT NULL REFERENCES purchase_order(id),
    warehouse_id    INT NOT NULL REFERENCES warehouse(id),
    received_by_id  INT REFERENCES auth_user(id),
    received_date   DATE NOT NULL,
    delivery_ref    VARCHAR(50),
    vehicle_reg     VARCHAR(20),
    status          ENUM('draft','qc_pending','qc_done','putaway_done') DEFAULT 'draft',
    notes           TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE grn_line (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    grn_id          INT NOT NULL REFERENCES goods_received_note(id),
    po_line_id      INT REFERENCES purchase_order_line(id),
    product_id      INT NOT NULL REFERENCES product(id),
    variant_id      INT REFERENCES product_variant(id),
    qty_received    DECIMAL(12,3) NOT NULL,
    qty_accepted    DECIMAL(12,3),
    qty_rejected    DECIMAL(12,3) DEFAULT 0.000,
    reject_reason   TEXT,
    unit_cost       DECIMAL(12,4) NOT NULL,
    batch_number    VARCHAR(50),
    expiry_date     DATE,
    putaway_bin_id  INT REFERENCES warehouse_location(id)
);

CREATE TABLE qc_inspection (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    grn_line_id     INT NOT NULL REFERENCES grn_line(id),
    inspected_by_id INT REFERENCES auth_user(id),
    inspected_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    result          ENUM('pass','fail','partial') NOT NULL,
    defect_type     VARCHAR(100),
    action          ENUM('accepted','returned_to_supplier','quarantined','written_off'),
    photos_json     JSON,
    notes           TEXT
);

CREATE TABLE supplier_invoice (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    invoice_number  VARCHAR(50) NOT NULL,
    supplier_id     INT NOT NULL REFERENCES supplier(id),
    po_id           INT REFERENCES purchase_order(id),
    invoice_date    DATE NOT NULL,
    due_date        DATE,
    subtotal        DECIMAL(14,2),
    tax_total       DECIMAL(14,2),
    total           DECIMAL(14,2),
    amount_paid     DECIMAL(14,2) DEFAULT 0.00,
    status          ENUM('unpaid','partial','paid','overdue') DEFAULT 'unpaid',
    journal_entry_id INT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 5.7 Packaging & Dispatch (TribesSuppliers)

```sql
CREATE TABLE packaging_order (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    pack_number     VARCHAR(30) UNIQUE NOT NULL,    -- PACK-2025-0001
    status          ENUM('pending','picking','packed','ready_dispatch','cancelled') DEFAULT 'pending',
    priority        ENUM('low','normal','high','urgent') DEFAULT 'normal',
    assigned_to_id  INT REFERENCES auth_user(id),
    customer_id     INT REFERENCES customer(id),
    requested_date  DATE,
    packed_date     DATE,
    notes           TEXT,
    created_by_id   INT REFERENCES auth_user(id),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE packaging_order_line (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    packaging_order_id  INT NOT NULL REFERENCES packaging_order(id),
    product_id          INT NOT NULL REFERENCES product(id),
    variant_id          INT REFERENCES product_variant(id),
    qty_requested       DECIMAL(12,3) NOT NULL,
    qty_picked          DECIMAL(12,3) DEFAULT 0.000,
    qty_packed          DECIMAL(12,3) DEFAULT 0.000,
    pick_bin_id         INT REFERENCES warehouse_location(id),
    batch_number        VARCHAR(50)
);

CREATE TABLE shipment (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    shipment_number     VARCHAR(30) UNIQUE NOT NULL,    -- SHIP-2025-0001
    packaging_order_id  INT REFERENCES packaging_order(id),
    customer_id         INT REFERENCES customer(id),
    recipient_name      VARCHAR(150),
    delivery_address    TEXT NOT NULL,
    delivery_province   VARCHAR(50),
    carrier             VARCHAR(100),
    tracking_number     VARCHAR(100),
    vehicle_reg         VARCHAR(20),
    driver_name         VARCHAR(100),
    driver_phone        VARCHAR(30),
    status              ENUM('pending','collected','in_transit',
                             'out_for_delivery','delivered','failed','returned') DEFAULT 'pending',
    dispatch_date       DATE,
    estimated_delivery  DATE,
    actual_delivery     DATE,
    pod_image           VARCHAR(255),       -- proof of delivery photo
    recipient_signature VARCHAR(255),       -- signature image
    notes               TEXT,
    created_by_id       INT REFERENCES auth_user(id),
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE shipment_line (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    shipment_id     INT NOT NULL REFERENCES shipment(id),
    product_id      INT NOT NULL REFERENCES product(id),
    variant_id      INT REFERENCES product_variant(id),
    qty_shipped     DECIMAL(12,3) NOT NULL,
    batch_number    VARCHAR(50),
    unit_value      DECIMAL(12,2)
);

CREATE TABLE delivery_attempt (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    shipment_id     INT NOT NULL REFERENCES shipment(id),
    attempt_date    DATETIME NOT NULL,
    outcome         ENUM('delivered','not_home','wrong_address','refused','rescheduled'),
    notes           TEXT,
    gps_lat         DECIMAL(10,7),
    gps_lng         DECIMAL(10,7),
    recorded_by_id  INT REFERENCES auth_user(id)
);

CREATE TABLE cycle_count (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    count_number    VARCHAR(30) UNIQUE NOT NULL,
    warehouse_id    INT NOT NULL REFERENCES warehouse(id),
    count_type      ENUM('full','partial','spot') DEFAULT 'partial',
    status          ENUM('planned','in_progress','completed','approved') DEFAULT 'planned',
    planned_date    DATE,
    completed_at    DATETIME,
    approved_by_id  INT REFERENCES auth_user(id),
    variance_value  DECIMAL(14,2),
    notes           TEXT
);

CREATE TABLE cycle_count_line (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    cycle_count_id  INT NOT NULL REFERENCES cycle_count(id),
    product_id      INT NOT NULL REFERENCES product(id),
    variant_id      INT REFERENCES product_variant(id),
    bin_location_id INT REFERENCES warehouse_location(id),
    system_qty      DECIMAL(12,3),
    counted_qty     DECIMAL(12,3),
    variance        DECIMAL(12,3),
    variance_value  DECIMAL(14,2),
    counted_by_id   INT REFERENCES auth_user(id),
    adjustment_posted BOOL DEFAULT FALSE
);
```

### 5.8 Sales / POS (TribesCoffeeClub & Storefront)

```sql
CREATE TABLE sale_order (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    order_number    VARCHAR(30) UNIQUE NOT NULL,   -- TCK-2025-00001 / SO-2025-00001
    module          ENUM('coffeeclub','suppliers','tailoring') NOT NULL,
    sale_type       ENUM('pos','table','takeaway','delivery','wholesale','account') NOT NULL,
    status          ENUM('open','held','completed','void','refunded') DEFAULT 'open',
    customer_id     INT REFERENCES customer(id),
    table_number    VARCHAR(10),
    covers          INT,
    cashier_id      INT REFERENCES auth_user(id),
    waiter_id       INT REFERENCES auth_user(id),
    terminal_id     VARCHAR(30),
    subtotal        DECIMAL(14,2) DEFAULT 0.00,
    discount_amount DECIMAL(14,2) DEFAULT 0.00,
    tax_total       DECIMAL(14,2) DEFAULT 0.00,
    total           DECIMAL(14,2) DEFAULT 0.00,
    notes           TEXT,
    opened_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at    DATETIME,
    journal_entry_id INT
);

CREATE TABLE sale_order_line (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    order_id        INT NOT NULL REFERENCES sale_order(id),
    product_id      INT NOT NULL REFERENCES product(id),
    variant_id      INT REFERENCES product_variant(id),
    product_name    VARCHAR(200),       -- snapshot at time of sale
    qty             DECIMAL(12,3) NOT NULL,
    unit_price      DECIMAL(12,2) NOT NULL,
    discount_pct    DECIMAL(5,2) DEFAULT 0.00,
    tax_rate        DECIMAL(5,2) DEFAULT 10.00,
    tax_inclusive   BOOL DEFAULT TRUE,
    line_total      DECIMAL(14,2),
    course          VARCHAR(20),        -- restaurant: Starter / Main / Dessert
    sent_to_kitchen BOOL DEFAULT FALSE,
    notes           TEXT
);

-- Modifiers for café items (extra shot, oat milk, no sugar, etc.)
CREATE TABLE order_line_modifier (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    line_id         INT NOT NULL REFERENCES sale_order_line(id),
    modifier_name   VARCHAR(100) NOT NULL,
    price_adjustment DECIMAL(10,2) DEFAULT 0.00
);

CREATE TABLE modifier_group (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    product_id  INT NOT NULL REFERENCES product(id),
    name        VARCHAR(100),               -- "Milk Type", "Size", "Extras"
    required    BOOL DEFAULT FALSE,
    multi_select BOOL DEFAULT FALSE
);

CREATE TABLE modifier_option (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    modifier_group_id   INT NOT NULL REFERENCES modifier_group(id),
    name                VARCHAR(100) NOT NULL,
    price_adjustment    DECIMAL(10,2) DEFAULT 0.00
);

CREATE TABLE payment (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    order_id        INT NOT NULL REFERENCES sale_order(id),
    payment_method  ENUM('cash','eftpos','visa','mastercard',
                         'mobile_money','account_credit','voucher') NOT NULL,
    amount          DECIMAL(14,2) NOT NULL,
    reference       VARCHAR(100),
    tendered        DECIMAL(14,2),
    change_given    DECIMAL(14,2),
    paid_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_by_id INT REFERENCES auth_user(id),
    journal_entry_id INT
);

CREATE TABLE cash_session (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    terminal_id     VARCHAR(30) NOT NULL,
    module          ENUM('coffeeclub','suppliers') NOT NULL,
    cashier_id      INT REFERENCES auth_user(id),
    opened_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    closed_at       DATETIME,
    opening_float   DECIMAL(12,2) DEFAULT 0.00,
    closing_cash    DECIMAL(12,2),
    expected_cash   DECIMAL(12,2),
    variance        DECIMAL(12,2),
    status          ENUM('open','closed') DEFAULT 'open',
    notes           TEXT
);
```

### 5.9 Restaurant Tables & Kitchen (TribesCoffeeClub)

```sql
CREATE TABLE restaurant_table (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    table_number    VARCHAR(10) NOT NULL,
    section         VARCHAR(50),            -- Indoor, Outdoor, Bar, Private
    capacity        INT DEFAULT 4,
    status          ENUM('available','occupied','reserved','cleaning') DEFAULT 'available',
    current_order_id INT REFERENCES sale_order(id)
);

CREATE TABLE kitchen_ticket (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    order_id        INT NOT NULL REFERENCES sale_order(id),
    ticket_number   INT NOT NULL,
    status          ENUM('new','acknowledged','preparing','ready','delivered') DEFAULT 'new',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at DATETIME,
    ready_at        DATETIME,
    delivered_at    DATETIME
);

CREATE TABLE kitchen_ticket_line (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id       INT NOT NULL REFERENCES kitchen_ticket(id),
    order_line_id   INT NOT NULL REFERENCES sale_order_line(id),
    qty             DECIMAL(12,3),
    modifiers_text  TEXT,
    notes           TEXT
);

CREATE TABLE table_reservation (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    table_id        INT NOT NULL REFERENCES restaurant_table(id),
    customer_id     INT REFERENCES customer(id),
    guest_name      VARCHAR(150),
    guest_phone     VARCHAR(30),
    covers          INT,
    reserved_for    DATETIME NOT NULL,
    duration_mins   INT DEFAULT 90,
    status          ENUM('confirmed','seated','cancelled','no_show') DEFAULT 'confirmed',
    notes           TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 5.10 ParadiseTailoring

```sql
CREATE TABLE tailoring_order (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    order_number    VARCHAR(30) UNIQUE NOT NULL,    -- PT-2025-00001
    customer_id     INT NOT NULL REFERENCES customer(id),
    salesperson_id  INT REFERENCES auth_user(id),
    tailor_id       INT REFERENCES auth_user(id),
    status          ENUM('quote','confirmed','cutting','sewing',
                         'finishing','ready','collected','cancelled') DEFAULT 'quote',
    garment_type    VARCHAR(100) NOT NULL,          -- Dress, Suit, Shirt, Skirt...
    style_notes     TEXT,
    reference_image VARCHAR(255),
    measurements_json JSON,                        -- {"chest":92,"waist":78,"hip":96,...}
    fabric_product_id INT REFERENCES product(id),
    fabric_qty      DECIMAL(10,3),
    labour_charge   DECIMAL(12,2) DEFAULT 0.00,
    fabric_charge   DECIMAL(12,2) DEFAULT 0.00,
    accessories_charge DECIMAL(12,2) DEFAULT 0.00,
    discount_amount DECIMAL(12,2) DEFAULT 0.00,
    total           DECIMAL(12,2) DEFAULT 0.00,
    deposit_paid    DECIMAL(12,2) DEFAULT 0.00,
    balance_due     DECIMAL(12,2),
    promised_date   DATE,
    completed_date  DATE,
    collected_date  DATE,
    dispatch_required BOOL DEFAULT FALSE,
    notes           TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tailoring_stage_log (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    tailoring_order_id  INT NOT NULL REFERENCES tailoring_order(id),
    stage               VARCHAR(50) NOT NULL,
    notes               TEXT,
    changed_by_id       INT REFERENCES auth_user(id),
    changed_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tailoring shipment (if customer requests delivery)
CREATE TABLE tailoring_shipment (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    tailoring_order_id  INT NOT NULL REFERENCES tailoring_order(id),
    shipment_id         INT REFERENCES shipment(id),    -- reuses TribesSuppliers dispatch
    dispatch_date       DATE,
    status              ENUM('pending','dispatched','delivered') DEFAULT 'pending',
    notes               TEXT
);
```

### 5.11 Accounting (Double-Entry)

```sql
CREATE TABLE account (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    code            VARCHAR(10) UNIQUE NOT NULL,
    name            VARCHAR(150) NOT NULL,
    account_type    ENUM('asset','liability','equity','revenue','expense','cogs') NOT NULL,
    account_subtype VARCHAR(50),
    module          ENUM('coffeeclub','suppliers','tailoring','shared') DEFAULT 'shared',
    parent_id       INT REFERENCES account(id),
    is_system       BOOL DEFAULT FALSE,
    normal_balance  ENUM('debit','credit') NOT NULL,
    is_active       BOOL DEFAULT TRUE,
    description     TEXT
);

CREATE TABLE fiscal_year (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(50) NOT NULL,       -- FY 2025
    start_date  DATE NOT NULL,              -- 2025-01-01
    end_date    DATE NOT NULL,              -- 2025-12-31
    is_closed   BOOL DEFAULT FALSE
);

CREATE TABLE fiscal_period (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    fiscal_year_id  INT NOT NULL REFERENCES fiscal_year(id),
    name            VARCHAR(20) NOT NULL,   -- Jan 2025
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    is_closed       BOOL DEFAULT FALSE
);

CREATE TABLE journal_entry (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    entry_number    VARCHAR(30) UNIQUE NOT NULL,    -- JE-2025-00001
    entry_type      ENUM('sale','purchase','payment','receipt','payroll',
                         'adjustment','depreciation','tax','manual') NOT NULL,
    module          ENUM('coffeeclub','suppliers','tailoring','shared'),
    reference_type  VARCHAR(50),
    reference_id    INT,
    fiscal_period_id INT REFERENCES fiscal_period(id),
    entry_date      DATE NOT NULL,
    description     TEXT,
    total_debit     DECIMAL(16,2),
    total_credit    DECIMAL(16,2),
    is_posted       BOOL DEFAULT FALSE,
    created_by_id   INT REFERENCES auth_user(id),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE journal_line (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    journal_entry_id    INT NOT NULL REFERENCES journal_entry(id),
    account_id          INT NOT NULL REFERENCES account(id),
    description         VARCHAR(255),
    debit               DECIMAL(16,2) DEFAULT 0.00,
    credit              DECIMAL(16,2) DEFAULT 0.00,
    module              ENUM('coffeeclub','suppliers','tailoring','shared'),
    CONSTRAINT chk_dr_cr CHECK (
        (debit > 0 AND credit = 0) OR (credit > 0 AND debit = 0)
    )
);

CREATE TABLE bank_account (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    account_id      INT NOT NULL REFERENCES account(id),
    bank_name       VARCHAR(100),
    account_number  VARCHAR(50),
    branch          VARCHAR(50),
    currency        VARCHAR(3) DEFAULT 'PGK',
    current_balance DECIMAL(16,2) DEFAULT 0.00,
    is_active       BOOL DEFAULT TRUE
);

CREATE TABLE ar_invoice (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    invoice_number  VARCHAR(30) UNIQUE NOT NULL,
    module          ENUM('coffeeclub','suppliers','tailoring') NOT NULL,
    customer_id     INT NOT NULL REFERENCES customer(id),
    sale_order_id   INT REFERENCES sale_order(id),
    invoice_date    DATE NOT NULL,
    due_date        DATE,
    subtotal        DECIMAL(14,2),
    tax_total       DECIMAL(14,2),
    total           DECIMAL(14,2),
    amount_paid     DECIMAL(14,2) DEFAULT 0.00,
    outstanding     DECIMAL(14,2),
    status          ENUM('draft','sent','partial','paid','overdue','void') DEFAULT 'draft',
    journal_entry_id INT REFERENCES journal_entry(id)
);
```

### 5.12 IRC Tax Tables

```sql
CREATE TABLE gst_return (
    id                      INT PRIMARY KEY AUTO_INCREMENT,
    return_period           VARCHAR(7) NOT NULL UNIQUE,     -- '2025-01'
    period_start            DATE NOT NULL,
    period_end              DATE NOT NULL,
    due_date                DATE NOT NULL,                  -- 21st of following month
    status                  ENUM('draft','finalised','filed') DEFAULT 'draft',
    total_taxable_sales     DECIMAL(16,2) DEFAULT 0.00,
    output_tax_collected    DECIMAL(16,2) DEFAULT 0.00,
    total_zero_rated_sales  DECIMAL(16,2) DEFAULT 0.00,
    total_exempt_sales      DECIMAL(16,2) DEFAULT 0.00,
    total_taxable_purchases DECIMAL(16,2) DEFAULT 0.00,
    input_tax_credits       DECIMAL(16,2) DEFAULT 0.00,
    net_gst_payable         DECIMAL(16,2) DEFAULT 0.00,
    net_gst_refundable      DECIMAL(16,2) DEFAULT 0.00,
    filed_date              DATE,
    irc_reference           VARCHAR(50),
    notes                   TEXT
);

CREATE TABLE swt_remittance (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    remittance_month    VARCHAR(7) NOT NULL UNIQUE,     -- '2025-01'
    due_date            DATE NOT NULL,                  -- 7th of following month
    period_start        DATE NOT NULL,
    period_end          DATE NOT NULL,
    total_gross_wages   DECIMAL(14,2) DEFAULT 0.00,
    total_swt_withheld  DECIMAL(14,2) DEFAULT 0.00,
    employee_count      INT DEFAULT 0,
    status              ENUM('draft','filed','paid') DEFAULT 'draft',
    filed_date          DATE,
    irc_reference       VARCHAR(50)
);

CREATE TABLE employee (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT UNIQUE NOT NULL REFERENCES auth_user(id),
    irc_tin         VARCHAR(20),
    tax_status      ENUM('resident','non_resident') DEFAULT 'resident',
    pay_frequency   ENUM('fortnightly','monthly') DEFAULT 'fortnightly',
    base_salary     DECIMAL(12,2),
    start_date      DATE,
    is_active       BOOL DEFAULT TRUE
);

CREATE TABLE payroll_run (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    pay_period_start DATE NOT NULL,
    pay_period_end   DATE NOT NULL,
    pay_date         DATE NOT NULL,
    status          ENUM('draft','approved','paid') DEFAULT 'draft',
    total_gross     DECIMAL(14,2) DEFAULT 0.00,
    total_swt       DECIMAL(14,2) DEFAULT 0.00,
    total_net       DECIMAL(14,2) DEFAULT 0.00,
    approved_by_id  INT REFERENCES auth_user(id),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE payroll_line (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    payroll_run_id  INT NOT NULL REFERENCES payroll_run(id),
    employee_id     INT NOT NULL REFERENCES employee(id),
    gross_wages     DECIMAL(12,2) NOT NULL,
    housing_benefit DECIMAL(12,2) DEFAULT 0.00,
    vehicle_benefit DECIMAL(12,2) DEFAULT 0.00,
    other_benefits  DECIMAL(12,2) DEFAULT 0.00,
    total_taxable   DECIMAL(12,2),
    swt_deducted    DECIMAL(12,2),
    net_pay         DECIMAL(12,2)
);

CREATE TABLE cit_return (
    id                      INT PRIMARY KEY AUTO_INCREMENT,
    tax_year                INT NOT NULL UNIQUE,
    due_date                DATE NOT NULL,              -- 30 April following year
    status                  ENUM('draft','finalised','filed') DEFAULT 'draft',
    total_revenue           DECIMAL(16,2) DEFAULT 0.00,
    assessable_income       DECIMAL(16,2) DEFAULT 0.00,
    total_deductions        DECIMAL(16,2) DEFAULT 0.00,
    taxable_income          DECIMAL(16,2) DEFAULT 0.00,
    cit_rate                DECIMAL(5,2) DEFAULT 30.00,
    gross_cit               DECIMAL(16,2) DEFAULT 0.00,
    provisional_tax_paid    DECIMAL(16,2) DEFAULT 0.00,
    net_cit_payable         DECIMAL(16,2) DEFAULT 0.00,
    filed_date              DATE,
    irc_reference           VARCHAR(50)
);

CREATE TABLE provisional_tax_instalment (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    tax_year        INT NOT NULL,
    quarter         INT NOT NULL,           -- 1=Mar 31, 2=Jun 30, 3=Sep 30, 4=Dec 31
    due_date        DATE NOT NULL,
    estimated_amount DECIMAL(14,2),
    amount_paid     DECIMAL(14,2) DEFAULT 0.00,
    paid_date       DATE,
    status          ENUM('pending','paid','overdue') DEFAULT 'pending'
);
```

---

## 6. MODULE 1 — TRIBESCOFFEECLUB RESTAURANT POS

### 6.1 Purpose
Full point-of-sale system for the café and restaurant operation — counter service (café), table service (restaurant), and a kitchen display system.

### 6.2 Roles in This Module
| Role | Login Dashboard | Can Do |
|---|---|---|
| `cashier` | POS Terminal (café counter) | Open session, take orders, process payment, print receipt |
| `barista` | POS Terminal (barista view) | See order queue, mark drinks ready |
| `waiter` | Waiter Dashboard | Open tables, take orders, send to kitchen, print bill |
| `coffee_manager` | Manager Dashboard | All of above + reports, void, refund, Z-report, staff |

### 6.3 Features

#### POS Terminal (cashier / barista)
- Full-screen touch-optimised layout, no scrolling on main grid
- Product grid with category tabs (Coffee / Food / Drinks / Retail)
- Modifier pop-up on item tap (milk type, size, extra shot, temperature, add-ons)
- Order build panel — running total, GST display, discount field
- Payment screen: Cash (with change calculator), EFTPOS, Split
- Print receipt (thermal) — includes TribesPOS branding, GST breakdown
- Hold order and recall
- Offline mode — IndexedDB queues orders, syncs when connection restored
- Quick PIN login for shift change (no need to full logout/login)
- Cash session: open with float, close with Z-report

#### Waiter Dashboard
- Visual table floor plan — colour-coded by status (green=free, amber=occupied, red=overdue)
- Open table → assign to waiter → build order by course (Starter / Main / Dessert)
- Send to kitchen → generates WebSocket kitchen ticket
- Add items to existing open table order
- Print bill (itemised), split bill by seat or by item, even split
- Table merge and transfer
- Reservation list view (today's bookings)

#### Kitchen Display System (KDS)
- Dark-theme fullscreen display (runs on a kitchen screen)
- Real-time via Django Channels WebSocket
- Colour-coded ticket age: green (<5 min), amber (5–10 min), red (>10 min)
- Tap to acknowledge, tap to mark ready → waiter notified
- Display modifiers and notes prominently

#### Manager Dashboard (coffee_manager)
- Today's KPIs: Total Sales, Orders Count, Average Order Value, Cash vs Card split
- Hourly sales chart (Chart.js line chart)
- Sales by category (donut chart)
- Low stock alerts (ingredients / coffee beans / milk)
- Open cash sessions status
- Staff activity (who is logged in)
- Void/Refund approval queue
- Z-Report generation per terminal
- Quick reports: Daily Sales Summary, Sales by Product, Payment Method Breakdown

### 6.4 Business Logic

```python
# apps/coffeeclub/services.py

@transaction.atomic
def complete_sale(order_id: int, payments: list) -> dict:
    order = SaleOrder.objects.select_for_update().get(id=order_id, module='coffeeclub')
    assert order.status == 'open'

    total_paid = sum(p['amount'] for p in payments)
    assert total_paid >= order.total, "Underpayment"

    # 1. Record payments
    for p in payments:
        Payment.objects.create(order=order, **p)

    # 2. Deduct stock (deducts BOM components for composite items)
    for line in order.lines.select_related('product').all():
        deduct_bom_stock(line.product, line.qty, warehouse='coffeeclub_main')

    # 3. Auto-post accounting journal
    for payment in payments:
        post_journal(
            rule='cash_sale' if payment['method'] == 'cash' else 'eftpos_sale',
            context={'order': order, 'payment': payment}
        )

    order.status = 'completed'
    order.completed_at = timezone.now()
    order.save()
    return build_receipt(order)


# BOM deduction: Flat White = 18g ground coffee + 200ml milk + 1 cup
def deduct_bom_stock(product, qty_sold, warehouse):
    for bom in product.bom_items.select_related('component').all():
        component_qty = bom.quantity * qty_sold
        update_stock(bom.component, -component_qty, warehouse)
        record_movement(bom.component, 'sale', -component_qty, ref=product)
```

### 6.5 Accounting Journals — TribesCoffeeClub

```
CASH SALE:
  DR  1000  Cash in Hand                 (total inc GST)
  CR  4000  Café Revenue                 (GST-exclusive amount)
  CR  2100  GST Output Tax Payable       (GST portion)

EFTPOS SALE:
  DR  1010  EFTPOS Clearing              (total inc GST)
  CR  4000  Café Revenue
  CR  2100  GST Output Tax Payable

ACCOUNT/CREDIT SALE:
  DR  1100  Accounts Receivable
  CR  4000  Café Revenue
  CR  2100  GST Output Tax Payable

COGS DEDUCTION (per BOM component used):
  DR  5000  COGS — Café
  CR  1200  Inventory — Café Ingredients

CASH SESSION VARIANCE:
  DR/CR  6400  Cash Variance             (over/short)
```

---

## 7. MODULE 2 — TRIBESSUPPLIERS INVENTORY

### 7.1 Purpose
Complete supply chain management — from raising a purchase order with a supplier, through receiving, quality control, bin putaway, pick-and-pack, and dispatch to customers, with a storefront counter POS.

### 7.2 Supply Chain Pipeline
```
Reorder Alert
    → Purchase Order (raised by purchasing officer)
        → PO Approval (inventory manager approves)
            → PO Sent to Supplier
                → Goods Received Note + QC Inspection
                    → Putaway to Bin Location
                        → Packaging / Pick & Pack Order
                            → Shipment / Dispatch
                                → Proof of Delivery
                                    → Journal posted → Accounting
```

### 7.3 Roles in This Module
| Role | Dashboard | Can Do |
|---|---|---|
| `inventory_staff` | Inventory Staff View | View stock, record movements, cycle count |
| `receiver` | Receiving Dashboard | Create GRN, perform QC, assign putaway bins |
| `packer` | Packing Dashboard | View pack queue, confirm picks, mark packed |
| `dispatcher` | Dispatch Dashboard | Create shipments, update delivery status, log POD |
| `inventory_manager` | Inventory Manager Dashboard | Everything + approve POs, reports, cycle counts |

### 7.4 Features

#### Purchasing
- Reorder alert list (products below min stock threshold) with one-click "Create PO"
- PO create form — supplier, warehouse, line items with qty and cost
- PO approval workflow: `inventory_staff` drafts → `inventory_manager` approves → sent to supplier via email PDF
- PO list with status tracking (draft / approved / sent / partial / received)
- Supplier portal email: auto-generated PO PDF sent on approval
- AP invoice matching against PO + GRN

#### Receiving Warehouse
- Expected deliveries list (POs with status='sent', sorted by expected date)
- GRN creation — scan or enter quantities against each PO line
- QC Inspection per line: pass / fail / partial, photo evidence upload, reject reason
- Rejected goods actions: return to supplier / quarantine / write-off
- Putaway task list — assign QC-passed items to specific bin (aisle-rack-shelf-bin)
- Bin stock view — see exactly what is at each location

#### Packaging / Pick & Pack
- Pack order list with priority queue (urgent first)
- Pick list — shows: product name, qty needed, bin location, batch number
- Barcode scan to confirm each pick line
- Packaging material consumption logging (boxes, tape, labels deducted from stock)
- Mark order packed → triggers dispatch queue
- ZPL label printing for cartons

#### Dispatch
- Dispatch queue (packed orders awaiting collection or dispatch)
- Create shipment: assign carrier / own vehicle / driver / tracking number
- Delivery address with PNG province field
- Status updates: collected → in transit → out for delivery → delivered / failed
- Proof of delivery: upload photo + signature capture
- Failed delivery: log attempt, reason, reschedule date
- Delivery attempt history per shipment

#### Inventory Manager Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│  TRIBESUPPLIERS — INVENTORY MANAGER          [Live Refresh] │
├─────────────────────────────────────────────────────────────┤
│        SUPPLY CHAIN PIPELINE                                │
│  [12 Open POs]→[3 Pending GRN]→[1,842 SKUs]→              │
│  [8 Pack Orders]→[6 In Transit]                            │
├──────────────┬──────────────────┬───────────────────────────┤
│ WAREHOUSE    │  TODAY ACTIVITY  │  DISPATCH STATUS          │
│ SKUs: 284    │  Received: 3     │  Pending:     4           │
│ Low stock: 7 │  Packed:   8     │  In Transit:  6           │
│ Expiring: 2  │  Dispatched: 5   │  Delivered:   3           │
│ Quarantine:1 │  POs raised: 2   │  Failed:      1           │
├──────────────┴──────────────────┴───────────────────────────┤
│  PO APPROVAL QUEUE                                          │
│  PO-2025-042  Supplier A  K8,400   [Approve] [Reject]       │
│  PO-2025-043  Supplier B  K3,200   [Approve] [Reject]       │
├─────────────────────────────────────────────────────────────┤
│  LOW STOCK ALERTS (7)          EXPIRING SOON (2)            │
│  Product X — Stock: 3 / Min:20 │ Product Y — Exp: 15 Feb   │
└─────────────────────────────────────────────────────────────┘
```

#### Inventory Staff View
- Stock on hand table (filterable by category, warehouse, location)
- Stock movement history
- Manual stock adjustment form (with reason and journal auto-post)
- Cycle count entry
- Bin stock lookup by scanning a barcode

#### Storefront POS
- Same POS engine as TribesCoffeeClub
- Loaded with TribesSuppliers product catalogue
- Wholesale pricing for account customers
- Revenue posts to Suppliers revenue account

### 7.5 Accounting Journals — TribesSuppliers

```
GOODS RECEIVED (on GRN posting):
  DR  1200  Inventory — Goods             (cost of goods)
  DR  2110  GST Input Tax Receivable      (GST on purchase)
  CR  2000  Accounts Payable              (total invoice)

AP PAYMENT:
  DR  2000  Accounts Payable
  CR  1001  Bank — BSP Operating

SALE (storefront / wholesale):
  DR  1000  Cash / 1010 EFTPOS / 1100 AR
  CR  4300  Retail Sales Revenue
  CR  2100  GST Output Tax Payable

COGS ON DISPATCH:
  DR  5300  COGS — Retail
  CR  1200  Inventory — Goods

STOCK WRITE-OFF:
  DR  6500  Stock Write-off Expense
  CR  1200  Inventory — Goods
```

---

## 8. MODULE 3 — PARADISETAILORING

### 8.1 Purpose
End-to-end management of custom tailoring orders — from the initial quote and measurement taking, through production stages, to collection or delivery.

### 8.2 Roles in This Module
| Role | Dashboard | Can Do |
|---|---|---|
| `tailor_salesperson` | Salesperson View | Create orders, take measurements, collect deposit, update customer |
| `tailor_staff` | Tailor Work View | View assigned orders, update production stage |
| `tailoring_admin` | Admin Dashboard | Full module view, reports, pricing, staff, dispatch |

### 8.3 Features

#### Salesperson / Order Entry
- New order form:
  - Customer selection or quick-create
  - Garment type (Dress, Suit, Shirt, Skirt, Traditional, Uniform, Other)
  - Style notes and reference image upload
  - Measurement entry (full body measurement template — 15 fields)
  - Fabric selection from inventory (shows available stock in metres)
  - Labour charge + fabric charge + accessories + discount = total
  - Promised date picker
  - Deposit collection (posts deposit journal immediately)
- Order receipt / job ticket printing
- Customer notification (SMS or print-out with order number and due date)

#### Measurement Template Fields
```
Neck | Chest | Bust | Waist | Hips | Shoulder Width | Sleeve Length
Back Length | Dress Length | Inseam | Outseam | Thigh | Knee | Ankle | Rise
```

#### Tailor Work View
- My orders list (filtered to assigned tailor, sorted by promised date)
- Stage update buttons: Quote → Confirmed → Cutting → Sewing → Finishing → Ready
- Notes per stage (e.g. "Zipper issue — waiting for replacement")
- View full measurements and style notes
- Print production card (A4, all measurements, notes)

#### Tailoring Admin Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│  PARADISE TAILORING — ADMIN                                 │
├──────────────┬──────────────┬──────────────┬───────────────┤
│ Open Orders  │  Ready Today │  Overdue     │ Revenue MTD   │
│    24        │      3       │     2 ⚠️     │  K 18,400     │
├──────────────┴──────────────┴──────────────┴───────────────┤
│  KANBAN — ORDER PIPELINE                                    │
│  [Confirmed:5] [Cutting:4] [Sewing:7] [Finishing:3] [Ready:3]│
├─────────────────────────────────────────────────────────────┤
│  FABRIC STOCK LEVELS                                        │
│  Fabric A (Blue Floral)  22m available  ✅                  │
│  Fabric B (White Cotton)  3m available  ⚠️ Low              │
├─────────────────────────────────────────────────────────────┤
│  OVERDUE ORDERS                                             │
│  PT-2025-018  Mary S  Dress  Due: 3 Feb  [Contact Customer] │
│  PT-2025-021  John B  Suit   Due: 1 Feb  [Contact Customer] │
└─────────────────────────────────────────────────────────────┘
```

#### Order Tracking & Dispatch
- Order status visible to admin at all times via Kanban view
- When status = Ready: notify salesperson → customer contacted for collection
- If delivery requested: create a TribesSuppliers shipment (reuses dispatch module)
- Mark collected: collect balance payment, print final receipt

### 8.4 Business Logic

```python
# apps/tailoring/services.py

@transaction.atomic
def confirm_tailoring_order(order_id: int, deposit_amount: Decimal) -> TailoringOrder:
    order = TailoringOrder.objects.select_for_update().get(id=order_id)

    # 1. Reserve fabric in stock
    if order.fabric_product and order.fabric_qty:
        reserve_stock(order.fabric_product, order.fabric_qty, warehouse='fabric_store')

    # 2. Record deposit received
    Payment.objects.create(
        order_id=None,
        tailoring_order=order,
        payment_method='cash',
        amount=deposit_amount,
    )

    # 3. Post deposit journal
    post_journal('tailoring_deposit', {
        'order': order,
        'deposit': deposit_amount,
    })

    order.deposit_paid = deposit_amount
    order.balance_due = order.total - deposit_amount
    order.status = 'confirmed'
    order.save()
    return order


@transaction.atomic
def collect_tailoring_order(order_id: int, balance_payment: Decimal) -> dict:
    order = TailoringOrder.objects.select_for_update().get(id=order_id)

    # 1. Deduct fabric from stock (unreserve + remove)
    if order.fabric_product and order.fabric_qty:
        deduct_reserved_stock(order.fabric_product, order.fabric_qty, 'fabric_store')

    # 2. Recognise full revenue
    post_journal('tailoring_revenue', {
        'order': order,
        'balance_paid': balance_payment,
    })

    order.status = 'collected'
    order.collected_date = date.today()
    order.save()
    return build_tailoring_receipt(order)
```

### 8.5 Accounting Journals — ParadiseTailoring

```
DEPOSIT RECEIVED:
  DR  1000  Cash in Hand               (deposit amount)
  CR  2200  Customer Deposits          (liability — unearned)

ON COLLECTION / REVENUE RECOGNITION:
  DR  2200  Customer Deposits          (reverse deposit liability)
  DR  1000  Cash in Hand               (balance payment)
  CR  4200  Tailoring Revenue          (GST-exclusive total)
  CR  2100  GST Output Tax Payable     (GST on total)

FABRIC COGS:
  DR  5200  COGS — Fabric
  CR  1210  Inventory — Fabric

SHIPMENT (if delivery):
  DR  6700  Delivery Expense
  CR  1000  Cash / 2000 AP
```

---

## 9. MODULE 4 — ACCOUNTING DASHBOARD

### 9.1 Purpose
The accountant has a single, comprehensive dashboard that aggregates financial data across all three operating modules (TribesCoffeeClub, TribesSuppliers, ParadiseTailoring) into a unified view.

### 9.2 Role
| Role | Dashboard |
|---|---|
| `accountant` | Full accounting dashboard — all modules |

### 9.3 Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│  TRIBESPOS — ACCOUNTING               [Period: Jan 2025 ▼]  │
├────────────┬─────────────┬──────────────┬───────────────────┤
│ Revenue    │  Expenses   │  Net P&L     │  Bank Balance     │
│ K 142,300  │  K 98,100   │  K 44,200    │  K 34,800         │
│ All modules│  All modules│  This period │  All accounts     │
├────────────┴─────────────┴──────────────┴───────────────────┤
│  REVENUE BY MODULE                                          │
│  CoffeeClub  K 52,000  ████████████████                     │
│  Suppliers   K 68,400  ████████████████████████             │
│  Tailoring   K 21,900  ███████                              │
├─────────────────────────────────────────────────────────────┤
│  ACCOUNTS RECEIVABLE AGING            │  AP AGING           │
│  Current (0–30d):  K 8,200            │  K 12,400           │
│  31–60 days:       K 3,100            │  K 5,200            │
│  61–90 days:       K 1,800  ⚠️        │  K 2,100  ⚠️        │
│  90+ days:         K 400   🔴         │  K 800   🔴         │
├─────────────────────────────────────────────────────────────┤
│  IRC TAX COMPLIANCE STATUS                                  │
│  🟢 GST Dec 2024    — Filed 18 Jan                          │
│  🟡 GST Jan 2025    — Draft ready  [Review & File]          │
│  🟡 SWT Jan 2025    — K 3,100  Due 7 Feb  [Review & File]   │
│  🔴 Prov Tax Q1     — K 8,000  Due 31 Mar                   │
│  [View Full Tax Calendar]                                   │
├─────────────────────────────────────────────────────────────┤
│  RECENT JOURNAL ENTRIES               [View All Journals]   │
│  JE-2025-0089  Sale CAFE    K 4,200   Today    ✅ Posted     │
│  JE-2025-0088  AP Invoice   K 1,800   Today    ✅ Posted     │
│  JE-2025-0087  Payroll      K 12,400  Yesterday ✅ Posted    │
├─────────────────────────────────────────────────────────────┤
│  UNRECONCILED BANK ITEMS: 12   [Open Bank Reconciliation]   │
└─────────────────────────────────────────────────────────────┘
```

### 9.4 Accounting Features

#### Chart of Accounts
Full double-entry chart of accounts with module tagging:

| Code | Name | Type | Module |
|---|---|---|---|
| 1000 | Cash in Hand | Asset | Shared |
| 1001 | Bank — BSP Operating | Asset | Shared |
| 1010 | EFTPOS Clearing | Asset | Shared |
| 1100 | Accounts Receivable | Asset | Shared |
| 1200 | Inventory — Café Ingredients | Asset | CoffeeClub |
| 1210 | Inventory — Fabric | Asset | Tailoring |
| 1220 | Inventory — Goods (Suppliers) | Asset | Suppliers |
| 1230 | Inventory — Packaging Materials | Asset | Suppliers |
| 1500 | Fixed Assets | Asset | Shared |
| 2000 | Accounts Payable | Liability | Shared |
| 2100 | GST Output Tax Payable | Liability | Shared |
| 2110 | GST Input Tax Receivable | Asset | Shared |
| 2200 | Customer Deposits | Liability | Tailoring |
| 2210 | SWT Payable | Liability | Shared |
| 2220 | CIT Payable | Liability | Shared |
| 2230 | Provisional Tax Payable | Liability | Shared |
| 3000 | Owner's Equity | Equity | Shared |
| 3100 | Retained Earnings | Equity | Shared |
| 4000 | Revenue — Café | Revenue | CoffeeClub |
| 4100 | Revenue — Restaurant | Revenue | CoffeeClub |
| 4200 | Revenue — Tailoring | Revenue | Tailoring |
| 4300 | Revenue — Retail Sales | Revenue | Suppliers |
| 4400 | Revenue — Wholesale | Revenue | Suppliers |
| 5000 | COGS — Café | COGS | CoffeeClub |
| 5100 | COGS — Restaurant Food | COGS | CoffeeClub |
| 5200 | COGS — Fabric | COGS | Tailoring |
| 5300 | COGS — Retail Goods | COGS | Suppliers |
| 6000 | Wages — CoffeeClub | Expense | CoffeeClub |
| 6010 | Wages — Suppliers | Expense | Suppliers |
| 6020 | Wages — Tailoring | Expense | Tailoring |
| 6100 | Rent & Occupancy | Expense | Shared |
| 6200 | Utilities | Expense | Shared |
| 6300 | Depreciation | Expense | Shared |
| 6400 | Cash Variance | Expense | Shared |
| 6500 | Stock Write-off | Expense | Shared |
| 6600 | Superannuation | Expense | Shared |
| 6700 | Delivery & Freight | Expense | Suppliers |

#### Financial Reports (all exportable PDF + Excel)
- Profit & Loss — by period, by module, combined
- Balance Sheet
- Cash Flow Statement
- Trial Balance
- General Ledger (drill-down to individual journal lines)
- AR Aging Report
- AP Aging Report
- GST Return Summary
- Customer Statement
- Supplier Statement

#### Other Accounting Features
- Manual journal entry (with authorisation)
- Bank account management
- Bank reconciliation (import statement CSV, match to journal lines)
- Fiscal year and period management
- Journal entry audit trail (immutable — reversing entries only)

---

## 10. MODULE 5 — SUPERADMIN DASHBOARD (MD)

### 10.1 Purpose
The Managing Director has a single, intelligent overview of the entire TribesPOS system — all three business modules, accounting health, IRC tax status, staff activity, and system metrics.

### 10.2 Role
| Role | Dashboard |
|---|---|
| `superadmin` | Cross-module overview — no data hidden |

### 10.3 Dashboard Layout

```
╔══════════════════════════════════════════════════════════════════════╗
║  TRIBESPOS — MANAGING DIRECTOR OVERVIEW        [Today · Live]       ║
╠══════════════╦═══════════════╦═══════════════╦══════════════════════╣
║ TOTAL REVENUE║ TOTAL EXPENSES║ NET PROFIT    ║ CASH POSITION        ║
║ K 142,300    ║ K 98,100      ║ K 44,200      ║ K 34,800             ║
║ +12% vs MTH  ║ -3% vs MTH   ║ +18% vs MTH  ║ All accounts         ║
╠══════════════╩═══════════════╩═══════════════╩══════════════════════╣
║  REVENUE TREND (last 6 months)  │  BY MODULE (this month)          ║
║  [Line chart — all 3 modules]   │  CoffeeClub  K52,000  ████        ║
║                                 │  Suppliers   K68,400  ████████    ║
║                                 │  Tailoring   K21,900  ███         ║
╠═════════════════════════════════╪══════════════════════════════════╣
║  MODULE STATUS SUMMARY                                              ║
║  ┌─────────────────────┐ ┌────────────────────┐ ┌────────────────┐ ║
║  │ TRIBESCOFFEECLUB    │ │ TRIBESSUPPLIERS    │ │ PARADISE       │ ║
║  │ Sales today: K9,800 │ │ Open POs:      12  │ │ Open orders:24 │ ║
║  │ Tables open: 4      │ │ In warehouse: 284  │ │ Overdue:    2  │ ║
║  │ Cash sess:  2 open  │ │ Dispatching:   6   │ │ Ready:      3  │ ║
║  │ [Open Module →]     │ │ [Open Module →]    │ │ [Open Module→] │ ║
║  └─────────────────────┘ └────────────────────┘ └────────────────┘ ║
╠═════════════════════════════════════════════════════════════════════╣
║  IRC TAX COMPLIANCE                                                 ║
║  🟢 GST Jan 2025    Filed 18 Feb                                    ║
║  🟡 SWT Feb 2025    K3,100 due in 4 days    [View]                  ║
║  🔴 Prov Tax Q1     K8,000  OVERDUE 2 days  [View Urgently]         ║
╠══════════════════════╦══════════════════════════════════════════════╣
║  STAFF ACTIVITY      ║  TOP PRODUCTS — THIS MONTH                  ║
║  Active now: 18      ║  1. Flat White × 842  K4,631                ║
║  Cashiers: 4         ║  2. Grilled Chicken   K3,200                ║
║  Floor:    6         ║  3. Blue Floral 1m    K2,100                ║
║  Warehouse:5         ╠══════════════════════════════════════════════╣
║  Tailoring:3         ║  SYSTEM HEALTH                               ║
║  [View All Staff]    ║  ✅ All services running                     ║
║                      ║  ✅ Last backup: 2 hrs ago                   ║
║                      ║  ⚠️  Disk usage: 71%                         ║
╚══════════════════════╩══════════════════════════════════════════════╝
```

### 10.4 SuperAdmin Capabilities
- View any record in any module without restriction
- Create, edit, deactivate any user account or role
- System-wide configuration (tax rates, GST registration, bank accounts)
- Override any transaction (void, refund, adjustment) with audit log
- Export any report across any module
- View full audit trail of all system actions
- Manage fiscal years and close accounting periods
- Database backup trigger

---

## 11. IRC PNG TAX COMPLIANCE ENGINE

### 11.1 PNG Tax Obligations

| Tax | Rate | Period | Due Date |
|---|---|---|---|
| Goods & Services Tax (GST) | 10% | Monthly | 21st of following month |
| Salary & Wages Tax (SWT) | Marginal fortnightly rates | Monthly | 7th of following month |
| Corporate Income Tax (CIT) | 30% resident companies | Annual | 30 April following year |
| CIT Provisional Tax | 25% of prior year × 4 | Quarterly | 31 Mar / 30 Jun / 30 Sep / 31 Dec |
| Withholding Tax — Dividends | 17% resident / 15% non-resident | On payment | 7th of following month |
| Withholding Tax — Interest | 15% | On payment | 7th of following month |

### 11.2 GST Auto-Calculation

```python
# apps/irc_tax/services/gst_service.py

def generate_gst_return(year: int, month: int) -> GSTReturn:
    """
    Runs on 1st of every month via Celery.
    Aggregates all completed sales (output tax) and posted supplier
    invoices (input tax credits) for the prior month.
    """
    import calendar
    from datetime import date

    period_start = date(year, month, 1)
    period_end   = date(year, month, calendar.monthrange(year, month)[1])
    due_month    = month % 12 + 1
    due_year     = year + (1 if month == 12 else 0)
    due_date     = date(due_year, due_month, 21)

    with transaction.atomic():
        gst, _ = GSTReturn.objects.get_or_create(
            return_period=f"{year:04d}-{month:02d}",
            defaults={'period_start': period_start,
                      'period_end': period_end,
                      'due_date': due_date}
        )
        if gst.status == 'draft':
            _aggregate_output_tax(gst, period_start, period_end)
            _aggregate_input_tax(gst, period_start, period_end)
            _compute_net_position(gst)
    return gst
```

### 11.3 SWT Fortnightly Calculation

```python
# apps/irc_tax/swt_tables.py

# PNG Resident Individual — Annual Marginal Brackets (2024)
# Tax-free threshold: K20,000 per annum
SWT_RESIDENT_BRACKETS = [
    (0,       20_000,    0,        0.00),
    (20_001,  33_000,    0,        0.22),
    (33_001,  70_000,    2_860,    0.30),
    (70_001,  250_000,   13_960,   0.35),
    (250_001, float('inf'), 76_960, 0.42),
]

SWT_NON_RESIDENT_BRACKETS = [
    (0,       33_000,    0,        0.22),
    (33_001,  70_000,    7_260,    0.30),
    (70_001,  250_000,   18_360,   0.35),
    (250_001, float('inf'), 81_360, 0.42),
]

def calculate_swt_fortnightly(gross_fortnight: float,
                               is_resident: bool = True) -> float:
    """
    Annualise gross (×26), apply marginal brackets, divide by 26.
    """
    annual = gross_fortnight * 26
    brackets = SWT_RESIDENT_BRACKETS if is_resident else SWT_NON_RESIDENT_BRACKETS
    annual_tax = 0.0
    for (low, high, base, rate) in brackets:
        if annual <= low:
            break
        taxable = min(annual, high) - low
        annual_tax = base + (taxable * rate)
    return round(annual_tax / 26, 2)
```

### 11.4 Tax Calendar & Alerts

```python
# apps/irc_tax/tasks.py

@shared_task
def auto_generate_monthly_returns():
    """Runs on the 1st of every month at 00:05."""
    today = date.today()
    year  = today.year - (1 if today.month == 1 else 0)
    month = 12 if today.month == 1 else today.month - 1
    generate_gst_return(year, month)
    generate_swt_remittance(year, month)

@shared_task
def daily_tax_deadline_alert():
    """Runs every morning at 08:00. Sends email for due-soon or overdue items."""
    deadlines = get_upcoming_tax_deadlines(months_ahead=1)
    for dl in deadlines:
        days_until = (dl['due_date'] - date.today()).days
        if days_until <= 7:
            send_tax_alert_email(dl, days_until)

CELERY_BEAT_SCHEDULE = {
    'monthly-tax-returns': {
        'task': 'apps.irc_tax.tasks.auto_generate_monthly_returns',
        'schedule': crontab(hour=0, minute=5, day_of_month=1),
    },
    'daily-tax-alerts': {
        'task': 'apps.irc_tax.tasks.daily_tax_deadline_alert',
        'schedule': crontab(hour=8, minute=0),
    },
}
```

### 11.5 IRC Return PDFs
WeasyPrint generates filing-ready PDFs styled as official IRC forms:
- **GST Return** — Part A (output tax), Part B (input credits), Part C (net payable), authorisation block
- **SWT Monthly Remittance** — employee list, gross wages, SWT withheld, total
- **CIT Annual Return** — income statement, deductions, taxable income, tax calculation, provisional credits
- All PDFs include company name, TIN, GST registration number, and period

---

## 12. SHARED ACCOUNTING ENGINE

### 12.1 Automated Journal Posting Rules

```python
# apps/accounting/journal_rules.py

POSTING_RULES = {
    # ── TribesCoffeeClub ─────────────────────────────────────────
    'cash_sale': [
        ('DR', '1000', 'total'),
        ('CR', 'revenue_account', 'subtotal'),
        ('CR', '2100', 'tax_amount'),
    ],
    'eftpos_sale': [
        ('DR', '1010', 'total'),
        ('CR', 'revenue_account', 'subtotal'),
        ('CR', '2100', 'tax_amount'),
    ],
    'account_sale': [
        ('DR', '1100', 'total'),
        ('CR', 'revenue_account', 'subtotal'),
        ('CR', '2100', 'tax_amount'),
    ],
    'cogs_deduction': [
        ('DR', 'cogs_account', 'cost'),
        ('CR', 'inventory_account', 'cost'),
    ],

    # ── TribesSuppliers ──────────────────────────────────────────
    'purchase_invoice': [
        ('DR', '1220', 'subtotal'),
        ('DR', '2110', 'tax_amount'),
        ('CR', '2000', 'total'),
    ],
    'ap_payment': [
        ('DR', '2000', 'amount'),
        ('CR', '1001', 'amount'),
    ],

    # ── ParadiseTailoring ────────────────────────────────────────
    'tailoring_deposit': [
        ('DR', '1000', 'deposit'),
        ('CR', '2200', 'deposit'),
    ],
    'tailoring_revenue': [
        ('DR', '2200', 'deposit'),
        ('DR', '1000', 'balance'),
        ('CR', '4200', 'subtotal'),
        ('CR', '2100', 'tax_amount'),
        ('DR', '5200', 'fabric_cost'),
        ('CR', '1210', 'fabric_cost'),
    ],

    # ── Payroll (all modules) ────────────────────────────────────
    'payroll_payment': [
        ('DR', 'wages_account', 'gross'),
        ('CR', '2210', 'swt'),
        ('CR', '1001', 'net_pay'),
    ],
    'swt_remittance': [
        ('DR', '2210', 'swt_amount'),
        ('CR', '1001', 'swt_amount'),
    ],
}
```

### 12.2 `post_journal()` Function

```python
# apps/accounting/services.py

@transaction.atomic
def post_journal(rule: str, context: dict) -> JournalEntry:
    """
    Core accounting function. Called by every module after any financial event.
    Creates an immutable JournalEntry + JournalLines and validates balance.
    """
    lines_spec = POSTING_RULES[rule]
    entry = JournalEntry.objects.create(
        entry_number=generate_entry_number(),
        entry_type=context.get('entry_type', 'sale'),
        module=context.get('module', 'shared'),
        reference_type=context.get('reference_type'),
        reference_id=context.get('reference_id'),
        fiscal_period=get_current_period(),
        entry_date=date.today(),
        description=context.get('description', rule),
    )

    total_debit = total_credit = Decimal('0.00')
    for (side, account_code, amount_key) in lines_spec:
        account = resolve_account(account_code, context)
        amount  = resolve_amount(amount_key, context)
        if amount == 0:
            continue
        JournalLine.objects.create(
            journal_entry=entry,
            account=account,
            debit=amount  if side == 'DR' else 0,
            credit=amount if side == 'CR' else 0,
            module=context.get('module'),
        )
        if side == 'DR': total_debit  += amount
        else:            total_credit += amount

    assert total_debit == total_credit, \
        f"Journal {entry.entry_number} does not balance: DR={total_debit} CR={total_credit}"

    entry.total_debit  = total_debit
    entry.total_credit = total_credit
    entry.is_posted    = True
    entry.save()
    return entry
```

---

## 13. USER ROLES & ACCESS CONTROL

### 13.1 Role Definitions

```python
# apps/accounts/permissions.py

MODULE_PERMISSIONS = {

    'superadmin': {
        'modules':   ['coffeeclub', 'suppliers', 'tailoring', 'accounting', 'admin'],
        'can_void':  True,
        'can_refund': True,
        'can_approve_po': True,
        'can_view_all_reports': True,
        'can_manage_users': True,
        'can_close_period': True,
    },

    # ── Module 1 ─────────────────────────────
    'cashier': {
        'modules': ['coffeeclub'],
        'actions': ['pos_sale', 'open_session', 'close_session', 'print_receipt'],
    },
    'barista': {
        'modules': ['coffeeclub'],
        'actions': ['view_order_queue', 'mark_drink_ready'],
    },
    'waiter': {
        'modules': ['coffeeclub'],
        'actions': ['open_table', 'take_order', 'send_to_kitchen',
                    'print_bill', 'split_bill'],
    },
    'coffee_manager': {
        'modules': ['coffeeclub'],
        'actions': ['all_coffeeclub', 'void_sale', 'refund', 'z_report',
                    'view_reports', 'manage_coffeeclub_staff'],
    },

    # ── Module 2 ─────────────────────────────
    'inventory_staff': {
        'modules': ['suppliers'],
        'actions': ['view_stock', 'stock_adjustment', 'cycle_count'],
    },
    'receiver': {
        'modules': ['suppliers'],
        'actions': ['create_grn', 'qc_inspection', 'putaway'],
    },
    'packer': {
        'modules': ['suppliers'],
        'actions': ['view_pack_queue', 'confirm_pick', 'mark_packed'],
    },
    'dispatcher': {
        'modules': ['suppliers'],
        'actions': ['create_shipment', 'update_delivery_status',
                    'log_proof_of_delivery'],
    },
    'inventory_manager': {
        'modules': ['suppliers'],
        'actions': ['all_suppliers', 'approve_po', 'view_reports',
                    'manage_suppliers_staff'],
    },

    # ── Module 3 ─────────────────────────────
    'tailor_salesperson': {
        'modules': ['tailoring'],
        'actions': ['create_order', 'take_measurements', 'collect_deposit',
                    'collect_balance', 'view_own_orders'],
    },
    'tailor_staff': {
        'modules': ['tailoring'],
        'actions': ['view_assigned_orders', 'update_stage', 'print_production_card'],
    },
    'tailoring_admin': {
        'modules': ['tailoring'],
        'actions': ['all_tailoring', 'view_reports', 'manage_tailoring_staff'],
    },

    # ── Module 4 ─────────────────────────────
    'accountant': {
        'modules': ['accounting'],
        'actions': ['view_all_journals', 'manual_journal', 'bank_reconciliation',
                    'view_all_reports', 'irc_tax_returns', 'ar_ap_management'],
    },
}
```

### 13.2 Permission Decorator / Mixin

```python
# apps/core/mixins.py

class RoleRequiredMixin(LoginRequiredMixin):
    required_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        role = request.user.staff_profile.role
        if role not in self.required_roles and role != 'superadmin':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


# Usage example:
class ApprovePOView(RoleRequiredMixin, UpdateView):
    required_roles = ['inventory_manager']
    model = PurchaseOrder
```

---

## 14. API ENDPOINTS

All endpoints prefixed `/api/v1/`. JWT bearer token required.

### Authentication
```
POST  /api/v1/auth/token/             # Username + password → access + refresh tokens
POST  /api/v1/auth/token/refresh/     # Refresh access token
POST  /api/v1/auth/pin-login/         # PIN + terminal_id → short-lived POS token
GET   /api/v1/auth/me/                # Current user profile + role + dashboard URL
```

### Products & Stock
```
GET   /api/v1/products/               # ?module=coffeeclub&category=&search=&barcode=
POST  /api/v1/products/               # Create product
GET   /api/v1/products/{id}/
PUT   /api/v1/products/{id}/
GET   /api/v1/products/barcode/{code}/ # Barcode lookup
GET   /api/v1/stock/                  # Stock on hand (all warehouses)
GET   /api/v1/stock/low/              # Products below min stock
POST  /api/v1/stock/adjust/           # Manual adjustment
POST  /api/v1/stock/transfer/         # Inter-warehouse transfer
```

### TribesCoffeeClub POS
```
POST  /api/v1/coffeeclub/orders/               # Open new order
GET   /api/v1/coffeeclub/orders/{id}/
PATCH /api/v1/coffeeclub/orders/{id}/          # Add/edit lines
POST  /api/v1/coffeeclub/orders/{id}/pay/      # Process payment → complete
POST  /api/v1/coffeeclub/orders/{id}/void/
POST  /api/v1/coffeeclub/orders/{id}/hold/
POST  /api/v1/coffeeclub/orders/{id}/recall/
POST  /api/v1/coffeeclub/orders/sync/          # Offline batch sync
GET   /api/v1/coffeeclub/tables/               # Table floor plan + status
POST  /api/v1/coffeeclub/tables/{id}/open/
POST  /api/v1/coffeeclub/tables/{id}/close/
GET   /api/v1/coffeeclub/kitchen/tickets/      # Active kitchen tickets
PATCH /api/v1/coffeeclub/kitchen/tickets/{id}/ # Acknowledge / ready / delivered
GET   /api/v1/coffeeclub/sessions/current/
POST  /api/v1/coffeeclub/sessions/open/
POST  /api/v1/coffeeclub/sessions/close/       # Triggers Z-report
```

### TribesSuppliers
```
GET   /api/v1/suppliers/pos/orders/            # Storefront POS (same flow as coffeeclub)
POST  /api/v1/purchase-orders/
GET   /api/v1/purchase-orders/
GET   /api/v1/purchase-orders/{id}/
POST  /api/v1/purchase-orders/{id}/approve/
POST  /api/v1/purchase-orders/{id}/send/
POST  /api/v1/purchase-orders/{id}/receive/    # Creates GRN
GET   /api/v1/grn/
GET   /api/v1/grn/{id}/
POST  /api/v1/grn/{id}/qc/                    # QC inspection per line
POST  /api/v1/grn/{id}/putaway/               # Confirm putaway locations
GET   /api/v1/packaging-orders/
POST  /api/v1/packaging-orders/
POST  /api/v1/packaging-orders/{id}/pick/      # Confirm pick lines
POST  /api/v1/packaging-orders/{id}/pack/      # Mark as packed
GET   /api/v1/shipments/
POST  /api/v1/shipments/
PATCH /api/v1/shipments/{id}/status/
POST  /api/v1/shipments/{id}/deliver/          # POD upload
POST  /api/v1/shipments/{id}/fail/             # Log failed attempt
GET   /api/v1/cycle-counts/
POST  /api/v1/cycle-counts/
POST  /api/v1/cycle-counts/{id}/submit/
```

### ParadiseTailoring
```
GET   /api/v1/tailoring/orders/
POST  /api/v1/tailoring/orders/
GET   /api/v1/tailoring/orders/{id}/
POST  /api/v1/tailoring/orders/{id}/confirm/   # Deposit + reserve fabric
PATCH /api/v1/tailoring/orders/{id}/stage/     # Update production stage
POST  /api/v1/tailoring/orders/{id}/collect/   # Final payment + complete
POST  /api/v1/tailoring/orders/{id}/dispatch/  # Create shipment for delivery
```

### Accounting
```
GET   /api/v1/accounts/                        # Chart of accounts
GET   /api/v1/journal-entries/
POST  /api/v1/journal-entries/                 # Manual journal
GET   /api/v1/reports/pl/                      # P&L ?module=&start=&end=
GET   /api/v1/reports/balance-sheet/
GET   /api/v1/reports/trial-balance/
GET   /api/v1/reports/ar-aging/
GET   /api/v1/reports/ap-aging/
```

### IRC Tax
```
GET   /api/v1/tax/calendar/                    # All upcoming deadlines
POST  /api/v1/tax/gst/generate/               # Trigger GST return for period
GET   /api/v1/tax/gst/{period}/               # GST return detail
GET   /api/v1/tax/gst/{period}/pdf/           # Download IRC-format PDF
PATCH /api/v1/tax/gst/{period}/finalise/
GET   /api/v1/tax/swt/
POST  /api/v1/tax/swt/generate/
GET   /api/v1/tax/swt/{period}/pdf/
GET   /api/v1/payroll/swt-calculator/         # ?gross=&is_resident=true
POST  /api/v1/payroll/runs/
POST  /api/v1/payroll/runs/{id}/approve/
GET   /api/v1/tax/cit/{year}/
POST  /api/v1/tax/cit/{year}/generate/
```

---

## 15. DJANGO PROJECT STRUCTURE

```
tribespos/                              ← Django project root
│
├── config/
│   ├── settings/
│   │   ├── base.py                    ← Shared settings
│   │   ├── development.py             ← DEBUG=True, local MySQL
│   │   └── production.py             ← DEBUG=False, Redis, HTTPS
│   ├── urls.py                        ← Root URL configuration
│   ├── asgi.py                        ← ASGI (Channels + WebSocket)
│   └── wsgi.py
│
├── apps/
│   │
│   ├── core/                          ← Shared base classes & utilities
│   │   ├── models.py                  ← TimeStampedModel, SoftDeleteModel
│   │   ├── mixins.py                  ← RoleRequiredMixin, LoginRequiredMixin
│   │   ├── utils.py                   ← Sequence number generator, money helpers
│   │   └── templatetags/             ← Custom filters (currency, date)
│   │
│   ├── accounts/                      ← Auth, StaffProfile, role routing
│   │   ├── models.py                  ← StaffProfile, Employee
│   │   ├── views.py                   ← login_view (routes by role), logout
│   │   ├── forms.py
│   │   └── permissions.py
│   │
│   ├── products/                      ← Products, Categories, UOM, BOM, Variants
│   ├── warehouse/                     ← Warehouse, WarehouseLocation, StockLocation,
│   │                                  ← StockMovement, services.py
│   ├── customers/                     ← Customer CRUD, loyalty, statements
│   ├── suppliers/                     ← Supplier CRUD, ledger
│   │
│   ├── coffeeclub/                    ← MODULE 1: TribesCoffeeClub
│   │   ├── models.py                  ← RestaurantTable, KitchenTicket, Reservation
│   │   ├── services.py                ← complete_sale(), deduct_bom_stock()
│   │   ├── consumers.py               ← Django Channels WebSocket (KDS)
│   │   ├── routing.py
│   │   ├── views/
│   │   │   ├── pos.py                 ← POS terminal
│   │   │   ├── tables.py              ← Floor plan, table management
│   │   │   ├── kitchen.py             ← KDS view
│   │   │   └── manager.py             ← Manager dashboard
│   │   └── templates/coffeeclub/
│   │       ├── pos_terminal.html
│   │       ├── floor_plan.html
│   │       ├── kitchen_display.html
│   │       ├── manager_dashboard.html
│   │       ├── waiter_dashboard.html
│   │       ├── receipt.html
│   │       └── z_report.html
│   │
│   ├── tribes_suppliers/              ← MODULE 2: TribesSuppliers
│   │   ├── models.py                  ← GRN, QCInspection, PackagingOrder,
│   │   │                              ← Shipment, DeliveryAttempt, CycleCount
│   │   ├── services/
│   │   │   ├── procurement.py         ← create_po(), approve_po()
│   │   │   ├── receiving.py           ← complete_grn(), post_qc()
│   │   │   ├── packaging.py           ← create_pack_order(), confirm_pick()
│   │   │   └── dispatch.py            ← create_shipment(), mark_delivered()
│   │   ├── views/
│   │   │   ├── purchasing.py          ← PO CRUD, approval
│   │   │   ├── receiving.py           ← GRN, QC, putaway
│   │   │   ├── packing.py             ← Pack queue, pick list
│   │   │   ├── dispatch.py            ← Shipments, POD
│   │   │   ├── inventory_staff.py     ← Stock view, adjustments
│   │   │   └── manager.py             ← Inventory manager dashboard
│   │   └── templates/tribes_suppliers/
│   │       ├── manager_dashboard.html
│   │       ├── inventory_staff_view.html
│   │       ├── purchasing_dashboard.html
│   │       ├── po_create.html
│   │       ├── po_detail.html
│   │       ├── grn_create.html
│   │       ├── qc_inspection.html
│   │       ├── putaway.html
│   │       ├── packing_dashboard.html
│   │       ├── pick_list.html
│   │       ├── dispatch_dashboard.html
│   │       ├── shipment_detail.html
│   │       └── cycle_count.html
│   │
│   ├── tailoring/                     ← MODULE 3: ParadiseTailoring
│   │   ├── models.py                  ← TailoringOrder, StageLog, TailoringShipment
│   │   ├── services.py                ← confirm_order(), collect_order()
│   │   ├── views/
│   │   │   ├── salesperson.py         ← Order entry, deposit
│   │   │   ├── tailor.py              ← Assigned order queue, stage update
│   │   │   └── admin.py               ← Admin dashboard, Kanban
│   │   └── templates/tailoring/
│   │       ├── admin_dashboard.html
│   │       ├── salesperson_view.html
│   │       ├── tailor_work_view.html
│   │       ├── order_create.html
│   │       ├── order_detail.html
│   │       ├── kanban.html
│   │       ├── job_ticket.html        ← Printable production card
│   │       └── receipt.html
│   │
│   ├── accounting/                    ← MODULE 4: Accounting Engine
│   │   ├── models.py                  ← Account, FiscalYear, JournalEntry, JournalLine,
│   │   │                              ← BankAccount, ARInvoice, SupplierInvoice
│   │   ├── services.py                ← post_journal(), generate_entry_number()
│   │   ├── journal_rules.py           ← POSTING_RULES dict
│   │   ├── reports.py                 ← P&L, Balance Sheet, Trial Balance, Aging
│   │   ├── views.py                   ← Accountant dashboard, all accounting views
│   │   └── templates/accounting/
│   │       ├── accountant_dashboard.html
│   │       ├── chart_of_accounts.html
│   │       ├── journal_list.html
│   │       ├── journal_detail.html
│   │       ├── bank_reconciliation.html
│   │       ├── ar_aging.html
│   │       ├── ap_aging.html
│   │       └── reports/
│   │           ├── pl.html
│   │           ├── balance_sheet.html
│   │           └── trial_balance.html
│   │
│   ├── irc_tax/                       ← IRC PNG Tax Compliance
│   │   ├── models.py                  ← GSTReturn, SWTRemittance, PayrollRun,
│   │   │                              ← PayrollLine, CITReturn, ProvisionalTax
│   │   ├── constants.py               ← GST supply types
│   │   ├── swt_tables.py              ← SWT bracket tables + calculator
│   │   ├── tasks.py                   ← Celery: auto-generate + deadline alerts
│   │   ├── services/
│   │   │   ├── gst_service.py
│   │   │   ├── swt_service.py
│   │   │   └── cit_service.py
│   │   ├── pdf/
│   │   │   ├── gst_return_pdf.py      ← WeasyPrint IRC-format GST return
│   │   │   ├── swt_remittance_pdf.py
│   │   │   └── cit_return_pdf.py
│   │   └── templates/irc_tax/
│   │       ├── tax_dashboard.html
│   │       ├── tax_calendar.html
│   │       ├── gst_return_detail.html
│   │       ├── swt_remittance_detail.html
│   │       ├── payroll_run.html
│   │       ├── cit_return.html
│   │       └── print/
│   │           ├── gst_irc_form.html
│   │           └── swt_irc_form.html
│   │
│   ├── superadmin/                    ← MODULE 5: SuperAdmin (MD)
│   │   ├── views.py                   ← MD dashboard, system config
│   │   └── templates/superadmin/
│   │       ├── md_dashboard.html
│   │       └── system_config.html
│   │
│   └── api/                           ← DRF API router
│       ├── urls.py
│       └── router.py
│
├── templates/
│   ├── base.html                      ← MDB5 base with sidebar navigation
│   ├── base_pos.html                  ← Full-screen POS base (no sidebar)
│   ├── base_kds.html                  ← Dark-theme kitchen display base
│   └── components/
│       ├── navbar.html
│       ├── sidebar.html               ← Role-aware sidebar menu
│       └── alerts.html
│
├── static/
│   ├── css/
│   │   ├── tribespos.css              ← Custom styles, brand colours
│   │   └── pos.css                    ← POS terminal styles
│   ├── js/
│   │   ├── pos/
│   │   │   ├── terminal.js            ← POS main logic
│   │   │   ├── sw.js                  ← Service Worker (offline)
│   │   │   └── sync.js                ← Offline order sync
│   │   └── kitchen/
│   │       └── kds.js                 ← WebSocket KDS client
│   └── img/
│       └── tribespos_logo.png
│
├── media/                             ← User uploads (product images, POD photos)
├── requirements.txt
├── manage.py
├── .env.example
└── docker-compose.yml
```

---

## 16. SETTINGS & CONFIGURATION

### `requirements.txt`
```
Django==4.2.16
mysqlclient==2.2.4
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.1
channels==4.1.0
channels-redis==4.2.0
celery==5.4.0
redis==5.0.8
django-environ==0.11.2
WeasyPrint==62.3
openpyxl==3.1.5
python-barcode==0.15.1
Pillow==10.4.0
django-filter==24.3
django-crispy-forms==2.3
crispy-bootstrap5==2024.2
django-import-export==4.1.1
django-simple-history==3.7.0
gunicorn==23.0.0
whitenoise==6.7.0
```

### `config/settings/base.py`
```python
from pathlib import Path
import environ

env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent.parent
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'channels',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'import_export',
    'simple_history',
    'crispy_forms',
    'crispy_bootstrap5',
    # TribesPOS apps
    'apps.core',
    'apps.accounts',
    'apps.products',
    'apps.warehouse',
    'apps.customers',
    'apps.suppliers',
    'apps.coffeeclub',
    'apps.tribes_suppliers',
    'apps.tailoring',
    'apps.accounting',
    'apps.irc_tax',
    'apps.superadmin',
    'apps.api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':     env('DB_NAME'),
        'USER':     env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST':     env('DB_HOST', default='localhost'),
        'PORT':     env('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [env('REDIS_URL', default='redis://localhost:6379')]},
    }
}

CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

LANGUAGE_CODE = 'en-au'
TIME_ZONE = 'Pacific/Port_Moresby'   # UTC+10 — PNG timezone
USE_I18N = True
USE_TZ = True

STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL   = '/media/'
MEDIA_ROOT  = BASE_DIR / 'media'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

LOGIN_URL          = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'     # Overridden by role-based routing

# ── TribesPOS Business Configuration ──────────────────────────────────
TRIBESPOS_CONFIG = {
    'SYSTEM_NAME':          'TribesPOS',
    'COMPANY_NAME':         'Harhurum',
    'COMPANY_WEBSITE':      'harhurum.com.pg',
    'DEFAULT_CURRENCY':     'PGK',
    'CURRENCY_SYMBOL':      'K',
    'DEFAULT_GST_RATE':     10.0,
    'TAX_INCLUSIVE':        True,
    'FISCAL_YEAR_START':    1,          # January
    # IRC details
    'IRC_TIN':              env('IRC_TIN', default=''),
    'GST_REG_NUMBER':       env('GST_REG', default=''),
    'CIT_RATE':             30.0,
    'SWT_TAX_FREE_THRESHOLD': 20_000.0,
    # Notifications
    'MANAGER_EMAIL':        env('MANAGER_EMAIL', default=''),
    'TAX_ALERT_EMAIL':      env('TAX_ALERT_EMAIL', default=''),
    'LOW_STOCK_EMAIL':      env('LOW_STOCK_EMAIL', default=''),
    # Receipt
    'RECEIPT_FOOTER':       'Thank you! | harhurum.com.pg',
}
```

### `.env.example`
```
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=tribespos
DB_USER=tribespos_user
DB_PASSWORD=strongpassword
DB_HOST=localhost
DB_PORT=3306

REDIS_URL=redis://localhost:6379

IRC_TIN=
GST_REG=
MANAGER_EMAIL=manager@harhurum.com.pg
TAX_ALERT_EMAIL=accounts@harhurum.com.pg
LOW_STOCK_EMAIL=manager@harhurum.com.pg
```

### `docker-compose.yml`
```yaml
version: '3.9'

services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file: .env

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: tribespos
      MYSQL_USER: tribespos_user
      MYSQL_PASSWORD: strongpassword
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery:
    build: .
    command: celery -A config worker -l info
    depends_on:
      - db
      - redis
    env_file: .env

  celery-beat:
    build: .
    command: celery -A config beat -l info
    depends_on:
      - db
      - redis
    env_file: .env

volumes:
  mysql_data:
```

---

## 17. UI/UX GUIDELINES

### Design System
**Framework:** MDB5 (Material Design for Bootstrap 5)  
**Icons:** Material Icons  

### Brand Colours
```css
:root {
    --tribes-primary:    #1A237E;   /* Deep Indigo — TribesPOS brand */
    --tribes-accent:     #FF6F00;   /* Amber — Papua New Guinea energy */
    --tribes-success:    #2E7D32;   /* Green */
    --tribes-danger:     #B71C1C;   /* Red */
    --tribes-warning:    #F57F17;   /* Amber */
    --tribes-background: #F5F5F5;
    --tribes-surface:    #FFFFFF;
    --tribes-text:       #212121;
}
```

### Module Colour Coding
- **TribesCoffeeClub** → Deep Teal `#00695C`
- **TribesSuppliers** → Deep Blue `#1565C0`
- **ParadiseTailoring** → Deep Purple `#6A1B9A`
- **Accounting** → Dark Green `#2E7D32`
- **SuperAdmin** → Deep Indigo `#1A237E`

Each module's sidebar header and accent colours match its module colour. Users immediately know which module they are in.

### POS Terminal Layout
```
┌──────────────────────────────────────────────────────────────┐
│  TribesCoffeeClub  │  Cashier: Jane  │  Session: OPEN  10:32 │
├──────────────────────────────┬───────────────────────────────┤
│  [Coffee] [Food] [Drinks]    │  ORDER #TCK-2025-00142        │
│                              │  ─────────────────────────────│
│  ┌──────┐ ┌──────┐ ┌──────┐ │  Flat White    ×1    K 5.50   │
│  │Flat  │ │Latte │ │Cap-  │ │  Latte × 2 shots ×1  K 7.00   │
│  │White │ │      │ │ puc- │ │  Grilled Chkn  ×1    K 18.00  │
│  │K5.50 │ │K6.00 │ │cino  │ │                               │
│  └──────┘ └──────┘ └──────┘ │  ─────────────────────────────│
│  ┌──────┐ ┌──────┐ ┌──────┐ │  Subtotal           K 27.73   │
│  │Long  │ │Short │ │Iced  │ │  GST (incl.)         K 2.77   │
│  │Black │ │Black │ │Latte │ │  TOTAL              K 30.50   │
│  │K4.50 │ │K4.00 │ │K7.50 │ │                               │
│  └──────┘ └──────┘ └──────┘ │  [  CASH  ] [ EFTPOS ] [ACCT]│
│                              │                               │
│  [HOLD]  [DISCOUNT]  [NOTES]│           [ PAY ]             │
└──────────────────────────────┴───────────────────────────────┘
```

### Sidebar Navigation (role-aware)
The sidebar only shows sections the logged-in role can access. Each module has its own collapsible section with its module accent colour.

### Kitchen Display
- Black background, white text
- Large font for item names and modifiers
- Colour-coded ticket age: green (fresh), amber (5–10 min), red (>10 min)
- Tap/click anywhere on ticket to cycle: new → acknowledged → ready

---

## 18. DEPLOYMENT

### Production Stack
```
Internet → Nginx
              ├── /static/          → Whitenoise (static files)
              ├── /ws/              → Daphne (ASGI WebSocket — Kitchen Display)
              └── /                 → Gunicorn (WSGI — Django)

MySQL 8 (dedicated server or RDS)
Redis 7 (Celery broker + Channel Layers + cache)
Celery worker (background tasks)
Celery beat (scheduled tasks — tax returns, alerts)
```

### Initial Setup Commands
```bash
# 1. Create database
mysql -u root -p -e "CREATE DATABASE tribespos CHARACTER SET utf8mb4;"

# 2. Run migrations
python manage.py migrate

# 3. Seed initial data
python manage.py setup_tribespos   # Custom management command (see below)

# 4. Create superadmin
python manage.py createsuperuser

# 5. Collect static
python manage.py collectstatic --noinput
```

### `setup_tribespos` Management Command
This management command (in `apps/core/management/commands/setup_tribespos.py`) seeds:
- Default chart of accounts (all accounts from Section 9.4)
- Default tax rates (GST 10%, Zero-rated, Exempt)
- Default units of measure (kg, g, L, mL, pcs, m, roll, box)
- Default warehouses (CoffeeClub Main, Suppliers Main, Fabric Store)
- Default fiscal year (current calendar year)
- Default fiscal periods (12 months)

---

## 19. IMPLEMENTATION PHASES

### Phase 1 — Foundation (Weeks 1–2)
- [ ] Django project scaffold: `tribespos/`, all apps, Docker
- [ ] MySQL connection, all migrations
- [ ] `StaffProfile` + all 14 roles
- [ ] Login view with role-based redirect to correct dashboard
- [ ] MDB5 base templates with module-coloured sidebar
- [ ] `setup_tribespos` management command (COA, tax rates, warehouses)
- [ ] Product catalog (CRUD + categories + variants + BOM)
- [ ] Warehouse + stock locations + stock movements service

### Phase 2 — TribesCoffeeClub POS (Weeks 3–5)
- [ ] POS terminal (offline-capable with Service Worker + IndexedDB)
- [ ] Product modifier groups and options
- [ ] `complete_sale()` service with BOM deduction
- [ ] Cash session open/close
- [ ] Z-report
- [ ] Receipt printing (thermal-optimised HTML template)
- [ ] Restaurant table floor plan
- [ ] Waiter order management + course system
- [ ] Kitchen Display System (Django Channels WebSocket)
- [ ] Bill split (by seat, by item, even)
- [ ] Coffee Manager dashboard

### Phase 3 — TribesSuppliers (Weeks 6–9)
- [ ] Supplier CRUD + AP ledger
- [ ] Purchase Order: create, approval workflow, email PDF
- [ ] GRN creation against PO
- [ ] QC Inspection form with photo upload
- [ ] Bin/location putaway assignment
- [ ] Packaging / Pick & Pack queue
- [ ] Barcode scan confirmation for picks
- [ ] Shipment creation + status tracking
- [ ] Proof of delivery (photo + signature)
- [ ] Failed delivery attempt logging
- [ ] Cycle count (plan, count, variance, approve)
- [ ] Inventory Manager dashboard
- [ ] Inventory Staff view
- [ ] Receiving / Packing / Dispatch role dashboards
- [ ] Storefront POS (reuse coffeeclub POS, suppliers product catalogue)

### Phase 4 — ParadiseTailoring (Weeks 10–11)
- [ ] Tailoring order form (customer, garment, measurements, fabric, pricing)
- [ ] Deposit collection + stock reservation
- [ ] Production stage Kanban board
- [ ] Tailor work view (assigned orders, stage update)
- [ ] Salesperson view (order entry, customer comms)
- [ ] Job ticket / production card printing
- [ ] Balance collection on pickup
- [ ] Optional shipment via TribesSuppliers dispatch
- [ ] Tailoring Admin dashboard

### Phase 5 — Accounting & IRC Tax (Weeks 12–14)
- [ ] Full double-entry accounting (all journal rules from Section 12)
- [ ] `post_journal()` function integrated into all module services
- [ ] Manual journal entry with authorisation
- [ ] AR invoicing + aging report
- [ ] AP aging + payment recording
- [ ] Bank reconciliation (import CSV, match lines)
- [ ] GST module: auto-aggregate from sales + purchases
- [ ] GST return IRC-format PDF (WeasyPrint)
- [ ] SWT module: payroll runs, fortnightly calculator
- [ ] SWT remittance IRC-format PDF
- [ ] CIT annual return + provisional instalment schedule
- [ ] Tax Calendar dashboard
- [ ] Celery tasks: auto-generate returns on 1st of month
- [ ] Daily tax deadline email alerts
- [ ] Accountant dashboard

### Phase 6 — SuperAdmin & Reporting (Week 15)
- [ ] SuperAdmin MD dashboard (cross-module KPIs, all charts)
- [ ] P&L by module + combined
- [ ] Balance Sheet, Trial Balance, Cash Flow
- [ ] All reports exportable to PDF and Excel
- [ ] Staff management across all modules
- [ ] System configuration panel
- [ ] Performance optimisation (N+1 query fix, caching)
- [ ] UAT with Harhurum staff (all modules)

---

## 20. CLAUDE CODE INSTRUCTIONS

### How to Use This Blueprint

Feed this entire file to Claude Code at the start of each session. Work phase by phase.

### Recommended Session Prompts

**Session 1 — Scaffold:**
```
Using TRIBESPOS_BLUEPRINT.md, scaffold the entire Django project 'tribespos'
with all apps from Section 15. Include: Docker setup, requirements.txt,
base settings, .env.example, and run the initial migrations.
Create the StaffProfile model (Section 5.1) with all 14 roles.
Implement the login view that routes each role to its dashboard URL
(Section 3 — Login Routing).
```

**Session 2 — Products & Stock:**
```
Using TRIBESPOS_BLUEPRINT.md Section 5.4 and 5.5, implement:
- Product, ProductVariant, BOMItem models with admin
- Warehouse, WarehouseLocation, StockLocation, StockMovement models
- warehouse/services.py with update_stock(), record_movement(),
  reserve_stock(), deduct_reserved_stock()
- setup_tribespos management command that seeds COA, tax rates,
  warehouses, UOMs, and fiscal year
```

**Session 3 — CoffeeClub POS:**
```
Using TRIBESPOS_BLUEPRINT.md Sections 6 and 5.8-5.9, implement:
- SaleOrder, SaleOrderLine, Payment, CashSession models
- ModifierGroup, ModifierOption, OrderLineModifier models
- RestaurantTable, KitchenTicket, TableReservation models
- coffeeclub/services.py: complete_sale() and deduct_bom_stock()
- POS terminal view at /coffeeclub/pos/ with offline service worker
- Kitchen Display System using Django Channels WebSocket
- Coffee Manager dashboard at /coffeeclub/manager/
```

**Session 4 — TribesSuppliers:**
```
Using TRIBESPOS_BLUEPRINT.md Sections 7 and 5.6-5.7, implement:
- PurchaseOrder, GRN, QCInspection, PackagingOrder, Shipment models
- CycleCount, DeliveryAttempt models
- All four services: procurement.py, receiving.py, packaging.py, dispatch.py
- All role dashboards: inventory manager, receiving, packing, dispatch, staff
```

**Session 5 — Tailoring:**
```
Using TRIBESPOS_BLUEPRINT.md Section 8 and 5.10, implement:
- TailoringOrder, TailoringStageLog, TailoringShipment models
- tailoring/services.py: confirm_tailoring_order(), collect_tailoring_order()
- All three views: salesperson, tailor_work, admin/kanban
- Printable job ticket and receipt templates
```

**Session 6 — Accounting + IRC Tax:**
```
Using TRIBESPOS_BLUEPRINT.md Sections 9, 11, and 12, implement:
- All accounting models (Section 5.11)
- All IRC tax models (Section 5.12)
- accounting/journal_rules.py with POSTING_RULES from Section 12.1
- accounting/services.py: post_journal() function from Section 12.2
- irc_tax/swt_tables.py: calculate_swt_fortnightly() from Section 11.3
- irc_tax/services/gst_service.py: generate_gst_return() from Section 11.2
- Celery tasks from Section 11.4
- Accountant dashboard from Section 9.3
- WeasyPrint IRC-format PDF for GST return
```

**Session 7 — SuperAdmin:**
```
Using TRIBESPOS_BLUEPRINT.md Section 10, implement the SuperAdmin MD dashboard.
It must aggregate KPIs from all three modules (coffeeclub, suppliers, tailoring),
show the IRC tax compliance status panel, staff activity, top products, and
system health. Use Chart.js for the revenue trend and by-module charts.
```

### Critical Implementation Rules for Claude Code

1. **All monetary values** → `DECIMAL(14,2)` — never `float`
2. **All stock movements** → always create a `StockMovement` record — never update `qty_on_hand` directly
3. **All financial transactions** → always call `post_journal()` — never skip
4. **Journal entries are immutable** → corrections via reversing entry only
5. **Sequence numbers** (SO-2025-00001 etc.) → generate inside `select_for_update()` transaction
6. **All `complete_*` service functions** → wrap in `@transaction.atomic`
7. **Module scoping** → all querysets must be filtered by `module` field
8. **Role checking** → use `RoleRequiredMixin` on every view, not just `LoginRequiredMixin`
9. **Time zone** → `TIME_ZONE = 'Pacific/Port_Moresby'` (UTC+10) — always use `timezone.now()`
10. **N+1 prevention** → use `select_related` and `prefetch_related` on all list views
11. **Soft delete** → set `is_active=False`, never hard-delete products, customers, or suppliers
12. **POS offline** → Service Worker caches: product catalogue, pending orders queue in IndexedDB, auto-syncs on reconnect

---

*TribesPOS Blueprint v2.0 — Definitive Edition*  
*System: Django 4.2 · MySQL 8 · MDB5 · DRF · Channels · Celery · WeasyPrint*  
*Modules: TribesCoffeeClub · TribesSuppliers · ParadiseTailoring · Accounting · SuperAdmin*  
*PNG IRC Tax Compliance: GST · SWT · CIT · WHT*
