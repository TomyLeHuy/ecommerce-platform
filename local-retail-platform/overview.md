# Local Retail Platform - Complete Project Overview

## 🎯 Project Vision
A B2B2C e-commerce platform connecting local merchants with customers within a 150km radius. Merchants can manage products via a SaaS dashboard, while customers browse and purchase from local shops.

---

## 📊 Architecture Overview

### Tech Stack
**Backend:**
- Django 5.2.7 + Django REST Framework
- PostgreSQL (currently using SQLite for development)
- JWT Authentication (djangorestframework-simplejwt)
- Python 3.12 with Poetry for dependency management
- PostGIS ready (for geo-spatial features)

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Axios for API calls
- React Context for state management

### Architecture Pattern
- **Decoupled API-First**: Frontend and backend communicate via REST API
- **JWT Authentication**: Token-based auth with auto-refresh
- **React Context**: Global state for cart and authentication
- **Server Components + Client Components**: Next.js app router pattern

---

## 📁 Complete File Structure

```
local-retail-platform/
├── backend/
│   ├── pyproject.toml              # Poetry dependencies
│   ├── config.yaml                 # Application configuration
│   ├── manage.py                   # Django management script
│   ├── db.sqlite3                  # SQLite database (dev)
│   │
│   ├── core/                       # Django project settings
│   │   ├── settings.py             # Main Django settings (uses config.yaml)
│   │   ├── urls.py                 # Main URL routing
│   │   └── wsgi.py                 # WSGI application
│   │
│   └── src/
│       ├── config/
│       │   └── configManager.py    # Pydantic-based config management
│       │
│       ├── utils/
│       │   └── models.py           # Shared Pydantic models
│       │
│       ├── merchants/              # Merchant management app
│       │   ├── models.py           # MerchantProfile, Shop, Subscription
│       │   ├── admin.py            # Django admin configuration
│       │   └── apps.py             # App configuration
│       │
│       ├── customers/              # Customer management app
│       │   ├── models.py           # CustomerProfile, FavoriteShop, LoyaltyToken, DigitalReceipt
│       │   ├── serializers.py      # DRF serializers for customers
│       │   ├── views.py            # API views for registration, profile
│       │   ├── urls.py             # Customer API routes
│       │   ├── admin.py            # Django admin configuration
│       │   └── apps.py             # App configuration
│       │
│       ├── products/               # Product catalog app
│       │   ├── models.py           # Category, Product, ProductImage
│       │   ├── serializers.py      # DRF serializers for products
│       │   ├── views.py            # API views for product browsing
│       │   ├── urls.py             # Product API routes
│       │   ├── admin.py            # Django admin configuration
│       │   └── apps.py             # App configuration
│       │
│       ├── orders/                 # Order management app
│       │   ├── models.py           # Order, OrderItem, OrderStatusHistory
│       │   ├── admin.py            # Django admin configuration
│       │   ├── apps.py             # App configuration
│       │   ├── serializers.py      # ⚠️ TO BE CREATED
│       │   ├── views.py            # ⚠️ TO BE UPDATED
│       │   └── urls.py             # ⚠️ TO BE CREATED
│       │
│       ├── payments/               # Payment processing (placeholder)
│       │   └── models.py           # Empty (future implementation)
│       │
│       ├── notifications/          # Notification system (placeholder)
│       │   └── models.py           # Empty (future implementation)
│       │
│       └── analytics/              # Analytics (placeholder)
│           └── models.py           # Empty (future implementation)
│
└── frontend/
    ├── package.json                # NPM dependencies
    ├── next.config.js              # Next.js configuration
    ├── tailwind.config.js          # Tailwind CSS config
    ├── .env.local                  # Environment variables
    │
    ├── lib/
    │   ├── api.ts                  # API client with Axios + interceptors
    │   └── cart.ts                 # Shopping cart utilities
    │
    ├── context/
    │   ├── CartContext.tsx         # Global cart state management
    │   └── AuthContext.tsx         # Global authentication state
    │
    ├── components/
    │   ├── Header.tsx              # Main navigation header
    │   ├── Footer.tsx              # Site footer
    │   ├── CartButton.tsx          # Cart icon with badge
    │   └── ProductCard.tsx         # Product display card
    │
    └── app/
        ├── layout.tsx              # Root layout (AuthProvider + CartProvider)
        ├── page.tsx                # Homepage
        ├── globals.css             # Global styles
        │
        ├── products/
        │   ├── page.tsx            # Products listing page
        │   └── [slug]/
        │       └── page.tsx        # Product detail page
        │
        ├── cart/
        │   └── page.tsx            # Shopping cart page
        │
        ├── checkout/
        │   └── page.tsx            # ⚠️ TO BE CREATED
        │
        ├── customer/
        │   ├── register/
        │   │   └── page.tsx        # Customer registration
        │   ├── login/
        │   │   └── page.tsx        # Customer login
        │   ├── dashboard/
        │   │   └── page.tsx        # Customer dashboard
        │   └── orders/
        │       ├── page.tsx        # ⚠️ TO BE CREATED (order history)
        │       └── [id]/
        │           └── page.tsx    # ⚠️ TO BE CREATED (order detail)
        │
        └── merchant/
            ├── login/
            │   └── page.tsx        # Merchant login
            ├── dashboard/
            │   └── page.tsx        # Merchant dashboard
            ├── products/
            │   ├── page.tsx        # Product management
            │   └── new/
            │       └── page.tsx    # Add product (placeholder)
            └── orders/
                └── page.tsx        # ⚠️ TO BE CREATED (merchant orders)
```

