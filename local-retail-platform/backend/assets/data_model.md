# Backend Data Model - Complete Overview

## Core Entities & Relationships

### 1. User Management (Django Auth + Extensions)

**Django User** (Built-in)
- Extends to either `MerchantProfile` or `CustomerProfile`
- One user can only be one type (merchant OR customer)

---

### 2. Merchants Module (B2B)

#### MerchantProfile
- **Purpose**: Extended merchant user information
- **Key Fields**: company_name, tax_id, location coordinates, DATEV integration
- **Relationships**:
  - Has ONE Subscription
  - Owns MANY Shops

#### Subscription
- **Purpose**: Manage merchant subscription tiers
- **Tiers**:
  - Free: 7.3% commission, €0/month
  - Premium: 3.1% commission, €299/month
- **Key Fields**: tier, status, billing dates
- **Business Logic**: Commission rate calculated based on tier

#### Shop
- **Purpose**: Merchant's storefront(s)
- **Key Fields**: name, delivery_radius_km, contact info
- **Relationships**:
  - Belongs to ONE Merchant
  - Has MANY Products
  - Receives MANY Orders
  - Issues MANY Digital Receipts
- **Business Rule**: Can set delivery radius (max 500km)

---

### 3. Products Module

#### Category
- **Purpose**: Hierarchical product categorization
- **Structure**: Self-referencing (parent/child)
- **Key Fields**: name, slug, parent_id
- **Example**: Electronics → Smartphones → iPhone

#### Product
- **Purpose**: Individual product listings
- **Key Fields**: 
  - Pricing: price, sale_price, cost_price
  - Inventory: stock_quantity, min_stock_level, max_stock_level
  - Dimensions: weight, length, width, height
  - Stats: view_count, sales_count
- **Relationships**:
  - Belongs to ONE Shop
  - Belongs to ONE Category
  - Has MANY Images
  - Appears in MANY OrderItems
- **Business Logic**:
  - Auto-calculates current_price (uses sale_price if available)
  - Stock status determination (in_stock, low_stock, out_of_stock)
  - Profit margin calculation

#### ProductImage
- **Purpose**: Product photo gallery
- **Key Fields**: image, is_primary, display_order
- **Business Rule**: Only ONE image can be primary per product

---

### 4. Customers Module (B2C)

#### CustomerProfile
- **Purpose**: Extended customer user information
- **Key Fields**: location coordinates, search preferences, spending stats
- **Relationships**:
  - Has MANY FavoriteShops
  - Has MANY LoyaltyTokens
  - Receives MANY DigitalReceipts
  - Places MANY Orders

#### FavoriteShop
- **Purpose**: Customer's saved shops (travel feature)
- **Business Rule**: Allows customers to access shops outside 150km radius
- **Unique Constraint**: One customer can favorite a shop only once

#### LoyaltyToken
- **Purpose**: Reward system tracking
- **Token Value**: €1 per 100€ spent
- **Transaction Types**:
  - earned: From purchases
  - spent: Redeemed on orders
  - expired: Token expiration
  - admin_adjustment: Manual adjustments
- **Key Fields**: amount, balance_after, transaction_type
- **Business Logic**: Maintains running balance

#### DigitalReceipt
- **Purpose**: Digital Kassenzettel (receipt) management
- **Key Fields**: 
  - receipt_number (unique)
  - expense_type (personal/business)
  - return_deadline
  - exported_to_datev (DATEV integration)
- **Relationships**:
  - Belongs to ONE Customer
  - Issued by ONE Shop
  - Linked to ONE Order (optional - can be in-store purchase)
- **Business Rules**:
  - Tracks return deadline
  - Auto-archives after deadline
  - Can be categorized for tax purposes

---

### 5. Orders Module

#### Order
- **Purpose**: Customer purchase records
- **Status Flow**: 
  ```
  pending → confirmed → processing → shipped → delivered
                    ↓
                cancelled/refunded
  ```
