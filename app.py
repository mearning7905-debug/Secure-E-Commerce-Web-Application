from flask import Flask, jsonify, render_template, request, session, redirect, url_for, flash, send_file
import random
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import io
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# app.secret_key = "secret123"
app.secret_key = os.environ.get("SECRET_KEY", "secret123")

# Absolute DB path - fixes PythonAnywhere deployment
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smartpay_final.db")

# --- DATABASE CONNECTION ---
def get_db():
    conn = sqlite3.connect("smartpay_final.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- INITIALIZE DATABASE ---
def init_db():
    conn = get_db()
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        username TEXT,
        email TEXT UNIQUE,
        mobile TEXT,
        card TEXT,
        password TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        item_name TEXT,
        card_last4 TEXT,
        bank_name TEXT,
        payment_method TEXT,
        amount REAL,
        status TEXT,
        time TEXT
    )
    """)

    # 3. ADMIN TABLE
    conn.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    # 4. OTP TABLE
    conn.execute("""
    CREATE TABLE IF NOT EXISTS otp (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        otp TEXT,
        created_at TEXT
    )
    """)
    
    # 5. FRAUD LOGS TABLE
    conn.execute("""
    CREATE TABLE IF NOT EXISTS fraud_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        user_id INTEGER,
        entered_name TEXT,
        registered_name TEXT,
        entered_card_last4 TEXT,
        stored_card_last4 TEXT,
        fraud_reason TEXT,
        admin_notes TEXT,
        timestamp TEXT,
        amount REAL
    )
    """)
    
    # Default Admin insert
    conn.execute("INSERT OR IGNORE INTO admin (username, password) VALUES (?, ?)", ("Admin", "1234"))

    conn.commit()
    conn.close()


products = [
    # ========= AC SERIES =========
    {"id": 1, "name": "AC", "price": 92000, "image": "images/ac.jpg"},
    {"id": 2, "name": "Fridge", "price": 90000, "image": "images/fridge1.jpg"},
    {"id": 3,"name": "Washing Machine","price": 25000,"image": "images/washingmachine.jpg",},
    {"id": 4, "name": "TV", "price": 85000, "image": "images/tv1.jpg"},
    {"id": 5, "name": "Headphones", "price": 2500, "image": "images/headphone.jpg"},
    {"id": 6, "name": "Phone", "price": 125000, "image": "images/phone1.jpg"},
    {"id": 7, "name": "AC", "price": 60000, "image": "images/ac1.jpg"},
    {"id": 8, "name": "Oven", "price": 8000, "image": "images/oven.jpg"},
    {"id": 9, "name": "TV", "price": 30000, "image": "images/tv1.jpg"},
    {"id": 10, "name": "Fridge", "price": 80000, "image": "images/fridge2.jpg"},
    {"id": 11, "name": "Printer", "price": 6000, "image": "images/printer.jpg"},
    {"id": 12, "name": "Laptop", "price": 55000, "image": "images/laptop.jpg"},
    {"id": 13, "name": "Speaker", "price": 4500, "image": "images/speaker.jpg"},
    {"id": 14, "name": "Computer", "price": 50000, "image": "images/computer.jpg"},
    {"id": 15, "name": "Electric Kettle", "price": 1200, "image": "images/kettle.jpg"},
    {"id": 16, "name": "USB Drive", "price": 600, "image": "images/usb.jpg"},
    {"id": 17, "name": "Hard Drive", "price": 4000, "image": "images/hard drive.jpg"},
    {"id": 18, "name": "Keyboard", "price": 800, "image": "images/keyboard.jpg"},
    {"id": 19, "name": "Camera", "price": 25000, "image": "images/camera.jpg"},
    {"id": 20, "name": "Router", "price": 3000, "image": "images/router.jpg"},
    {"id": 21, "name": "Projector", "price": 40000, "image": "images/projector.jpg"},
    {"id": 22,"name": "Game Console","price": 30000,"image": "images/gameconsole.jpg",},
    {"id": 23, "name": "Power Bank", "price": 1200, "image": "images/powerbank.jpg"},
    {"id": 24, "name": "Smart Watch", "price": 8000, "image": "images/watch.jpg"},
    {"id": 25, "name": "Tablet", "price": 20000, "image": "images/tablet.jpg"},
    {"id": 26, "name": "AC", "price": 92000, "image": "images/ac2.jpg"},
    {"id": 27, "name": "AC", "price": 92000, "image": "images/ac3.jpg"},
    {"id": 28, "name": "AC", "price": 92000, "image": "images/ac4.jpg"},
    {"id": 29, "name": "AC", "price": 92000, "image": "images/ac5.jpg"},
    {"id": 30, "name": "AC", "price": 92000, "image": "images/ac6.jpg"},
    {"id": 31, "name": "AC", "price": 92000, "image": "images/ac7.jpg"},
    {"id": 32, "name": "AC", "price": 92000, "image": "images/ac8.jpg"},
    {"id": 33, "name": "AC", "price": 92000, "image": "images/ac9.jpg"},
    {"id": 34, "name": "AC", "price": 92000, "image": "images/ac10.jpg"},
    {"id": 35, "name": "AC", "price": 92000, "image": "images/ac11.jpg"},
    {"id": 36, "name": "AC", "price": 92000, "image": "images/ac12.jpg"},
    {"id": 37, "name": "AC", "price": 92000, "image": "images/ac13.jpg"},
    {"id": 38, "name": "AC", "price": 92000, "image": "images/ac14.jpg"},
    {"id": 39, "name": "Fridge", "price": 35000, "image": "images/fridge3.jpg"},
    {"id": 40, "name": "Fridge", "price": 35000, "image": "images/fridge4.jpg"},
    {"id": 41, "name": "Fridge", "price": 35000, "image": "images/fridge5.jpg"},
    {"id": 42, "name": "Fridge", "price": 35000, "image": "images/fridge6.jpg"},
    {"id": 43, "name": "Fridge", "price": 35000, "image": "images/fridge7.jpg"},
    {"id": 44, "name": "Fridge", "price": 35000, "image": "images/fridge8.jpg"},
    {"id": 45, "name": "Fridge", "price": 35000, "image": "images/fridge9.jpg"},
    {"id": 46, "name": "Fridge", "price": 35000, "image": "images/fridge10.jpg"},
    {"id": 47, "name": "Fridge", "price": 35000, "image": "images/fridge11.jpg"},
    {"id": 48, "name": "Fridge", "price": 35000, "image": "images/fridge12.jpg"},
    {"id": 49,"name": "Washing Machine","price": 25000,"image": "images/washingmachine1.jpg",},
    {"id": 50,"name": "Washing Machine","price": 25000,"image": "images/washingmachine2.jpg",},    
    {"id": 51,"name": "Washing Machine","price": 25000,"image": "images/washingmachine3.jpg",},
    {"id": 52,"name": "Washing Machine","price": 25000,"image": "images/washingmachine4.jpg",},
    {"id": 53,"name": "Washing Machine","price": 25000,"image": "images/washingmachine5.jpg",},
    {"id": 54,"name": "Washing Machine","price": 25000,"image": "images/washingmachine6.jpg",},
    {"id": 55,"name": "Washing Machine","price": 25000,"image": "images/washingmachine7.jpg",},
    {"id": 56,"name": "Washing Machine","price": 25000,"image": "images/washingmachine8.jpg",},
    {"id": 58,"name": "Washing Machine","price": 25000,"image": "images/washingmachine10.jpg",},
    {"id": 59,"name": "Washing Machine","price": 25000,"image": "images/washingmachine11.jpg",},
    {"id": 60,"name": "Washing Machine","price": 25000,"image": "images/washingmachine12.jpg",},
    {"id": 61, "name": "TV", "price": 30000, "image": "images/tv1.jpg"},
    {"id": 62, "name": "TV", "price": 30000, "image": "images/tv2.jpg"},
    {"id": 63, "name": "TV", "price": 30000, "image": "images/tv3.jpg"},
    {"id": 64, "name": "TV", "price": 30000, "image": "images/tv4.jpg"},
    {"id": 65, "name": "TV", "price": 30000, "image": "images/tv5.jpg"},
    {"id": 66, "name": "TV", "price": 30000, "image": "images/tv6.jpg"},
    {"id": 67, "name": "TV", "price": 30000, "image": "images/tv7.jpg"},
    {"id": 68, "name": "TV", "price": 30000, "image": "images/tv8.jpg"},
    {"id": 69, "name": "TV", "price": 30000, "image": "images/tv9.jpg"},
    {"id": 70, "name": "Headphones", "price": 2500, "image": "images/headphone2.jpg"},
    {"id": 71, "name": "Headphones", "price": 2500, "image": "images/headphone3.jpg"},
    {"id": 72, "name": "Headphones", "price": 2500, "image": "images/headphone4.jpg"},
    {"id": 73, "name": "Headphones", "price": 2500, "image": "images/headphone5.jpg"},
    {"id": 74, "name": "Headphones", "price": 2500, "image": "images/headphone6.jpg"},
    {"id": 75, "name": "Headphones", "price": 2500, "image": "images/headphone7.jpg"},
    {"id": 76, "name": "Headphones", "price": 2500, "image": "images/headphone8.jpg"},
    {"id": 77, "name": "Headphones", "price": 2500, "image": "images/headphone9.jpg"},
    {"id": 78, "name": "Headphones", "price": 2500, "image": "images/headphone10.jpg"},
    {"id": 79, "name": "Phone", "price": 35000, "image": "images/phone2.jpg"},
    {"id": 80, "name": "Phone", "price": 35000, "image": "images/phone3.jpg"},
    {"id": 81, "name": "Phone", "price": 35000, "image": "images/phone4.jpg"},
    {"id": 82, "name": "Phone", "price": 35000, "image": "images/phone5.jpg"},
    {"id": 83, "name": "Phone", "price": 35000, "image": "images/phone6.jpg"},
    {"id": 84, "name": "Phone", "price": 35000, "image": "images/phone7.jpg"},
    {"id": 85, "name": "Phone", "price": 35000, "image": "images/phone8.jpg"},
    {"id": 86, "name": "Phone", "price": 35000, "image": "images/phone9.jpg"},
    {"id": 87, "name": "Phone", "price": 35000, "image": "images/phone10.jpg"},
    {"id": 88, "name": "Phone", "price": 35000, "image": "images/phone11.jpg"},
    {"id": 89, "name": "Phone", "price": 35000, "image": "images/phone12.jpg"},
]

# --- Signup Route ---
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        card = request.form.get("card")
        mobile = request.form.get("mobile")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if password != confirm:
            flash("❌ Passwords do not match!", "danger")
            return redirect(url_for("signup"))

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        
        if user:
            conn.close()
            flash("⚠ User already exists. Please login.", "warning")
            return redirect(url_for("login"))

        card_last4 = card[-4:]
        # Insert new user with full_name
        conn.execute(
            "INSERT INTO users (username, email, card, mobile, password) VALUES (?,?,?,?,?)",
            (username, email, card_last4, mobile, generate_password_hash(password))
        )
        conn.commit()
        conn.close()

        # Set session data to "log in" the user immediately
        session["user_email"] = email
        session['card_last4'] = card[-4:]
        # session['username'] = username

        # # If user came from buying flow, continue to checkout
        if session.get('pending_checkout'):
            return redirect(url_for('checkout'))

        return redirect(url_for("dashboard"))
    return render_template("signup.html")

# --- Login Route ---
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        # 🔥 SAFETY CHECK
        if not email or not password:
            flash("❌ Please enter all fields", "danger")
            return redirect(url_for("login"))

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()

        conn.close()

        # 🔥 MAIN LOGIN CHECK
        if user is not None:
            if check_password_hash(user["password"], password):

                session["user_email"] = email
                session["card_last4"] = user["card"]
                session["username"] = user["username"]

                # ✅ IF USER WAS BUYING PRODUCT
                if session.get("pending_checkout"):
                    return redirect(url_for("checkout"))

                return redirect(url_for("dashboard"))

        # ❌ LOGIN FAILED
        flash("❌ Invalid Email or Password", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---- User dashboard ----- 
@app.route("/dashboard")
def dashboard():
    if "user_email" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for("login"))

    email = session["user_email"]
    conn = get_db()

    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    
    if user:
        session["card_last4"] = user["card"]
        session["username"] = user["username"]
    
    transactions = conn.execute("SELECT * FROM transactions WHERE email = ?", (email,)).fetchall()
    conn.close()

    # Fetch cart items
    cart = session.get("cart", {})
    cart_items = []
    subtotal = 0

    for pid, qty in cart.items():
        product = next((p for p in products if p["id"] == int(pid)), None)
        if product:
            price = product["price"]
            total = price * qty
            subtotal += total
            cart_items.append({
                "id": product["id"],
                "name": product["name"],
                "price": price,
                "image": product["image"],
                "qty": qty,
                "total": total
            })

    tax = round(subtotal * 0.18)
    total = subtotal + tax

    return render_template(
        "dashboard.html",
        user=user,
        transactions=transactions,
        cart_items=cart_items,
        subtotal=subtotal,
        tax=tax,
        total=total,
        pending_checkout=session.get("pending_checkout")
    )


# ---- ADD TO CART -----
@app.route("/update_cart/<int:product_id>/<action>")
def update_cart(product_id, action):

    cart=session.get("cart",{})

    pid=str(product_id)

    if pid in cart:

        if action=="plus":
            cart[pid]+=1

        elif action=="minus":
            cart[pid]-=1
            if cart[pid]<=0:
                del cart[pid]

    session["cart"]=cart

    return jsonify({"status":"ok"})


@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):

    cart = session.get("cart", {})

    pid = str(product_id)

    if pid in cart:
        cart[pid] += 1
    else:
        cart[pid] = 1

    session["cart"] = cart
    session.modified = True

    total_items = sum(cart.values())

    return jsonify({
        "status": "success",
        "total_items": total_items
    })
    

@app.route("/clear_cart")
def clear_cart():

    session["cart"] = {}
    session.modified = True

    return jsonify({"status":"cleared"})


@app.route("/cart_data")
def cart_data():

    cart = session.get("cart", {})
    items = []

    subtotal = 0

    for pid, qty in cart.items():

        product = next((p for p in products if p["id"] == int(pid)), None)

        if product:

            price = product["price"]
            subtotal += price * qty

            items.append({
                "id": product["id"],
                "name": product["name"],
                "price": price,
                "image": product["image"],
                "qty": qty
            })

    tax = round(subtotal * 0.18)
    total = subtotal + tax

    return jsonify({
        "items": items,
        "subtotal": subtotal,
        "tax": tax,
        "total": total
    })

@app.route("/cart")
def view_cart():
    if "user_email" not in session:
        return redirect(url_for("login"))
    
    cart = session.get("cart", {})
    cart_items = []
    subtotal = 0

    for pid, qty in cart.items():
        product = next((p for p in products if p["id"] == int(pid)), None)
        if product:
            price = product["price"]
            total = price * qty
            subtotal += total
            cart_items.append({
                "id": product["id"],
                "name": product["name"],
                "price": price,
                "image": product["image"],
                "qty": qty,
                "total": total
            })

    tax = round(subtotal * 0.18)
    total = subtotal + tax

    return render_template(
        "cart.html",
        cart_items=cart_items,
        subtotal=subtotal,
        tax=tax,
        total=total
    )

@app.route("/remove_from_cart/<int:product_id>")
def remove_from_cart(product_id):

    cart = session.get("cart", {})

    pid = str(product_id)

    if pid in cart:
        del cart[pid]

    session["cart"] = cart
    session.modified = True

    return jsonify({"status":"removed"})

# ---------------- PROCESS PAYMENT ----------------
@app.route("/process-checkout", methods=["POST"])
def process_payment():

    email = request.form.get("email")
    password = request.form.get("password")
    mobile = request.form.get("mobile")

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    ).fetchone()

    if not user:
        return jsonify({"status": "fraud", "msg": "⚠ Fraud Detected"})

    if not check_password_hash(user["password"], password) or user["mobile"] != mobile:
        return jsonify({"status": "fraud", "msg": "⚠ Fraud Detected - Data mismatch"})

    otp = str(random.randint(1000, 9999))

    conn.execute(
        "INSERT INTO otp (email, otp, created_at) VALUES (?,?,?)",
        (email, otp, datetime.now())
    )

    conn.commit()
    conn.close()

    print("OTP:", otp)  # testing

    session["otp_email"] = email

    return jsonify({"status": "otp_sent"})


# ---------------- ADMIN ----------------
@app.route("/admin-login", methods=["POST"])
def admin_login():

    username = request.form.get("username")
    password = request.form.get("password")

    conn = get_db()

    admin = conn.execute(
        "SELECT * FROM admin WHERE username=? AND password=?",
        (username, password)
    ).fetchone()

    conn.close()

    if admin:
        session['is_admin'] = True 
        return redirect(url_for('admin_dashboard')) 
       
    else:
        return "Invalid Admin"



@app.route("/")
def index():
    return render_template("main.html")


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return "Product not found", 404
    reviews = []  # placeholder — no review table yet
    return render_template("product_detail.html", product=product, reviews=reviews)


@app.route("/shop")
def home():
    conn = get_db()
    all_users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    
    return render_template("products.html", products=products, users=all_users)


# ================= SEARCH API =================
@app.route("/search/<product>")
def search_product(product):
    results = []
    for p in products:
        if product.lower() in p["name"].lower():
            results.append(
                {
                    "id": p["id"],
                    "name": p["name"],
                    "price": p["price"],
                    "image": url_for("static", filename=p["image"]),
                }
            )
    return jsonify(results)


@app.route("/filter/<category>")  
def filter_products(category):
    cat = category.lower()
    
    if cat == "all":
        return jsonify(products)

    filtered = [
        p for p in products 
        if cat in p['name'].lower() or p['name'].lower() in cat
    ]
    
    return jsonify(filtered)


# ================= FRAUD DETECTION HELPER =================
def validate_user_checkout(email, entered_name, entered_card_number):
    """
    Validate user checkout data against stored user data.
    Returns: (is_valid, fraud_reason, user_id, registered_name)
    """
    conn = get_db()
    user = conn.execute("SELECT id, username, card FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    
    if not user:
        return False, "User not found", None, None
    
    user_id = user['id']
    registered_name = user['username']
    stored_card = user['card']
    
    # Normalize inputs (trim, lowercase for comparison)
    entered_name_clean = entered_name.strip().lower()
    registered_name_clean = registered_name.strip().lower()
    entered_card_last4 = entered_card_number[-4:] if entered_card_number else ""
    stored_card_last4 = stored_card[-4:] if stored_card else ""
    
    # Check for name mismatch
    if entered_name_clean != registered_name_clean:
        return False, "Name mismatch", user_id, registered_name
    
    # Check for card mismatch
    if entered_card_last4 and stored_card_last4 and entered_card_last4 != stored_card_last4:
        return False, "Card mismatch", user_id, registered_name
    
    return True, None, user_id, registered_name


def log_fraud_attempt(email, user_id, entered_name, registered_name, entered_card_last4, 
                      stored_card_last4, fraud_reason, amount):
    """
    Log fraud attempt to fraud_logs table.
    """
    conn = get_db()
    conn.execute("""
        INSERT INTO fraud_logs (user_email, user_id, entered_name, registered_name, 
                                entered_card_last4, stored_card_last4, fraud_reason, 
                                timestamp, amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (email, user_id, entered_name, registered_name, entered_card_last4, 
          stored_card_last4, fraud_reason, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), amount))
    conn.commit()
    conn.close()


