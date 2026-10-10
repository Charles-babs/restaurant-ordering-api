# Restaurant Ordering API

A RESTful Restaurant Ordering API built with Django and Django REST Framework.

The API allows customers to browse available menu items, place and manage orders, and track order status. Staff users can manage order status through a controlled workflow.

## Live Deployment

The API is deployed on Render:

https://restaurant-ordering-api-6tae.onrender.com

Live menu endpoint:

https://restaurant-ordering-api-6tae.onrender.com/api/menu/

## Technologies Used

- Python
- Django
- Django REST Framework
- Simple JWT
- PostgreSQL
- Gunicorn
- Uvicorn
- WhiteNoise
- Render

## Features

- Browse available menu items
- JWT authentication
- Place restaurant orders
- View customer orders
- View individual orders
- Add items to pending orders
- Remove items from pending orders
- Computed order totals
- Customer-specific order access
- Staff-only order status management
- Order filtering by status
- Validation of unavailable menu items
- Controlled order status transitions
- Automated API tests

## Authentication

The API uses JWT authentication.

### Obtain Access and Refresh Tokens

**POST**

`/api/token/`

Example request:

```json
{
    "username": "customer1",
    "password": "your-password"
}
```

Example response:

```json
{
    "refresh": "refresh-token",
    "access": "access-token"
}
```

For protected endpoints, send the access token using:

`Authorization: Bearer <access_token>`

### Refresh Access Token

**POST**

`/api/token/refresh/`

```json
{
    "refresh": "your-refresh-token"
}
```

## API Endpoints

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/api/menu/` | List available menu items | Public |
| POST | `/api/orders/` | Place a new order | Customer |
| GET | `/api/orders/` | View customer's orders | Customer |
| GET | `/api/orders/{id}/` | View a specific order | Order owner |
| PATCH | `/api/orders/{id}/add-item/` | Add an item to a pending order | Order owner |
| DELETE | `/api/orders/{id}/items/{item_id}/` | Remove an item from a pending order | Order owner |
| PATCH | `/api/orders/{id}/status/` | Update order status | Staff only |
| POST | `/api/token/` | Obtain JWT tokens | Public |
| POST | `/api/token/refresh/` | Refresh JWT access token | Public |

## Placing an Order

**POST**

`/api/orders/`

Example:

```json
{
    "items": [
        {
            "menu_item": 1,
            "quantity": 2
        }
    ]
}
```

A successfully created order returns HTTP `201 Created`.

## Adding an Item to an Order

**PATCH**

`/api/orders/{id}/add-item/`

Example:

```json
{
    "menu_item": 2,
    "quantity": 1
}
```

Items can only be added while the order is `pending`.

## Removing an Item

**DELETE**

`/api/orders/{id}/items/{item_id}/`

Items can only be removed while the order is `pending`.

## Order Status Workflow

Valid order status transitions are:

`pending → preparing → ready → completed`

An order can also be cancelled only while it is pending:

`pending → cancelled`

Only staff users can update order status.

Invalid status transitions return HTTP `400 Bad Request`.

## Business Rules

- Customers can only access their own orders.
- Only pending orders can be modified.
- Only staff users can update order status.
- Unavailable menu items cannot be ordered.
- Attempting to order an unavailable menu item returns HTTP `400 Bad Request`.
- Order totals are calculated from the related order items.
- Invalid order status transitions are rejected.

## Filtering Orders

Authenticated customers can filter their own orders by status.

Example:

`GET /api/orders/?status=pending`

## Demo Accounts

The following accounts can be used by the assessor to test customer and staff permissions.

### Customer Account

Username: `customer1`

Password: `customer001`

### Staff Account

Username: `project_admin`

Password: `charles1234`

These accounts are for demonstration/testing purposes only.

## Running the Project Locally

Clone the repository:

```bash
git clone https://github.com/Charles-babs/restaurant-ordering-api.git
cd restaurant-ordering-api
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

The local API will be available at:

`http://127.0.0.1:8000/`

## Automated Tests

The project includes automated tests covering important API business rules and permissions.

Run:

```bash
python manage.py test
```

Tests include:

- A customer cannot view another customer's order.
- An unavailable menu item cannot be ordered.
- A customer cannot change an order's status.
- Staff can change a pending order to preparing.
- Invalid status transitions are rejected.

## Deployment

The project is deployed on Render using:

- Render Web Service
- Render PostgreSQL
- Gunicorn/Uvicorn
- Environment variables for sensitive configuration
- WhiteNoise for static files

The virtual environment, local SQLite database, environment files, and generated static files are excluded from the Git repository.

## Author

Charles Babatunde