---

## 🔧 Backend Files - Detailed Breakdown

### Configuration Layer

#### `config.yaml`
**Purpose**: Central configuration file for all backend settings
**Key Sections**:
- `backend`: Debug mode, secret key, CORS origins
- `database`: SQLite config (ready for PostgreSQL)
- `jwt`: Token lifetime settings
- `business`: Business rules (geo radius: 150km, loyalty: €1 per €100, commissions: 7.3% free / 3.1% premium)
- `payments`: Stripe/PayPal config (placeholders)
- `email`: Email backend config

#### `src/config/configManager.py`
**Purpose**: Pydantic-based configuration validator and manager
**Features**:
- Type-safe configuration loading
- Validates config on startup
- Singleton pattern for global access
- Used by Django settings

#### `core/settings.py`
**Purpose**: Main Django settings file
**Key Features**:
- Loads config from `configManager`
- CORS configured for localhost:3000
- JWT auth with 60min access tokens, 7 day refresh
- REST Framework with JWT authentication
- AllowAny default permissions (products are public)
- German locale (de-de, Europe/Berlin)

### Data Models Layer

#### `src/utils/models.py`
**Purpose**: Shared Pydantic models for data validation
**Models**:
- `UserRole`, `SubscriptionTier`, `OrderStatus`, `PaymentStatus` enums
- `GeoLocation`: Latitude/longitude validation
- `MoneyAmount`: Decimal with currency support
- `SearchRadius`: Geographic search parameters
- `LoyaltyTokenCalculation`: Token calculation logic

#### `src/merchants/models.py`
**Purpose**: Merchant-related database models
**Models**:
1. **MerchantProfile** (extends User):
   - Company name, tax ID, phone
   - Business address + geo coordinates
   - DATEV client ID for accounting integration
   - Verification status
   - OneToOne with Django User

2. **Subscription**:
   - Tier: free (7.3%) or premium (3.1%)
   - Status: active/cancelled/suspended/expired
   - Premium dates and billing info
   - Properties: commission_rate, monthly_fee, is_premium

3. **Shop**:
   - Belongs to MerchantProfile
   - Name, slug, description, logo, banner
   - Delivery radius (default 150km, max 500km)
   - Contact info (email, phone)
   - Settings: accepts_online_orders, accepts_in_store_pickup
   - Statistics: total_products, total_orders
   - Property: is_operational (checks active, verified, subscription)

#### `src/products/models.py`
**Purpose**: Product catalog models
**Models**:
1. **Category**:
   - Hierarchical (parent/child)
   - Name, slug, description, icon
   - Display order for sorting
   - Property: full_path (shows hierarchy)

2. **Product**:
   - Belongs to Shop and Category
   - Name, slug, SKU, barcode, descriptions
   - Pricing: price, sale_price, cost_price
   - Inventory: stock_quantity, min_stock_level, max_stock_level
   - Dimensions: weight, length, width, height
   - Status: is_active, is_featured
   - SEO: meta_title, meta_description
   - Stats: view_count, sales_count
   - Properties: current_price, is_in_stock, is_low_stock, stock_status, profit_margin

3. **ProductImage**:
   - Multiple images per product
   - Display order, is_primary flag
   - Alt text for accessibility
   - Auto-ensures only one primary image

