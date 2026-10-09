# Restaurant Ordering API

A REST API for a restaurant food ordering system built with Django and Django REST Framework.

The API allows customers to browse available menu items, place orders, view their own orders, and modify pending orders. Staff users can manage order statuses.

## Technologies Used

- Python
- Django
- Django REST Framework
- Simple JWT
- SQLite
- Postman

## Features

- JWT authentication
- View available menu items
- Place orders containing multiple menu items
- Automatically calculate order totals
- View customer-specific orders
- Add items to pending orders
- Remove items from pending orders
- Prevent modification after preparation begins
- Prevent unavailable menu items from being ordered
- Staff-only order status management
- Controlled order status transitions
- Order filtering by status
- Automated API tests

## Installation

Clone or extract the project and navigate into the project directory.

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run database migrations:

```bash
python manage.py migrate
```

Create an administrator account if required:

```bash
python manage.py createsuperuser
```

Start the development server:

```bash
python manage.py runserver
```

The API will be available locally at:

`http://127.0.0.1:8000/`

## Authentication

This project uses JWT authentication.

### Obtain Access and Refresh Tokens

**POST**

`/api/token/`

Example request:

```json
{
    "username": "your_username",
    "password": "your_password"
}
```

A successful request returns an access token and refresh token.

Authenticated requests should send the access token using Bearer authentication.

### Refresh Access Token

**POST**

`/api/token/refresh/`

Example:

```json
{
    "refresh": "your_refresh_token"
}
```

## API Endpoints

### View Menu

**GET**

`/api/menu/`

Returns all menu items currently marked as available.

Authentication is not required.

### Create an Order

**POST**

`/api/orders/`

Authentication is required.

Example:

```json
{
    "items": [
        {
            "menu_item": 1,
            "quantity": 2
        },
        {
            "menu_item": 2,
            "quantity": 1
        }
    ]
}
```

New orders are created with a `pending` status.

The total price is calculated automatically from the prices and quantities of the related order items.

### View Customer Orders

**GET**

`/api/orders/`

Returns only orders belonging to the authenticated customer.

Orders can optionally be filtered by status:

`/api/orders/?status=pending`

### View Specific Order

**GET**

`/api/orders/{id}/`

Returns the specified order only if it belongs to the authenticated customer.

### Add Item to Order

**PATCH**

`/api/orders/{id}/add-item/`

Example:

```json
{
    "menu_item": 3,
    "quantity": 2
}
```

Items can only be added while the order is `pending`.

### Remove Item from Order

**DELETE**

`/api/orders/{id}/items/{item_id}/`

Items can only be removed while the order is `pending`.

### Update Order Status

**PATCH**

`/api/orders/{id}/status/`

Only staff users can access this endpoint.

Example:

```json
{
    "status": "preparing"
}
```

## Order Status Rules

The normal order sequence is:

`pending → preparing → ready → completed`

An order may also transition:

`pending → cancelled`

Invalid transitions are rejected with a `400 Bad Request` response.

Completed and cancelled orders cannot transition to another status.

## Business Rules

1. Customers can only access their own orders.
2. Orders can only be modified while their status is `pending`.
3. Only staff users can update order statuses.
4. Unavailable menu items cannot be added to an order.
5. Order status transitions must follow the allowed sequence.
6. Order totals are calculated from the related order items rather than stored directly on the Order model.

## Running Automated Tests

Run:

```bash
python manage.py test
```

The test suite verifies important API behavior including:

- Customers cannot view another customer's orders.
- Unavailable menu items cannot be ordered.
- Normal customers cannot update order status.
- Staff users can perform valid status transitions.
- Invalid status transitions are rejected.

## Admin Panel

The Django administration interface is available at:

`http://127.0.0.1:8000/admin/`

Staff or superuser credentials are required.

## Author

Restaurant Ordering API — Django REST Framework Project