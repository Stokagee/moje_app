# Application Context for RF Learning Materials

## Learning Objectives
- Understand the application architecture
- Know available API endpoints
- Understand database schema
- Identify UI elements for testing

---

## System Overview

### Frontend (React Native/Expo Web)
- **URL**: `http://localhost:8081/`
- **Technology**: React Native with Expo (~54.0.7)
- **Pages**: FormPage, Page2 (List), Page3 (Orders), Page4 (Dispatch)
- **Testing**: Comprehensive `data-testid` attributes on all elements

### Backend (FastAPI)
- **URL**: `http://localhost:8000`
- **API Base**: `http://localhost:8000/api/v1`
- **Authentication**: **NONE** (open for testing!)
- **Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Features**: Form API, Courier API, Order API, Dispatch API

### Database (PostgreSQL)
- **Connection**: `localhost:5432`
- **Database**: `moje_app`
- **User/Password**: `postgres` / `postgres`
- **Tables**: form_data, attachments, instructions, couriers, orders, dispatch_logs

---

## API Endpoints Reference

### Form API (`/api/v1/form`)

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| POST | `/form/` | Create form submission | None |
| GET | `/form/` | List all forms (paginated) | None |
| GET | `/form/{id}` | Get form by ID | None |
| DELETE | `/form/{id}` | Delete form | None |
| POST | `/form/evaluate-name` | Check for easter egg | None |
| POST | `/form/{id}/attachment` | Upload file attachment | None |
| GET | `/form/{id}/attachments` | Get attachments | None |
| PUT | `/form/{id}/instructions` | Create/update instructions | None |
| GET | `/form/{id}/instructions` | Get instructions | None |

**Example Request (POST /form/):**
```json
{
    "first_name": "Jan",
    "last_name": "Novák",
    "phone": "+420123456789",
    "gender": "male",
    "email": "jan.novak@example.com"
}
```

**Easter Egg Names:** `neo`, `trinity`, `morpheus`, `jan`, `pavla`, `matrix`

---

### Courier API (`/api/v1/couriers`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/couriers/` | Create courier |
| GET | `/couriers/` | List all couriers |
| GET | `/couriers/available` | Get available couriers with GPS |
| GET | `/couriers/{id}` | Get courier by ID |
| PUT | `/couriers/{id}` | Update courier details |
| PATCH | `/couriers/{id}/location` | Update GPS location |
| PATCH | `/couriers/{id}/status` | Update status (available/busy/offline) |
| DELETE | `/couriers/{id}` | Delete courier |

**Courier Status Values:**
- `offline` - Not at work
- `available` - Free for orders
- `busy` - Currently delivering

---

### Order API (`/api/v1/orders`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/orders/` | Create order |
| GET | `/orders/` | List all orders |
| GET | `/orders/pending` | Get pending orders (SEARCHING status) |
| GET | `/orders/by-status/{status}` | Filter by status |
| GET | `/orders/{id}` | Get order with courier details |
| PATCH | `/orders/{id}/status` | Update order status |
| POST | `/orders/{id}/pickup` | Mark as picked up |
| POST | `/orders/{id}/deliver` | Mark as delivered |
| POST | `/orders/{id}/cancel` | Cancel order |
| DELETE | `/orders/{id}` | Delete order |

**Order Status Flow:**
```
CREATED → SEARCHING → ASSIGNED → PICKED → DELIVERED
                     ↓
                   CANCELLED
```

---

### Dispatch API (`/api/v1/dispatch`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/dispatch/auto/{order_id}` | Auto-assign nearest courier |
| POST | `/dispatch/manual` | Manually assign courier to order |
| GET | `/dispatch/available-couriers/{order_id}` | Get suitable couriers |
| GET | `/dispatch/logs/order/{order_id}` | Get dispatch history |
| GET | `/dispatch/logs/courier/{courier_id}` | Get courier history |

**Dispatch Algorithm:**
1. Find couriers with `status=available` + valid GPS
2. Filter by `required_tags` (must have ALL)
3. For VIP orders: prefer couriers with `vip` tag
4. Phase 1: Search within 2km
5. Phase 2: Expand to 5km
6. Select closest by GPS distance

---

## Database Schema

### form_data
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PRIMARY KEY |
| first_name | String(100) | NOT NULL, INDEXED |
| last_name | String(100) | NOT NULL, INDEXED |
| phone | String | NOT NULL, INDEXED (9-15 chars) |
| gender | String | NOT NULL, INDEXED (male/female/other) |
| email | String | UNIQUE, NOT NULL |