#### `src/customers/models.py`
**Purpose**: Customer-related models
**Models**:
1. **CustomerProfile** (extends User):
   - Phone, date of birth
   - Shipping address + geo coordinates
   - Search preferences (default_search_radius_km)
   - Marketing consents
   - Statistics: total_orders, total_spent
   - Properties: has_location, has_complete_profile

2. **FavoriteShop**:
   - Saved shops for "travel" feature
   - Customer can favorite shops outside their radius
   - Personal notes field
   - Unique constraint: one favorite per customer-shop pair

3. **LoyaltyToken**:
   - Transaction history for token system
   - Types: earned/spent/expired/admin_adjustment
   - Amount (positive for earned, negative for spent)
   - balance_after for running balance
   - Links to Order if applicable
   - Class method: get_customer_balance()
   - Property: token_value_euros

4. **DigitalReceipt**:
   - Digital receipt storage (Kassenzettel)
   - Types: online/in_store
   - Expense classification: personal/business
   - Purchase info: date, amount, tax
   - Return policy: deadline, is_returnable
   - DATEV export tracking
   - Properties: is_return_period_active, days_until_return_deadline

#### `src/orders/models.py`
**Purpose**: Order management models
**Models**:
1. **Order**:
   - Belongs to CustomerProfile and Shop
   - order_number (auto-generated: ORD-timestamp-random)
   - Status: pending/confirmed/processing/shipped/delivered/cancelled/refunded
   - Fulfillment: delivery or pickup
   - Shipping address (snapshot from customer at order time)
   - Pricing: subtotal, tax_amount, shipping_cost, discount_amount
   - Loyalty: tokens_used, tokens_value
   - Payment: payment_status, payment_method
   - Tracking: tracking_number, tracking_url
   - Timestamps: ordered_at, confirmed_at, shipped_at, delivered_at, cancelled_at
   - Properties: is_paid, can_be_cancelled, is_completed

2. **OrderItem**:
   - Line items in an order
   - Product snapshot: name, SKU, price at order time (preserves history)
   - Quantity, line_total (calculated)
   - Tax: rate (default 19%), amount (calculated)
   - Auto-calculates totals on save

3. **OrderStatusHistory**:
   - Audit trail for order status changes
   - Status, notes, changed_by
   - Timestamp for each change

### API Layer

#### `src/products/serializers.py`
**Purpose**: DRF serializers for product API
**Serializers**:
- `CategorySerializer`: Includes subcategories recursively
- `ProductImageSerializer`: Image data
- `ShopBasicSerializer`: Minimal shop info for product listings
- `ProductListSerializer`: Minimal product data for listings
- `ProductDetailSerializer`: Full product details
- `ProductCreateUpdateSerializer`: For merchant product management

#### `src/products/views.py`
**Purpose**: API endpoints for products
**ViewSets**:
1. **CategoryViewSet** (ReadOnly):
   - List categories
   - Root categories endpoint
   - AllowAny permission

2. **ProductViewSet**:
   - List products (public)
   - Product detail (public)
   - search_nearby() - Geo-based search (placeholder for PostGIS)
   - featured() - Featured products
   - related() - Related products by category
   - my_products() - Merchant's products (authenticated)
   - Permissions: AllowAny for read, IsAuthenticated for write

#### `src/products/urls.py`
**Purpose**: Route product API endpoints
**Routes**:
- `/api/products/categories/` - Categories
- `/api/products/products/` - Products
- All ViewSet custom actions auto-registered

#### `src/customers/serializers.py`
**Purpose**: DRF serializers for customer API
**Serializers**:
- `UserSerializer`: Basic user info
- `CustomerRegistrationSerializer`: Registration with password validation
- `CustomerProfileSerializer`: Full profile with token balance
- `CustomerProfileUpdateSerializer`: Update profile and user fields
- `FavoriteShopSerializer`: Favorite shops
- `LoyaltyTokenSerializer`: Token transactions

#### `src/customers/views.py`
**Purpose**: API endpoints for customers
**ViewSets**:
1. **CustomerRegistrationViewSet**:
   - register() - Creates user + profile, returns JWT tokens

2. **CustomerProfileViewSet**:
   - me() - Get current user's profile
   - update/partial_update - Update profile
   - token_balance() - Get loyalty token balance
   - Auto-creates profile if missing

3. **FavoriteShopViewSet**:
   - CRUD operations for favorite shops
   - Filtered to current user

