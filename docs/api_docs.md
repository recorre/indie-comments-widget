# API documentation for 41300_teste
**Version:** 1.0.0

> API documentation for 41300_teste


## `/create/comments?Instance=41300_teste`

### POST
**Summary:** Create a new record in comments

**Description:** —

#### Parameters:
- **None** () — required: ❌

#### Request Body:
- Content-Type: `application/json`
  - **thread_referencia_id** (integer) — required: ❌ — 
  - **parent_id** (integer) — required: ❌ — 
  - **author_name** (string) — required: ❌ — 
  - **author_email_hash** (string) — required: ❌ — 
  - **content** (string) — required: ❌ — 
  - **created_at** (string) — required: ❌ — 
  - **is_approved** (integer) — required: ❌ — 

#### Responses:
- **201** — Successfully created the record
- **400** — Bad Request
- **500** — Server error

## `/read/comments?Instance=41300_teste`

### GET
**Summary:** Retrieve all records from comments

**Description:** ### Filtering and query options

Use query parameters to filter results. Operators use bracket notation:

| Operator | Example | Meaning |
|---|---|---|
| `field` | `?status=active` | Equal (default) |
| `field[ne]` | `?status[ne]=inactive` | Not equal |
| `field[gt]` | `?price[gt]=100` | Greater than |
| `field[gte]` | `?date[gte]=2024-05-01` | Greater than or equal |
| `field[lt]` | `?score[lt]=500` | Less than |
| `field[lte]` | `?score[lte]=800` | Less than or equal |
| `field[in]` | `?type[in]=a,b,c` | In list (comma-separated) |
| `field[like]` | `?name[like]=john` | Partial match |

**Examples**
- `?price[gte]=100&price[lte]=200`
- `?name[like]=john`
- `?status=active`

**Additional helpers**
- **Pagination**: `page`, `limit` (defaults 1, 10)
- **Totals**: `includeTotal=true` adds `total` and `totalPages`
- **Sorting**: `sort=colA,colB`, `order=asc,desc`
- **Single record**: `only=latest` or `only=oldest` (optional `by=column`, defaults `id`)

#### Parameters:
- **None** () — required: ❌

#### Responses:
- **200** — Successfully retrieved records
- **400** — Bad Request
- **500** — Server error

## `/read/comments/{id}?Instance=41300_teste`

### GET
**Summary:** Retrieve a record by ID from comments

**Description:** —

#### Parameters:
- **None** () — required: ❌
- **id** (integer) — required: ✅

#### Responses:
- **200** — Successfully retrieved the record
- **400** — Bad Request
- **404** — Record Not Found
- **500** — Server error

## `/search/comments?Instance=41300_teste`

### POST
**Summary:** Search for records in comments

**Description:** —

#### Parameters:
- **None** () — required: ❌

#### Request Body:
- Content-Type: `application/json`
  - **thread_referencia_id** (integer) — required: ❌ — 
  - **parent_id** (integer) — required: ❌ — 
  - **author_name** (string) — required: ❌ — 
  - **author_email_hash** (string) — required: ❌ — 
  - **content** (string) — required: ❌ — 
  - **created_at** (string) — required: ❌ — 
  - **is_approved** (integer) — required: ❌ — 

#### Responses:
- **200** — Successfully retrieved matching records
- **400** — Bad Request
- **500** — Server error

## `/update/comments/{id}?Instance=41300_teste`

### PUT
**Summary:** Update a record in comments

**Description:** —

#### Parameters:
- **None** () — required: ❌
- **id** (integer) — required: ✅

#### Request Body:
- Content-Type: `application/json`
  - **thread_referencia_id** (integer) — required: ❌ — 
  - **parent_id** (integer) — required: ❌ — 
  - **author_name** (string) — required: ❌ — 
  - **author_email_hash** (string) — required: ❌ — 
  - **content** (string) — required: ❌ — 
  - **created_at** (string) — required: ❌ — 
  - **is_approved** (integer) — required: ❌ — 

#### Responses:
- **200** — Successfully updated the record
- **400** — Bad Request
- **500** — Server error

## `/delete/comments/{id}?Instance=41300_teste`

### DELETE
**Summary:** Delete a record from comments

**Description:** —

#### Parameters:
- **None** () — required: ❌
- **id** (integer) — required: ✅

#### Responses:
- **200** — Successfully deleted the record
- **400** — Bad Request
- **404** — Record Not Found
- **500** — Server error

## `/create/threads?Instance=41300_teste`

