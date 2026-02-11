# Service Contract Management System

A full-stack application for managing service contracts, quotations, and custom forms between admins and clients.

## 🚀 Features

### Authentication & Authorization
- **JWT-based authentication** with secure password hashing (bcrypt)
- **Role-based access control** (Admin & Client roles)
- Protected routes and API endpoints

### Admin Features
- **Form Builder**: Create custom forms with multiple field types (text, textarea, email, number)
- **Form Management**: View all forms and their submission status
- **Quotation Creation**: Create detailed quotations for submitted forms
- **Email Notifications**: Automatic email alerts to clients when quotations are created
- **Contract Management**: View and download all generated contracts

### Client Features
- **Form Submission**: Fill out and submit custom forms assigned by admin
- **Quotation Review**: View received quotations with pricing and details
- **Quotation Response**: Approve or reject quotations
- **Contract Access**: Download PDF contracts for approved quotations

### Technical Features
- **PDF Generation**: Automatic contract generation using ReportLab
- **Email Integration**: SMTP-based email notifications (configurable)
- **MongoDB Database**: Persistent data storage
- **REST API**: Complete API with proper error handling
- **Responsive UI**: Modern, clean interface using Tailwind CSS and shadcn/ui

## 🏗️ Tech Stack

### Backend
- **FastAPI** - Modern, high-performance Python web framework
- **MongoDB** - NoSQL database with Motor (async driver)
- **JWT** - JSON Web Tokens for authentication
- **ReportLab** - PDF generation
- **Passlib/Bcrypt** - Password hashing
- **AIOSMTPLIB** - Async email sending

### Frontend
- **React 19** - UI library
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Pre-built component library
- **Lucide React** - Icon library

## 📦 Project Structure

```
/app/
├── backend/
│   ├── server.py           # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   ├── .env               # Environment variables
│   └── contracts/         # Generated PDF contracts
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main application
│   │   ├── pages/         # Page components
│   │   │   ├── LoginPage.js
│   │   │   ├── RegisterPage.js
│   │   │   ├── AdminDashboard.js
│   │   │   └── ClientDashboard.js
│   │   └── components/    # Reusable UI components
│   ├── package.json
│   └── .env              # Frontend environment variables
└── README.md
```

## 🔧 Configuration

### Backend Environment Variables (.env)
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
CORS_ORIGINS="*"
JWT_SECRET="your-secret-key-change-in-production-12345"

# SMTP Configuration (optional - for email notifications)
SMTP_HOST=""
SMTP_PORT="587"
SMTP_USER=""
SMTP_PASS=""
```

### Frontend Environment Variables (.env)
```env
REACT_APP_BACKEND_URL=https://your-domain.com
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
```

## 🚦 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB
- Yarn package manager

### Installation

1. **Backend Setup**
```bash
cd /app/backend
pip install -r requirements.txt
```

2. **Frontend Setup**
```bash
cd /app/frontend
yarn install
```

### Running the Application

Both services are managed by supervisor:

```bash
# Restart all services
sudo supervisorctl restart all

# Restart backend only
sudo supervisorctl restart backend

# Restart frontend only
sudo supervisorctl restart frontend

# Check status
sudo supervisorctl status
```

### Default Users (for testing)

**Admin Account:**
- Email: `admin@test.com`
- Password: `admin123`

**Client Account:**
- Email: `client@test.com`
- Password: `client123`

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info

### Forms
- `POST /api/forms` - Create form (Admin only)
- `GET /api/forms` - Get all forms
- `GET /api/forms/{id}` - Get specific form
- `POST /api/forms/{id}/submit` - Submit form (Client)

### Quotations
- `POST /api/quotations` - Create quotation (Admin only)
- `GET /api/quotations` - Get all quotations
- `GET /api/quotations/{id}` - Get specific quotation
- `POST /api/quotations/{id}/respond` - Respond to quotation (Client)

### Contracts
- `GET /api/contracts` - Get all contracts
- `GET /api/contracts/{id}/download` - Download contract PDF

## 🔒 Security Features

- Password hashing using bcrypt
- JWT token-based authentication
- Role-based access control
- CORS protection
- Request validation using Pydantic models
- SQL injection prevention (NoSQL database)

## 📧 Email Notifications

To enable email notifications:

1. Update the SMTP settings in `/app/backend/.env`
2. Add your SMTP credentials:
   - SMTP_HOST: Your SMTP server
   - SMTP_PORT: Usually 587 for TLS
   - SMTP_USER: Your email address
   - SMTP_PASS: Your email password or app password

Example for Gmail:
```env
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-email@gmail.com"
SMTP_PASS="your-app-password"
```

## 📝 Workflow

1. **Admin creates a form** → Assigns it to a client
2. **Client logs in** → Sees assigned form
3. **Client fills and submits** → Form marked as submitted
4. **Admin creates quotation** → Client receives email notification
5. **Client reviews quotation** → Approves or rejects
6. **If approved** → Contract PDF is automatically generated
7. **Both parties can download** → The contract PDF

## 🎨 UI Features

- Clean, modern design
- Responsive layout
- Tab-based navigation
- Status badges for forms, quotations, and contracts
- Form validation
- Loading states
- Error handling with user-friendly messages

## 🧪 Testing

Test the API using curl:

```bash
# Register user
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"test123","role":"client"}'

# Login
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

## 🐛 Troubleshooting

**Backend not starting?**
```bash
# Check logs
tail -f /var/log/supervisor/backend.err.log

# Verify MongoDB is running
sudo systemctl status mongodb
```

**Frontend not loading?**
```bash
# Check logs
tail -f /var/log/supervisor/frontend.err.log

# Clear node_modules and reinstall
cd /app/frontend
rm -rf node_modules
yarn install
```

## 📄 License

This project is created for demonstration purposes.

## 🤝 Support

For issues or questions, please check the logs:
- Backend: `/var/log/supervisor/backend.*.log`
- Frontend: `/var/log/supervisor/frontend.*.log`