### attachments
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PRIMARY KEY |
| form_id | Integer | FOREIGN KEY → form_data(id) CASCADE |
| filename | String | NOT NULL |
| content_type | String | NOT NULL (application/pdf, text/plain) |
| data | LargeBinary | NOT NULL (max 1MB) |
| instructions | Text | NULL |

### instructions
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PRIMARY KEY |
| form_id | Integer | FOREIGN KEY → form_data(id) UNIQUE |
| text | Text | NOT NULL |

### couriers
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PRIMARY KEY |
| name | String(100) | NOT NULL |
| phone | String(20) | NOT NULL |
| email | String | UNIQUE, NOT NULL |
| lat | Float | NULL (GPS latitude) |
| lng | Float | NULL (GPS longitude) |
| status | String | NOT NULL (available/busy/offline) |
| tags | JSON | Default: [] |
| created_at | Timestamp | NOT NULL |

### orders
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PRIMARY KEY |
| customer_name | String(100) | NOT NULL |
| customer_phone | String(20) | NOT NULL |
| pickup_address | String(200) | NOT NULL |
| pickup_lat | Float | NOT NULL |
| pickup_lng | Float | NOT NULL |
| delivery_address | String(200) | NOT NULL |
| delivery_lat | Float | NOT NULL |
| delivery_lng | Float | NOT NULL |
| status | String | NOT NULL (CREATED/SEARCHING/ASSIGNED/PICKED/DELIVERED/CANCELLED) |
| is_vip | Boolean | Default: false |
| required_tags | JSON | Default: [] |
| courier_id | Integer | FOREIGN KEY → couriers.id (NULL) |
| created_at | Timestamp | NOT NULL |

### dispatch_logs
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PRIMARY KEY |
| order_id | Integer | FOREIGN KEY → orders(id) |
| courier_id | Integer | FOREIGN KEY → couriers(id) |
| action | String | NOT NULL (auto_assigned/manual_assigned/auto_failed/rejected) |
| created_at | Timestamp | NOT NULL |

---

## UI Elements (data-testid attributes)

### FormPage (`/fe/mojeApp/src/component/pages/FormPage.js`)

**Form Inputs:**
```
[data-testid="firstName-input"]
[data-testid="lastName-input"]
[data-testid="phone-input"]
[data-testid="email-input"]
```

**Gender Picker:**
```
[data-testid="genderPicker"]
[data-testid="gender-option-male"]
[data-testid="gender-option-female"]
[data-testid="gender-option-other"]
```

**Additional Fields:**
```
[data-testid="instructions-textarea"]
[data-testid="file-uploader-dropzone"]
[data-testid="selected-file-text"]
```

**Actions:**
```
[data-testid="submitButton"]
```

**Modals:**
```
[data-testid="formValidationModal"]
[data-testid="formSuccessModal"]
[data-testid="formSuccessModal-primary"]
[data-testid="formSuccessModal-secondary"]
```

**Page Container:**
```
[data-testid="form-page-container"]
```

---

### Page2 - List View (`/fe/mojeApp/src/component/pages/Page2.js`)

**Container & Title:**
```
[data-testid="page2Title"]
[data-testid="list-container"]
[data-testid="list-empty-state"]
[data-testid="page2-loading-container"]
[data-testid="page2-loading-text"]
```

**List Items (Dynamic):**
```
[data-testid="list-item-{id}"]
[data-testid="list-item-{id}-name"]
[data-testid="list-item-{id}-email"]
[data-testid="list-item-{id}-id"]
[data-testid="list-item-{id}-checkbox"]
[data-testid="list-item-{id}-delete"]
```

**Actions:**
```
[data-testid="refreshButton"]
[data-testid="backButton"]
```

**Detail Modal:**
```
[data-testid="info-modal"]
[data-testid="info-email-value"]
[data-testid="info-modal-ok"]
```

---

### Page3 - Orders (`/fe/mojeApp/src/component/pages/Page3.js`)

**Header & Loading:**
```
[data-testid="page3-title"]
[data-testid="orders-loading"]
[data-testid="orders-empty-state"]
```

**Stats Panel:**
```
[data-testid="orders-stats-panel"]
[data-testid="stat-box-total"]
[data-testid="stat-box-pending"]
[data-testid="stat-box-active"]
[data-testid="stat-box-completed"]
```

**Order List:**
```
[data-testid="orders-list"]
[data-testid="orders-refresh-button"]
```

**Order Cards (Dynamic):**
```
[data-testid="order-card-{id}"]
[data-testid="order-status-{status}"]
[data-testid="order-priority-{priority}"]
```

---

### Page4 - Dispatch (`/fe/mojeApp/src/component/pages/Page4.js`)

**Header:**
```
[data-testid="page4-title"]
[data-testid="dispatch-loading"]
[data-testid="dispatch-refresh-button"]
[data-testid="dispatch-split-view"]
```

