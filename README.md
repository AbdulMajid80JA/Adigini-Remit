# Adigini-Remit
💸 Ultra-fast African remittance infrastructure engine. Built with Flask, SQLite, and Paystack API. Features live black market rate overrides, automated database backups, and an interactive WhatsApp support dashboard.
markdown

# Adigini Remit - Next-Generation African Remittance Engine 🚀

Adigini Remit is a high-performance cross-border transaction framework built explicitly to empower the global African diaspora. The platform circumvents traditional banking bottlenecks to route liquidity instantly and securely, offering real-time competitive market exchange rates and automated payout executions.

---

## ⚡ Production Feature Matrix

### 💱 Live Operations Layout
* **Dynamic Multi-Currency Pricing:** Backend-driven black-market rate management updates calculation values across customer forms instantly.
* **Minor Unit Conversion:** Securely handles currency payload tracking in minor units (cents/kobo) to guarantee seamless transaction settlements.
* **On-Page Destination Estimates:** Front-end JavaScript calculations show users accurate delivery values in GHS dynamically as inputs shift.

### 🔒 Enterprise Protection & Administration
* **Authorization Token Shield:** Administrative ledger screens are fully isolated behind a session-based validation wrapper to prevent URL-bypassing attempts.
* **Automated Redundancy Routing:** Generates timestamped database snapshot backups into a separate directory (`backups/`) at server runtime and on manual command.
* **Multimedia Compliance Vault:** Dedicated multi-part document processing pipelines allow administrators to securely upload user portraits and KYC identity files directly to disk.
* **Asynchronous Filtering Pipeline:** Search engine strings pass criteria straight to backend SQL execution layers to look up ledger rows instantly by name or phone string.

### 🔌 Gateway & Platform Integrations
* **Paystack Inline Engine v2:** Renders safe overlay checkout payment modals to process deposits without shifting user interface contexts.
* **Single-Click Paystack Disbursal:** Integrates server-to-server Payout Transfer API protocols directly inside ledger rows for one-click liquidity disbursement.
* **Interactive Helpdesk:** Standalone customer support routing panel synced with JavaScript text encoders for streamlined WhatsApp operators dispatch.

---

## 🛠️ Core Technology Infrastructure
* **Backend Runtime Core:** Python 3.12+ (Flask Web Server Engine)
* **Storage Layer Engine:** SQLite3 (Relational Ledger & Parameter Metadata Tables)
* **Frontend Controller:** Semantic HTML5, CSS3 Theme Variables, Vanilla JS Execution Core
* **Integrations Pipeline:** Paystack Web SDK v2 & Secure Outbound JSON Transfer APIs

---

## 📦 Directory Structure Mapping
```text
adigini-remit/
├── backups/                 # Auto-generated database snapshot backups storage
├── services/
│   ├── __init__.py
│   ├── exchange_service.py  # Third-party baseline API exchange fetchers
│   └── paystack_service.py  # Deposit checkout session token generators
├── static/
│   ├── css/
│   │   └── style.css        # Theme stylesheet variables (Dark-mode palette)
│   ├── js/
│   │   └── app.js           # Front-end calculation & validation logic
│   └── uploads/             # Multi-part compliance image storage folder
├── templates/
│   ├── index.html           # Core transaction converter portal landing page
│   ├── about.html           # Marketing value proposition panel
│   ├── contact.html         # Live communication node options template
│   ├── support.html         # Interactive helpdesk hub & HTML FAQ accordion grid
│   ├── admin-login.html     # Encrypted administration terminal login screen
│   ├── dashboard.html       # Live master ledger manager panel
│   ├── otp.html             # Multi-factor security verification challenge
│   └── success.html         # Dynamic system receipt variable dashboard
├── .env                     # Local environmental parameter configuration arrays
├── app.py                   # Central server routing engine instance script
└── database.db              # Active transactional ledger repository
```

---

## 🚀 Installation & Local Environment Setup

### 1. Clone the Target Ledger Repository
```bash
git clone github.com
cd adigini-remit
```

### 2. Isolate Virtual Environment Dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install System Extension Profiles
```bash
pip install flask requests python-dotenv
```

### 4. Configure Local Environmental Parameter Profiles (`.env`)
Create a new file named exactly `.env` right in your main root project directory next to `app.py`, and fill it with your credentials:

```ini
# Core Web Platform Key Variables
FLASK_SECRET_KEY=adigini_remit_secure_production_key_2026

# Paystack API Payment Gateway Credentials
PAYSTACK_PUBLIC_KEY=pk_test_your_real_paystack_public_key_here
PAYSTACK_SECRET_KEY=sk_test_your_real_paystack_secret_key_here

# System SMTP Email Automation Engine Configurations
SMTP_SERVER=gmail.com
SMTP_PORT=587
SMTP_USER=your-business-email@gmail.com
SMTP_PASSWORD=your-google-app-generated-password
ADMIN_EMAIL=admin@adiginiremit.com
```

### 5. Initialize the Core Web Server Execution Instance
```bash
python app.py
```
Open up your secure browser network viewport link to run the application terminal interface locally: `http://127.0.0.1:5000`

---

## 🔒 Security Compliance Protocol Directive
Do **NOT** push your hidden local `.env` configuration text files or your active production `database.db` files up onto public GitHub repositories. Ensure your tracking scripts use a standard `.gitignore` template file layout to safely filter out local cache profiles and credentials.

---

## 📄 Platform Legal Frameworks
This project includes modern embedded legal templates configuration views accessible under public endpoints mapping routes:
* **Terms of Service (`/terms`):** Regulates transaction execution agreements and fixed 3% calculation rules.
* **Privacy Policies (`/privacy`):** Limits information processing disclosures and defines secure storage layers isolation metrics.