4. **LoyaltyTokenViewSet** (ReadOnly):
   - List token transactions
   - balance() - Get current balance
   - Filtered to current user

#### `src/customers/urls.py`
**Purpose**: Route customer API endpoints
**Routes**:
- `/api/customers/register/` - Registration
- `/api/customers/profile/me/` - Current user profile
- `/api/customers/favorites/` - Favorite shops
- `/api/customers/tokens/` - Token history

#### `core/urls.py`
**Purpose**: Main URL routing
**Routes**:
- `/admin/` - Django admin panel
- `/api/auth/token/` - JWT login
- `/api/auth/token/refresh/` - Token refresh
- `/api/products/` - Product endpoints
- `/api/customers/` - Customer endpoints
- Media files served in DEBUG mode

### Admin Interface

All `admin.py` files provide rich Django admin interfaces with:
- Custom list displays
- Filters and search
- Organized fieldsets
- Readonly fields
- Visual status indicators
- Color-coded displays
- Inlines for related objects

---

## 🎨 Frontend Files - Detailed Breakdown

### Configuration

#### `.env.local`
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_SITE_NAME=Local Retail Platform
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

#### `next.config.js`
**Purpose**: Next.js configuration
**Key Config**:
- Image domains: Allows 127.0.0.1:8000 for product images
- Remote patterns for Django media files

### Core Utilities

#### `lib/api.ts`
**Purpose**: Axios-based API client with interceptors
**Features**:
- Base URL configuration
- Auto-adds JWT token to requests (from localStorage)
- Token refresh on 401 errors
- Request/response interceptors
- TypeScript interfaces for all data types
- API methods organized by resource:
  - `api.products.*` - Product operations
  - `api.categories.*` - Category operations
  - `api.customers.*` - Customer operations
  - `api.auth.*` - Authentication

**Key Methods**:
```typescript
// Products
api.products.list(params)
api.products.get(slug)
api.products.featured()
api.products.searchNearby(params)
api.products.related(slug)

// Customers
api.customers.register(data)
api.customers.getProfile()
api.customers.updateProfile(data)
api.customers.getTokenBalance()

// Auth
api.auth.login(username, password)
api.auth.logout()
api.auth.isAuthenticated()
```

#### `lib/cart.ts`
**Purpose**: Shopping cart business logic
**Features**:
- localStorage persistence
- Cart operations: add, remove, update quantity, clear
- Calculations: subtotal, tax (19% VAT), shipping (free over €50), total
- Utility functions: getCartItemCount, isInCart, getProductQuantity

**Data Structure**:
```typescript
interface CartItem {
  product: Product;
  quantity: number;
  addedAt: string;
}

interface Cart {
  items: CartItem[];
  updatedAt: string;
}
```

### State Management

#### `context/CartContext.tsx`
**Purpose**: Global cart state using React Context
**Provides**:
- cart: Current cart object
- itemCount: Total items in cart
- totals: { subtotal, tax, shipping, total }
- addToCart(product, quantity)
- removeFromCart(productId)
- updateQuantity(productId, quantity)
- clearCart()
- isInCart(productId)
- getQuantity(productId)
- refreshCart()

**Features**:
- Prevents hydration mismatches
- Auto-loads cart on mount
- Real-time calculations

#### `context/AuthContext.tsx`
**Purpose**: Global authentication state
**Provides**:
- user: Current user object or null
- isAuthenticated: Boolean
- isLoading: Boolean
- login(username, password)
- logout()
- register(data)
- refreshUser()

**Features**:
- Auto-loads user on mount
- Fetches profile from API
- Handles token expiration
- Provides user info globally

### Components

#### `components/Header.tsx`
**Purpose**: Main navigation header
**Features**:
- Logo and branding
- Search bar (desktop + mobile)
- User menu with dropdown (shows username when logged in)
- Cart button with badge
- Navigation links
- Mobile hamburger menu
- Merchant portal link

**Auth Integration**:
- Shows "Login" when not authenticated
- Shows username + dropdown when authenticated
- Dropdown: Dashboard, Orders, Logout

#### `components/Footer.tsx`
**Purpose**: Site footer
**Sections**:
- Brand info and location indicator
- Shop links (products, featured, cart)
- Customer links (account, orders, register)
- Merchant links (portal, dashboard)
- Copyright and legal links

#### `components/CartButton.tsx`
**Purpose**: Cart icon with item count badge
**Features**:
- Uses CartContext for item count
- Badge shows count (up to 99+)
- Links to cart page
- Responsive (shows/hides text)