# ================= EMAIL OTP HELPER =================
def send_otp_email(user_email, otp, amount):
    """
    Send OTP to user's email (Gmail SMTP).
    Returns True if sent successfully, False otherwise.
    """
    try:
        # Email configuration (using Gmail)
        sender_email = "securepay.noreply@gmail.com"  # Change to your email
        sender_password = "your_app_password_here"    # Change to your app-specific password
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🛡️ SecurePay - Your OTP Verification Code"
        msg['From'] = sender_email
        msg['To'] = user_email
        
        # Email body
        text = f"""
Hi,

Your OTP for transaction of ₹{amount} is:

{otp}

This OTP expires in 30 seconds and is valid only for this transaction.

Do not share this code with anyone.

SecurePay Team
        """
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
                <div style="background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <h2 style="color: #00d2ff; margin-bottom: 20px;">🛡️ SecurePay OTP Verification</h2>
                    
                    <p style="color: #333; font-size: 16px;">Hi,</p>
                    
                    <p style="color: #666; line-height: 1.6;">
                        Your OTP for transaction of <strong>₹{amount}</strong> is:
                    </p>
                    
                    <div style="background: #f0f0f0; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; border-left: 4px solid #00d2ff;">
                        <p style="font-size: 32px; letter-spacing: 5px; color: #00d2ff; font-weight: bold; margin: 0;">
                            {otp}
                        </p>
                    </div>
                    
                    <p style="color: #999; font-size: 12px; margin-top: 20px;">
                        ⏱️ This OTP expires in 30 seconds and is valid only for this transaction.
                    </p>
                    
                    <p style="color: #d9534f; font-weight: bold; font-size: 14px;">
                        ⚠️ Do not share this code with anyone. SecurePay staff will never ask for your OTP.
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    
                    <p style="color: #999; font-size: 12px; margin: 0;">
                        SecurePay Team<br>
                        Email: support@securepay.com
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Note: For production, use environment variables or secure config
        # For testing, you can use a test email service like Mailtrap
        # Uncomment below to actually send. For now, just log and return True
        
        # try:
        #     server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        #     server.login(sender_email, sender_password)
        #     server.sendmail(sender_email, user_email, msg.as_string())
        #     server.quit()
        #     print(f"✅ OTP email sent to {user_email}")
        #     return True
        # except Exception as e:
        #     print(f"❌ Email sending failed: {e}")
        #     return False
        
        # For now, just log to console (will be sent in production)
        print(f"✅ OTP Email would be sent to: {user_email}")
        print(f"OTP: {otp}")
        return True
        
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False


