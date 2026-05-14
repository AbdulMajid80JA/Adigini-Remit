from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import sqlite3
import requests
import os
import smtplib
import shutil
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from functools import wraps
from werkzeug.utils import secure_filename

load_dotenv()

from services.exchange_service import get_exchange_rates
from services.paystack_service import initialize_payment         

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "adigini_remit_secure_fallback_key_2026")

PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_PUBLIC = os.getenv("PAYSTACK_PUBLIC_KEY")

SMTP_SERVER = os.getenv("SMTP_SERVER", "gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "your-email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-app-password")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@adiginiremit.com")

UPLOAD_FOLDER = os.path.join('static', 'uploads')
BACKUP_FOLDER = os.path.join('backups')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['BACKUP_FOLDER'] = BACKUP_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# =========================================================================
# AUTOMATED BACKUP ENGINE
# =========================================================================
def execute_db_backup():
    """
    Clones the operational database file into a timestamped directory architecture.
    """
    db_source = 'database.db'
    if os.path.exists(db_source):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_{timestamp}.db"
        backup_dest = os.path.join(app.config['BACKUP_FOLDER'], backup_filename)
        try:
            shutil.copy2(db_source, backup_dest)
            print(f"[BACKUP SYSTEM] Secure snapshot generated: {backup_dest}")
            return True
        except Exception as e:
            print(f"[BACKUP ERROR] Snapshot engine failed: {str(e)}")
    return False