- **Key Fields**:
  - Pricing: subtotal, tax_amount, shipping_cost, discount_amount, total
  - Loyalty: tokens_used, tokens_value
  - Shipping: address fields, tracking info
  - Fulfillment: delivery or in-store pickup
- **Relationships**:
  - Belongs to ONE Customer
  - Belongs to ONE Shop
  - Contains MANY OrderItems
  - Has MANY StatusHistory records
  - Generates ONE DigitalReceipt
  - Can generate LoyaltyToken transactions

#### OrderItem
- **Purpose**: Individual items in an order
- **Key Feature**: Snapshots product data at order time
- **Fields Captured**: product_name, product_sku, unit_price
- **Business Logic**:
  - Calculates line_total (unit_price × quantity)
  - Calculates tax_amount (based on tax_rate)
- **Why Snapshot?**: Preserves historical pricing even if product is deleted/changed

#### OrderStatusHistory
- **Purpose**: Audit trail for order status changes
- **Key Fields**: status, notes, changed_by, created_at
- **Business Value**: Complete order lifecycle tracking

---

## Key Business Rules Implemented

### 1. Geographic Search (Core Feature)
- Merchants set shop location (latitude/longitude)
- Customers have default search radius (150km, max 500km)
- **Future**: PostGIS for efficient geo-queries using ST_DWithin

### 2. Inventory Management
- Low stock alerts when stock ≤ min_stock_level
- Automatic stock status calculation
- Sales count tracking per product

### 3. Pricing & Commissions
- Support for sale prices
- Merchant commission based on subscription tier
- 19% VAT calculation on orders
- Loyalty token system (€1 per €100)

### 4. Multi-Merchant Orders
- Each order belongs to ONE shop only
- Customers must place separate orders for different shops
- Each shop manages its own orders independently

### 5. Digital Receipts
- All purchases generate digital receipts
- Return period tracking
- DATEV export for business expenses
- Archive old receipts automatically

---

## Not Yet Implemented (Placeholders)

### Payments App
- Payment transaction records
- Stripe/PayPal integration tracking
- Refund management

### Notifications App
- Real-time order notifications for merchants
- Low stock alerts
- Customer order updates
- Email/Push notification management

### Analytics App
- Sales analytics per merchant
- Product performance tracking
- Customer behavior analysis
- Revenue reporting

---

## Database Indexes (Performance)

Key indexes created for:
- Product.slug (SEO-friendly URLs)
- Product.sku (inventory lookups)
- Product.shop + is_active (merchant queries)
- Order.order_number (order tracking)
- Order.customer + ordered_at (customer order history)
- Category.slug (category browsing)

---

## Foreign Key Behaviors

**CASCADE**: Delete parent → delete children
- User → MerchantProfile/CustomerProfile
- Shop → Products
- Product → ProductImages
- Order → OrderItems

**PROTECT**: Prevent deletion if referenced
- Product → OrderItems (preserve order history)

**SET_NULL**: Keep record, remove reference
- Category → Products (product stays, category removed)
- Shop → DigitalReceipts

---

## Unique Constraints

1. **MerchantProfile.tax_id** - One tax ID per merchant
2. **Product.sku** - Globally unique product identifiers
3. **Product.shop + slug** - Unique slug per shop
4. **Order.order_number** - Unique order tracking
5. **DigitalReceipt.receipt_number** - Unique receipts
6. **FavoriteShop.customer + shop** - Can't favorite same shop twice

---

## Future Enhancements Ready

1. **PostGIS Integration**: Schema supports lat/lng for geo-queries
2. **AI/ML**: Sales data ready for predictions
3. **Multi-Shop Orders**: Architecture can extend to support marketplace-wide carts
4. **Bulk Ordering**: Fields exist for collective merchant orders
5. **Advanced Analytics**: Comprehensive data tracking in place