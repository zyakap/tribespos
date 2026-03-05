# HARHURUM POS SYSTEM — TECHNICAL BLUEPRINT
**Client:** Harhurum.com.pg (Papua New Guinea)  
**Replacing:** HikePOS (hikeup.com) + Xero  
**Stack:** Django 4.x · MySQL 8.x · Material Design (Materialize CSS / MDB)  
**Prepared for:** Claude Code Implementation  

---

## TABLE OF CONTENTS

1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Database Schema](#3-database-schema)
4. [Django App Structure](#4-django-app-structure)
5. [Module Specifications](#5-module-specifications)
   - 5.1 Supplier & Procurement
   - 5.2 Warehouse & Inventory
   - 5.3 Tailoring / Custom Orders
   - 5.4 Coffee Shop POS
   - 5.5 Restaurant POS
   - 5.6 Accounting Engine
   - 5.7 IRC Tax Compliance & Automated Returns
   - 5.8 Reporting & Dashboard
   - 5.9 User & Role Management
6. [API Endpoints](#6-api-endpoints)
7. [UI/UX Guidelines](#7-uiux-guidelines)
8. [File & Folder Structure](#8-file--folder-structure)
9. [Settings & Configuration](#9-settings--configuration)
10. [Third-Party Integrations](#10-third-party-integrations)
11. [Security](#11-security)
12. [Deployment](#12-deployment)
13. [Implementation Phases](#13-implementation-phases)
14. [Claude Code Build Instructions](#14-claude-code-build-instructions)

---

## 1. SYSTEM OVERVIEW

### Business Context
Harhurum operates multiple business units from a single location in Papua New Guinea:
- **Retail/Wholesale** — supplier-sourced goods, warehouse-managed
- **Tailoring** — custom clothing orders with fabric tracking
- **Coffee Shop** — café-style counter service
- **Restaurant** — table-service dining

All units share a single stock database, customer database, and accounting ledger. The system must eliminate the need for both HikePOS and Xero by providing a unified, offline-capable POS with full double-entry accounting.

### Core Design Principles
- **Single source of truth** — one Django project, multiple business-unit apps
- **Double-entry accounting** — every transaction posts journal entries automatically
- **Offline-first POS** — service workers + IndexedDB for POS terminals
- **Role-based access** — staff see only what their role permits
- **Multi-terminal** — multiple POS stations per business unit
- **PNG tax compliance** — GST (10%) built-in, VAT-ready

---

## 2. ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                        HARHURUM POS                             │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ Supplier │  │Warehouse │  │Tailoring │  │  Coffee/Rest │   │
│  │  Portal  │  │  & Stock │  │  Orders  │  │   POS Tills  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘   │
│       │              │              │               │           │
│  ─────┴──────────────┴──────────────┴───────────────┴─────      │
│                    Django Core (REST + Views)                   │
│  ─────────────────────────────────────────────────────────      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │Accounting│  │Reporting │  │ Customer │  │ User / RBAC  │   │
│  │  Engine  │  │Dashboard │  │  & Loyalty│  │  Management  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │
│                                                                 │
│                     MySQL 8.x Database                          │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django 4.2 LTS |
| Database | MySQL 8.0 |
| ORM | Django ORM (with select_related / prefetch_related) |
| REST API | Django REST Framework (DRF) 3.15 |
| Frontend Templates | Django Templates + Materialize CSS 1.0 / MDB5 |
| Async Tasks | Celery + Redis |
| Caching | Redis |
| File Storage | Django FileSystem (local) or S3-compatible |
| Authentication | Django Auth + SimpleJWT |
| PDF Generation | WeasyPrint |
| Excel Export | openpyxl |
| Barcode | python-barcode + ZPL for label printing |
| WebSocket (kitchen display) | Django Channels + Redis |
| Offline POS | Service Worker + IndexedDB (vanilla JS) |

---

## 3. DATABASE SCHEMA

### 3.1 Core / Shared Tables

```sql
-- ─────────────────────────────────────────
-- BUSINESS UNITS
-- ─────────────────────────────────────────
CREATE TABLE business_unit (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    code            VARCHAR(20) UNIQUE NOT NULL,   -- CAFE, REST, TAIL, WHS
    name            VARCHAR(100) NOT NULL,
    unit_type       ENUM('cafe','restaurant','tailoring','warehouse') NOT NULL,
    address         TEXT,
    phone           VARCHAR(30),
    is_active       BOOL DEFAULT TRUE,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- USERS & ROLES
-- ─────────────────────────────────────────
CREATE TABLE auth_user ( ... );  -- Django default

CREATE TABLE staff_profile (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT UNIQUE REFERENCES auth_user(id),
    business_unit_id INT REFERENCES business_unit(id),
    role            ENUM('superadmin','manager','cashier','waiter',
                         'barista','tailor','warehouse','accountant') NOT NULL,
    pin             VARCHAR(6),                    -- quick POS login
    is_active       BOOL DEFAULT TRUE
);

-- ─────────────────────────────────────────
-- CUSTOMERS
-- ─────────────────────────────────────────
CREATE TABLE customer (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    code            VARCHAR(20) UNIQUE,
    name            VARCHAR(150) NOT NULL,
    phone           VARCHAR(30),
    email           VARCHAR(150),
    address         TEXT,
    loyalty_points  INT DEFAULT 0,
    credit_limit    DECIMAL(12,2) DEFAULT 0.00,
    outstanding_balance DECIMAL(12,2) DEFAULT 0.00,
    customer_type   ENUM('walk_in','account','wholesale') DEFAULT 'walk_in',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- SUPPLIERS
-- ─────────────────────────────────────────
CREATE TABLE supplier (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    code            VARCHAR(20) UNIQUE NOT NULL,
    name            VARCHAR(150) NOT NULL,
    contact_person  VARCHAR(100),
    phone           VARCHAR(30),
    email           VARCHAR(150),
    address         TEXT,
    payment_terms   INT DEFAULT 30,               -- days
    currency        VARCHAR(3) DEFAULT 'PGK',
    tax_number      VARCHAR(50),
    is_active       BOOL DEFAULT TRUE,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 Inventory / Warehouse

```sql
-- ─────────────────────────────────────────
-- CATEGORIES
-- ─────────────────────────────────────────
CREATE TABLE category (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    parent_id       INT REFERENCES category(id),
    name            VARCHAR(100) NOT NULL,
    business_unit_id INT REFERENCES business_unit(id),  -- NULL = global
    sort_order      INT DEFAULT 0
);

-- ─────────────────────────────────────────
-- UNITS OF MEASURE
-- ─────────────────────────────────────────
CREATE TABLE unit_of_measure (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(30) NOT NULL,          -- kg, g, litre, pcs, roll
    abbreviation    VARCHAR(10) NOT NULL
);

-- ─────────────────────────────────────────
-- PRODUCTS / ITEMS
-- ─────────────────────────────────────────
CREATE TABLE product (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    sku             VARCHAR(50) UNIQUE NOT NULL,
    barcode         VARCHAR(50),
    name            VARCHAR(200) NOT NULL,
    category_id     INT REFERENCES category(id),
    uom_id          INT REFERENCES unit_of_measure(id),
    product_type    ENUM('goods','service','composite','fabric') NOT NULL,
    cost_price      DECIMAL(12,4) DEFAULT 0.0000,
    sell_price      DECIMAL(12,2) DEFAULT 0.00,
    sell_price_wholesale DECIMAL(12,2),
    tax_rate        DECIMAL(5,2) DEFAULT 10.00,   -- GST %
    tax_inclusive   BOOL DEFAULT TRUE,
    track_inventory BOOL DEFAULT TRUE,
    min_stock_level DECIMAL(12,3) DEFAULT 0.000,
    reorder_qty     DECIMAL(12,3) DEFAULT 0.000,
    image           VARCHAR(255),
    description     TEXT,
    is_active       BOOL DEFAULT TRUE,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Product variants (size, colour)
CREATE TABLE product_variant (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    product_id      INT REFERENCES product(id),
    sku_suffix      VARCHAR(20),                   -- e.g. -RED-XL
    attribute_json  JSON,                          -- {"color":"Red","size":"XL"}
    barcode         VARCHAR(50),
    cost_price      DECIMAL(12,4),
    sell_price      DECIMAL(12,2),
    is_active       BOOL DEFAULT TRUE
);

-- Bill of Materials (composite products / menu items)
CREATE TABLE bom_item (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    parent_product_id INT REFERENCES product(id),
    component_product_id INT REFERENCES product(id),
    quantity        DECIMAL(12,4) NOT NULL
);

-- ─────────────────────────────────────────
-- WAREHOUSES / LOCATIONS
-- ─────────────────────────────────────────
CREATE TABLE warehouse (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    business_unit_id INT REFERENCES business_unit(id),
    name            VARCHAR(100) NOT NULL,
    location_type   ENUM('main','cold_room','bar','kitchen','fabric_store') DEFAULT 'main',
    is_active       BOOL DEFAULT TRUE
);

-- Stock on hand per location
CREATE TABLE stock_location (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    product_id      INT REFERENCES product(id),
    variant_id      INT REFERENCES product_variant(id),
    warehouse_id    INT REFERENCES warehouse(id),
    qty_on_hand     DECIMAL(12,3) DEFAULT 0.000,
    qty_reserved    DECIMAL(12,3) DEFAULT 0.000,  -- for tailoring orders
    qty_available   DECIMAL(12,3) AS (qty_on_hand - qty_reserved) STORED,
    last_updated    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_stock (product_id, variant_id, warehouse_id)
);

-- Full audit trail of every stock movement
CREATE TABLE stock_movement (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    product_id      INT REFERENCES product(id),
    variant_id      INT REFERENCES product_variant(id),
    warehouse_id    INT REFERENCES warehouse(id),
    movement_type   ENUM('purchase','sale','adjustment','transfer_in',
                         'transfer_out','production','waste','return') NOT NULL,
    reference_type  VARCHAR(50),                  -- PurchaseOrder, SaleOrder, etc
    reference_id    INT,
    qty             DECIMAL(12,3) NOT NULL,        -- positive = in, negative = out
    unit_cost       DECIMAL(12,4),
    total_cost      DECIMAL(14,4),
    notes           TEXT,
    created_by_id   INT REFERENCES auth_user(id),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.3 Procurement

```sql
-- ─────────────────────────────────────────
-- PURCHASE ORDERS
-- ─────────────────────────────────────────
CREATE TABLE purchase_order (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    po_number       VARCHAR(30) UNIQUE NOT NULL,   -- PO-2024-0001
    supplier_id     INT REFERENCES supplier(id),
    warehouse_id    INT REFERENCES warehouse(id),
    status          ENUM('draft','sent','partial','received','cancelled') DEFAULT 'draft',
    order_date      DATE NOT NULL,
    expected_date   DATE,
    received_date   DATE,
    subtotal        DECIMAL(14,2) DEFAULT 0.00,
    tax_total       DECIMAL(14,2) DEFAULT 0.00,
    total           DECIMAL(14,2) DEFAULT 0.00,
    notes           TEXT,
    created_by_id   INT REFERENCES auth_user(id),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE purchase_order_line (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    po_id           INT REFERENCES purchase_order(id),
    product_id      INT REFERENCES product(id),
    variant_id      INT REFERENCES product_variant(id),
    qty_ordered     DECIMAL(12,3) NOT NULL,
    qty_received    DECIMAL(12,3) DEFAULT 0.000,
    unit_cost       DECIMAL(12,4) NOT NULL,
    tax_rate        DECIMAL(5,2) DEFAULT 10.00,
    line_total      DECIMAL(14,2)
);

-- Goods Received Note
CREATE TABLE goods_received_note (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    grn_number      VARCHAR(30) UNIQUE NOT NULL,
    po_id           INT REFERENCES purchase_order(id),
    warehouse_id    INT REFERENCES warehouse(id),
    received_date   DATE NOT NULL,
    notes           TEXT,
    created_by_id   INT REFERENCES auth_user(id),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE grn_line (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    grn_id          INT REFERENCES goods_received_note(id),
    po_line_id      INT REFERENCES purchase_order_line(id),
    product_id      INT REFERENCES product(id),
    variant_id      INT REFERENCES product_variant(id),
    qty_received    DECIMAL(12,3) NOT NULL,
    unit_cost       DECIMAL(12,4) NOT NULL
);

-- Supplier Invoice (AP)
CREATE TABLE supplier_invoice (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    invoice_number  VARCHAR(50) NOT NULL,
    supplier_id     INT REFERENCES supplier(id),
    po_id           INT REFERENCES purchase_order(id),
    invoice_date    DATE NOT NULL,
    due_date        DATE,
    subtotal        DECIMAL(14,2),
    tax_total       DECIMAL(14,2),
    total           DECIMAL(14,2),
    amount_paid     DECIMAL(14,2) DEFAULT 0.00,
    status          ENUM('unpaid','partial','paid','overdue') DEFAULT 'unpaid',
    journal_entry_id INT,                          -- FK set after accounting posts
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.4 Sales / POS

```sql
-- ─────────────────────────────────────────
-- SALES ORDERS (all channels)
-- ─────────────────────────────────────────
CREATE TABLE sale_order (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    order_number    VARCHAR(30) UNIQUE NOT NULL,   -- SO-CAFE-2024-00001
    business_unit_id INT REFERENCES business_unit(id),
    customer_id     INT REFERENCES customer(id),  -- NULL = walk-in
    sale_type       ENUM('pos','table','takeaway','delivery','wholesale') NOT NULL,
    status          ENUM('open','held','completed','void','refunded') DEFAULT 'open',
    table_number    VARCHAR(10),
    covers          INT,                           -- restaurant: number of diners
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
    order_id        INT REFERENCES sale_order(id),
    product_id      INT REFERENCES product(id),
    variant_id      INT REFERENCES product_variant(id),
    product_name    VARCHAR(200),                  -- snapshot
    qty             DECIMAL(12,3) NOT NULL,
    unit_price      DECIMAL(12,2) NOT NULL,
    discount_pct    DECIMAL(5,2) DEFAULT 0.00,
    tax_rate        DECIMAL(5,2) DEFAULT 10.00,
    tax_inclusive   BOOL DEFAULT TRUE,
    line_total      DECIMAL(14,2),
    course          VARCHAR(20),                   -- restaurant: Starter/Main/Dessert
    sent_to_kitchen BOOL DEFAULT FALSE,
    notes           TEXT
);

-- Modifier / Add-ons (cafe: extra shot, no sugar etc.)
CREATE TABLE order_line_modifier (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    line_id         INT REFERENCES sale_order_line(id),
    modifier_name   VARCHAR(100) NOT NULL,
    price_adjustment DECIMAL(10,2) DEFAULT 0.00
);

-- ─────────────────────────────────────────
-- PAYMENTS
-- ─────────────────────────────────────────
CREATE TABLE payment (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    order_id        INT REFERENCES sale_order(id),
    payment_method  ENUM('cash','card_visa','card_mastercard','eftpos',
                         'mobile_money','account_credit','voucher') NOT NULL,
    amount          DECIMAL(14,2) NOT NULL,
    reference       VARCHAR(100),                  -- card auth, mobile ref
    tendered        DECIMAL(14,2),                 -- cash tendered
    change_given    DECIMAL(14,2),
    paid_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_by_id INT REFERENCES auth_user(id),
    journal_entry_id INT
);

-- Cash drawer sessions
CREATE TABLE cash_session (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    terminal_id     VARCHAR(30) NOT NULL,
    cashier_id      INT REFERENCES auth_user(id),
    business_unit_id INT REFERENCES business_unit(id),
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

### 3.5 Tailoring Module

```sql
-- ─────────────────────────────────────────
-- TAILORING ORDERS
-- ─────────────────────────────────────────
CREATE TABLE tailoring_order (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    order_number    VARCHAR(30) UNIQUE NOT NULL,   -- TAIL-2024-00001
    customer_id     INT REFERENCES customer(id),
    tailor_id       INT REFERENCES auth_user(id),
    status          ENUM('quote','confirmed','cutting','sewing',
                         'finishing','ready','collected','cancelled') DEFAULT 'quote',
    garment_type    VARCHAR(100) NOT NULL,          -- Dress, Suit, Shirt, etc.
    style_notes     TEXT,
    measurements_json JSON,                        -- {"chest":92,"waist":78,...}
    fabric_product_id INT REFERENCES product(id),  -- selected fabric
    fabric_qty      DECIMAL(10,3),                 -- metres required
    labour_charge   DECIMAL(12,2) DEFAULT 0.00,
    fabric_charge   DECIMAL(12,2) DEFAULT 0.00,
    additional_charge DECIMAL(12,2) DEFAULT 0.00,
    discount_amount DECIMAL(12,2) DEFAULT 0.00,
    total           DECIMAL(12,2) DEFAULT 0.00,
    deposit_paid    DECIMAL(12,2) DEFAULT 0.00,
    balance_due     DECIMAL(12,2),
    promised_date   DATE,
    completed_date  DATE,
    collected_date  DATE,
    notes           TEXT,
    created_by_id   INT REFERENCES auth_user(id),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Progress tracking
CREATE TABLE tailoring_stage_log (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    tailoring_order_id INT REFERENCES tailoring_order(id),
    stage           VARCHAR(50) NOT NULL,
    notes           TEXT,
    changed_by_id   INT REFERENCES auth_user(id),
    changed_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.6 Restaurant — Tables & Kitchen

```sql
CREATE TABLE restaurant_table (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    business_unit_id INT REFERENCES business_unit(id),
    table_number    VARCHAR(10) NOT NULL,
    section         VARCHAR(50),                   -- Indoor, Outdoor, Bar
    capacity        INT DEFAULT 4,
    status          ENUM('available','occupied','reserved','cleaning') DEFAULT 'available',
    current_order_id INT REFERENCES sale_order(id)
);

CREATE TABLE kitchen_ticket (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    order_id        INT REFERENCES sale_order(id),
    ticket_number   INT NOT NULL,
    status          ENUM('new','acknowledged','preparing','ready','delivered') DEFAULT 'new',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at DATETIME,
    ready_at        DATETIME
);

CREATE TABLE kitchen_ticket_line (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id       INT REFERENCES kitchen_ticket(id),
    order_line_id   INT REFERENCES sale_order_line(id),
    qty             DECIMAL(12,3),
    notes           TEXT
);
```

### 3.7 Accounting (Double-Entry)

```sql
-- ─────────────────────────────────────────
-- CHART OF ACCOUNTS
-- ─────────────────────────────────────────
CREATE TABLE account (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    code            VARCHAR(10) UNIQUE NOT NULL,   -- 1000, 2000, etc.
    name            VARCHAR(150) NOT NULL,
    account_type    ENUM('asset','liability','equity','revenue','expense','cogs') NOT NULL,
    account_subtype VARCHAR(50),
    parent_id       INT REFERENCES account(id),
    is_system       BOOL DEFAULT FALSE,            -- protected system accounts
    normal_balance  ENUM('debit','credit') NOT NULL,
    is_active       BOOL DEFAULT TRUE,
    description     TEXT
);

-- ─────────────────────────────────────────
-- FISCAL PERIODS
-- ─────────────────────────────────────────
CREATE TABLE fiscal_year (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(50) NOT NULL,           -- FY 2024-2025
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    is_closed       BOOL DEFAULT FALSE
);

CREATE TABLE fiscal_period (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    fiscal_year_id  INT REFERENCES fiscal_year(id),
    name            VARCHAR(20) NOT NULL,           -- Jan 2025
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    is_closed       BOOL DEFAULT FALSE
);

-- ─────────────────────────────────────────
-- JOURNAL ENTRIES
-- ─────────────────────────────────────────
CREATE TABLE journal_entry (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    entry_number    VARCHAR(30) UNIQUE NOT NULL,   -- JE-2024-00001
    entry_type      ENUM('sale','purchase','payment','receipt','adjustment',
                         'payroll','depreciation','manual') NOT NULL,
    reference_type  VARCHAR(50),
    reference_id    INT,
    fiscal_period_id INT REFERENCES fiscal_period(id),
    entry_date      DATE NOT NULL,
    description     TEXT,
    total_debit     DECIMAL(16,2),
    total_credit    DECIMAL(16,2),
    is_posted       BOOL DEFAULT FALSE,
    is_reconciled   BOOL DEFAULT FALSE,
    created_by_id   INT REFERENCES auth_user(id),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE journal_line (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    journal_entry_id INT REFERENCES journal_entry(id),
    account_id      INT REFERENCES account(id),
    description     VARCHAR(255),
    debit           DECIMAL(16,2) DEFAULT 0.00,
    credit          DECIMAL(16,2) DEFAULT 0.00,
    business_unit_id INT REFERENCES business_unit(id),
    sort_order      INT DEFAULT 0,
    CONSTRAINT chk_debit_credit CHECK (
        (debit > 0 AND credit = 0) OR (credit > 0 AND debit = 0)
    )
);

-- ─────────────────────────────────────────
-- ACCOUNTS RECEIVABLE / PAYABLE
-- ─────────────────────────────────────────
CREATE TABLE ar_invoice (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    invoice_number  VARCHAR(30) UNIQUE NOT NULL,
    customer_id     INT REFERENCES customer(id),
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

-- ─────────────────────────────────────────
-- BANK / CASH ACCOUNTS
-- ─────────────────────────────────────────
CREATE TABLE bank_account (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    account_id      INT REFERENCES account(id),   -- links to COA
    bank_name       VARCHAR(100),
    account_number  VARCHAR(50),
    bsb_or_branch   VARCHAR(30),
    currency        VARCHAR(3) DEFAULT 'PGK',
    current_balance DECIMAL(16,2) DEFAULT 0.00,
    is_active       BOOL DEFAULT TRUE
);

CREATE TABLE bank_transaction (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    bank_account_id INT REFERENCES bank_account(id),
    transaction_date DATE NOT NULL,
    description     VARCHAR(255),
    debit           DECIMAL(14,2) DEFAULT 0.00,
    credit          DECIMAL(14,2) DEFAULT 0.00,
    running_balance DECIMAL(14,2),
    is_reconciled   BOOL DEFAULT FALSE,
    journal_line_id INT REFERENCES journal_line(id),
    imported_at     DATETIME
);

-- ─────────────────────────────────────────
-- TAX CONFIGURATION
-- ─────────────────────────────────────────
CREATE TABLE tax_rate (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(50) NOT NULL,          -- GST, Exempt, Zero-rated
    rate            DECIMAL(5,2) NOT NULL,
    tax_type        ENUM('gst','import','exempt','zero') DEFAULT 'gst',
    sales_account_id INT REFERENCES account(id),
    purchase_account_id INT REFERENCES account(id),
    is_default      BOOL DEFAULT FALSE
);
```

---

## 4. DJANGO APP STRUCTURE

```
harhurum/                          # Django project root
├── config/                        # Project settings package
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   ├── core/                      # Shared models, utilities, base classes
│   ├── accounts/                  # User auth, staff profiles, RBAC
│   ├── customers/                 # Customer management, loyalty
│   ├── suppliers/                 # Supplier management
│   ├── products/                  # Products, categories, UOM, BOM
│   ├── warehouse/                 # Warehouses, stock levels, movements
│   ├── procurement/               # Purchase orders, GRN, supplier invoices
│   ├── pos/                       # POS terminal (shared across units)
│   ├── cafe/                      # Coffee shop specific (modifiers, menu)
│   ├── restaurant/                # Restaurant tables, kitchen display
│   ├── tailoring/                 # Tailoring orders, measurements
│   ├── accounting/                # COA, journals, AR, AP, bank
│   ├── reporting/                 # Reports, dashboards, exports
│   └── api/                       # DRF API (consumed by POS frontend)
│
├── templates/
│   ├── base.html                  # Material Design base
│   ├── components/
│   └── [app-specific]/
│
├── static/
│   ├── css/
│   ├── js/
│   │   ├── pos/                   # Offline POS JS
│   │   └── kitchen/               # Kitchen display JS
│   └── img/
│
├── media/                         # User uploads (product images)
├── requirements.txt
├── manage.py
└── .env
```

---

## 5. MODULE SPECIFICATIONS

### 5.1 Supplier & Procurement Module (`apps/suppliers`, `apps/procurement`)

**Views / Pages:**
- Supplier list, create, edit, detail
- Supplier ledger (all transactions with supplier)
- Purchase Order list, create (from reorder suggestions or manual)
- PO detail with line item entry
- Goods Received Note creation against PO
- Supplier Invoice matching against GRN/PO
- AP Aging report

**Business Logic:**
```python
# When GRN is posted:
# 1. Increase stock_location.qty_on_hand
# 2. Create stock_movement (type=purchase)
# 3. Update product.cost_price (weighted average)
# 4. Create journal entry:
#    DR  Inventory Account        (cost of goods received)
#    DR  GST Input Tax            (if applicable)
#    CR  Accounts Payable         (total invoice amount)

# When Supplier Invoice paid:
#    DR  Accounts Payable
#    CR  Bank / Cash
```

**Key Models:** `Supplier`, `PurchaseOrder`, `PurchaseOrderLine`, `GoodsReceivedNote`, `GRNLine`, `SupplierInvoice`

---

### 5.2 Warehouse & Inventory Module (`apps/warehouse`, `apps/products`)

**Views / Pages:**
- Product catalog (list, create, edit, bulk import via CSV)
- Product detail (variants, BOM, stock across warehouses)
- Stock on hand dashboard (filterable by warehouse/category)
- Stock adjustment (write-off, correction, damage)
- Inter-warehouse transfer
- Stock take / stocktake reconciliation
- Low stock / reorder alerts
- Barcode label printing

**Business Logic:**
```python
# Stock Adjustment:
#    DR  Stock Adjustment Expense   (if writing off)
#    CR  Inventory Account

# For composite/BOM products (café menu items), 
# sale deducts each component from stock proportionally.

def deduct_bom_stock(product, qty_sold, warehouse):
    for bom_item in product.bom_items.all():
        component_qty = bom_item.quantity * qty_sold
        update_stock(bom_item.component, -component_qty, warehouse)
        record_movement(bom_item.component, 'sale', -component_qty)
```

**Inventory Valuation:** Weighted Average Cost (WAC) — recalculated on each GRN.

---

### 5.3 Tailoring Orders Module (`apps/tailoring`)

**Views / Pages:**
- New tailoring order form (customer, garment, measurements, fabric selection)
- Order list (filterable by status, tailor, date)
- Order detail / production card (print-friendly)
- Stage update (Kanban board view)
- Deposit receipt printing
- Balance collection at pickup
- Fabric stock consumption report

**Business Logic:**
```python
# On order confirmation:
# 1. Reserve fabric_qty in stock_location.qty_reserved
# 2. Create deposit payment record
# 3. Post journal entry for deposit received

# On order collection + final payment:
# 1. Deduct fabric from stock (unreserve + deduct)
# 2. Create sale_order record linking to tailoring_order
# 3. Post revenue journal entries
# 4. Issue receipt / invoice

# Journal for revenue recognition:
#    DR  Cash / AR
#    CR  Tailoring Revenue
#    DR  Fabric COGS
#    CR  Inventory (Fabric)
```

**Measurement Template Fields:**
- Neck, Chest, Waist, Hips, Shoulder Width, Sleeve Length, Back Length, Inseam, Outseam, Thigh, Knee, Ankle

---

### 5.4 Coffee Shop POS Module (`apps/cafe`, `apps/pos`)

**Views / Pages:**
- POS terminal (touch-optimized, works offline)
- Menu grid with categories (Drinks / Food / Retail)
- Item modifiers panel (milk type, size, extra shots, temperature)
- Order build + quick checkout
- Split payment
- Cash session open/close
- Barista queue display (order screen)
- Void / refund

**POS Terminal Architecture (offline-first):**
```javascript
// Service Worker caches:
// - Product catalog (synced on session open)
// - Pending orders queue (IndexedDB)
// - Auto-sync when connection restored

// POST to /api/pos/sync/ with batched orders
```

**Business Logic:**
```python
# Café sale journal:
#    DR  Cash / EFTPOS Clearing
#    CR  Café Revenue
#    CR  GST Payable

# BOM deduction for each menu item sold
# Cash session variance posts to:
#    DR/CR  Cash Variance Expense/Income
```

---

### 5.5 Restaurant POS Module (`apps/restaurant`)

**Views / Pages:**
- Table floor plan (visual, drag-configurable)
- Open table / assign waiter
- Order by course (Starter / Main / Dessert)
- Send to kitchen (fires kitchen ticket)
- Kitchen Display System (KDS) — real-time WebSocket
- Bill split (by seat / by item / even split)
- Table merge / transfer
- End-of-night takings summary

**Kitchen Display System:**
```python
# Django Channels consumer
class KitchenConsumer(AsyncWebsocketConsumer):
    async def receive(self, text_data):
        # Broadcast new ticket to kitchen group
        await self.channel_layer.group_send(
            'kitchen_display',
            {'type': 'kitchen_ticket', 'data': ticket_data}
        )
```

**Business Logic:**
```python
# Table status transitions:
# available → occupied (on order open)
# occupied → available (on bill paid + table closed)

# Restaurant sale journal (same as café):
#    DR  Cash / AR (account customer)
#    CR  Restaurant Revenue
#    CR  GST Payable
```

---

### 5.6 Accounting Engine (`apps/accounting`)

**Chart of Accounts — Default Setup:**

| Code | Account Name | Type |
|---|---|---|
| 1000 | Cash in Hand | Asset |
| 1010 | EFTPOS Clearing | Asset |
| 1100 | Accounts Receivable | Asset |
| 1200 | Inventory — Goods | Asset |
| 1210 | Inventory — Fabric | Asset |
| 1500 | Fixed Assets | Asset |
| 2000 | Accounts Payable | Liability |
| 2100 | GST Payable | Liability |
| 2110 | GST Receivable (Input Tax) | Asset |
| 2200 | Customer Deposits | Liability |
| 3000 | Owner's Equity | Equity |
| 3100 | Retained Earnings | Equity |
| 4000 | Café Revenue | Revenue |
| 4100 | Restaurant Revenue | Revenue |
| 4200 | Tailoring Revenue | Revenue |
| 4300 | Retail Sales Revenue | Revenue |
| 5000 | Cost of Goods Sold — Food | COGS |
| 5100 | Cost of Goods Sold — Beverage | COGS |
| 5200 | Cost of Goods Sold — Fabric | COGS |
| 5300 | Cost of Goods Sold — Retail | COGS |
| 6000 | Staff Wages | Expense |
| 6100 | Rent | Expense |
| 6200 | Utilities | Expense |
| 6300 | Depreciation | Expense |
| 6400 | Cash Variance | Expense |
| 6500 | Stock Write-off | Expense |

**Financial Reports:**
- Profit & Loss (by period, by business unit)
- Balance Sheet
- Cash Flow Statement
- Trial Balance
- General Ledger
- GST Return summary
- AR Aging
- AP Aging

**Automated Journal Posting Rules:**

```python
# apps/accounting/journal_rules.py

POSTING_RULES = {
    'cash_sale': [
        ('DR', '1000', 'total_including_tax'),
        ('CR', 'revenue_account', 'subtotal'),
        ('CR', '2100', 'tax_amount'),           # GST Payable
    ],
    'eftpos_sale': [
        ('DR', '1010', 'total_including_tax'),
        ('CR', 'revenue_account', 'subtotal'),
        ('CR', '2100', 'tax_amount'),
    ],
    'account_sale': [
        ('DR', '1100', 'total_including_tax'),  # AR
        ('CR', 'revenue_account', 'subtotal'),
        ('CR', '2100', 'tax_amount'),
    ],
    'cogs_deduction': [
        ('DR', 'cogs_account', 'cost_of_goods'),
        ('CR', 'inventory_account', 'cost_of_goods'),
    ],
    'purchase_invoice': [
        ('DR', 'inventory_account', 'subtotal'),
        ('DR', '2110', 'tax_amount'),           # GST Receivable
        ('CR', '2000', 'total'),                # AP
    ],
    'ap_payment': [
        ('DR', '2000', 'amount'),
        ('CR', '1000', 'amount'),               # or bank account
    ],
    'tailoring_deposit': [
        ('DR', '1000', 'deposit_amount'),
        ('CR', '2200', 'deposit_amount'),       # Customer Deposits (Liability)
    ],
    'tailoring_collection': [
        ('DR', '2200', 'deposit_amount'),       # Reverse deposit
        ('DR', '1000', 'balance_paid'),
        ('CR', '4200', 'subtotal'),             # Tailoring Revenue
        ('CR', '2100', 'tax_amount'),
        ('DR', '5200', 'fabric_cost'),
        ('CR', '1210', 'fabric_cost'),          # Inventory Fabric
    ],
}
```

---

### 5.7 IRC Tax Compliance & Automated Returns (`apps/irc_tax`)

This module implements full compliance with Papua New Guinea's Internal Revenue Commission (IRC) rules. Every tax obligation is tracked, auto-calculated from live transaction data, and generates a filing-ready return that can be exported as PDF or submitted via the IRC's myIRC portal.

---

#### PNG Tax Obligations Summary for Harhurum

| Tax Type | Rate | Period | IRC Due Date | Governed By |
|---|---|---|---|---|
| Goods & Services Tax (GST) | 10% on taxable supplies | Monthly | **21st of following month** | Goods and Services Tax Act 2003 |
| Salary & Wages Tax (SWT) | Marginal rates (fortnightly) | Monthly | **7th of following month** | Income Tax Act 1959 |
| Corporate Income Tax (CIT) | 30% of net profit | Annual | **30 April** (following year) | Income Tax Act 1959 |
| Provisional Tax (CIT instalments) | Based on prior year CIT | Quarterly | Mar 31 / Jun 30 / Sep 30 / Dec 31 | Income Tax Act 1959 |
| Withholding Tax — Dividends | 17% (resident) / 15% (non-resident) | On payment | 7th of following month | Income Tax Act 1959 |
| Withholding Tax — Interest | 15% | On payment | 7th of following month | Income Tax Act 1959 |

> **Note:** PNG fiscal year = 1 January to 31 December. All tax is in PGK.

---

#### 5.7.1 GST Module

**IRC Rules Applied:**
- GST is imposed at 10% on the value of goods and services sold in PNG using the invoice credit method — registered businesses collect output tax on sales and claim input tax credits on purchases.
- Exported goods and services attract a zero rate of GST. Medical, educational, and financial services are exempt.
- GST returns and payment are due by the 21st day of the month following the tax period.
- Directors of companies that fail to comply with GST obligations are personally liable for a penalty equal to the outstanding tax liability.

**GST Supply Classifications in the System:**

```python
# apps/irc_tax/constants.py

GST_SUPPLY_TYPES = {
    'TAXABLE':    {'rate': 10.0,  'code': 'T',  'label': 'Taxable Supply (10%)'},
    'ZERO_RATED': {'rate': 0.0,   'code': 'Z',  'label': 'Zero-Rated Supply'},
    'EXEMPT':     {'rate': 0.0,   'code': 'E',  'label': 'GST Exempt'},
    'OUT_OF_SCOPE': {'rate': 0.0, 'code': 'OS', 'label': 'Out of Scope'},
}

# Zero-rated examples for Harhurum context:
ZERO_RATED_CATEGORIES = [
    'exports',
    'sale_of_going_concern',
]

# Exempt supply categories:
EXEMPT_CATEGORIES = [
    'medical_services',
    'educational_services',
    'financial_services',
    'residential_rent',
]
```

**Database Schema — GST:**

```sql
-- GST Return (one per month)
CREATE TABLE gst_return (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    return_period       VARCHAR(7) NOT NULL,        -- '2025-01' (YYYY-MM)
    period_start        DATE NOT NULL,
    period_end          DATE NOT NULL,
    due_date            DATE NOT NULL,              -- 21st of following month
    status              ENUM('draft','finalised','filed','amended') DEFAULT 'draft',

    -- OUTPUT TAX (Sales)
    total_taxable_sales         DECIMAL(16,2) DEFAULT 0.00,  -- GST-exclusive
    output_tax_collected        DECIMAL(16,2) DEFAULT 0.00,  -- GST on sales
    total_zero_rated_sales      DECIMAL(16,2) DEFAULT 0.00,
    total_exempt_sales          DECIMAL(16,2) DEFAULT 0.00,
    total_gross_sales           DECIMAL(16,2) DEFAULT 0.00,

    -- INPUT TAX CREDITS (Purchases)
    total_taxable_purchases     DECIMAL(16,2) DEFAULT 0.00,
    input_tax_credits           DECIMAL(16,2) DEFAULT 0.00,  -- GST on purchases

    -- NET POSITION
    net_gst_payable             DECIMAL(16,2) DEFAULT 0.00,  -- output - input
    net_gst_refundable          DECIMAL(16,2) DEFAULT 0.00,  -- if input > output

    -- Adjustments
    adjustments_amount          DECIMAL(16,2) DEFAULT 0.00,
    adjustment_notes            TEXT,

    filed_date          DATE,
    filed_by_id         INT REFERENCES auth_user(id),
    irc_reference       VARCHAR(50),                -- IRC confirmation number
    notes               TEXT,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Detailed GST transaction lines (audit trail per return)
CREATE TABLE gst_return_line (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    gst_return_id       INT REFERENCES gst_return(id),
    line_type           ENUM('output','input','adjustment') NOT NULL,
    transaction_type    VARCHAR(50),                -- sale, purchase_invoice, credit_note
    reference_type      VARCHAR(50),
    reference_id        INT,
    transaction_date    DATE NOT NULL,
    supplier_customer   VARCHAR(150),
    description         VARCHAR(255),
    gst_exclusive_amount DECIMAL(14,2),
    gst_amount          DECIMAL(14,2),
    supply_type         VARCHAR(10)                 -- T, Z, E, OS
);
```

**Auto-Calculation Logic:**

```python
# apps/irc_tax/services/gst_service.py

from decimal import Decimal
from django.db import transaction as db_transaction
from apps.pos.models import SaleOrder, SaleOrderLine
from apps.procurement.models import SupplierInvoice
from .models import GSTReturn, GSTReturnLine

def generate_gst_return(year: int, month: int) -> GSTReturn:
    """
    Auto-generates a GST return for a given month by aggregating:
    - All completed sale orders (output tax)
    - All posted supplier invoices (input tax credits)
    - Any credit notes / adjustments
    """
    import calendar
    from datetime import date

    period_start = date(year, month, 1)
    period_end = date(year, month, calendar.monthrange(year, month)[1])
    
    # Due date = 21st of following month
    if month == 12:
        due_date = date(year + 1, 1, 21)
    else:
        due_date = date(year, month + 1, 21)

    with db_transaction.atomic():
        gst_return, created = GSTReturn.objects.get_or_create(
            return_period=f"{year:04d}-{month:02d}",
            defaults={
                'period_start': period_start,
                'period_end': period_end,
                'due_date': due_date,
                'status': 'draft',
            }
        )

        # Clear existing draft lines and recalculate
        if gst_return.status == 'draft':
            gst_return.lines.all().delete()
            _calculate_output_tax(gst_return, period_start, period_end)
            _calculate_input_tax(gst_return, period_start, period_end)
            _update_return_totals(gst_return)

    return gst_return


def _calculate_output_tax(gst_return, start, end):
    """Aggregate GST from completed sales."""
    sales = SaleOrder.objects.filter(
        status='completed',
        completed_at__date__gte=start,
        completed_at__date__lte=end,
    ).select_related('business_unit')

    for order in sales:
        for line in order.lines.select_related('product').all():
            supply_type = line.product.gst_supply_type  # T / Z / E / OS
            
            if supply_type == 'T':
                if line.product.tax_inclusive:
                    gst_excl = line.line_total / Decimal('1.10')
                    gst_amt = line.line_total - gst_excl
                else:
                    gst_excl = line.line_total
                    gst_amt = line.line_total * Decimal('0.10')
            else:
                gst_excl = line.line_total
                gst_amt = Decimal('0.00')

            GSTReturnLine.objects.create(
                gst_return=gst_return,
                line_type='output',
                transaction_type='sale',
                reference_type='SaleOrder',
                reference_id=order.id,
                transaction_date=order.completed_at.date(),
                supplier_customer=order.customer.name if order.customer else 'Walk-in',
                description=f"Sale {order.order_number}",
                gst_exclusive_amount=gst_excl.quantize(Decimal('0.01')),
                gst_amount=gst_amt.quantize(Decimal('0.01')),
                supply_type=supply_type,
            )


def _calculate_input_tax(gst_return, start, end):
    """Aggregate GST input tax credits from supplier invoices."""
    invoices = SupplierInvoice.objects.filter(
        invoice_date__gte=start,
        invoice_date__lte=end,
        status__in=['unpaid', 'partial', 'paid'],
    ).select_related('supplier')

    for inv in invoices:
        GSTReturnLine.objects.create(
            gst_return=gst_return,
            line_type='input',
            transaction_type='purchase_invoice',
            reference_type='SupplierInvoice',
            reference_id=inv.id,
            transaction_date=inv.invoice_date,
            supplier_customer=inv.supplier.name,
            description=f"Invoice {inv.invoice_number}",
            gst_exclusive_amount=inv.subtotal,
            gst_amount=inv.tax_total,
            supply_type='T',
        )


def _update_return_totals(gst_return):
    from django.db.models import Sum
    lines = gst_return.lines.all()

    output = lines.filter(line_type='output')
    inputs = lines.filter(line_type='input')

    gst_return.total_taxable_sales = output.filter(
        supply_type='T').aggregate(s=Sum('gst_exclusive_amount'))['s'] or 0
    gst_return.total_zero_rated_sales = output.filter(
        supply_type='Z').aggregate(s=Sum('gst_exclusive_amount'))['s'] or 0
    gst_return.total_exempt_sales = output.filter(
        supply_type='E').aggregate(s=Sum('gst_exclusive_amount'))['s'] or 0
    gst_return.output_tax_collected = output.aggregate(
        s=Sum('gst_amount'))['s'] or 0

    gst_return.total_taxable_purchases = inputs.aggregate(
        s=Sum('gst_exclusive_amount'))['s'] or 0
    gst_return.input_tax_credits = inputs.aggregate(
        s=Sum('gst_amount'))['s'] or 0

    net = gst_return.output_tax_collected - gst_return.input_tax_credits
    gst_return.net_gst_payable = max(net, Decimal('0.00'))
    gst_return.net_gst_refundable = max(-net, Decimal('0.00'))
    gst_return.total_gross_sales = (
        gst_return.total_taxable_sales +
        gst_return.total_zero_rated_sales +
        gst_return.total_exempt_sales
    )
    gst_return.save()
```

**GST Return — IRC Form Layout (PDF Export):**

```
┌─────────────────────────────────────────────────────────┐
│         GOODS AND SERVICES TAX RETURN                   │
│         Internal Revenue Commission — Papua New Guinea  │
│─────────────────────────────────────────────────────────│
│  Taxpayer Name:  Harhurum                               │
│  TIN:            [configured in settings]               │
│  GST Reg No:     [configured in settings]               │
│  Period:         January 2025   Due: 21 February 2025   │
│─────────────────────────────────────────────────────────│
│  PART A — SALES / OUTPUT TAX                            │
│  1. Total Taxable Sales (GST excl.)     K ___________   │
│  2. Output Tax (10% of Line 1)          K ___________   │
│  3. Zero-Rated Sales                    K ___________   │
│  4. Exempt Sales                        K ___________   │
│  5. Total Gross Sales (1+3+4)           K ___________   │
│─────────────────────────────────────────────────────────│
│  PART B — PURCHASES / INPUT TAX CREDITS                 │
│  6. Total Taxable Purchases (GST excl.) K ___________   │
│  7. Input Tax Credits                   K ___________   │
│─────────────────────────────────────────────────────────│
│  PART C — NET POSITION                                  │
│  8. Net GST Payable (Line 2 – Line 7)   K ___________   │
│     OR Refund Claimable                 K ___________   │
│─────────────────────────────────────────────────────────│
│  Adjustments:                           K ___________   │
│─────────────────────────────────────────────────────────│
│  Authorised Signature: _____________  Date: __________  │
└─────────────────────────────────────────────────────────┘
```

---

#### 5.7.2 Salary & Wages Tax (SWT) Module

**IRC Rules Applied:**
- Businesses paying salary or wages to employees are required to withhold SWT at prescribed marginal rates and remit to the IRC on the seventh day of the month following the month of payment.
- The tax period is a fortnight. Tax is assessed by reference to salary or wage income derived in that fortnight.
- The salary and wage earners are not required to submit tax returns. The tax-free threshold is K20,000 per annum.
- Directors are personally liable for any unpaid SWT obligations. Directors who fail to ensure company compliance may be penalised at 20% of the unpaid tax liability per annum.

**SWT Fortnightly Tax Rates (Resident Employees — 2024):**

```python
# apps/irc_tax/swt_tables.py

# Resident individual fortnightly SWT rates (Income Tax Act 1959, 2024)
# Annual tax-free threshold: K20,000 (K769.23 per fortnight)
# Formula: calculate annual equivalent, apply marginal rates, divide by 26

SWT_RESIDENT_ANNUAL_BRACKETS = [
    # (annual_income_from, annual_income_to, base_tax, marginal_rate)
    (0,        20_000,    0,        0.00),   # Tax-free threshold
    (20_001,   33_000,    0,        0.22),   # 22% on income over K20,000
    (33_001,   70_000,    2_860,    0.30),   # 30%
    (70_001,   250_000,   13_960,   0.35),   # 35%
    (250_001,  float('inf'), 76_960, 0.42),  # 42%
]

SWT_NON_RESIDENT_ANNUAL_BRACKETS = [
    # Non-residents pay from K1 (no tax-free threshold)
    (0,        33_000,    0,        0.22),
    (33_001,   70_000,    7_260,    0.30),
    (70_001,   250_000,   18_360,   0.35),
    (250_001,  float('inf'), 81_360, 0.42),
]


def calculate_swt_fortnightly(gross_fortnight: float, is_resident: bool = True) -> float:
    """
    Calculate SWT to deduct from a single fortnightly pay.
    
    Steps per Income Tax Act formula:
    1. Annualise the fortnightly gross (× 26)
    2. Apply marginal brackets to find annual tax
    3. Divide annual tax by 26 = fortnightly SWT
    """
    annual = gross_fortnight * 26
    brackets = SWT_RESIDENT_ANNUAL_BRACKETS if is_resident else SWT_NON_RESIDENT_ANNUAL_BRACKETS
    
    annual_tax = 0.0
    for (low, high, base, rate) in brackets:
        if annual <= low:
            break
        taxable = min(annual, high) - low
        annual_tax = base + (taxable * rate)
    
    return round(annual_tax / 26, 2)


def calculate_swt_with_benefits(
    gross_fortnight: float,
    housing_benefit: float = 0.0,
    vehicle_benefit: float = 0.0,
    other_benefits: float = 0.0,
    is_resident: bool = True,
) -> dict:
    """
    Full SWT calculation including taxable benefits per IRC rules.
    Housing and vehicle benefits are added to gross before tax calculation.
    """
    total_gross = gross_fortnight + housing_benefit + vehicle_benefit + other_benefits
    swt = calculate_swt_fortnightly(total_gross, is_resident)
    return {
        'gross_wages': gross_fortnight,
        'taxable_benefits': housing_benefit + vehicle_benefit + other_benefits,
        'total_taxable': total_gross,
        'swt_deducted': swt,
        'net_pay': gross_fortnight - swt,
    }
```

**SWT Database Schema:**

```sql
CREATE TABLE employee (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT REFERENCES auth_user(id),
    staff_profile_id INT REFERENCES staff_profile(id),
    irc_tin         VARCHAR(20),                   -- Employee TIN
    tax_status      ENUM('resident','non_resident') DEFAULT 'resident',
    pay_frequency   ENUM('fortnightly','monthly') DEFAULT 'fortnightly',
    base_salary     DECIMAL(12,2),
    bank_account    VARCHAR(50),
    bsp_branch      VARCHAR(50),
    start_date      DATE,
    end_date        DATE,
    is_active       BOOL DEFAULT TRUE
);

CREATE TABLE payroll_run (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    pay_period_start DATE NOT NULL,
    pay_period_end  DATE NOT NULL,
    pay_date        DATE NOT NULL,
    period_number   INT,                           -- 1–26 for fortnight
    status          ENUM('draft','approved','paid') DEFAULT 'draft',
    total_gross     DECIMAL(14,2) DEFAULT 0.00,
    total_swt       DECIMAL(14,2) DEFAULT 0.00,
    total_net       DECIMAL(14,2) DEFAULT 0.00,
    created_by_id   INT REFERENCES auth_user(id),
    approved_by_id  INT REFERENCES auth_user(id),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE payroll_line (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    payroll_run_id  INT REFERENCES payroll_run(id),
    employee_id     INT REFERENCES employee(id),
    gross_wages     DECIMAL(12,2) NOT NULL,
    housing_benefit DECIMAL(12,2) DEFAULT 0.00,
    vehicle_benefit DECIMAL(12,2) DEFAULT 0.00,
    other_benefits  DECIMAL(12,2) DEFAULT 0.00,
    total_taxable   DECIMAL(12,2),
    swt_deducted    DECIMAL(12,2),
    net_pay         DECIMAL(12,2),
    is_resident     BOOL DEFAULT TRUE,
    notes           TEXT
);

-- Monthly SWT remittance to IRC
CREATE TABLE swt_remittance (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    remittance_month VARCHAR(7) NOT NULL,          -- '2025-01'
    due_date        DATE NOT NULL,                 -- 7th of following month
    period_start    DATE NOT NULL,
    period_end      DATE NOT NULL,
    total_gross_wages DECIMAL(14,2) DEFAULT 0.00,
    total_swt_withheld DECIMAL(14,2) DEFAULT 0.00,
    employee_count  INT DEFAULT 0,
    status          ENUM('draft','filed','paid') DEFAULT 'draft',
    filed_date      DATE,
    paid_date       DATE,
    irc_reference   VARCHAR(50),
    journal_entry_id INT REFERENCES journal_entry(id),
    notes           TEXT
);

-- Employee SWT Summary (annual, for employee records)
CREATE TABLE swt_annual_summary (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    employee_id     INT REFERENCES employee(id),
    tax_year        INT NOT NULL,
    total_gross     DECIMAL(14,2),
    total_swt       DECIMAL(14,2),
    total_net       DECIMAL(14,2)
);
```

**SWT Automated Remittance Generation:**

```python
# apps/irc_tax/services/swt_service.py

def generate_swt_remittance(year: int, month: int) -> SWTRemittance:
    """
    Aggregates all payroll runs for the month and creates the
    monthly SWT remittance record due to IRC by 7th of following month.
    """
    from datetime import date
    import calendar

    period_start = date(year, month, 1)
    period_end = date(year, month, calendar.monthrange(year, month)[1])
    
    if month == 12:
        due_date = date(year + 1, 1, 7)
    else:
        due_date = date(year, month + 1, 7)

    runs = PayrollRun.objects.filter(
        status='paid',
        pay_period_start__gte=period_start,
        pay_period_end__lte=period_end,
    )

    totals = runs.aggregate(
        gross=Sum('total_gross'),
        swt=Sum('total_swt'),
        count=Count('payrollline__employee', distinct=True),
    )

    remittance, _ = SWTRemittance.objects.update_or_create(
        remittance_month=f"{year:04d}-{month:02d}",
        defaults={
            'due_date': due_date,
            'period_start': period_start,
            'period_end': period_end,
            'total_gross_wages': totals['gross'] or 0,
            'total_swt_withheld': totals['swt'] or 0,
            'employee_count': totals['count'] or 0,
            'status': 'draft',
        }
    )

    # Auto-post journal entry
    post_journal('swt_remittance', {'remittance': remittance})

    return remittance
```

**SWT Journal Posting Rule:**
```python
# On payroll payment:
#    DR  Wages Expense           (gross wages)
#    CR  SWT Payable             (tax withheld)
#    CR  Bank / Cash             (net pay to employee)

# On SWT remittance to IRC:
#    DR  SWT Payable
#    CR  Bank                    (payment to IRC)
```

---

#### 5.7.3 Corporate Income Tax (CIT) Module

**IRC Rules Applied:**
- Resident companies in PNG are assessed CIT at 30% on trading profits and other non-exempt income. Non-resident companies are taxed at 48%.
- Fiscal year: 1 January – 31 December. CIT return due 30 April of following year.
- Provisional (instalment) tax paid quarterly based on prior year liability.

```sql
CREATE TABLE cit_return (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    tax_year        INT NOT NULL UNIQUE,           -- 2025
    due_date        DATE NOT NULL,                 -- 30 April following year
    status          ENUM('draft','finalised','filed') DEFAULT 'draft',

    -- Income
    total_revenue           DECIMAL(16,2) DEFAULT 0.00,
    exempt_income           DECIMAL(16,2) DEFAULT 0.00,
    assessable_income       DECIMAL(16,2) DEFAULT 0.00,

    -- Deductions
    cogs                    DECIMAL(16,2) DEFAULT 0.00,
    operating_expenses      DECIMAL(16,2) DEFAULT 0.00,
    depreciation            DECIMAL(16,2) DEFAULT 0.00,
    interest_expense        DECIMAL(16,2) DEFAULT 0.00,
    other_deductions        DECIMAL(16,2) DEFAULT 0.00,
    total_deductions        DECIMAL(16,2) DEFAULT 0.00,

    -- Tax Calculation
    taxable_income          DECIMAL(16,2) DEFAULT 0.00,
    cit_rate                DECIMAL(5,2) DEFAULT 30.00,
    gross_cit               DECIMAL(16,2) DEFAULT 0.00,
    provisional_tax_paid    DECIMAL(16,2) DEFAULT 0.00,
    swt_credits             DECIMAL(16,2) DEFAULT 0.00,
    net_cit_payable         DECIMAL(16,2) DEFAULT 0.00,

    filed_date              DATE,
    irc_reference           VARCHAR(50),
    notes                   TEXT
);

-- Quarterly provisional tax instalments
CREATE TABLE provisional_tax_instalment (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    tax_year        INT NOT NULL,
    quarter         INT NOT NULL,                  -- 1=Mar, 2=Jun, 3=Sep, 4=Dec
    due_date        DATE NOT NULL,
    estimated_amount DECIMAL(14,2),
    amount_paid     DECIMAL(14,2) DEFAULT 0.00,
    paid_date       DATE,
    status          ENUM('pending','paid','overdue') DEFAULT 'pending',
    journal_entry_id INT REFERENCES journal_entry(id)
);
```

**CIT Auto-Calculation from Accounting Data:**

```python
# apps/irc_tax/services/cit_service.py

def generate_cit_return(tax_year: int) -> CITReturn:
    """
    Builds CIT return from the accounting engine's P&L data.
    All figures pulled directly from posted journal entries.
    """
    from apps.accounting.reports import generate_pl
    from datetime import date

    pl = generate_pl(
        start=date(tax_year, 1, 1),
        end=date(tax_year, 12, 31),
    )

    total_revenue = pl['total_revenue']
    total_cogs = pl['total_cogs']
    total_expenses = pl['total_expenses']
    depreciation = pl['depreciation']

    assessable_income = total_revenue           # less exempt income if applicable
    total_deductions = total_cogs + total_expenses
    taxable_income = max(assessable_income - total_deductions, 0)
    gross_cit = taxable_income * Decimal('0.30')

    provisional_paid = ProvisionalTaxInstalment.objects.filter(
        tax_year=tax_year, status='paid'
    ).aggregate(s=Sum('amount_paid'))['s'] or 0

    net_cit = max(gross_cit - provisional_paid, 0)

    cit, _ = CITReturn.objects.update_or_create(
        tax_year=tax_year,
        defaults={
            'due_date': date(tax_year + 1, 4, 30),
            'total_revenue': total_revenue,
            'assessable_income': assessable_income,
            'cogs': total_cogs,
            'operating_expenses': total_expenses,
            'depreciation': depreciation,
            'total_deductions': total_deductions,
            'taxable_income': taxable_income,
            'gross_cit': gross_cit,
            'provisional_tax_paid': provisional_paid,
            'net_cit_payable': net_cit,
        }
    )
    return cit


def create_provisional_instalments(tax_year: int, prior_year_cit: Decimal):
    """
    Creates 4 quarterly provisional tax instalment records.
    Each instalment = 25% of prior year CIT.
    Due dates: 31 Mar, 30 Jun, 30 Sep, 31 Dec of current year.
    """
    from datetime import date
    quarters = [
        (1, date(tax_year, 3, 31)),
        (2, date(tax_year, 6, 30)),
        (3, date(tax_year, 9, 30)),
        (4, date(tax_year, 12, 31)),
    ]
    instalment_amount = (prior_year_cit / 4).quantize(Decimal('0.01'))
    
    for quarter, due_date in quarters:
        ProvisionalTaxInstalment.objects.get_or_create(
            tax_year=tax_year,
            quarter=quarter,
            defaults={
                'due_date': due_date,
                'estimated_amount': instalment_amount,
                'status': 'pending',
            }
        )
```

---

#### 5.7.4 Withholding Tax (WHT) Module

**IRC Rules Applied:**
- A non-resident's PNG-sourced passive income — including dividends, interest, and royalties — may be subject to withholding tax. The payer must withhold the relevant amount and remit to IRC.
- Resident dividend WHT: 17% | Non-resident dividend WHT: 15%
- Interest WHT: 15% | Royalty WHT: 10%
- Remittance due: 7th of following month (same as SWT)

```sql
CREATE TABLE withholding_tax_transaction (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    wht_type        ENUM('dividend','interest','royalty','management_fee') NOT NULL,
    payment_date    DATE NOT NULL,
    payee_name      VARCHAR(150) NOT NULL,
    payee_tin       VARCHAR(20),
    payee_residence ENUM('resident','non_resident') DEFAULT 'resident',
    gross_amount    DECIMAL(14,2) NOT NULL,
    wht_rate        DECIMAL(5,2) NOT NULL,
    wht_amount      DECIMAL(14,2) NOT NULL,
    net_paid        DECIMAL(14,2) NOT NULL,
    remitted_to_irc BOOL DEFAULT FALSE,
    remittance_date DATE,
    journal_entry_id INT REFERENCES journal_entry(id),
    notes           TEXT
);
```

---

#### 5.7.5 Tax Compliance Dashboard

**Views / Pages in `apps/irc_tax`:**

- **Tax Calendar** — visual calendar showing all upcoming IRC due dates with traffic-light status (green=filed, amber=due soon, red=overdue)
- **GST Return Wizard** — step-through form: review auto-calculated figures → adjust if needed → finalise → generate IRC-format PDF
- **SWT Remittance Form** — monthly summary per employee → approve → generate payment advice
- **CIT Return Dashboard** — full year P&L → taxable income → CIT calculation → provisional schedule
- **WHT Register** — log of all withholding tax transactions
- **Tax Obligations Summary** — single-screen overview of all outstanding and upcoming tax liabilities

**Tax Calendar Data Model:**

```python
# apps/irc_tax/utils.py

def get_upcoming_tax_deadlines(months_ahead: int = 3) -> list[dict]:
    """
    Returns all upcoming IRC tax deadlines within the next N months.
    Used to populate the compliance dashboard calendar and send alerts.
    """
    from datetime import date, timedelta
    import calendar
    
    today = date.today()
    deadlines = []
    
    for offset in range(months_ahead + 1):
        year = today.year + (today.month + offset - 1) // 12
        month = (today.month + offset - 1) % 12 + 1
        _, last_day = calendar.monthrange(year, month)
        
        # GST due 21st of following month (for prior month's transactions)
        if month == 12:
            gst_year, gst_month = year + 1, 1
        else:
            gst_year, gst_month = year, month + 1
        deadlines.append({
            'type': 'GST',
            'description': f"GST Return — {date(year, month, 1).strftime('%B %Y')}",
            'due_date': date(gst_year, gst_month, 21),
            'period': f"{year:04d}-{month:02d}",
            'colour': 'blue',
        })
        
        # SWT due 7th of following month
        if month == 12:
            swt_year, swt_month = year + 1, 1
        else:
            swt_year, swt_month = year, month + 1
        deadlines.append({
            'type': 'SWT',
            'description': f"SWT Remittance — {date(year, month, 1).strftime('%B %Y')}",
            'due_date': date(swt_year, swt_month, 7),
            'period': f"{year:04d}-{month:02d}",
            'colour': 'orange',
        })
    
    # Add quarterly provisional tax dates
    current_year = today.year
    for quarter, due in [
        (1, date(current_year, 3, 31)),
        (2, date(current_year, 6, 30)),
        (3, date(current_year, 9, 30)),
        (4, date(current_year, 12, 31)),
    ]:
        if due >= today:
            deadlines.append({
                'type': 'CIT_PROVISIONAL',
                'description': f"Provisional Tax Q{quarter} — {current_year}",
                'due_date': due,
                'period': f"{current_year}-Q{quarter}",
                'colour': 'red',
            })
    
    # Annual CIT return
    cit_due = date(today.year, 4, 30)
    if cit_due >= today:
        deadlines.append({
            'type': 'CIT_ANNUAL',
            'description': f"CIT Annual Return — FY{today.year - 1}",
            'due_date': cit_due,
            'period': str(today.year - 1),
            'colour': 'purple',
        })
    
    return sorted(deadlines, key=lambda x: x['due_date'])
```

---

#### 5.7.6 Automated Alerts & Celery Tasks

```python
# apps/irc_tax/tasks.py  (Celery tasks)

from celery import shared_task
from datetime import date, timedelta
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def auto_generate_monthly_returns():
    """
    Runs on 1st of every month (midnight).
    Auto-generates GST return and SWT remittance for the prior month.
    """
    today = date.today()
    if today.month == 1:
        year, month = today.year - 1, 12
    else:
        year, month = today.year, today.month - 1
    
    from apps.irc_tax.services.gst_service import generate_gst_return
    from apps.irc_tax.services.swt_service import generate_swt_remittance
    
    gst = generate_gst_return(year, month)
    swt = generate_swt_remittance(year, month)
    
    # Notify accountant / manager
    send_tax_deadline_alert(gst, swt)


@shared_task
def check_tax_deadline_alerts():
    """
    Runs daily. Sends alerts when tax deadlines are within 7 days or overdue.
    """
    deadlines = get_upcoming_tax_deadlines(months_ahead=1)
    today = date.today()
    alert_email = settings.HARHURUM_CONFIG.get('TAX_ALERT_EMAIL', '')
    
    for dl in deadlines:
        days_until = (dl['due_date'] - today).days
        if days_until <= 7:
            status = 'OVERDUE' if days_until < 0 else f"DUE IN {days_until} DAYS"
            send_mail(
                subject=f"[Harhurum Tax Alert] {dl['type']} {status} — {dl['description']}",
                message=f"""
Tax Compliance Alert

{dl['description']}
Due Date: {dl['due_date'].strftime('%d %B %Y')}
Status: {status}

Please log into Harhurum POS to review and file this return.
IRC Portal: https://irc.gov.pg/
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[alert_email],
                fail_silently=True,
            )


# Celery Beat Schedule (add to config/settings/base.py)
CELERY_BEAT_SCHEDULE = {
    'auto-generate-monthly-returns': {
        'task': 'apps.irc_tax.tasks.auto_generate_monthly_returns',
        'schedule': crontab(hour=0, minute=5, day_of_month=1),  # 1st of month
    },
    'check-tax-deadline-alerts': {
        'task': 'apps.irc_tax.tasks.check_tax_deadline_alerts',
        'schedule': crontab(hour=8, minute=0),  # Daily 8am
    },
}
```

---

#### 5.7.7 IRC Tax App Structure

```
apps/irc_tax/
├── __init__.py
├── models.py           # GSTReturn, GSTReturnLine, SWTRemittance, PayrollRun,
│                       # PayrollLine, Employee, CITReturn, ProvisionalTaxInstalment,
│                       # WithholdingTaxTransaction
├── constants.py        # GST_SUPPLY_TYPES, SWT brackets
├── swt_tables.py       # calculate_swt_fortnightly(), SWT bracket tables
├── tasks.py            # Celery: auto-generate returns, deadline alerts
├── urls.py
├── views.py            # All IRC tax views
├── forms.py
├── serializers.py
├── admin.py
├── services/
│   ├── gst_service.py      # generate_gst_return(), output/input tax aggregation
│   ├── swt_service.py      # generate_swt_remittance(), payroll processing
│   ├── cit_service.py      # generate_cit_return(), provisional instalments
│   └── wht_service.py      # withholding tax recording
├── reports/
│   ├── gst_return_pdf.py   # WeasyPrint → IRC GST Return format PDF
│   ├── swt_return_pdf.py   # SWT monthly remittance PDF
│   └── cit_return_pdf.py   # CIT annual return PDF
└── templates/
    └── irc_tax/
        ├── dashboard.html        # Tax compliance dashboard
        ├── tax_calendar.html     # Visual deadline calendar
        ├── gst_return_detail.html
        ├── gst_return_list.html
        ├── swt_remittance_detail.html
        ├── swt_remittance_list.html
        ├── payroll_run.html
        ├── cit_return.html
        ├── wht_register.html
        └── print/
            ├── gst_return_irc.html    # IRC-format print template
            └── swt_remittance_irc.html
```

---

#### 5.7.8 Additional COA Accounts for Tax Compliance

Add these to the Chart of Accounts (Section 5.6):

| Code | Account Name | Type | Notes |
|---|---|---|---|
| 2100 | GST Output Tax Payable | Liability | GST collected on sales |
| 2110 | GST Input Tax Receivable | Asset | GST paid on purchases |
| 2120 | GST Clearing | Liability | Net GST payable to IRC |
| 2200 | SWT Payable | Liability | Withheld from staff wages |
| 2210 | Provisional Tax Payable | Liability | CIT instalment due |
| 2220 | CIT Payable | Liability | Final CIT owing |
| 2230 | Withholding Tax Payable | Liability | WHT on dividends/interest |
| 6010 | Wages — Café | Expense | |
| 6020 | Wages — Restaurant | Expense | |
| 6030 | Wages — Tailoring | Expense | |
| 6040 | Wages — Warehouse | Expense | |
| 6050 | Wages — Admin | Expense | |
| 6060 | Superannuation Expense | Expense | Employer super contributions |

---

#### 5.7.9 IRC Tax API Endpoints

```
# GST
GET    /api/v1/tax/gst/                          # List all GST returns
POST   /api/v1/tax/gst/generate/                 # Trigger auto-generation for period
GET    /api/v1/tax/gst/{period}/                 # Detail (e.g. 2025-01)
PATCH  /api/v1/tax/gst/{period}/finalise/        # Lock return
GET    /api/v1/tax/gst/{period}/pdf/             # Download IRC-format PDF
GET    /api/v1/tax/gst/{period}/lines/           # Detailed transaction lines

# SWT
GET    /api/v1/tax/swt/                          # List remittances
POST   /api/v1/tax/swt/generate/                 # Generate monthly remittance
GET    /api/v1/tax/swt/{period}/                 # Detail
GET    /api/v1/tax/swt/{period}/pdf/             # Download PDF

# Payroll
GET    /api/v1/payroll/runs/                     # List payroll runs
POST   /api/v1/payroll/runs/                     # Create payroll run
POST   /api/v1/payroll/runs/{id}/approve/        # Approve
POST   /api/v1/payroll/runs/{id}/pay/            # Mark as paid → journal entry
GET    /api/v1/payroll/swt-calculator/           # Fortnightly SWT calc (params: gross, resident)

# CIT
GET    /api/v1/tax/cit/{year}/                   # CIT return for year
POST   /api/v1/tax/cit/{year}/generate/
GET    /api/v1/tax/cit/{year}/pdf/
GET    /api/v1/tax/cit/provisional/              # Instalment schedule

# WHT
GET    /api/v1/tax/wht/                          # WHT register
POST   /api/v1/tax/wht/                          # Record WHT transaction

# Calendar
GET    /api/v1/tax/calendar/                     # All upcoming deadlines
GET    /api/v1/tax/obligations/                  # Outstanding tax liabilities summary
```

---

### 5.8 Reporting & Dashboard (`apps/reporting`)

**Dashboard KPIs (home screen):**
- Today's total sales (all units)
- Sales by business unit (donut chart)
- Hourly sales chart (line)
- Top 10 selling items (bar chart)
- Low stock alerts count
- Open tailoring orders count
- Outstanding AR total
- Outstanding AP total
- Cash position (bank + cash)

**Reports (all exportable to PDF + Excel):**
- Daily Sales Summary (per terminal, per unit)
- Z-Report (end-of-day per cash session)
- Sales by Product / Category
- Sales by Payment Method
- Stock Valuation Report
- Purchase History
- Supplier Statement
- Customer Statement
- Tailoring Order Report
- GST Summary Report
- Profit & Loss
- Balance Sheet
- Cash Flow

---

### 5.9 User & Role Management (`apps/accounts`)

**Roles & Permissions Matrix:**

| Feature | Superadmin | Manager | Accountant | Cashier | Waiter | Barista | Tailor | Warehouse |
|---|---|---|---|---|---|---|---|---|
| Dashboard | Full | Full | Finance only | Own unit | Own unit | Own unit | Own unit | Stock only |
| Products CRUD | ✅ | ✅ | View | View | View | View | View | ✅ |
| Stock Adjust | ✅ | ✅ | — | — | — | — | — | ✅ |
| PO / GRN | ✅ | ✅ | View | — | — | — | — | ✅ |
| POS Sale | ✅ | ✅ | — | ✅ | ✅ | ✅ | — | — |
| Void Sale | ✅ | ✅ | — | — | — | — | — | — |
| Tailoring | ✅ | ✅ | View | — | — | — | ✅ | — |
| Accounting | ✅ | View | ✅ | — | — | — | — | — |
| User Mgmt | ✅ | — | — | — | — | — | — | — |
| Reports | ✅ | ✅ | ✅ | Basic | — | — | Basic | Basic |

---

## 6. API ENDPOINTS

All endpoints prefixed with `/api/v1/`

### Authentication
```
POST   /api/v1/auth/token/          # JWT login
POST   /api/v1/auth/token/refresh/  # Refresh token
POST   /api/v1/auth/pin-login/      # Quick PIN login for POS
```

### Products
```
GET    /api/v1/products/            # List (supports ?search=, ?category=, ?barcode=)
POST   /api/v1/products/            # Create
GET    /api/v1/products/{id}/       # Detail
PUT    /api/v1/products/{id}/       # Update
GET    /api/v1/products/search/?barcode={code}  # Barcode lookup
GET    /api/v1/products/low-stock/  # Reorder alerts
```

### POS / Sales
```
POST   /api/v1/pos/orders/          # Create new order
GET    /api/v1/pos/orders/{id}/     # Get order
PATCH  /api/v1/pos/orders/{id}/     # Update order (add lines)
POST   /api/v1/pos/orders/{id}/pay/ # Process payment
POST   /api/v1/pos/orders/{id}/void/ # Void order
POST   /api/v1/pos/sync/            # Bulk offline sync
GET    /api/v1/pos/sessions/current/ # Current cash session
POST   /api/v1/pos/sessions/open/   # Open session
POST   /api/v1/pos/sessions/close/  # Close session
```

### Restaurant
```
GET    /api/v1/restaurant/tables/   # All tables + status
POST   /api/v1/restaurant/tables/{id}/open/    # Open table
POST   /api/v1/restaurant/tables/{id}/close/   # Close / pay table
GET    /api/v1/kitchen/tickets/     # Active kitchen tickets (WebSocket preferred)
PATCH  /api/v1/kitchen/tickets/{id}/ # Update ticket status
```

### Tailoring
```
GET    /api/v1/tailoring/orders/    # List
POST   /api/v1/tailoring/orders/    # Create
GET    /api/v1/tailoring/orders/{id}/
PATCH  /api/v1/tailoring/orders/{id}/stage/ # Update stage
POST   /api/v1/tailoring/orders/{id}/collect/ # Final payment
```

### Inventory
```
GET    /api/v1/stock/               # Stock on hand
POST   /api/v1/stock/adjust/        # Manual adjustment
POST   /api/v1/stock/transfer/      # Inter-warehouse transfer
POST   /api/v1/stock/stocktake/     # Stocktake submission
```

### Procurement
```
GET    /api/v1/purchase-orders/
POST   /api/v1/purchase-orders/
POST   /api/v1/purchase-orders/{id}/send/
POST   /api/v1/purchase-orders/{id}/receive/  # Create GRN
GET    /api/v1/suppliers/
GET    /api/v1/suppliers/{id}/ledger/
```

### Accounting
```
GET    /api/v1/accounts/            # Chart of accounts
GET    /api/v1/journal-entries/     # Journal list
POST   /api/v1/journal-entries/     # Manual journal
GET    /api/v1/reports/pl/          # P&L
GET    /api/v1/reports/balance-sheet/
GET    /api/v1/reports/trial-balance/
GET    /api/v1/reports/gst/
GET    /api/v1/reports/ar-aging/
GET    /api/v1/reports/ap-aging/
```

---

## 7. UI/UX GUIDELINES

### Material Design Implementation

**Base Template:** MDB5 (Material Design for Bootstrap 5) free tier  
**Color Palette:**
```css
:root {
    --primary:      #1565C0;   /* Deep Blue */
    --secondary:    #FF6F00;   /* Amber — brand accent */
    --success:      #2E7D32;
    --danger:       #C62828;
    --background:   #F5F5F5;
    --surface:      #FFFFFF;
    --on-primary:   #FFFFFF;
    --on-secondary: #000000;
}
```

**Navigation:** Left sidebar with collapsible sections per business unit  
**POS Terminal:** Full-screen mode, 44px minimum touch targets, no scroll on main order grid

### Key UI Screens

**1. POS Terminal Layout:**
```
┌──────────────────────────────────────────────────────┐
│  [Business Unit]     [Cashier]     [Session: OPEN]   │
├────────────────────────────┬─────────────────────────┤
│  CATEGORIES (scrollable)   │  ORDER LINES            │
│  ┌──────┐ ┌──────┐        │  Item 1    x2   K12.00  │
│  │Coffee│ │ Food │        │  Item 2    x1    K5.50  │
│  └──────┘ └──────┘        │                         │
│                            │  ─────────────────────  │
│  PRODUCT GRID              │  Subtotal      K17.50  │
│  ┌──────┐ ┌──────┐        │  GST (10%)      K1.75  │
│  │Latte │ │Flat  │        │  TOTAL         K19.25  │
│  │K5.50 │ │White │        │                         │
│  └──────┘ └──────┘        │  [CASH] [CARD] [ACCT]  │
│                            │         [PAY]           │
└────────────────────────────┴─────────────────────────┘
```

**2. Dashboard:**
- Top KPI cards (revenue today, orders, stock alerts)
- Sales chart (Chart.js)
- Business unit breakdown
- Recent transactions feed

**3. Kitchen Display:**
- Dark background, large text
- Colour-coded by age (green → yellow → red)
- Tap to acknowledge / complete

---

## 8. FILE & FOLDER STRUCTURE

```
harhurum/
├── config/
│   ├── settings/
│   │   ├── base.py          # Common settings
│   │   ├── development.py   # DEBUG=True, SQLite option
│   │   └── production.py    # DEBUG=False, MySQL, Redis
│   ├── urls.py
│   ├── asgi.py              # Channels ASGI
│   └── wsgi.py
│
├── apps/
│   ├── core/
│   │   ├── models.py        # TimeStampedModel, SoftDeleteModel base classes
│   │   ├── utils.py         # Number generators (PO-2024-0001), money helpers
│   │   ├── mixins.py        # LoginRequiredMixin, RoleRequiredMixin
│   │   └── templatetags/    # Custom template filters
│   │
│   ├── accounts/
│   │   ├── models.py        # StaffProfile
│   │   ├── views.py         # Login, logout, user CRUD
│   │   ├── forms.py
│   │   ├── serializers.py   # DRF
│   │   └── permissions.py   # Custom DRF permissions
│   │
│   ├── products/
│   │   ├── models.py        # Category, UOM, Product, ProductVariant, BOMItem
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── forms.py
│   │   ├── admin.py
│   │   └── signals.py       # Auto-update cost on GRN
│   │
│   ├── warehouse/
│   │   ├── models.py        # Warehouse, StockLocation, StockMovement
│   │   ├── services.py      # adjust_stock(), transfer_stock(), record_movement()
│   │   ├── views.py
│   │   └── serializers.py
│   │
│   ├── procurement/
│   │   ├── models.py        # PurchaseOrder, GRN, SupplierInvoice
│   │   ├── services.py      # receive_grn() → updates stock + journals
│   │   ├── views.py
│   │   └── serializers.py
│   │
│   ├── pos/
│   │   ├── models.py        # SaleOrder, SaleOrderLine, Payment, CashSession
│   │   ├── services.py      # complete_sale() → stock deduction + journals
│   │   ├── views.py         # Terminal view, sync endpoint
│   │   └── serializers.py
│   │
│   ├── cafe/
│   │   ├── models.py        # ModifierGroup, Modifier (inherits pos models)
│   │   └── views.py
│   │
│   ├── restaurant/
│   │   ├── models.py        # RestaurantTable, KitchenTicket
│   │   ├── consumers.py     # Django Channels WebSocket
│   │   ├── routing.py
│   │   └── views.py
│   │
│   ├── tailoring/
│   │   ├── models.py        # TailoringOrder, TailoringStageLog
│   │   ├── services.py      # confirm_order(), collect_order()
│   │   └── views.py
│   │
│   ├── accounting/
│   │   ├── models.py        # Account, FiscalYear, JournalEntry, JournalLine, etc.
│   │   ├── services.py      # post_journal(), auto_post_sale(), etc.
│   │   ├── journal_rules.py # POSTING_RULES dict
│   │   ├── reports.py       # P&L, Balance Sheet, Trial Balance generators
│   │   └── views.py
│   │
│   ├── irc_tax/
│   │   ├── models.py        # GSTReturn, SWTRemittance, PayrollRun, CITReturn, etc.
│   │   ├── constants.py     # GST supply types, SWT bracket tables
│   │   ├── swt_tables.py    # calculate_swt_fortnightly()
│   │   ├── tasks.py         # Celery: auto-generate returns, deadline alerts
│   │   ├── views.py         # Tax dashboard, return CRUD
│   │   ├── urls.py
│   │   ├── services/
│   │   │   ├── gst_service.py
│   │   │   ├── swt_service.py
│   │   │   ├── cit_service.py
│   │   │   └── wht_service.py
│   │   └── reports/
│   │       ├── gst_return_pdf.py
│   │       ├── swt_return_pdf.py
│   │       └── cit_return_pdf.py
│   │
│   ├── reporting/
│   │   ├── views.py         # Dashboard, report views
│   │   ├── exports.py       # PDF + Excel export helpers
│   │   └── charts.py        # Chart.js data builders
│   │
│   └── api/
│       ├── urls.py          # API URL routing
│       └── router.py        # DRF router
│
├── templates/
│   ├── base.html
│   ├── base_pos.html        # POS-specific (no sidebar, full screen)
│   ├── base_kitchen.html    # KDS (dark theme)
│   ├── components/
│   │   ├── navbar.html
│   │   ├── sidebar.html
│   │   ├── alerts.html
│   │   └── pagination.html
│   ├── accounts/
│   ├── products/
│   ├── warehouse/
│   ├── procurement/
│   ├── pos/
│   │   ├── terminal.html    # Main POS screen
│   │   ├── receipt.html     # Printable receipt
│   │   └── z_report.html
│   ├── restaurant/
│   │   ├── floor_plan.html
│   │   └── kitchen_display.html
│   ├── tailoring/
│   ├── accounting/
│   └── reporting/
│       └── dashboard.html
│
├── static/
│   ├── css/
│   │   ├── main.css         # Custom overrides
│   │   └── pos.css          # POS terminal styles
│   ├── js/
│   │   ├── pos/
│   │   │   ├── terminal.js  # POS main logic
│   │   │   ├── sw.js        # Service Worker
│   │   │   └── sync.js      # Offline sync
│   │   ├── kitchen/
│   │   │   └── display.js   # WebSocket + UI updates
│   │   └── charts/
│   │       └── dashboard.js # Chart.js charts
│   └── img/
│
├── requirements.txt
├── manage.py
├── .env.example
└── docker-compose.yml
```

---

## 9. SETTINGS & CONFIGURATION

### `requirements.txt`
```
Django==4.2.16
mysqlclient==2.2.4
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.1
django-channels==4.1.0
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

### `config/settings/base.py` (key sections)
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    'channels',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'import_export',
    'simple_history',
    # Local apps
    'apps.core',
    'apps.accounts',
    'apps.customers',
    'apps.suppliers',
    'apps.products',
    'apps.warehouse',
    'apps.procurement',
    'apps.pos',
    'apps.cafe',
    'apps.restaurant',
    'apps.tailoring',
    'apps.accounting',
    'apps.irc_tax',
    'apps.reporting',
    'apps.api',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='3306'),
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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

# Business configuration
HARHURUM_CONFIG = {
    'COMPANY_NAME': 'Harhurum',
    'COMPANY_WEBSITE': 'harhurum.com.pg',
    'DEFAULT_CURRENCY': 'PGK',
    'DEFAULT_TAX_RATE': 10.0,
    'TAX_INCLUSIVE': True,
    'RECEIPT_FOOTER': 'Thank you for your business!',
    'LOW_STOCK_NOTIFY_EMAIL': env('MANAGER_EMAIL', default=''),
    # IRC Tax Compliance
    'IRC_TIN': env('HARHURUM_TIN', default=''),           # Taxpayer ID Number
    'IRC_GST_REG_NO': env('HARHURUM_GST_REG', default=''), # GST Registration Number
    'TAX_ALERT_EMAIL': env('TAX_ALERT_EMAIL', default=''),  # Who receives deadline alerts
    'CIT_RATE': 30.0,                                      # Corporate income tax %
    'SWT_TAX_FREE_THRESHOLD': 20_000.0,                    # Annual K20,000
    'FISCAL_YEAR_START_MONTH': 1,                          # January
}
```

---

## 10. THIRD-PARTY INTEGRATIONS

### Payment Terminals
- **EFTPOS:** Integration via bank-provided SDK (BSP Papua New Guinea / Westpac PNG)
- Payment recorded manually if no SDK → cashier enters reference number
- Future: direct API integration if bank supports it

### Email / Notifications
- Django email (SMTP) for low-stock alerts, PO emails to suppliers, AR invoice emails
- Optional: Twilio SMS for order-ready notifications (tailoring)

### Label Printing
- ZPL format for Zebra label printers (barcode labels on received stock)
- python-barcode generates barcodes for new products

### Data Import
- Bulk product import via CSV/Excel (django-import-export)
- Customer import
- Opening stock balance import

---

## 11. SECURITY

### Authentication
- Session auth for Django admin + web UI
- JWT for API / POS terminals
- PIN login for quick POS access (short-lived token, terminal-scoped)
- Session timeout: 8 hours (configurable)

### Authorization
- Django permissions + custom `RoleRequiredMixin`
- DRF custom permission classes per endpoint
- Object-level permissions: users only see their business unit data

### Data Protection
- All passwords hashed (Django default: PBKDF2)
- HTTPS enforced in production (HSTS)
- CSRF protection on all forms
- SQL injection prevention via ORM (no raw queries except in reports — parameterized)
- Audit trail: `django-simple-history` on all financial models
- DB user has minimum required privileges (no DROP/CREATE in production)

### Audit Trail
- All model changes tracked via `simple_history`
- Journal entries are **immutable** — corrections via reversing entry only
- Cash session discrepancies auto-flagged and emailed to manager

---

## 12. DEPLOYMENT

### Production Server (Linux / Ubuntu 22.04)
```
Nginx  →  Gunicorn (Django WSGI)
       →  Daphne (Django ASGI / Channels for WebSocket)
MySQL 8 (local or RDS)
Redis (Celery broker + cache + Channels)
```

### `docker-compose.yml` (development)
```yaml
version: '3.9'
services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes: ['.:/app']
    ports: ['8000:8000']
    depends_on: [db, redis]
    env_file: .env

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: harhurum_pos
    volumes: ['mysql_data:/var/lib/mysql']
    ports: ['3306:3306']

  redis:
    image: redis:7-alpine
    ports: ['6379:6379']

  celery:
    build: .
    command: celery -A config worker -l info
    depends_on: [db, redis]
    env_file: .env

volumes:
  mysql_data:
```

### Initial Setup Commands
```bash
python manage.py migrate
python manage.py setup_accounts          # Creates chart of accounts
python manage.py setup_business_units    # Creates 4 business units
python manage.py setup_tax_rates         # Creates GST 10%
python manage.py createsuperuser
python manage.py collectstatic
```

---

## 13. IMPLEMENTATION PHASES

### Phase 1 — Core Foundation (Weeks 1–3)
- [ ] Project scaffolding (Django project, apps, Docker)
- [ ] Database setup, all migrations
- [ ] User authentication, staff profiles, RBAC
- [ ] Business unit setup
- [ ] Product catalog (CRUD, categories, variants)
- [ ] Warehouse + stock location + stock movements
- [ ] Basic Material Design templates + sidebar nav

### Phase 2 — Procurement & Inventory (Weeks 4–5)
- [ ] Supplier management
- [ ] Purchase orders (create, send, receive)
- [ ] Goods Received Notes → stock update
- [ ] Supplier invoices (AP)
- [ ] Stock adjustments, transfers
- [ ] Low stock alerts
- [ ] Barcode label printing
- [ ] CSV import for products + opening stock

### Phase 3 — POS Terminals (Weeks 6–8)
- [ ] Café POS terminal (offline-capable)
- [ ] Modifiers / add-ons
- [ ] Cash session open/close + Z-report
- [ ] Payment processing (cash + card)
- [ ] Receipt printing
- [ ] Restaurant table floor plan
- [ ] Table order management + course sending
- [ ] Kitchen Display System (WebSocket)
- [ ] Bill split

### Phase 4 — Tailoring Module (Week 9)
- [ ] Tailoring order form + measurements
- [ ] Fabric selection + reservation
- [ ] Production Kanban board
- [ ] Deposit + balance collection
- [ ] Order card / job ticket printing

### Phase 5 — IRC Tax Compliance & Accounting Engine (Weeks 10–12)
- [ ] Chart of accounts setup (including all tax accounts)
- [ ] Fiscal year + periods
- [ ] Auto journal posting (all transaction types)
- [ ] Manual journal entry
- [ ] **GST Module** — auto-generate monthly returns from sales + purchase data
- [ ] **GST Return PDF** — IRC-format printable return (WeasyPrint)
- [ ] **SWT Module** — employee records, payroll runs, fortnightly SWT calculator
- [ ] **SWT Remittance** — monthly aggregation, journal posting, PDF
- [ ] **CIT Module** — annual return from P&L, provisional instalment schedule
- [ ] **WHT Register** — dividend/interest withholding recording
- [ ] **Tax Calendar Dashboard** — visual deadline tracker with traffic-light alerts
- [ ] **Celery tasks** — auto-generate returns on 1st of month, daily deadline alerts
- [ ] AR invoicing + aging
- [ ] AP aging + payment recording
- [ ] Bank accounts + reconciliation

### Phase 6 — Reporting & Polish (Week 12)
- [ ] Dashboard with KPIs + charts
- [ ] P&L, Balance Sheet, Trial Balance
- [ ] All reports with PDF + Excel export
- [ ] Customer management + account statements
- [ ] Role permissions fine-tuning
- [ ] Performance optimisation (query optimisation, caching)
- [ ] User acceptance testing with Harhurum staff

---

## 14. CLAUDE CODE BUILD INSTRUCTIONS

> Feed this section first when starting a new Claude Code session.

### How to Use This Blueprint with Claude Code

1. **Start with scaffolding:**
   ```
   "Using the HARHURUM_POS_BLUEPRINT.md, create the Django project structure 
   with all apps listed in Section 4. Include Docker, requirements.txt, 
   and base settings."
   ```

2. **Build module by module (Phase order):**
   ```
   "Build Phase 1 from the blueprint: models for products app (Section 3.2), 
   including Category, UOM, Product, ProductVariant, BOMItem. 
   Include migrations, admin registration, and serializers."
   ```

3. **Reference specific sections:**
   - Schema → Section 3
   - App logic → Section 5
   - API endpoints → Section 6
   - Templates → Section 7
   - Settings → Section 9

4. **Accounting engine — build last:**
   ```
   "Implement the accounting services in apps/accounting/services.py 
   using the POSTING_RULES from Section 5.6. The post_journal() function 
   should accept a rule key + context dict and create JournalEntry + 
   JournalLine records atomically."
   ```

5. **IRC Tax Module — build after accounting engine:**
   ```
   "Build the apps/irc_tax app from Section 5.7 of the blueprint.
   Start with models.py and constants.py (GST supply types, SWT brackets),
   then implement gst_service.py with generate_gst_return() that auto-aggregates
   from completed SaleOrders and SupplierInvoices. Then swt_service.py with
   payroll and SWT remittance. Use WeasyPrint for IRC-format PDF generation."
   ```

6. **SWT Calculator:**
   ```
   "Implement calculate_swt_fortnightly() from Section 5.7.2 using the
   SWT_RESIDENT_ANNUAL_BRACKETS table. Include a view at
   /api/v1/payroll/swt-calculator/ that accepts gross and is_resident params
   and returns the fortnightly SWT deduction amount."
   ```

### Critical Implementation Notes for Claude Code

- **Always use `select_related` / `prefetch_related`** on list views to prevent N+1 queries
- **Journal entries must be atomic** — wrap in `transaction.atomic()` with rollback on failure
- **Stock movements must always accompany** any stock level change — never update `qty_on_hand` directly without creating a `StockMovement` record
- **Currency:** All monetary values stored as `DECIMAL(14,2)` — never use float
- **Dates:** Always store in UTC, display in PNG time (UTC+10)
- **Sequence numbers** (PO-2024-0001 etc.) must be generated inside `transaction.atomic()` with `select_for_update()` to prevent duplicates
- **Soft delete:** Use `is_active=False` not hard DELETE for products, customers, suppliers
- **BOM deduction** must be called inside `complete_sale()` — never skip even if stock tracking is off
- **All API views** must check `business_unit` ownership before returning data

### Example: Implementing `complete_sale()`

```python
# apps/pos/services.py
from django.db import transaction
from apps.accounting.services import post_journal
from apps.warehouse.services import deduct_stock

@transaction.atomic
def complete_sale(order_id: int, payments: list[dict]) -> dict:
    """
    Finalise a sale order:
    1. Validate order status
    2. Record payments
    3. Deduct stock (including BOM components)
    4. Post accounting journals
    5. Update order status to completed
    6. Return receipt data
    """
    order = SaleOrder.objects.select_for_update().get(id=order_id)
    
    assert order.status == 'open', "Order already processed"
    
    total_paid = sum(p['amount'] for p in payments)
    assert total_paid >= order.total, "Underpayment"
    
    # 1. Record payments
    for p in payments:
        Payment.objects.create(order=order, **p)
    
    # 2. Deduct stock per line
    for line in order.lines.select_related('product').all():
        deduct_stock(line.product, line.qty, order.business_unit.main_warehouse)
    
    # 3. Post journals
    for payment in payments:
        post_journal(
            rule=f"{payment['method']}_sale",
            context={
                'order': order,
                'payment': payment,
                'revenue_account': order.business_unit.revenue_account,
            }
        )
    
    # 4. Complete order
    order.status = 'completed'
    order.completed_at = timezone.now()
    order.save()
    
    return build_receipt_data(order)
```

---

*Blueprint version 1.0 — Prepared for Harhurum.com.pg POS Implementation*  
*Stack: Django 4.2 · MySQL 8 · Materialize/MDB5 · DRF · Django Channels*  
*Replace: HikePOS + Xero → Single unified system*
