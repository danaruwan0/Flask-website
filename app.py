from flask import Flask, render_template, request, flash, redirect, url_for
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
import sqlite3

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'srilanka-design-solutions-2024'

# Email Configuration
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', '')

# Initialize Database with PROPER table structure
def init_db():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    
    # Drop old table if exists (to fix structure)
    c.execute('''DROP TABLE IF EXISTS messages''')
    
    # Create NEW table with CORRECT columns
    c.execute('''CREATE TABLE messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT NOT NULL,
                  service TEXT DEFAULT 'Not Specified',
                  message TEXT NOT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()
    print("[DATABASE] New database table created with service column")

# Initialize on startup
init_db()

def send_email_to_admin(name, user_email, service, user_message):
    """Send contact form message to admin email"""
    try:
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = f"Design Quote Request: {name}"
        
        # Email body
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #4a6bff;">🎨 New Design Service Request</h2>
                <hr style="border: 1px solid #eee;">
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <h3 style="color: #333;">👤 Client Details:</h3>
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Email:</strong> <a href="mailto:{user_email}">{user_email}</a></p>
                    <p><strong>Service Needed:</strong> {service}</p>
                    <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div style="background-color: #eef2ff; padding: 15px; border-radius: 5px;">
                    <h3 style="color: #333;">📋 Project Requirements:</h3>
                    <p style="white-space: pre-wrap;">{user_message}</p>
                </div>
                
                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee;">
                    <p style="color: #666; font-size: 12px;">
                        This email was sent from Sri Lanka Design Solutions website.
                        <br>📍 Oluvil, Sri Lanka | 📞 +94 757232425
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
            
        print("[SUCCESS] Design quote request sent to admin")
        return True
        
    except Exception as e:
        print(f"[ERROR] Email sending failed: {str(e)}")
        return False

def send_confirmation_to_user(name, user_email, service):
    """Send confirmation email to user"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = user_email
        msg['Subject'] = "✅ Thank You for Your Design Quote Request!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4a6bff;">Thank You, {name}!</h2>
                
                <p>We have received your request for <strong>{service}</strong> services.</p>
                <p>Our team will review your requirements and get back to you within <strong>24 hours</strong>.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>📞 Our Contact Info:</strong></p>
                    <p>Phone: +94 757232425</p>
                    <p>Email: info@srilankadesigns.com</p>
                    <p>Location: Oluvil, Sri Lanka</p>
                    <p>Hours: Mon-Sat, 9AM-6PM (IST)</p>
                </div>
                
                <div style="background-color: #eef2ff; padding: 15px; border-radius: 5px;">
                    <p><strong>Services We Offer:</strong></p>
                    <ul>
                        <li>3D Modeling & Visualization (Blender + CAD)</li>
                        <li>Architectural/Engineering CAD Design</li>
                        <li>Quantity Surveying & Cost Estimation</li>
                        <li>Product/Industrial Design</li>
                    </ul>
                </div>
                
                <p style="color: #666; font-size: 14px; margin-top: 20px;">
                    This is an automated confirmation email from Sri Lanka Design Solutions.
                    <br>10+ Years of Professional Experience | Fast Delivery | Trusted Service
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
            
        print(f"[SUCCESS] Confirmation sent to client: {user_email}")
        return True
        
    except Exception as e:
        print(f"[ERROR] User confirmation failed: {str(e)}")
        return False

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        service = request.form.get('service', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validate form
        if not name or not email or not message:
            flash('Please fill all required fields!', 'error')
            return redirect(url_for('contact'))
        
        if not service:
            service = "Not specified"
        
        try:
            # 1. Save to database (FIXED - with service column)
            conn = sqlite3.connect('messages.db')
            c = conn.cursor()
            c.execute("INSERT INTO messages (name, email, service, message) VALUES (?, ?, ?, ?)",
                     (name, email, service, message))
            conn.commit()
            conn.close()
            
            print(f"[DATABASE] Quote request saved: {name}, {service}")
            
            # 2. Send email to ADMIN
            admin_sent = send_email_to_admin(name, email, service, message)
            
            # 3. Send confirmation to USER
            user_sent = send_confirmation_to_user(name, email, service)
            
            if admin_sent and user_sent:
                flash('✅ Your quote request has been sent successfully! Check your email for confirmation.', 'success')
            elif admin_sent:
                flash('✅ Request sent! Confirmation email may be delayed.', 'warning')
            else:
                flash('⚠️ Request saved but email failed. We will contact you soon.', 'warning')
                
        except Exception as e:
            print(f"[ERROR] Database/Email error: {str(e)}")
            flash(f'❌ Error: {str(e)}', 'error')
        
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/services')
def services():
    services_list = [
        {'name': '3D Modeling & Visualization Artist', 'desc': 'Expert in Blender + CAD for architectural visualization, product modeling, and realistic rendering.', 'icon': 'fas fa-cube'},
        {'name': 'Architectural/Engineering CAD Designer', 'desc': 'Professional CAD designs for architecture, engineering plans, and construction documentation.', 'icon': 'fas fa-drafting-compass'},
        {'name': 'Quantity Surveyor', 'desc': 'Construction cost estimation, bill of quantities, and project budgeting for Sri Lankan projects.', 'icon': 'fas fa-calculator'},
        {'name': 'Product/Industrial Designer', 'desc': 'CAD + Blender for product prototyping, industrial design, and manufacturing-ready models.', 'icon': 'fas fa-industry'}
    ]
    return render_template('services.html', services=services_list)

@app.route('/admin')
def admin():
    # Password: admin123 (change this in production)
    password = request.args.get('password', '')
    if password != 'admin123':
        return "Unauthorized - Sri Lanka Design Solutions Admin Access", 401
    
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("SELECT * FROM messages ORDER BY timestamp DESC")
    messages = c.fetchall()
    conn.close()
    
    return render_template('admin.html', messages=messages)

@app.route('/admin/delete/<int:msg_id>', methods=['POST'])
def delete_message(msg_id):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()
    return '', 200

@app.route('/test-email')
def test_email():
    """Test email configuration"""
    test_sent = send_email_to_admin("Test Client", "test@example.com", "3D Modeling", "This is a test message from the website.")
    if test_sent:
        return "✅ Test email sent successfully to admin!"
    else:
        return "❌ Test email failed. Check your .env configuration."

if __name__ == '__main__':
    # Check email configuration
    if not EMAIL_USER or not EMAIL_PASSWORD:
        print("[WARNING] Email credentials not set in .env file")
        print("Please create .env file with EMAIL_USER and EMAIL_PASSWORD")
    
    print("\n" + "="*50)
    print("🇱🇰 Sri Lanka Design Solutions")
    print("="*50)
    print(f"📍 Location: Oluvil, Sri Lanka")
    print(f"📞 Phone: +94 757232425")
    print(f"💼 Services: 3D Modeling, CAD Design, Quantity Survey, Product Design")
    print(f"🎯 Experience: 10+ Years International")
    print("="*50)
    print("[DATABASE] Creating fresh database...")
    print("\nStarting website...")
    
    app.run(debug=True, host='0.0.0.0', port=5000)