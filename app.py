from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
import re
from pathlib import Path
from functools import wraps

try:
    from config import Config
except ModuleNotFoundError:
    Config = None

BASE_DIR = Path(__file__).resolve().parent
if (BASE_DIR / "template").is_dir():
    TEMPLATE_DIR = BASE_DIR / "template"
elif (BASE_DIR / "templates").is_dir():
    TEMPLATE_DIR = BASE_DIR / "templates"
else:
    TEMPLATE_DIR = BASE_DIR / "template"

app = Flask(__name__, template_folder=str(TEMPLATE_DIR))

if Config is not None:
    app.config.from_object(Config)

app.secret_key = app.config.get("SECRET_KEY", "infymart-secret-key")


DATABASE_BOOTSTRAP_SQL = """
drop database if exists project;
create database project;
use project;

DROP TABLE IF EXISTS  orders;
DROP TABLE IF EXISTS  products;
DROP TABLE IF EXISTS  retailers;
DROP TABLE IF EXISTS  customers;
DROP TABLE IF EXISTS  admins;
DROP TABLE IF EXISTS  coupon;
DROP TABLE IF EXISTS  cart;


create table customers(
phonenumber bigint(11)primary key,
username varchar(25) not null,
city enum('Delhi','Hyderabad','Mumbai','Kolkata','bengalore') DEFAULT 'bengalore',
password varchar(25) not null);


create table retailers(
retailer_name varchar(25) primary key,
retailer_email varchar(25) not null,
location enum('delhi','hyderabad','mumbai','kolkata','bengalore') DEFAULT 'bengalore',
category enum('wearables','household','electronics','eatables') DEFAULT 'eatables',
password varchar(25) not null);



create table admins(
email varchar(25) primary key,
admin_name varchar(25),
password varchar(25));



create table products(
product_name varchar(25) primary key ,
brand varchar(25) not null,
category varchar(25) not null,
price decimal(7,2) not null,
product_size varchar(25),
color varchar(25) not null,
rating int(11) DEFAULT 3,
discount int(11) DEFAULT 5,
show_on_homepage varchar(25) DEFAULT 'no',
FOREIGN KEY(brand) REFERENCES retailers(retailer_name));




create table orders(
order_id int(11) primary key AUTO_INCREMENT,
product_name varchar(25) not null,
phonenumber bigint(11),
order_count int(11),
status enum('cancled','delivered','pending')Default 'pending',
FOREIGN KEY(product_name) REFERENCES products(product_name),
FOREIGN KEY(phonenumber) REFERENCES customers(phonenumber))AUTO_INCREMENT=1000;


create table coupon(
coupon_name varchar(25) primary key,
coupon_discount int(11) default 5,
start_date date,
end_date date);


create table cart(
product_name varchar(25),
phonenumber bigint(11),
category varchar(25),
final_price int(11),
product_size varchar(25),
FOREIGN KEY(phonenumber) REFERENCES customers(phonenumber));







insert into customers values(9988776655,"Jhon","bengalore","Jhon@123");
insert into customers values(8433456789,"Kavya","Delhi","Kavya1234");
insert into customers values(7799456754,"Rakesh","Hyderabad","Rokz@4321");
insert into customers values(8843552345,"Swetha","Mumbai","Sweety@34");
insert into customers values(6785432312,"Mohamadh","Kolkata","Moh@madh07");
insert into customers values(9834523456,"Jenny","Mumbai","jenny#Kulu");
insert into customers values(7856231245,"Raghav","bengalore","Raghav$345");
insert into customers values(8954321267,"Priya","Delhi","Priy@#12");


insert into retailers (retailer_name,retailer_email,password) values("Nike","nikeindia@gmail.com","123XYZ");
insert into retailers (retailer_name,retailer_email,password) values("Reliance","Reliance@gmail.com","XYZ123");
insert into retailers (retailer_name,retailer_email,password) values("Trends_india","Trends_india@gmail.com","CDEF4321");
insert into retailers (retailer_name,retailer_email,password) values("Infy_products","Infy_products@gmail.com","Qwerty123");
insert into retailers (retailer_name,retailer_email,password) values("Bapple","appleindia@gmail.com","RTYU5432");


insert into admins values("infyadmin1@gmail.com","Admin 1","secretcode123");
insert into admins values("infyadmin2@gmail.com","Admin 2","code123");

insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Nike shoes","Nike","Wearables",1250,"10","Red",4,25,"yes");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Earphones","Nike","Electronics",400,"1meter","Black",3,15,"no");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Protine Cokkies","Nike","Eatables",150,"Small","brown",3,33,"no");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Treadmill","Nike","Household",9999,"Large","Dark blue",3,37,"no");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Nike T-shirt","Nike","Wearables",580,"Medium","Blue",3,45,"no");

insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Shorts","Reliance","Wearables",250,"XL","Brown",3,45,"no");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Gulab Jamun","Reliance","Eatables",200,"KG","Black",4,10,"yes");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Plum cake","Reliance","Eatables",150,"Small","brown",3,33,"no");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Sofa set","Reliance","Household",12999,"Large","Dark red",3,37,"no");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Iron box","Reliance","Electronics",980,"1200W","White",3,25,"no");

insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Formal shirt","Trends_india","Wearables",950,"XXL","Yellow",3,25,"no");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Induction","Trends_india","Electronics",1400,"1500W","Black",4,15,"yes");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Saree","Trends_india","Wearables",750,"2.5meters","pink",3,33,"no");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Dry fruits","Trends_india","Eatables",299,"250grams","brown",2,47,"no");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Chair","Trends_india","Household",680,"Medium","Blue",3,45,"no");

insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("T-shirt","Infy_products","Wearables",450,"Medium","White",3,25,"no");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Laptop","Infy_products","Electronics",40000,"i7 8gb","Black",4,15,"yes");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Chips","Infy_products","Eatables",50,"50grms","Green",3,30,"no");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Office chair","Infy_products","Household",9999,"Large","Dark blue",2,57,"no");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Mouse","Infy_products","Electronics",480,"Medium","Black",3,15,"no");

insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Bag","Bapple","Wearables",1150,"Large","Red",3,25,"no");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Phone","Bapple","Electronics",44000,"6gb","Black",3,15,"no");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Cokkies","Bapple","Eatables",150,"Small","brown",3,33,"no");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Gaming chair","Bapple","Household",29999,"Large","Dark blue",4,37,"yes");
insert into products (product_name,brand,category,price,product_size,color,rating,discount,show_on_homepage)values("Bottle","Bapple","wearables",580,"Medium","Blue",3,45,"no");




insert into coupon values ("Festival123",25,"2023-11-20","2024-01-10");
insert into coupon values ("Anniversary",30,"2023-05-08","2023-06-23");
insert into coupon values ("Summer_sale",45,"2023-04-12","2023-05-15");
"""