#### `components/ProductCard.tsx`
**Purpose**: Reusable product display card
**Features**:
- Product image (or placeholder)
- Category, name, description
- Current price (with sale price strikethrough)
- Stock status badges (in stock, low stock, out of stock)
- Discount percentage badge
- Featured badge
- Shop info with location
- SKU display
- Hover effects

### Pages

#### `app/layout.tsx`
**Purpose**: Root layout wrapper
**Features**:
- Wraps app in AuthProvider (outermost)
- Wraps in CartProvider
- Includes Header and Footer
- Flex layout for sticky footer

#### `app/page.tsx`
**Purpose**: Homepage
**Sections**:
- Hero with search bar
- Quick stats (products, radius, merchants)
- Features section (3 cards)
- Featured products grid
- Recent products grid
**Data**: Fetches featured + recent products from API

#### `app/products/page.tsx`
**Purpose**: Products listing/browse page
**Features**:
- Search bar (functional)
- Filter button (placeholder)
- Product grid (responsive)
- Pagination (12 per page)
- Results count
- Empty state
**Data**: Fetches paginated products with search

#### `app/products/[slug]/page.tsx`
**Purpose**: Product detail page (dynamic route)
**Features**:
- Breadcrumb navigation
- Image gallery with thumbnails
- Product info (name, category, price, stock)
- Discount badge
- Stock status indicators
- Add to Cart button (functional!)
- Shop information card
- Product stats (sales, SKU)
- Full description
- Specifications table (dimensions)
- Related products section
**Data**: Fetches product by slug + related products

#### `app/cart/page.tsx`
**Purpose**: Shopping cart page
**Features**:
- Cart items list with images
- Quantity controls (+/-)
- Remove item button
- Real-time price updates
- Low stock warnings
- Order summary sidebar (sticky)
- Subtotal, tax (19%), shipping calculations
- Free shipping indicator (over €50)
- Proceed to checkout button
- Empty cart state
**Data**: Uses CartContext

#### `app/customer/register/page.tsx`
**Purpose**: Customer registration
**Features**:
- Form fields: username, email, password, confirm, first/last name
- Password validation (8+ chars)
- Password match validation
- Email uniqueness check
- Field-level error display
- Loading states
- Auto-login after registration
- Redirects to dashboard
**Data**: Calls api.customers.register() via AuthContext

#### `app/customer/login/page.tsx`
**Purpose**: Customer login
**Features**:
- Username and password fields
- Remember me checkbox
- Forgot password link (placeholder)
- Guest shopping option
- Merchant portal link
- Error handling
- Redirects to dashboard or previous page
**Data**: Calls api.auth.login() via AuthContext

#### `app/customer/dashboard/page.tsx`
**Purpose**: Customer dashboard
**Features**:
- Welcome message with name
- Profile incomplete warning
- Stats cards: total orders, total spent, loyalty tokens
- Quick actions: shop, orders, favorites
- Account information display
- Logout button
**Data**: Fetches profile from API, uses AuthContext

#### `app/merchant/login/page.tsx`
**Purpose**: Merchant login
**Features**:
- Similar to customer login
- Merchant-branded
- Redirects to merchant dashboard
**Data**: Uses api.auth.login()

#### `app/merchant/dashboard/page.tsx`
**Purpose**: Merchant dashboard
**Features**:
- Stats: total products, low stock, sales, revenue
- Quick actions: add product, manage products, view orders
- Recent products table
- Logout button
**Data**: Fetches merchant's products from API

#### `app/merchant/products/page.tsx`
**Purpose**: Product management for merchants
**Features**:
- Product table with images
- Search by name/SKU
- Status indicators
- Edit/delete buttons (placeholders)
- Add product button
**Data**: Lists merchant's products

#### `app/merchant/products/new/page.tsx`
**Purpose**: Add product (placeholder)
**Features**:
- Explains to use Django Admin
- Link to Django admin
- Instructions
**Future**: Full product creation form

---

## 🔄 How Everything Connects

### Authentication Flow
```
1. User clicks Login/Register
   ↓
2. Form submits to AuthContext method
   ↓
3. AuthContext calls api.auth.login() or api.customers.register()
   ↓
4. API client sends request to Django
   ↓
5. Django validates credentials
   ↓
6. Django returns JWT tokens + user data
   ↓
7. API client saves tokens to localStorage
   ↓
8. AuthContext loads user profile
   ↓
9. User state updated globally
   ↓
10. Header re-renders showing username
   ↓
11. Redirect to dashboard
```

