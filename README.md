# Healthcare Management System (HMS)

A high-security, automated Healthcare Management System specializing in seamless appointment logistics, bidirectional WhatsApp communication, and inter-hospital patient data portability.

![CI/CD](https://github.com/yourusername/hms/workflows/CI%2FCD%20Pipeline/badge.svg)
![Security](https://github.com/yourusername/hms/workflows/Security%20Scan/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🏥 Key Features

### 1. Smart Appointment & WhatsApp Engine
- **Automated Scheduling**: Intelligent appointment booking with conflict detection
- **Bidirectional WhatsApp Communication**: Confirmations, reminders, rescheduling via WhatsApp
- **Waitlist Automation**: Automatic notifications when slots become available
- **Live Queue Management**: Real-time patient queue with estimated wait times

### 2. Universal Patient Vault (EMR)
- **QR-ID System**: Unique patient identification with QR codes
- **Encrypted Medical Records**: AES-256 encryption for all sensitive data
- **Multimedia History**: Support for lab reports, X-rays, scans, and documents
- **Dental Odontogram**: Interactive dental chart with treatment history
- **Ambient Scribing**: AI-powered clinical note transcription

### 3. Federated Patient Transfer ("The Handshake")
- **Permission-Based Access**: Time-limited, permission-controlled data sharing
- **Inter-Hospital Portability**: Secure patient data transfer between institutions
- **Audit Trail**: Complete logging of all data access and transfers

### 4. Doctor's Command Center
- **Real-Time Dashboard**: Live statistics and patient queue
- **Image Annotation**: X-ray and scan markup tools
- **Patient Overview**: Quick access to medical history and allergies

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Django 5.1, Django REST Framework |
| **Frontend** | Next.js 15, React 19, TypeScript |
| **Database** | PostgreSQL 16 |
| **Task Queue** | Celery + Redis |
| **Storage** | AWS S3 (encrypted) |
| **Styling** | Tailwind CSS |
| **Authentication** | JWT (access + refresh tokens) |
| **Containerization** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |

## 🔒 Security Features

- **HIPAA Compliance**: Designed to meet healthcare data protection standards
- **AES-256 Encryption**: All sensitive medical data encrypted at rest
- **Signed URLs**: S3 files accessible only via 10-minute expiring URLs
- **Audit Logging**: Comprehensive tracking of all data access
- **Role-Based Access Control**: Granular permissions (Admin, Doctor, Patient, Staff)
- **JWT Authentication**: Secure token-based authentication with refresh mechanism
- **Rate Limiting**: API protection against abuse

## 📁 Project Structure

```
HMS/
├── backend/                    # Django Backend
│   ├── apps/
│   │   ├── core/              # Shared utilities, encryption, permissions
│   │   ├── users/             # User authentication & management
│   │   ├── patients/          # Patient profiles & health data
│   │   ├── doctors/           # Doctor profiles & schedules
│   │   ├── clinics/           # Clinic management
│   │   ├── appointments/      # Appointment scheduling & queue
│   │   ├── notifications/     # WhatsApp & notification services
│   │   ├── emr/               # Electronic Medical Records
│   │   ├── transfers/         # Federated patient transfers
│   │   └── audit/             # Audit logging
│   ├── hms/                   # Django project settings
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # Next.js Frontend
│   ├── src/
│   │   ├── app/               # Next.js 15 App Router pages
│   │   ├── components/        # React components
│   │   ├── lib/               # Utilities & API client
│   │   ├── stores/            # Zustand state management
│   │   └── types/             # TypeScript type definitions
│   ├── package.json
│   └── Dockerfile
│
├── nginx/                      # Nginx configuration
├── .github/workflows/          # CI/CD pipelines
├── docker-compose.yml          # Production Docker setup
├── docker-compose.dev.yml      # Development Docker setup
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (optional)

### Option 1: Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/hms.git
   cd hms
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   # Development
   docker-compose -f docker-compose.dev.yml up -d

   # Production
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/
   - Django Admin: http://localhost:8000/admin/

### Option 2: Manual Setup

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export SECRET_KEY="your-secret-key"
export DATABASE_URL="postgres://user:password@localhost:5432/hms_db"
export REDIS_URL="redis://localhost:6379/0"
export AES_ENCRYPTION_KEY="your-32-byte-encryption-key-here"

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

#### Celery Workers

```bash
# In a separate terminal
celery -A hms worker -l info

# Celery Beat (for scheduled tasks)
celery -A hms beat -l info
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local
# Edit .env.local with your API URL

# Start development server
npm run dev
```

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/register/` | User registration |
| POST | `/api/users/token/` | Get JWT tokens |
| POST | `/api/users/token/refresh/` | Refresh access token |
| GET | `/api/users/me/` | Get current user |

### Patients
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/patients/` | List patients |
| GET | `/api/patients/{id}/` | Get patient details |
| GET | `/api/patients/by-qr/{patient_id}/` | Get patient by QR code |
| POST | `/api/patients/{id}/allergies/` | Add allergy |
| POST | `/api/patients/{id}/medications/` | Add medication |

### Appointments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/appointments/` | List appointments |
| POST | `/api/appointments/` | Create appointment |
| GET | `/api/appointments/available-slots/` | Get available slots |
| POST | `/api/appointments/{id}/cancel/` | Cancel appointment |
| POST | `/api/appointments/{id}/reschedule/` | Reschedule appointment |
| GET | `/api/appointments/live-queue/` | Get live queue |

### EMR
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/emr/records/` | List medical records |
| POST | `/api/emr/records/` | Create medical record |
| GET | `/api/emr/dental/{patient_id}/` | Get dental record |
| POST | `/api/emr/prescriptions/` | Create prescription |

### Transfers
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/transfers/access/` | Grant patient access |
| POST | `/api/transfers/requests/` | Create transfer request |
| POST | `/api/transfers/requests/{id}/accept/` | Accept transfer |

## 🔧 Configuration

### Environment Variables

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# Database
DATABASE_URL=postgres://user:password@localhost:5432/hms_db

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Encryption
AES_ENCRYPTION_KEY=your-32-byte-key-for-aes-256-encryption

# WhatsApp (Twilio/Wati)
WHATSAPP_API_KEY=your-api-key
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest --cov=. --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm run test
npm run type-check
npm run lint
```

## 📊 Database Schema

The system uses a PostgreSQL database with the following main tables:

- `users` - User accounts with role-based access
- `patients` - Patient profiles and demographics
- `doctors` - Doctor profiles and qualifications
- `clinics` - Clinic information and facilities
- `appointments` - Appointment scheduling
- `live_queue` - Real-time patient queue
- `medical_records` - EMR with encrypted notes
- `medical_files` - Uploaded documents and images
- `dental_records` - Dental odontogram data
- `prescriptions` - Medication prescriptions
- `patient_access` - Federated access permissions
- `transfer_requests` - Inter-hospital transfers
- `audit_logs` - HIPAA compliance logging

## 🚢 Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure secure `SECRET_KEY`
- [ ] Set up SSL/TLS certificates
- [ ] Configure production database
- [ ] Set up AWS S3 bucket with encryption
- [ ] Configure WhatsApp Business API
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Enable rate limiting
- [ ] Configure backup strategy
- [ ] Review security headers

### Scaling Considerations

- Use PostgreSQL connection pooling (PgBouncer)
- Scale Celery workers horizontally
- Use Redis Cluster for high availability
- Consider read replicas for database
- Implement CDN for static assets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/)
- [Next.js](https://nextjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Radix UI](https://www.radix-ui.com/)

## 📞 Support

For support, email support@hms-healthcare.com or create an issue in this repository.

---

Built with ❤️ for better healthcare management