def get_db_connection():
    return mysql.connector.connect(
        host=app.config.get("MYSQL_HOST", "localhost"),
        user=app.config.get("MYSQL_USER", "root"),
        password=app.config.get("MYSQL_PASSWORD", ""),
        database=app.config.get("MYSQL_DB", "project"),
        port=app.config.get("MYSQL_PORT", 3306),
        use_pure=True,
    )


def get_server_connection():
    return mysql.connector.connect(
        host=app.config.get("MYSQL_HOST", "localhost"),
        user=app.config.get("MYSQL_USER", "root"),
        password=app.config.get("MYSQL_PASSWORD", ""),
        port=app.config.get("MYSQL_PORT", 3306),
        use_pure=True,
    )


def init_db_if_missing():
    db_name = app.config.get("MYSQL_DB", "project")
    connection = None
    cursor = None
    try:
        connection = get_server_connection()
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
        db_exists = cursor.fetchone() is not None
        if db_exists:
            return

        for _ in connection.cmd_query_iter(DATABASE_BOOTSTRAP_SQL):
            continue

        connection.commit()
    except Error as error:
        print(f"Database initialization failed: {error}")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def normalize_customer_city(city):
    city_map = {
        "delhi": "Delhi",
        "hyderabad": "Hyderabad",
        "mumbai": "Mumbai",
        "kolkata": "Kolkata",
        "bangalore": "bengalore",
        "bengalore": "bengalore",
    }
    return city_map.get((city or "").strip().lower(), "bengalore")


def is_valid_username(username):
    return re.fullmatch(r"[A-Za-z ]{2,25}", username or "") is not None


def is_valid_city(city):
    return (city or "").strip().lower() in {"delhi", "hyderabad", "mumbai", "kolkata", "bangalore", "bengalore"}


def is_valid_mobile(phone):
    return re.fullmatch(r"[6-9]\d{9}", phone or "") is not None


def is_valid_password(password):
    return re.fullmatch(r"(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}", password or "") is not None


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "customer_phone" not in session:
            return redirect(url_for("customer_login"))
        return view_func(*args, **kwargs)

    return wrapper


init_db_if_missing()

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/retailer_login")
def retailer_login():
    return render_template("retailer_login.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/customer_login", methods=["GET","POST"])