# ================= CHECKOUT ROUTE =================
@app.route("/pay/<int:product_id>")
def pay(product_id):

    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return "Product not found", 404

    # ✅ STORE SELECTED ITEM
    session["item"] = product["name"]
    session["amount"] = product["price"]
    session["item_image"] = product["image"]
    session["pending_checkout"] = True

    # 🔥 LOGIN CHECK
    if "user_email" not in session:
        return redirect(url_for("login"))

    return redirect(url_for("dashboard"))



@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "user_email" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    cart = session.get("cart", {})

    if "amount" not in session or not session.get("amount"):
        if cart:
            subtotal = 0
            item_names = []
            for pid, qty in cart.items():
                product = next((p for p in products if p["id"] == int(pid)), None)
                if product:
                    subtotal += product["price"] * qty
                    item_names.append(product["name"])
            session["item"] = ", ".join(item_names)
            session["amount"] = subtotal
        else:
            return redirect(url_for("home"))

    if request.method == "POST":
        email = session.get("user_email")
        cardholder_name = request.form.get("cardholder", "").strip()
        card_number = request.form.get("card_number", "").replace(" ", "").strip()
        cvv = request.form.get("cvv", "").strip()
        month = request.form.get("month", "")
        year = request.form.get("year", "")
        
        base_amt = float(session.get("amount", 0))
        tax = base_amt * 0.18
        total_payable = round(base_amt + tax, 2)

        # ============ FRAUD DETECTION LAYER ============
        # 1. Validate name and card against stored user data
        is_valid, fraud_reason, user_id, registered_name = validate_user_checkout(
            email, cardholder_name, card_number
        )
        
        if not is_valid:
            # Log fraud attempt
            entered_card_last4 = card_number[-4:] if card_number else "N/A"
            conn = get_db()
            stored_user = conn.execute("SELECT card FROM users WHERE email=?", (email,)).fetchone()
            stored_card_last4 = stored_user['card'][-4:] if stored_user and stored_user['card'] else "N/A"
            conn.close()
            
            log_fraud_attempt(
                email=email,
                user_id=user_id,
                entered_name=cardholder_name,
                registered_name=registered_name,
                entered_card_last4=entered_card_last4,
                stored_card_last4=stored_card_last4,
                fraud_reason=fraud_reason,
                amount=total_payable
            )
            
            # Set fraud result
            session["result"] = "❌ Transaction Flagged as Suspicious"
            session["fraud_reasons"] = [
                "Transaction flagged as suspicious. Please verify your details.",
                f"Reason: {fraud_reason}"
            ]
            return render_template("result.html")
        
        # 2. Validate card format and CVV
        if not cvv.isdigit() or len(cvv) != 3 or not card_number.isdigit() or len(card_number) != 16:
            session["result"] = "❌ Invalid Transaction"
            session["fraud_reasons"] = ["Invalid card details format. Please check your input."]
            return render_template("result.html")

        # ============ VALIDATION PASSED - PROCEED WITH PAYMENT ============
        otp_code = str(random.randint(1000, 9999))
        
        session.update({
            "card_number": card_number,  
            "payment_method": "Visa/MasterCard",
            "final_amount": total_payable, 
            "tx_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "txn_id": "TXN" + str(random.randint(100000, 999999)),
            "otp": otp_code,
            "otp_time": datetime.now().timestamp(),
            "otp_attempts": 0 
        })

        
        session["purchased_item"] = session.get("item")
        session["purchased_amount"] = session.get("final_amount")

        # ============ SEND OTP VIA EMAIL ============
        email_sent = send_otp_email(email, otp_code, total_payable)
        print(f"📧 OTP Email sent to {email}: {email_sent}")
        print(f"DEBUG: OTP is {session['otp']}")
        
        return render_template("otp.html", otp=session["otp"], amount=total_payable, email_sent=email_sent)

    
    cart = session.get("cart", {})
    cart_items = []
    subtotal = 0
    
    if cart:
        item_names = []
        for pid, qty in cart.items():
            product = next((p for p in products if p["id"] == int(pid)), None)
            if product:
                price = product["price"]
                total = price * qty
                subtotal += total
                cart_items.append({
                    "id": product["id"],
                    "name": product["name"],
                    "price": price,
                    "image": product["image"],
                    "qty": qty,
                    "total": total
                })
                item_names.append(product["name"])
        session["item"] = ", ".join(item_names)
        session["amount"] = subtotal
    
    tax = round(subtotal * 0.18) if subtotal > 0 else 0
    total = subtotal + tax

    return render_template(
        "checkout.html",
        item=session.get("item"), 
        amount=session.get("amount"),
        cart_items=cart_items,
        subtotal=subtotal,
        tax=tax,
        total=total
    )