### Shopping Flow
```
1. Customer browses products
   ↓
2. Clicks "Add to Cart"
   ↓
3. ProductDetailPage calls useCart().addToCart()
   ↓
4. CartContext adds product to cart
   ↓
5. Cart saved to localStorage
   ↓
6. Cart badge updates in Header
   ↓
7. Customer navigates to /cart
   ↓
8. CartPage displays items from CartContext
   ↓
9. Customer adjusts quantities
   ↓
10. CartContext updates cart & localStorage
   ↓
11. Totals recalculate automatically
   ↓
12. Customer clicks "Proceed to Checkout"
   ↓
13. [NEXT: Checkout flow to be implemented]
```

### API Request Flow
```
Frontend Component
   ↓
Calls api.products.list()
   ↓
lib/api.ts (Axios)
   ↓
Request Interceptor adds:
  Authorization: Bearer <JWT_TOKEN>
   ↓
HTTP Request → Django
   ↓
JWT Middleware validates token
   ↓
Extracts User from token
   ↓
View checks permissions
   ↓
Queries database
   ↓
Serializer formats data
   ↓
JSON Response ← Django
   ↓
Response Interceptor (handles 401)
   ↓
Returns data to component
   ↓
Component updates UI
```

### Order Creation Flow (To Be Implemented)
```
1. Customer in cart, clicks checkout
   ↓
2. Checkout page validates cart
   ↓
3. Customer enters/confirms shipping address
   ↓
4. Customer selects payment method
   ↓
5. Frontend sends POST to /api/orders/
   with: { cart_items, shipping_address, payment_method }
   + JWT token in header
   ↓
6. Django extracts user from JWT
   ↓
7. Gets/creates CustomerProfile
   ↓
8. Creates Order linked to CustomerProfile
   ↓
9. For each cart item:
      Creates OrderItem (snapshot of product)
      Decrements product stock
   ↓
10. Calculates loyalty tokens earned
    Creates LoyaltyToken transaction
   ↓
11. Creates DigitalReceipt
   ↓
12. Sends confirmation email (future)
   ↓
13. Returns order details
   ↓
14. Frontend clears cart
   ↓
15. Redirects to order confirmation page
```

---

## ✅ What's Fully Implemented

### Backend (Django)
✅ **Configuration Management**
- Pydantic-based config with config.yaml
- Environment-specific settings

✅ **Database Models**
- Merchants: Profile, Shop, Subscription
- Products: Category, Product, ProductImage
- Customers: Profile, FavoriteShop, LoyaltyToken, DigitalReceipt
- Orders: Order, OrderItem, OrderStatusHistory

✅ **Authentication**
- JWT token-based auth
- Token refresh mechanism
- Customer registration endpoint

✅ **API Endpoints - Products**
- List products (with pagination, search, filters)
- Product detail
- Categories (hierarchical)
- Featured products
- Related products
- Geographic search (placeholder for PostGIS)

✅ **API Endpoints - Customers**
- Registration with auto-login
- Profile management
- Favorite shops CRUD
- Loyalty token history

✅ **Admin Interface**
- Full CRUD for all models
- Rich displays with filters
- Visual status indicators
- Inline editing

✅ **Business Logic**
- Loyalty tokens: €1 per €100 spent
- Subscription tiers: 7.3% free, 3.1% premium
- Geo-based search framework (ready for PostGIS)
- Stock level tracking
- Tax calculation (19% VAT)
- Shipping cost (free over €50)

### Frontend (Next.js)
✅ **Global State**
- CartContext for shopping cart
- AuthContext for authentication

✅ **Navigation**
- Header with search, user menu, cart badge
- Footer with comprehensive links
- Responsive mobile menu

✅ **Product Browsing**
- Homepage with featured/recent products
- Products listing page with search
- Product detail pages with image gallery
- Add to cart functionality

✅ **Shopping Cart**
- View cart items
- Update quantities
- Remove items
- Real-time calculations
- Order summary
- Empty state

✅ **Authentication**
- Customer registration (with validation)
- Customer login
- Merchant login
- JWT token management
- Auto-refresh tokens
- Persistent login (localStorage)
- User menu in header

✅ **Dashboards**
- Customer dashboard (stats, quick actions)
- Merchant dashboard (product stats)
- Merchant product management