### POST
**Summary:** Create a new record in threads

**Description:** —

#### Parameters:
- **None** () — required: ❌

#### Request Body:
- Content-Type: `application/json`
  - **usuario_proprietario_id** (integer) — required: ❌ — 
  - **external_page_id** (string) — required: ❌ — 
  - **url** (string) — required: ❌ — 
  - **title** (string) — required: ❌ — 

#### Responses:
- **201** — Successfully created the record
- **400** — Bad Request
- **500** — Server error

## `/read/threads?Instance=41300_teste`

### GET
**Summary:** Retrieve all records from threads

**Description:** ### Filtering and query options

Use query parameters to filter results. Operators use bracket notation:

| Operator | Example | Meaning |
|---|---|---|
| `field` | `?status=active` | Equal (default) |
| `field[ne]` | `?status[ne]=inactive` | Not equal |
| `field[gt]` | `?price[gt]=100` | Greater than |
| `field[gte]` | `?date[gte]=2024-05-01` | Greater than or equal |
| `field[lt]` | `?score[lt]=500` | Less than |
| `field[lte]` | `?score[lte]=800` | Less than or equal |
| `field[in]` | `?type[in]=a,b,c` | In list (comma-separated) |
| `field[like]` | `?name[like]=john` | Partial match |

**Examples**
- `?price[gte]=100&price[lte]=200`
- `?name[like]=john`
- `?status=active`

**Additional helpers**
- **Pagination**: `page`, `limit` (defaults 1, 10)
- **Totals**: `includeTotal=true` adds `total` and `totalPages`
- **Sorting**: `sort=colA,colB`, `order=asc,desc`
- **Single record**: `only=latest` or `only=oldest` (optional `by=column`, defaults `id`)

#### Parameters:
- **None** () — required: ❌

#### Responses:
- **200** — Successfully retrieved records
- **400** — Bad Request
- **500** — Server error

## `/read/threads/{id}?Instance=41300_teste`

### GET
**Summary:** Retrieve a record by ID from threads

**Description:** —

#### Parameters:
- **None** () — required: ❌
- **id** (integer) — required: ✅

#### Responses:
- **200** — Successfully retrieved the record
- **400** — Bad Request
- **404** — Record Not Found
- **500** — Server error

## `/search/threads?Instance=41300_teste`

### POST
**Summary:** Search for records in threads

**Description:** —

#### Parameters:
- **None** () — required: ❌

#### Request Body:
- Content-Type: `application/json`
  - **usuario_proprietario_id** (integer) — required: ❌ — 
  - **external_page_id** (string) — required: ❌ — 
  - **url** (string) — required: ❌ — 
  - **title** (string) — required: ❌ — 

#### Responses:
- **200** — Successfully retrieved matching records
- **400** — Bad Request
- **500** — Server error

## `/update/threads/{id}?Instance=41300_teste`

### PUT
**Summary:** Update a record in threads

**Description:** —

#### Parameters:
- **None** () — required: ❌
- **id** (integer) — required: ✅

#### Request Body:
- Content-Type: `application/json`
  - **usuario_proprietario_id** (integer) — required: ❌ — 
  - **external_page_id** (string) — required: ❌ — 
  - **url** (string) — required: ❌ — 
  - **title** (string) — required: ❌ — 

#### Responses:
- **200** — Successfully updated the record
- **400** — Bad Request
- **500** — Server error

## `/delete/threads/{id}?Instance=41300_teste`

### DELETE
**Summary:** Delete a record from threads

**Description:** —

#### Parameters:
- **None** () — required: ❌
- **id** (integer) — required: ✅

#### Responses:
- **200** — Successfully deleted the record
- **400** — Bad Request
- **404** — Record Not Found
- **500** — Server error

## `/create/users?Instance=41300_teste`

### POST
**Summary:** Create a new record in users

**Description:** —

#### Parameters:
- **None** () — required: ❌

#### Request Body:
- Content-Type: `application/json`
  - **email** (string) — required: ❌ — 
  - **password_hash** (string) — required: ❌ — 
  - **api_key** (string) — required: ❌ — 
  - **plan_level** (string) — required: ❌ — 
  - **is_supporter** (integer) — required: ❌ — 
  - **name** (string) — required: ❌ — 

#### Responses:
- **201** — Successfully created the record
- **400** — Bad Request
- **500** — Server error

## `/read/users?Instance=41300_teste`

### GET
**Summary:** Retrieve all records from users