# =========================================================================
# DATABASE STRUCTURAL INITIALIZATION
# =========================================================================
def init_db():
    execute_db_backup() # Run backup before structural check sequences
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_name TEXT,
            sender_phone TEXT,
            recipient_name TEXT,
            recipient_phone TEXT,
            amount REAL,
            fee REAL,
            currency TEXT,
            status TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS black_market_rates (
            currency TEXT PRIMARY KEY,
            value REAL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS media_vault (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT UNIQUE,
            file_path TEXT
        )
    ''')
    c.execute("SELECT COUNT(*) FROM black_market_rates")
    if c.fetchone() == 0:
        default_rates = [
            ("USD", 14.55), ("EUR", 15.73), ("GBP", 18.50),
            ("SAR", 3.81), ("AED", 3.88), ("QAR", 3.92),
            ("NGN", 0.0092), ("XOF", 0.024)
        ]
        c.executemany("INSERT INTO black_market_rates VALUES (?, ?)", default_rates)
    conn.commit()
    conn.close()

init_db()

def get_db_rates():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT currency, value FROM black_market_rates")
    rates = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    return rates

def get_media_assets():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT label, file_path FROM media_vault")
    assets = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    return assets

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# =========================================================================
# PUBLIC ENDPOINTS & DYNAMIC API CHANNELS
# =========================================================================
@app.route('/')
def home():
    return render_template('index.html', rates=get_db_rates(), live_rates=get_exchange_rates(), paystack_public=PAYSTACK_PUBLIC)

@app.route('/api/rates')
def api_rates():
    """
    Returns live database rates as structured JSON payload data tokens.
    """
    return jsonify(get_db_rates())

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/support')
def customer_support_hub():
    return render_template('support.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            return redirect('/dashboard')
        return "Invalid Admin Credentials"
    return render_template('admin-login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/otp')
def otp():
    return render_template('otp.html')

@app.route('/pay', methods=['POST'])
def pay():
    sender_name = request.form['sender_name']
    sender_phone = request.form['sender_phone']
    recipient_name = request.form['recipient_name']
    recipient_phone = request.form['recipient_phone']
    amount = float(request.form['amount'])
    currency = request.form['currency']

    # Preserved original 3% baseline calculation rules logic
    service_fee = amount * 0.03
    total_amount = amount + service_fee

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions (sender_name, sender_phone, recipient_name, recipient_phone, amount, fee, currency, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (sender_name, sender_phone, recipient_name, recipient_phone, amount, service_fee, currency, 'Pending'))
    session['last_sender_phone'] = sender_phone
    conn.commit()
    conn.close()

    payment = initialize_payment(f"{sender_phone}@swiftremit.com", total_amount)
    if payment['status']:
        return redirect('/otp')
    return "Payment failed"

@app.route('/success')
def success():
    phone = session.get('last_sender_phone')
    if not phone: return redirect(url_for('home'))
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE sender_phone = ? AND status = 'Pending' ORDER BY id DESC LIMIT 1", (phone,))
    tx = c.fetchone()
    if tx:
        tx_data = {"id": tx["id"], "sender_name": tx["sender_name"], "sender_phone": tx["sender_phone"], "recipient_name": tx["recipient_name"], "recipient_phone": tx["recipient_phone"], "amount": f"{tx['amount']:.2f}", "fee": f"{tx['fee']:.2f}", "total": f"{(tx['amount'] + tx['fee']):.2f}", "currency": tx["currency"], "status": "Processing"}
        c.execute("UPDATE transactions SET status = 'Processing' WHERE id = ?", (tx["id"],))
        conn.commit()
        conn.close()
        return render_template('success.html', tx=tx_data)
    conn.close()
    return redirect(url_for('home'))

# =========================================================================
# COMPLIANCE & LEGAL LAYOUT CHANNELS
# =========================================================================
@app.route('/privacy')
def privacy_policy():
    """
    Renders the modern legal data protection architecture guidelines page.
    """
    return render_template('privacy.html')

@app.route('/terms')
def terms_of_service():
    """
    Renders the high-authority platform operations legal agreement page.
    """
    return render_template('terms.html')

# =========================================================================
# CENTRAL ADMIN DATA CONTROL PANEL
# =========================================================================
@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    search_query = request.args.get('search', '').strip()
    if search_query:
        c.execute("SELECT * FROM transactions WHERE sender_phone LIKE ? OR sender_name LIKE ? ORDER BY id DESC", (f'%{search_query}%', f'%{search_query}%'))
    else:
        c.execute("SELECT * FROM transactions ORDER BY id DESC")
    transactions = c.fetchall()
    conn.close()
    return render_template('dashboard.html', transactions=transactions, current_rates=get_db_rates(), media_files=get_media_assets(), search_val=search_query)

@app.route('/admin/backup-db', methods=['POST'])
@login_required
def trigger_manual_backup():
    if execute_db_backup():
        return redirect(url_for('dashboard'))
    return "Backup Failed", 500

@app.route('/admin/update-rate', methods=['POST'])
@login_required
def update_rate():
    currency = request.form.get('currency')
    new_value = request.form.get('value')
    if currency and new_value:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("UPDATE black_market_rates SET value = ? WHERE currency = ?", (float(new_value), currency))
        conn.commit()
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/admin/upload-media', methods=['POST'])
@login_required
def upload_media():
    label = request.form.get('label')
    if 'file' not in request.files or not label:
        return redirect(url_for('dashboard'))
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{label}_{file.filename}")
        relative_path = f"uploads/{filename}"
        full_saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(full_saved_path)
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO media_vault (label, file_path) VALUES (?, ?)", (label, relative_path))
        conn.commit()
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/admin/payout/<int:tx_id>', methods=['POST'])
@login_required
def automate_payout(tx_id):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
    tx = c.fetchone()
    if not tx or tx['status'] == 'Completed':
        conn.close()
        return redirect(url_for('dashboard'))
    paystack_api_headers = {"Authorization": f"Bearer {PAYSTACK_SECRET}", "Content-Type": "application/json"}
    try:
        recipient_payload = {"type": "nuban", "name": tx['recipient_name'], "account_number": tx['recipient_phone'], "bank_code": "057", "currency": "GHS"}
        rcp_response = requests.post("paystack.co", json=recipient_payload, headers=paystack_api_headers).json()
        if rcp_response.get('status'):
            recipient_code = rcp_response['data']['recipient_code']
            payout_payload = {"source": "balance", "amount": int(tx['amount'] * 100), "recipient": recipient_code, "reason": f"Remittance Payout Reference ID: #ADG-{tx_id}"}
            transfer_response = requests.post("paystack.co", json=payout_payload, headers=paystack_api_headers).json()
            if transfer_response.get('status'):
                c.execute("UPDATE transactions SET status = 'Completed' WHERE id = ?", (tx_id,))
                conn.commit()
    except Exception as e:
        print(f"[GATEWAY ERROR] {str(e)}")
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