# ================= VERIFY ADMIN =================
@app.route('/verify_admin', methods=['POST'])
def verify_admin():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Hardcoded check as requested: Admin / 1234
    if username == "Admin" and password == "1234":
        session['is_admin'] = True
        return jsonify({"success": True, "redirect": "/admin"})
    else:
        return jsonify({"success": False, "message": "Invalid data"})


@app.route('/admin')
def admin_redirect():
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect('/')

    conn = get_db()

    users = conn.execute("SELECT * FROM users").fetchall()
    transactions = conn.execute("SELECT * FROM transactions").fetchall()
    fraud_logs = conn.execute("SELECT * FROM fraud_logs ORDER BY timestamp DESC").fetchall()

    # 🔥 Calculate Statistics
    total_users = len(users)
    total_transactions = len(transactions)
    fraud_attempts = len(fraud_logs)

    blocked_count = sum(1 for tx in transactions if "Blocked" in tx["status"] or "❌" in tx["status"])
    success_count = sum(1 for tx in transactions if "Successful" in tx["status"] or "✅" in tx["status"])

    success_rate = round((success_count / total_transactions * 100), 1) if total_transactions > 0 else 0
    total_revenue = sum(tx["amount"] for tx in transactions if "Successful" in tx["status"] or "✅" in tx["status"])

    stats = {
        "total_users": total_users,
        "total_transactions": total_transactions,
        "blocked_count": blocked_count,
        "success_rate": success_rate,
        "total_revenue": round(total_revenue, 2),
        "fraud_attempts": fraud_attempts
    }

    # 🔥 GROUP transactions by email
    user_transactions = {}

    for tx in transactions:
        email = tx["email"]

        if email not in user_transactions:
            user_transactions[email] = []

        user_transactions[email].append({
            "id": tx["id"],
            "amount": tx["amount"],
            "status": tx["status"],
            "time": tx["time"],
            "item_name": tx["item_name"],
            "bank_name": tx["bank_name"]
        })

    conn.close()

    return render_template(
        "admin.html",
        db_users=users,
        user_transactions=user_transactions,
        transactions=transactions,
        fraud_logs=fraud_logs,
        stats=stats
    )