✅ **UI/UX**
- Responsive design (mobile/tablet/desktop)
- Loading states
- Error handling
- Empty states
- Visual feedback (badges, indicators)
- Gradient backgrounds
- Tailwind CSS styling

---

## ⚠️ What's Missing / Placeholder

### Critical for MVP (Next Steps)

1. **Orders Backend API** ⭐⭐⭐
   - `src/orders/serializers.py` - Create
   - `src/orders/views.py` - Update with API views
   - `src/orders/urls.py` - Create routes
   - Update `core/urls.py` to include orders
   - Endpoints needed:
     - POST `/api/orders/` - Create order
     - GET `/api/orders/` - List customer's orders
     - GET `/api/orders/{id}/` - Order detail
     - PATCH `/api/orders/{id}/` - Update status (merchant)

2. **Checkout Flow Frontend** ⭐⭐⭐
   - `app/checkout/page.tsx` - Create
   - Shipping address form
   - Payment method selection
   - Order summary
   - Place order button
   - Order confirmation

3. **Customer Order Pages** ⭐⭐⭐
   - `app/customer/orders/page.tsx` - Order history list
   - `app/customer/orders/[id]/page.tsx` - Order detail/tracking

4. **Merchant Order Management** ⭐⭐
   - `app/merchant/orders/page.tsx` - View incoming orders
   - Order fulfillment interface

### Important (Phase 2)

5. **Customer Profile Editing** ⭐⭐
   - Profile update form
   - Address management
   - Password change

6. **Category Filtering** ⭐⭐
   - Category navigation menu
   - Filter products by category
   - Category pages

7. **Shop Pages** ⭐⭐
   - Shop detail page
   - View all products from a shop
   - Shop information display

8. **Merchant Product Creation** ⭐⭐
   - Form in `app/merchant/products/new/page.tsx`
   - Image upload
   - Category selection

### Nice to Have (Phase 3)

9. **Geographic Search** ⭐
   - PostGIS integration
   - Actual geo-queries in backend
   - Location picker in frontend

10. **Payment Integration** ⭐
    - Stripe integration
    - PayPal integration
    - Payment processing

11. **Email Notifications** ⭐
    - Order confirmation emails
    - Shipping notifications
    - Low stock alerts for merchants

12. **Order Status Updates** ⭐
    - Status change workflow
    - Tracking number updates
    - Customer notifications

13. **Favorite Shops UI** ⭐
    - Display favorite shops
    - Add/remove favorites from shop pages

14. **Digital Receipt Management** ⭐
    - View receipts in customer dashboard
    - Filter receipts
    - DATEV export for business receipts

---

## 🚀 How to Continue Development

### Starting Point: Orders Backend

**Next immediate task**: Create the Orders API so customers can place orders.

**Files to create**:

1. **`backend/src/orders/serializers.py`**
```python
# Create serializers for:
# - OrderSerializer
# - OrderItemSerializer  
# - OrderCreateSerializer
# - OrderListSerializer
```

2. **`backend/src/orders/views.py`**
```python
# Create ViewSets for:
# - OrderViewSet (CRUD operations)
# - Include custom actions:
#   - List customer orders
#   - Create order from cart
#   - Update order status (merchant only)
```

3. **`backend/src/orders/urls.py`**
```python
# Register OrderViewSet routes
```

4. **Update `backend/core/urls.py`**
```python
# Add: path("api/orders/", include("src.orders.urls"))
```

5. **Update `frontend/lib/api.ts`**
```typescript
// Add orders API methods:
api.orders.create(orderData)
api.orders.list()
api.orders.get(id)
```

### Then: Checkout Flow

6. **`frontend/app/checkout/page.tsx`**
- Address form (use customer profile)
- Payment method selector
- Order summary
- Submit order button

7. **`frontend/app/customer/orders/page.tsx`**
- List of customer's orders
- Status indicators
- Link to order detail

8. **`frontend/app/customer/orders/[id]/page.tsx`**
- Order details
- Items ordered
- Shipping info
- Tracking info

---

## 🔑 Key Business Rules to Remember

1. **Loyalty Tokens**
   - €1 token per €100 spent
   - Tokens can be used as payment
   - Cannot be converted to cash

2. **Subscription Tiers**
   - Free: 7.3% commission, no monthly fee
   - Premium: 3.1% commission, €299/month

3. **Geo-Location**
   - Default search radius: 150km
   - Maximum radius: 500km
   - Customers can favorite shops to see them everywhere