**Pending Orders:**
```
[data-testid="pending-orders-section"]
[data-testid="pending-order-card-{id}"]
```

**Available Couriers:**
```
[data-testid="available-couriers-section"]
[data-testid="courier-card-{id}"]
```

---

### Navigation (`/fe/mojeApp/src/component/common/HamburgerMenu.js`)

**Mobile:**
```
[data-testid="hamburger-button"]
[data-testid="mobile-menu"]
[data-testid="menu-close-button"]
```

**Desktop:**
```
[data-testid="desktop-sidebar"]
```

**Menu Items:**
```
[data-testid="menu-item-FormPage"]
[data-testid="menu-item-Page2"]
[data-testid="menu-item-Page3"]
[data-testid="menu-item-Page4"]
```

---

## Test Data Generation

### Using FakerLibrary

```robotframework
*** Settings ***
Library    FakerLibrary

*** Test Cases ***
Generate Test Data
    ${first_name}=    FakerLibrary.First Name
    ${last_name}=     FakerLibrary.Last Name
    ${phone}=         FakerLibrary.Phone Number
    ${email}=         FakerLibrary.Email
    ${address}=       FakerLibrary.Address
    ${company}=       FakerLibrary.Company
```

**Useful Faker Methods:**
| Method | Example Output |
|--------|---------------|
| `First Name` | "John" |
| `Last Name` | "Doe" |
| `Email` | "john.doe@example.com" |
| `Phone Number` | "+1234567890" |
| `Address` | "123 Main St" |
| `Company` | "Acme Corp" |

---

## Cleanup Strategies

### Option 1: Teardown Cleanup
```robotframework
*** Test Cases ***
Create Form
    ${result}=    Create Form    ${session}    ${data}
    [Teardown]    Delete Form Data    ${session}    ${result}[id]
```

### Option 2: Suite Cleanup
```robotframework
*** Settings ***
Suite Teardown    Clean Up All Test Data

*** Keywords ***
Clean Up All Test Data
    [Arguments]    ${session}
    @{forms}=    Get All Forms    ${session}
    FOR    ${form}    IN    @{forms}
        IF    $form['email'].contains('@test.')
            Delete Form Data    ${session}    ${form}[id]
        END
    END
```

### Option 3: Database Cleanup
```sql
-- Direct SQL cleanup
DELETE FROM form_data WHERE email LIKE '%@test.example.com';
DELETE FROM orders WHERE customer_name LIKE 'Test%';
DELETE FROM couriers WHERE email LIKE '%@test.com';
```

---

## Quick Reference Commands

### Start Application

```bash
# Backend
cd be && uvicorn app.main:app --reload

# Frontend
cd fe/mojeApp && npm run web

# Database (Docker)
docker compose up -d db
```

### Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:8081 | UI testing |
| Backend API | http://localhost:8000 | API testing |
| Swagger Docs | http://localhost:8000/docs | API reference |
| Database | localhost:5432 | DB testing |
| Adminer | http://localhost:8080 | DB browser |

---

## Common Testing Scenarios

### 1. Form Submission Flow
```
UI: Fill form → Submit → Verify success modal
API: POST /form/ → Verify 201 response
DB: SELECT * FROM form_data WHERE email = '...'
```

### 2. Courier Management Flow
```
API: POST /couriers/ → PATCH /couriers/{id}/status
DB: Verify status = 'available'
UI: Check courier appears in available list
```

### 3. Order Lifecycle Flow
```
API: POST /orders/ → POST /dispatch/auto/{id} → POST /orders/{id}/pickup → POST /orders/{id}/deliver
DB: Verify order status progression
UI: Check order status in Page3
```

### 4. Easter Egg Trigger
```
UI: Fill form with first_name="neo"
API: Response contains easter_egg=true
Verify: secret_message in response
```

---

## References

### Backend Source
- `/be/app/api/endpoints/form_data.py` - Form API
- `/be/app/api/endpoints/couriers.py` - Courier API
- `/be/app/api/endpoints/orders.py` - Order API
- `/be/app/api/endpoints/dispatch.py` - Dispatch API
- `/be/app/models/` - Database models

### Frontend Source
- `/fe/mojeApp/src/component/pages/FormPage.js` - Form page
- `/fe/mojeApp/src/component/pages/Page2.js` - List view
- `/fe/mojeApp/src/component/pages/Page3.js` - Orders
- `/fe/mojeApp/src/component/pages/Page4.js` - Dispatch

### RF Test Examples
- `/RF/UI/tests/new_form.robot` - UI test example
- `/RF/API/tests/create_form.robot` - API test example
- `/RF/db/tests/verify_email.robot` - DB test example