@app.route("/verify", methods=["POST"])
def verify():
    entered = request.form.get("otp", "")
    stored = session.get("otp")

    if not stored:
        return redirect(url_for("checkout"))

    # 1. OTP Expiry Check (30 or 60 Seconds)
    if datetime.now().timestamp() - session.get("otp_time", 0) > 30:
        return render_template("otp.html", otp=stored, error="❌ OTP Expired", amount=session.get("amount"))

    # 2. Wrong OTP Logic
    if entered != stored:
        # Attempts counting start karshe
        session["otp_attempts"] = session.get("otp_attempts", 0) + 1
        session.modified=True
        
        # Jo 3 attempts thai jay to card blocked
        if session["otp_attempts"] >= 3:
            status = "❌ Card Blocked"
            fraud_reasons = ["Maximum OTP attempts exceeded (3/3)"]
            
            # Aa transaction ne database ma save karvu
            save_transaction(status, fraud_reasons)
            
            # Session mathi OTP kadhi nakhvo
            session.pop("otp", None)
            session["otp_attempts"] = 0 # Reset for next time
            
            # Direct result page par mokalvu jya card blocked dekhay
            session['result'] = status
            session['fraud_reasons'] = fraud_reasons
            return render_template("result.html")
        
        # Jo 3 thi ochi attempts hoy to vali OTP page j dekhade pan error sathe
        error_msg = f"❌ Invalid OTP. Attempt {session['otp_attempts']}/3"
        return render_template("otp.html", otp=stored, error=error_msg, amount=session.get("amount"))

    # 3. Success Logic (Correct OTP)
    status = "✅ Transaction Successful"
    save_transaction(status, [])
    session.pop("otp", None)
    session["otp_attempts"] = 0
    session['result'] = status
    return render_template("result.html")

