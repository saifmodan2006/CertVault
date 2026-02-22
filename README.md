# 🎓 CertVault – Certificate Management Platform

A full-featured, production-ready certificate management web application built with Flask, SQLAlchemy, and Bootstrap 5. Store, manage, and share your certificates securely forever.

---

## ✨ Features

### 👤 User Management
- Register / Login / Logout with secure password hashing (Werkzeug bcrypt)
- User profiles with bio, stats, and activity history
- First registered user automatically becomes Admin
- Password change from profile page
- Email verification support

### 📂 Certificate Management
- Upload PDF, JPG, PNG, WEBP, GIF certificates
- Drag & drop file upload with live preview
- Edit all certificate details anytime
- Delete certificates (removes file from storage)
- Download & print certificates
- Auto-categorize certificates (Technology, Business, Healthcare, Education, etc.)
- Certificate expiry tracking and date management

### 🔗 Sharing System
- Unique shareable link for every certificate
- Public/Private toggle (one click toggle)
- QR code generation for every certificate
- Beautiful public share page with certificate preview
- Share certificates via link or QR code

### 📊 Dashboard
- Real-time statistics (total, public, expiring, categories)
- Bar chart of certificate activity over time
- Donut chart of certificate categories (Chart.js)
- Expiry alerts for certificates expiring within 30 days
- Recent activity log with timestamps

### 🔍 Search & Filter
- Full-text search by title, issuer, tags
- Filter by category and status (active/expiring/expired)
- Sort by newest, oldest, or alphabetical
- Quick category filters

### 🔒 Security
- Password hashing with Werkzeug (bcrypt)
- Session-based authentication
- File type validation on upload
- SQL injection protection via SQLAlchemy ORM
- CSRF protection via form submissions
- Secure file handling and storage
- XSS protection through template escaping

### 🎨 UI/UX
- Modern glassmorphism design
- Dark/Light theme toggle (persisted to localStorage)
- Responsive design (Mobile, Tablet, Desktop)
- Bootstrap 5 framework
- Smooth animations and transitions
- Chart.js for data visualization

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/saifmodan2006/CertVault.git
cd CertVault
```

2. **Create a virtual environment**
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables** (Optional)
Create a `.env` file in the project root:
```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///certvault.db
FLASK_ENV=development
```

5. **Run the application**
```bash
python app.py
```

6. **Access the application**
Open your browser and go to `http://localhost:5000`

---

## 📦 Project Structure

```
CertVault/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── README.md             # This file
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles & theme
│   └── js/
│       └── main.js       # Frontend interactions & theme toggle
├── templates/
│   ├── base.html         # Base template with navbar
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # User dashboard with stats
│   ├── certificates.html # All user certificates
│   ├── upload.html       # Certificate upload form
│   ├── edit_certificate.html  # Edit certificate details
│   ├── certificate_detail.html # View certificate details
│   ├── share.html        # Public share page
│   ├── profile.html      # User profile page
│   ├── admin.html        # Admin panel
│   └── error.html        # Error page
└── uploads/              # Uploaded certificate files

```

---

## 🛠️ Technologies Used

- **Backend**: Flask 3.0.0, SQLAlchemy 2.0.23
- **Database**: SQLite with WAL mode
- **Frontend**: Bootstrap 5, Chart.js, JavaScript
- **Security**: Werkzeug (bcrypt), Flask-Mail
- **File Handling**: Pillow (image processing)
- **QR Codes**: qrcode library
- **Environment**: python-dotenv

---

## 📊 Database Schema

The application uses SQLite with the following main tables:
- **users**: User accounts with authentication
- **certificates**: Certificate records with metadata
- **activity_logs**: Track user actions and timestamp
- **share_links**: Public shareable certificate links

---

## 🐳 Docker Setup

To run with Docker:

```bash
docker-compose up --build
```

The application will be available at `http://localhost:5000`

---

## 🔐 Security Features

- **Password Security**: Uses Werkzeug's password hashing with bcrypt
- **Session Management**: Secure session-based authentication
- **File Validation**: Only allows specified file types (PDF, PNG, JPG, GIF, WEBP)
- **XSS Protection**: Template auto-escaping enabled
- **SQL Injection**: Protected via SQLAlchemy ORM
- **CSRF Protection**: Form-based CSRF tokens
- **File Size Limit**: Max upload size 16MB

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is open source and available under the MIT License - see the LICENSE file for details.

---

## 📧 Contact & Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: saifmodan2006@gmail.com

---

## 🎯 Roadmap

- [ ] Email verification for new accounts
- [ ] Two-factor authentication (2FA)
- [ ] Bulk certificate upload
- [ ] Certificate templates
- [ ] Advanced analytics
- [ ] Mobile app
- [ ] Integration with certificate authorities
- [ ] Automated certificate renewal reminders

---

## 💡 Tips

- **Theme Toggle**: Use the theme switcher in the navbar to toggle between dark and light modes
- **QR Codes**: Share certificates easily using generated QR codes
- **Search**: Use the search feature to quickly find certificates
- **Filtering**: Filter by category or expiry status for better organization
- **Admin Panel**: Access admin settings to manage all users and certificates