def customer_login():

    message = ""

    if request.method == "POST":

        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()

        if phone == "" or password == "":
            message = "Please fill all the fields!"
        else:
            connection = None
            cursor = None
            try:
                connection = get_db_connection()
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    "SELECT phonenumber, username, password FROM customers WHERE phonenumber = %s",
                    (phone,),
                )
                customer = cursor.fetchone()

                if not customer:
                    message = "You are not authorized to login!"
                elif customer["password"] != password:
                    message = "Please enter the correct password!"
                else:
                    session["customer_phone"] = str(customer["phonenumber"])
                    session["customer_name"] = customer["username"]
                    return redirect(url_for("customer_home"))
            except Error:
                message = "Database connection failed!"
            finally:
                if cursor is not None:
                    cursor.close()
                if connection is not None and connection.is_connected():
                    connection.close()

    return render_template("customer.html", message=message)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    message = ""

    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        username = request.form.get("username", "").strip()
        city = request.form.get("city", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not phone or not username or not city or not password or not confirm_password:
            message = "Please fill all the fields!"
        elif not is_valid_username(username):
            message = "Please fill all the fields!"
        elif not is_valid_city(city):
            message = "Please fill all the fields!"
        elif not is_valid_mobile(phone):
            message = "Incorrect Mobile number"
        elif not is_valid_password(password):
            message = "Incorrect Password"
        elif password != confirm_password:
            message = "Passwords do not match!"
        else:
            connection = None
            cursor = None
            try:
                normalized_city = normalize_customer_city(city)
                connection = get_db_connection()
                cursor = connection.cursor()
                cursor.execute("SELECT phonenumber FROM customers WHERE phonenumber = %s", (phone,))
                existing = cursor.fetchone()

                if existing:
                    message = "Mobile number already exists"
                else:
                    cursor.execute(
                        "INSERT INTO customers (phonenumber, username, city, password) VALUES (%s, %s, %s, %s)",
                        (phone, username, normalized_city, password),
                    )
                    connection.commit()
                    message = "Registration is done successfully"
            except Error:
                message = "Database connection failed!"
            finally:
                if cursor is not None:
                    cursor.close()
                if connection is not None and connection.is_connected():
                    connection.close()

    return render_template("signup.html", message=message)


@app.route("/customer_home")
@login_required
def customer_home():
    selected_category = request.args.get("category", "")
    message = request.args.get("message", "")

    connection = None
    cursor = None
    categories = []
    products = []
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
        categories = [row["category"] for row in cursor.fetchall()]

        if selected_category:
            cursor.execute(
                "SELECT product_name, brand, category, price, product_size, color, rating, discount FROM products WHERE LOWER(category)=LOWER(%s) ORDER BY product_name",
                (selected_category,),
            )
        else:
            cursor.execute(
                "SELECT product_name, brand, category, price, product_size, color, rating, discount FROM products ORDER BY product_name"
            )
        products = cursor.fetchall()
    except Error:
        message = "Database connection failed!"
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

    return render_template(
        "customer_home.html",
        categories=categories,
        products=products,
        selected_category=selected_category,
        message=message,
        customer_name=session.get("customer_name", "Customer"),
    )


@app.route("/add_to_cart", methods=["POST"])
@login_required
def add_to_cart():
    product_name = request.form.get("product_name", "").strip()
    if not product_name:
        return redirect(url_for("customer_home", message="Please fill all the fields!"))

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT product_name, category, price, discount, product_size FROM products WHERE product_name=%s",
            (product_name,),
        )
        product = cursor.fetchone()

        if not product:
            return redirect(url_for("customer_home", message="Product not found"))

        discounted_price = int(product["price"] - (product["price"] * product["discount"] / 100))
        cursor.execute(
            "INSERT INTO cart (product_name, phonenumber, category, final_price, product_size) VALUES (%s, %s, %s, %s, %s)",
            (
                product["product_name"],
                session["customer_phone"],
                product["category"],
                discounted_price,
                product["product_size"],
            ),
        )
        connection.commit()
        return redirect(url_for("customer_home", message="Product added to cart successfully"))
    except Error:
        return redirect(url_for("customer_home", message="Database connection failed!"))
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/cart")
@login_required
def cart_view():
    message = request.args.get("message", "")
    coupon_discount = int(session.get("coupon_discount", 0))

    connection = None
    cursor = None
    cart_items = []
    coupons = []
    total_price = 0
    final_price = 0
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT product_name, category, final_price, product_size FROM cart WHERE phonenumber=%s",
            (session["customer_phone"],),
        )
        cart_items = cursor.fetchall()

        total_price = sum(item["final_price"] for item in cart_items)
        final_price = int(total_price - (total_price * coupon_discount) / 100)

        cursor.execute("SELECT coupon_name, coupon_discount FROM coupon ORDER BY coupon_name")
        coupons = cursor.fetchall()
    except Error:
        message = "Database connection failed!"
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

    return render_template(
        "cart.html",
        cart_items=cart_items,
        coupons=coupons,
        total_price=total_price,
        final_price=final_price,
        coupon_discount=coupon_discount,
        applied_coupon=session.get("coupon_name", ""),
        message=message,
    )


