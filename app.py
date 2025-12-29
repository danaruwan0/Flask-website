from flask import Flask, render_template, request, flash, redirect, url_for
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
import sqlite3

# ================= LOAD ENV =================
load_dotenv()

app = Flask(__name__)
app.secret_key = 'srilanka-design-solutions-2024'

# ================= EMAIL CONFIG =================
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

DB_NAME = "messages.db"

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            service TEXT DEFAULT 'Not Specified',
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("[DATABASE] Table ready (safe)")

# ================= EMAIL FUNCTIONS =================
def send_email_to_admin(name, user_email, service, user_message):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = ADMIN_EMAIL
        msg["Subject"] = f"New Design Quote Request - {name}"

        body = f"""
        New Design Request

        Name    : {name}
        Email   : {user_email}
        Service : {service}
        Time    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        Message:
        {user_message}
        """

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        print("[EMAIL ERROR - ADMIN]", e)
        return False


def send_confirmation_to_user(name, user_email, service):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = user_email
        msg["Subject"] = "Thank you for contacting Sri Lanka Design Solutions"

        body = f"""
        Hello {name},

        Thank you for contacting Sri Lanka Design Solutions.

        Requested Service:
        {service}

        Our team will contact you within 24 hours.

        📞 +94 757232425
        📍 Oluvil, Sri Lanka

        Regards,
        Sri Lanka Design Solutions
        """

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        print("[EMAIL ERROR - USER]", e)
        return False

# ================= ROUTES =================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    services_list = [
        {"name": "3D Modeling & Visualization", "desc": "Blender + CAD"},
        {"name": "Architectural CAD Design", "desc": "Plans & Drawings"},
        {"name": "Quantity Surveying", "desc": "BOQ & Cost Estimation"},
        {"name": "Product Design", "desc": "Industrial & Manufacturing"}
    ]
    return render_template("services.html", services=services_list)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        service = request.form.get("service", "Not Specified")
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("❌ Please fill all required fields", "error")
            return redirect(url_for("contact"))

        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute(
                "INSERT INTO messages (name, email, service, message) VALUES (?, ?, ?, ?)",
                (name, email, service, message)
            )
            conn.commit()
            conn.close()

            admin_ok = send_email_to_admin(name, email, service, message)
            user_ok = send_confirmation_to_user(name, email, service)

            if admin_ok and user_ok:
                flash("✅ Message sent successfully!", "success")
            else:
                flash("⚠️ Message saved, email issue detected", "warning")

        except Exception as e:
            print("[ERROR]", e)
            flash("❌ Something went wrong", "error")

        return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/admin")
def admin():
    password = request.args.get("password")
    if password != "admin123":
        return "Unauthorized", 401

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM messages ORDER BY timestamp DESC")
    messages = c.fetchall()
    conn.close()

    return render_template("admin.html", messages=messages)


@app.route("/admin/delete/<int:msg_id>", methods=["POST"])
def delete_message(msg_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE id=?", (msg_id,))
    conn.commit()
    conn.close()
    return "", 200


@app.route("/test-email")
def test_email():
    ok = send_email_to_admin(
        "Test User",
        "test@example.com",
        "3D Modeling",
        "This is a test message"
    )
    return "✅ Email Sent" if ok else "❌ Email Failed"

# ================= MAIN =================
if __name__ == "__main__":
    init_db()

    print("=" * 50)
    print("🇱🇰 Sri Lanka Design Solutions")
    print("Server starting...")
    print("=" * 50)

    app.run(debug=True, host="0.0.0.0", port=5000)
