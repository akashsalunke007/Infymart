# Infymart Flask App

Infymart is a Flask + MySQL shopping app with HTML pages and JSON APIs.

## Prerequisites

- Python 3.10+
- MySQL 8+
- macOS (commands below use `brew` for MySQL service)

## 1) Clone and open project

```bash
git clone git@github-akashsalunke007:akashsalunke007/Infymart.git
cd Infymart
```

## 2) Create virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Configure environment variables

Create a `.env` file in project root:

```env
SECRET_KEY=infymart-secret-key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=project
MYSQL_PORT=3306
MYSQL_AUTOCOMMIT=True
```

## 4) Start MySQL

### macOS (Homebrew)

```bash
brew services start mysql
```

### Windows (MySQL Workbench)

- Open **MySQL Workbench** and connect to your local MySQL server (for example, `localhost:3306`).
- Make sure the MySQL server service is running:
    - Open `services.msc`
    - Start `MySQL80` (service name may vary, like `MySQL`)

Optional command-line check (Windows CMD):

```bat
mysql -u root -p -e "SELECT VERSION();"
```

Verify (macOS/Linux):

```bash
mysql -u root -e "SELECT VERSION();"
```

## 5) Run the Flask app

```bash
source .venv/bin/activate
python -m flask --app app run --port 5000
```

Open in browser:

- http://127.0.0.1:5000/

## Database bootstrap behavior

On app startup, `init_db_if_missing()` checks for database `project`.
If missing, it executes bootstrap SQL in `app.py` and seeds sample data.

> Note: bootstrap SQL includes `drop database if exists project;`.
> Use caution if you already have important data with this DB name.

## Useful API checks

Health:

```bash
curl -s http://127.0.0.1:5000/api/health
```

Customer signup (JSON):

```bash
curl -s -X POST http://127.0.0.1:5000/api/customers/signup \
  -H 'Content-Type: application/json' \
  -d '{"phone":"9876543210","username":"Akash","city":"Delhi","password":"Abcd@123"}'
```

Customer login (JSON):

```bash
curl -s -X POST http://127.0.0.1:5000/api/customers/login \
  -H 'Content-Type: application/json' \
  -d '{"phone":"9876543210","password":"Abcd@123"}'
```

## Main routes

- `/` - home page
- `/customer_login` - customer login page
- `/signup` - customer signup page
- `/admin_login` - admin login page
- `/retailer_login` - retailer login page
- `/api/health` - DB health check
- `/api/customers/signup` - customer signup API
- `/api/customers/login` - customer login API
