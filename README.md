# Task Application FastAPI

FastAPI application with JWT authentication, role-based access control, user management, and payment models.

## Setup and Run

### 1. Clone the project

```bash
git clone <repository-url>
cd task-application-fastapi
```

Clones the repository and moves into the project folder.

### 2. Install uv

```bash
pip install uv
```

Installs `uv`, the Python package and environment manager used by this project.

### 3. Create the virtual environment and install dependencies

```bash
uv sync
```

Creates a virtual environment and installs all dependencies from `pyproject.toml` and `uv.lock`.

This project requires Python `3.14` or newer. If `uv sync` says Python is missing, install it with:

```bash
uv python install 3.14
uv sync
```

### 4. Create the environment file

```bash
cp .env.example .env
```

Copies the example environment file. Update `.env` with your local settings before running the app.

### 5. Run the server

```bash
uv run uvicorn app.main:app --reload
```

Starts the FastAPI development server with auto-reload enabled.

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API docs:

```text
http://127.0.0.1:8000/docs
```

## Roles

The application uses roles for protected APIs:

- `user`: default application user role.
- `admin`: required for user management APIs.
- `payment`: required for payment APIs.
- `reports`: available in dependencies for report permissions.

The app creates tables automatically on startup, but roles must exist in the database before they can be assigned. You can insert the base roles with:


## Authentication

Protected endpoints require a bearer token:

```http
Authorization: Bearer <access_token>
```

You receive tokens from register or login endpoints.

## API Documentation

### Auth APIs

#### Register

```http
POST /api/auth/register
```

Creates a new user and returns access and refresh tokens.

Request body:

```json
{
  "email": "user@example.com",
  "password": "Password@123",
  "first_name": "John",
  "last_name": "Doe",
  "role_ids": [1]
}
```

Notes:

- Password must be at least 8 characters and contain a special character.
- `first_name` and `last_name` must contain only letters and be at least 2 characters.
- The current implementation assigns the `user` role during registration.

#### Login

```http
POST /api/auth/login
```

Authenticates a user and returns access and refresh tokens.

Request body:

```json
{
  "email": "user@example.com",
  "password": "Password@123"
}
```

#### Current User

```http
GET /api/auth/me
```

Returns the authenticated user's profile and roles.

Requires authentication.

### User APIs

All user management APIs require an authenticated user with the `admin` role.

#### List Users

```http
GET /api/users/
```

Returns a list of users.

Query parameters:

- `skip`: number of records to skip. Default: `0`.
- `limit`: maximum number of records to return. Default: `100`.
- `search`: optional search by first name or last name.
- `role`: optional role filter. Case-insensitive.

Example:

```http
GET /api/users/?skip=0&limit=20&search=john&role=admin
```

#### Get User Detail

```http
GET /api/users/{user_id}
```

Returns one user by ID.

#### Create User

```http
POST /api/users/
```

Creates a new user with selected roles.

Request body:

```json
{
  "email": "admin@example.com",
  "password": "Password@123",
  "first_name": "Admin",
  "last_name": "User",
  "role_ids": [1, 2]
}
```

#### Update User

```http
PATCH /api/users/{user_id}
```

Updates user fields. All fields are optional.

Request body:

```json
{
  "password": "NewPassword@123",
  "first_name": "Updated",
  "last_name": "Name",
  "role_ids": [1, 3],
  "is_active": true
}
```

#### Delete User

```http
DELETE /api/users/{user_id}
```

Deletes a user by ID.

Returns `204 No Content` on success.

### Payment APIs

Payment routes are defined in `app/api/payments.py`, but the router is not currently included in `app/main.py`. To enable these endpoints, include the payments router in the FastAPI app.

When enabled, payment APIs require an authenticated user with the `payment` role.

#### List Payments

```http
GET /api/payments/
```

Returns payments for the authenticated payment user.

Query parameters:

- `skip`: number of records to skip. Default: `0`.
- `limit`: maximum number of records to return. Default: `100`.
- `method`: optional payment method filter. Supported values: `payme`, `click`, `uzum`.
- `min_amount`: optional minimum payment amount.
- `max_amount`: optional maximum payment amount.

Example:

```http
GET /api/payments/?skip=0&limit=10&method=payme&min_amount=100&max_amount=500
```

Payment response fields:

```json
{
  "id": 1,
  "user_id": 1,
  "amount": "100.00",
  "method": "payme",
  "status": "pending",
  "created_at": "2026-05-20T10:00:00",
  "updated_at": "2026-05-20T10:00:00"
}
```

Supported payment methods:

- `payme`
- `click`
- `uzum`

Supported payment statuses:

- `pending`
- `completed`
- `failed`

## Pagination and Filtering

The project uses simple offset pagination:

- `skip` controls how many records are skipped.
- `limit` controls how many records are returned.

Example:

```http
GET /api/users/?skip=20&limit=10
```

This returns the third page when each page contains 10 records.

Available filters:

- Users: `search`, `role`
- Payments: `method`, `min_amount`, `max_amount`