**Description:** ### Filtering and query options

Use query parameters to filter results. Operators use bracket notation:

| Operator | Example | Meaning |
|---|---|---|
| `field` | `?status=active` | Equal (default) |
| `field[ne]` | `?status[ne]=inactive` | Not equal |
| `field[gt]` | `?price[gt]=100` | Greater than |
| `field[gte]` | `?date[gte]=2024-05-01` | Greater than or equal |
| `field[lt]` | `?score[lt]=500` | Less than |
| `field[lte]` | `?score[lte]=800` | Less than or equal |
| `field[in]` | `?type[in]=a,b,c` | In list (comma-separated) |
| `field[like]` | `?name[like]=john` | Partial match |

**Examples**
- `?price[gte]=100&price[lte]=200`
- `?name[like]=john`
- `?status=active`

**Additional helpers**
- **Pagination**: `page`, `limit` (defaults 1, 10)
- **Totals**: `includeTotal=true` adds `total` and `totalPages`
- **Sorting**: `sort=colA,colB`, `order=asc,desc`
- **Single record**: `only=latest` or `only=oldest` (optional `by=column`, defaults `id`)

#### Parameters:
- **None** () — required: ❌

#### Responses:
- **200** — Successfully retrieved records
- **400** — Bad Request
- **500** — Server error

## `/read/users/{id}?Instance=41300_teste`

### GET
**Summary:** Retrieve a record by ID from users

**Description:** —

#### Parameters:
- **None** () — required: ❌
- **id** (integer) — required: ✅

#### Responses:
- **200** — Successfully retrieved the record
- **400** — Bad Request
- **404** — Record Not Found
- **500** — Server error

## `/search/users?Instance=41300_teste`

### POST
**Summary:** Search for records in users

**Description:** —

#### Parameters:
- **None** () — required: ❌

#### Request Body:
- Content-Type: `application/json`
  - **email** (string) — required: ❌ — 
  - **password_hash** (string) — required: ❌ — 
  - **api_key** (string) — required: ❌ — 
  - **plan_level** (string) — required: ❌ — 
  - **is_supporter** (integer) — required: ❌ — 
  - **name** (string) — required: ❌ — 

#### Responses:
- **200** — Successfully retrieved matching records
- **400** — Bad Request
- **500** — Server error

## `/update/users/{id}?Instance=41300_teste`

### PUT
**Summary:** Update a record in users

**Description:** —

#### Parameters:
- **None** () — required: ❌
- **id** (integer) — required: ✅

#### Request Body:
- Content-Type: `application/json`
  - **email** (string) — required: ❌ — 
  - **password_hash** (string) — required: ❌ — 
  - **api_key** (string) — required: ❌ — 
  - **plan_level** (string) — required: ❌ — 
  - **is_supporter** (integer) — required: ❌ — 
  - **name** (string) — required: ❌ — 

#### Responses:
- **200** — Successfully updated the record
- **400** — Bad Request
- **500** — Server error

## `/delete/users/{id}?Instance=41300_teste`

### DELETE
**Summary:** Delete a record from users

**Description:** —

#### Parameters:
- **None** () — required: ❌
- **id** (integer) — required: ✅

#### Responses:
- **200** — Successfully deleted the record
- **400** — Bad Request
- **404** — Record Not Found
- **500** — Server error

## `/read/join/admin_comments_view?Instance=41300_teste`

### GET
**Summary:** Retrieve records from join view 'admin_comments_view'

**Description:** ### Filtering and query options

                Use query parameters to filter results. Operators use bracket notation:

                | Operator | Example | Meaning |
                |---|---|---|
                | `field` | `?status=active` | Equal (default) |
                | `field[ne]` | `?status[ne]=inactive` | Not equal |
                | `field[gt]` | `?price[gt]=100` | Greater than |
                | `field[gte]` | `?date[gte]=2024-05-01` | Greater than or equal |
                | `field[lt]` | `?score[lt]=500` | Less than |
                | `field[lte]` | `?score[lte]=800` | Less than or equal |
                | `field[in]` | `?type[in]=a,b,c` | In list (comma‑separated) |
                | `field[like]` | `?name[like]=john` | Partial match |

                **Examples**
                - `?price[gte]=100&price[lte]=200`
                - `?name[like]=john`
                - `?status=active`

#### Parameters:
- **None** () — required: ❌

#### Responses:
- **200** — Successfully retrieved join records
- **400** — Bad Request
- **404** — Join configuration not found
- **500** — Server error