@app.route("/remove_cart_item", methods=["POST"])
@login_required
def remove_cart_item():
    product_name = request.form.get("product_name", "").strip()

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM cart WHERE phonenumber=%s AND product_name=%s LIMIT 1",
            (session["customer_phone"], product_name),
        )
        connection.commit()
        return redirect(url_for("cart_view", message="Product removed from cart"))
    except Error:
        return redirect(url_for("cart_view", message="Database connection failed!"))
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/apply_coupon", methods=["POST"])
@login_required
def apply_coupon():
    coupon_name = request.form.get("coupon_name", "").strip()
    if not coupon_name:
        return redirect(url_for("cart_view", message="Please fill all the fields!"))

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT coupon_discount FROM coupon WHERE coupon_name=%s", (coupon_name,))
        coupon = cursor.fetchone()

        if not coupon:
            return redirect(url_for("cart_view", message="Invalid coupon"))

        session["coupon_name"] = coupon_name
        session["coupon_discount"] = int(coupon["coupon_discount"])
        return redirect(url_for("cart_view", message="coupon applied successfully"))
    except Error:
        return redirect(url_for("cart_view", message="Database connection failed!"))
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/place_order", methods=["POST"])
@login_required
def place_order():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT product_name FROM cart WHERE phonenumber=%s",
            (session["customer_phone"],),
        )
        cart_items = cursor.fetchall()

        if not cart_items:
            return redirect(url_for("cart_view", message="Cart is empty"))

        for item in cart_items:
            cursor.execute(
                "INSERT INTO orders (product_name, phonenumber, order_count, status) VALUES (%s, %s, %s, %s)",
                (item["product_name"], session["customer_phone"], 1, "pending"),
            )

        cursor.execute("DELETE FROM cart WHERE phonenumber=%s", (session["customer_phone"],))
        connection.commit()

        session.pop("coupon_name", None)
        session.pop("coupon_discount", None)
        return redirect(url_for("cart_view", message="Ordered placed successfully"))
    except Error:
        return redirect(url_for("cart_view", message="Database connection failed!"))
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/history")
@login_required
def order_history():
    message = ""
    orders = []

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT order_id, product_name, order_count, status FROM orders WHERE phonenumber=%s ORDER BY order_id DESC",
            (session["customer_phone"],),
        )
        orders = cursor.fetchall()
    except Error:
        message = "Database connection failed!"
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

    return render_template("history.html", orders=orders, message=message)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/api/health", methods=["GET"])
def api_health():
    connection = None
    try:
        connection = get_db_connection()
        return jsonify({"status": "ok", "database": "connected"}), 200
    except Error as error:
        return jsonify({"status": "error", "database": str(error)}), 500
    finally:
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/api/customers/signup", methods=["POST"])
def api_signup():
    data = request.get_json(silent=True) or {}
    phone = (data.get("phone") or "").strip()
    username = (data.get("username") or "").strip()
    city = (data.get("city") or "").strip()
    password = (data.get("password") or "").strip()

    if not phone or not username or not city or not password:
        return jsonify({"message": "phone, username, city and password are required"}), 400
    if not is_valid_username(username) or not is_valid_city(city):
        return jsonify({"message": "Invalid username or city"}), 400
    if not is_valid_mobile(phone):
        return jsonify({"message": "Incorrect Mobile number"}), 400
    if not is_valid_password(password):
        return jsonify({"message": "Incorrect Password"}), 400

    connection = None
    cursor = None
    try:
        normalized_city = normalize_customer_city(city)
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT phonenumber FROM customers WHERE phonenumber = %s", (phone,))
        existing = cursor.fetchone()

        if existing:
            return jsonify({"message": "Mobile number already exists"}), 409

        cursor.execute(
            "INSERT INTO customers (phonenumber, username, city, password) VALUES (%s, %s, %s, %s)",
            (phone, username, normalized_city, password),
        )
        connection.commit()
        return jsonify({"message": "Customer registered successfully"}), 201
    except Error as error:
        return jsonify({"message": "Database operation failed", "error": str(error)}), 500
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/api/customers/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    phone = (data.get("phone") or "").strip()
    password = (data.get("password") or "").strip()

    if not phone or not password:
        return jsonify({"message": "phone and password are required"}), 400

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT phonenumber, username, city, password FROM customers WHERE phonenumber = %s",
            (phone,),
        )
        customer = cursor.fetchone()

        if not customer or customer["password"] != password:
            return jsonify({"message": "Invalid phone or password"}), 401

        return jsonify(
            {
                "message": "Login successful",
                "customer": {
                    "phone": customer["phonenumber"],
                    "username": customer["username"],
                    "city": customer["city"],
                },
            }
        ), 200
    except Error as error:
        return jsonify({"message": "Database operation failed", "error": str(error)}), 500
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    app.run(debug=True)