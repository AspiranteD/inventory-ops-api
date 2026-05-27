# Inventory Ops API
> **Portfolio context:** Extracted from founder-led production systems — multi-marketplace inventory, orders, and warehouse execution. **[Full portfolio](https://github.com/AspiranteD)** · [aspiranted.github.io](https://aspiranted.github.io)

Production-grade **inventory & operations domain layer** from a full-scale ERP: 6 entity models and 6 services with business rules, side effects, and aggregations — the data backbone behind a **40,000+** reference inventory across multiple marketplaces.

## Architecture

```
src/
├── models/
│   ├── item.py          # PhysicalItem with scraping auto-pause, condition validation
│   ├── sale.py          # Sale with computed amount_due, in_person/online constraints
│   ├── order.py         # Order + OrderItem with warehouse state pipeline
│   ├── incident.py      # Post-sale incidents with pending return data
│   ├── listing.py       # Marketplace listings with stat accumulation, oscillation detection
│   └── expense.py       # Expenses with recurring support, payment status constraints
└── services/
    ├── inventory_service.py  # CRUD with side effects and business validation
    ├── sale_service.py       # Sale creation marks items unavailable, return data application
    ├── dashboard_service.py  # Multi-table aggregation for stats and daily reports
    ├── search_service.py     # Cross-table global search (items, sales, orders)
    ├── batch_service.py      # Bulk warehouse location updates
    └── export_service.py     # CSV/JSON inventory export
```

## Key Technical Features

### Domain Models with Real Business Constraints

**PhysicalItem** (`src/models/item.py`)
- LPN (License Plate Number) as primary key
- CHECK constraints: non-negative prices/weights, no future dates
- Scraping auto-pause: after 5 failed attempts, `scraping_needs_manual` flag is set
- Condition-specific validation: `CON_TARA` and `PARA_PIEZAS` conditions require 50+ character descriptions
- `do_not_list` flag to exclude available items from feeds (PortalHero, eBay)

**Sale** (`src/models/sale.py`)
- Computed `amount_due = MAX(total - paid, 0)` matching PostgreSQL `GENERATED ALWAYS AS` column
- Reference consistency constraint: online sales require `listing_id` or `lpn`, in-person sales require `lpn` and cannot have `listing_id`
- Payment state machine: `mark_paid()` auto-sets `payment_received_date`

**Order** (`src/models/order.py`)
- Warehouse status pipeline: BUSCAR -> ENCONTRADO -> PREPARADO -> ESPERANDO -> CANCELAR
- Extraction retry with auto-fail after 3 consecutive failures (extraction_attempts counter)
- Overdue detection based on `due_date` vs current time

**Incident** (`src/models/incident.py`)
- 1:1 relationship with Sale (unique constraint)
- Pending return workflow: `pending_condition_id`, `pending_purchase_price`, `pending_available`
- `apply_return_data()` extracts pending fields and marks as applied (idempotent)
- `mark_not_received()` flags items buyers never returned

**Listing** (`src/models/listing.py`)
- Dual pricing: `standard` (70% of reference, aggressive decline) vs `manual` (gradual from revised price)
- Stat accumulation on product_id rotation: conversations, favorites, views carry over
- Product_id oscillation detection (A->B->A pattern from platform republishing)
- Status priority chain: sold > banned > reserved > expired > on_hold > pending > published

### Service Layer with Side Effects

**InventoryService**: Creates items with duplicate check, validates condition descriptions, manages scraping lifecycle, validates image URLs (HTTP/HTTPS format), computes availability statistics.

**SaleService**: Creating a sale marks the physical item as unavailable. Payment status updates trigger date tracking. `apply_incident_return()` propagates pending return data (condition, price, availability) from incidents back to physical items.

**DashboardService**: Multi-table aggregation for business stats: inventory availability, sales totals, financial P&L (income vs expenses with profit margin), pending orders, active listings. Daily reports with per-entity detail breakdowns.

**BatchService**: Bulk warehouse location updates with per-item error tracking. Collects `updated` vs `errors` lists with descriptive messages.

**ExportService**: Inventory export in CSV and JSON formats with sorted output and proper null handling.

## Testing

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

**152 tests** covering:
- Item model (validation, scraping lifecycle, image URL parsing)
- Sale model (amount_due computation, reference consistency, payment state)
- Order model (due date validation, overdue detection, extraction retry)
- Incident model (pending return workflow, idempotent apply, not-received marking)
- Listing model (status priority, stat accumulation, oscillation detection)
- Expense model (recurring validation, payment status constraints)
- Inventory service (CRUD, duplicate check, condition validation, scraping, image URLs)
- Sale service (availability side effect, payment status, incident return propagation)
- Dashboard service (stats aggregation, daily reports, zero-division handling)
- Search service (multi-table search, empty query, result limiting)
- Batch service (success/failure tracking, error handling, empty batches)
- Export service (CSV/JSON output, sorted, null fields, multi-item)