@app.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):

    if not session.get('is_admin'):
        return jsonify({"message": "Unauthorized"}), 403

    conn = get_db()

    # 🔥 delete user transactions first
    conn.execute("DELETE FROM transactions WHERE email = (SELECT email FROM users WHERE id=?)", (user_id,))

    # 🔥 delete user
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "User deleted successfully"})


# ================= RESEND OTP =================
@app.route("/resend_otp")
def resend_otp():
    email = session.get("user_email")
    new_otp = str(random.randint(1000, 9999))
    
    session["otp"] = new_otp
    session["otp_time"] = datetime.now().timestamp()
    session["otp_attempts"] = 0  # Reset attempts on resend
    
    # Send new OTP via email
    send_otp_email(email, new_otp, session.get("final_amount", 0))
    print(f"📧 Resent OTP to {email}: {new_otp}")
    
    return render_template(
        "otp.html", 
        otp=session["otp"], 
        resent=True, 
        amount=session.get("final_amount"),
        email_sent=True
    )

# ================= SAVE TRANSACTION =================
def save_transaction(status, reasons):
    conn = get_db()
    item_name = session.get("item", "Product")
    conn.execute("""
        INSERT INTO transactions (email,item_name,card_last4, bank_name, payment_method, amount, status, time)
        VALUES (?,?, ?, ?, ?, ?, ?,?)
    """, (
        session.get("user_email"),
        item_name,
        session.get("card_number", "0000")[-4:],
        session.get("bank_name", "N/A"),
        session.get("payment_method", "Card"),
        session.get("final_amount", 0),
        status,
        session.get("tx_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ))
    conn.commit()
    conn.close()

    session["result"] = status
    session["fraud_reasons"] = reasons


@app.route("/view-invoice")
def view_invoice():
    if "user_email" not in session:
        return redirect(url_for("login"))
    
    email = session.get("user_email")
    
    # Fetch cart items
    cart = session.get("cart", {})
    cart_items = []
    subtotal = 0

    for pid, qty in cart.items():
        product = next((p for p in products if p["id"] == int(pid)), None)
        if product:
            price = product["price"]
            total = price * qty
            subtotal += total
            cart_items.append({
                "id": product["id"],
                "name": product["name"],
                "price": price,
                "image": product["image"],
                "qty": qty,
                "total": total
            })

    tax = round(subtotal * 0.18)
    total = subtotal + tax
    
    order_data = {
        "txn_id": session.get("txn_id", "INV-" + str(random.randint(100000, 999999))),
        "item": session.get("item", "Product"),
        "amount": session.get("amount", subtotal),
        "subtotal": subtotal,
        "tax": tax,
        "total": subtotal + tax,
        "email": email,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "cart_items": cart_items
    }
    
    return render_template("invoice.html", order=order_data)

@app.route("/history")
def history():
    conn = get_db()
    rows = conn.execute("SELECT * FROM transactions ORDER BY id DESC").fetchall()
    total = len(rows)
    success = len([r for r in rows if "Successful" in r['status']])
    failed = total - success
    success_amount = sum(r['amount'] for r in rows if "Successful" in r['status'])
    
    conn.close()
    return render_template("history.html", 
                           history=rows, 
                           total=total, 
                           success=success, 
                           failed=failed, 
                           success_amount=success_amount)


# PDF DOWNLOAD ROUTE
@app.route("/download-statement")
def download_statement():
    if "user_email" not in session: return redirect(url_for("login"))
    
    conn = get_db()
    transactions = conn.execute("SELECT * FROM transactions WHERE email=? ORDER BY time DESC", 
                                (session["user_email"],)).fetchall()
    conn.close()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Statement for {session['user_email']}", styles["Title"]))
    
    data = [["Date", "Card", "Amount", "Status"]]
    for tx in transactions:
        data.append([tx["time"], "****" + tx["card_last4"], f"Rs.{tx['amount']}", tx["status"]])

    table = Table(data)
    table.setStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey), ('GRID', (0, 0), (-1, -1), 1, colors.black)])
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="Statement.pdf", mimetype="application/pdf")


# ================= RUN =================
if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
    