---

Made with ❤️ by Saif
- Smooth animations & transitions
- Fully responsive (mobile-friendly)
- Keyboard shortcuts (Ctrl+K to search, Ctrl+U to upload)
- Ripple effects on buttons
- Animated number counters

---

## 🛠️ Tech Stack

| Layer    | Technology |
|----------|-----------|
| Backend  | Python Flask 3.0, SQLAlchemy |
| Database | SQLite (default) / PostgreSQL |
| Frontend | HTML5, Bootstrap 5.3, Chart.js |
| Storage  | Local filesystem (`/uploads`) |
| Auth     | Flask session + Werkzeug |
| QR Code  | `qrcode[pil]` library |

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone <your-repo>
cd certvault
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and set your SECRET_KEY
```

### 3. Run
```bash
python app.py
```

Visit: http://localhost:5000

---

## 🐳 Docker

```bash
docker compose up --build
```

---

## 🗄️ Database Schema

### `users`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| name | VARCHAR(100) | Full name |
| email | VARCHAR(120) UNIQUE | Login email |
| password_hash | VARCHAR(255) | Bcrypt hash |
| bio | TEXT | User bio |
| is_admin | BOOLEAN | Admin flag |
| created_at | DATETIME | Registration date |

### `certificates`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| user_id | FK → users | Owner |
| title | VARCHAR(200) | Certificate name |
| issuer | VARCHAR(200) | Issuing organization |
| description | TEXT | Details |
| issue_date | DATE | When issued |
| expiry_date | DATE (null) | Optional expiry |
| tags | VARCHAR(500) | Comma-separated |
| file_path | VARCHAR(500) | Stored filename |
| file_type | VARCHAR(20) | Extension (pdf/png…) |
| unique_id | VARCHAR(36) | UUID for share URL |
| is_public | BOOLEAN | Sharing status |
| category | VARCHAR(100) | Auto-categorized |
| created_at | DATETIME | Upload time |
| updated_at | DATETIME | Last edit time |

### `activity_logs`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| user_id | FK → users | Who did it |
| action | VARCHAR(100) | LOGIN/UPLOAD/EDIT/DELETE… |
| details | TEXT | Action description |
| ip_address | VARCHAR(45) | Client IP |
| created_at | DATETIME | When |

---

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/register` | Create account |
| GET/POST | `/login` | Sign in |
| GET | `/logout` | Sign out |
| GET | `/dashboard` | User dashboard |
| GET | `/certificates` | List certificates (+ search/filter) |
| GET/POST | `/upload` | Upload new certificate |
| GET | `/certificate/<id>` | Certificate detail |
| GET/POST | `/certificate/<id>/edit` | Edit certificate |
| POST | `/certificate/<id>/delete` | Delete certificate |
| GET | `/share/<uid>` | Public share page |
| GET | `/download/<id>` | Download file |
| GET | `/uploads/<filename>` | Serve uploaded file |
| GET | `/api/qr/<id>` | Generate QR code (JSON) |
| POST | `/api/toggle-privacy/<id>` | Toggle public/private (JSON) |
| GET | `/api/stats` | Dashboard stats (JSON) |
| GET | `/profile` | User profile |
| GET | `/admin` | Admin panel |

---

## 🚢 Deployment

### Render.com
1. Push to GitHub
2. Create new Web Service on Render
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python app.py`
5. Add environment variables from `.env.example`

### Railway
```bash
railway login
railway init
railway up
```

### VPS (Ubuntu)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📁 Project Structure

```
certvault/
├── app.py                 # Main Flask app
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker config
├── docker-compose.yml     # Docker Compose
├── .env.example           # Environment template
├── uploads/               # Certificate files (auto-created)
├── certvault.db           # SQLite database (auto-created)
├── static/
│   ├── css/style.css      # All styles
│   └── js/main.js         # All JavaScript
└── templates/
    ├── base.html          # Base layout + nav
    ├── index.html         # Landing page
    ├── login.html         # Login form
    ├── register.html      # Registration form
    ├── dashboard.html     # User dashboard
    ├── certificates.html  # Certificate list
    ├── upload.html        # Upload form
    ├── certificate_detail.html
    ├── edit_certificate.html
    ├── share.html         # Public share page
    ├── profile.html       # User profile
    ├── admin.html         # Admin panel
    └── error.html         # 404/403 errors
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + K` | Focus search |
| `Ctrl + U` | Go to upload |
| `Escape` | Close sidebar |

---

## 🔮 Future Features

- [ ] Email notifications for expiry (Flask-Mail)
- [ ] OAuth login (Google, GitHub)
- [ ] Blockchain certificate verification
- [ ] Mobile app (React Native)
- [ ] Organization/team accounts
- [ ] Resume integration export
- [ ] Cloud storage (AWS S3 / Cloudinary)
- [ ] OCR auto-extract from certificate images

---

## 📄 License

MIT License – use freely for personal and commercial projects.