4. **Tax & Shipping**
   - 19% VAT (German market)
   - Free shipping on orders over €50
   - Otherwise €4.99

5. **Stock Management**
   - Low stock alert at min_stock_level
   - Automatic notifications when restocking needed
   - Product unavailable when stock = 0

---

## 🛠️ Development Commands

### Backend
```bash
cd backend
poetry shell
python manage.py runserver          # Start server
python manage.py makemigrations     # Create migrations
python manage.py migrate            # Apply migrations
python manage.py createsuperuser    # Create admin user
python manage.py shell              # Django shell
```

### Frontend
```bash
cd frontend
npm run dev                         # Start dev server
npm run build                       # Production build
npm run lint                        # Run linter
```

### Testing APIs
```bash
# Test registration
curl -X POST http://127.0.0.1:8000/api/customers/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"Test123!","password_confirm":"Test123!"}'

# Test login
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"Test123!"}'

# Test products (public)
curl http://127.0.0.1:8000/api/products/products/

# Test authenticated endpoint
curl http://127.0.0.1:8000/api/customers/profile/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📚 Important URLs

**Frontend:**
- Homepage: http://localhost:3000
- Products: http://localhost:3000/products
- Cart: http://localhost:3000/cart
- Customer Login: http://localhost:3000/customer/login
- Customer Register: http://localhost:3000/customer/register
- Customer Dashboard: http://localhost:3000/customer/dashboard
- Merchant Login: http://localhost:3000/merchant/login
- Merchant Dashboard: http://localhost:3000/merchant/dashboard

**Backend:**
- API Root: http://127.0.0.1:8000
- Admin Panel: http://127.0.0.1:8000/admin/
- API Products: http://127.0.0.1:8000/api/products/products/
- API Customers: http://127.0.0.1:8000/api/customers/profile/me/

---

## 🎓 Code Patterns to Follow

### Backend Patterns

**Serializer Pattern**:
```python
class ModelSerializer(serializers.ModelSerializer):
    # Computed fields
    computed_field = serializers.SerializerMethodField()
    
    class Meta:
        model = Model
        fields = ['id', 'field1', 'computed_field']
        read_only_fields = ['id']
    
    def get_computed_field(self, obj):
        return obj.some_property
```

**ViewSet Pattern**:
```python
class ModelViewSet(viewsets.ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Filter to current user
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def custom_action(self, request):
        # Custom endpoint logic
        return Response(data)
```

### Frontend Patterns

**Page Component Pattern**:
```typescript
'use client';

export default function PageName() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchData();
  }, []);
  
  const fetchData = async () => {
    try {
      setLoading(true);
      const result = await api.resource.method();
      setData(result);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return ;
  if (!data) return ;
  
  return ;
}
```

**Context Pattern**:
```typescript
const Context = createContext(undefined);

export function Provider({ children }) {
  const [state, setState] = useState(initialState);
  
  return (
    
      {children}
    
  );
}

export function useHook() {
  const context = useContext(Context);
  if (!context) throw new Error('Must be used within Provider');
  return context;
}
```

---

## 💡 Tips for New Developer

1. **Start with Orders**: The most critical missing piece
2. **Test with Django Admin**: Create test data via admin panel
3. **Use Axios Interceptors**: Already handles auth tokens
4. **Check AuthContext First**: Most auth logic is there
5. **CartContext is Stateful**: Changes reflect immediately
6. **JWT Tokens Auto-Refresh**: Built into API client
7. **Use TypeScript Types**: Import from lib/api.ts
8. **Tailwind for Styling**: Already configured
9. **Django Admin is Your Friend**: Great for debugging
10. **Follow Existing Patterns**: Look at products/customers for examples

---

## 🐛 Common Issues & Solutions

**Issue**: User not staying logged in
**Solution**: AuthContext wraps app in layout.tsx, loads user on mount

**Issue**: Cart not updating
**Solution**: Use CartContext methods, not direct localStorage access

**Issue**: 401 errors on API calls
**Solution**: Check JWT token in localStorage, verify AuthContext loaded

**Issue**: CORS errors
**Solution**: Backend settings.py has CORS configured for localhost:3000

**Issue**: Images not loading
**Solution**: Check next.config.js has correct remote patterns

**Issue**: Django models not in admin
**Solution**: Check apps.py has correct name (e.g., 'src.products')

---

This overview should provide everything needed to continue development! Focus on Orders next - it's the critical piece to complete the MVP purchase flow.