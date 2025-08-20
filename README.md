# Inspora - Inspired Work Management Platform

Inspora is an enterprise-grade work management platform that scales, empowering teams to manage projects, tasks, goals, and workflows intelligently fully customizable and self-hosted.

## 🚀 Features

### Core Features
- **Project & Task Management**: Multiple layouts (List, Board, Calendar, Timeline/Gantt)
- **Goals & Portfolios**: Establish and connect work to company-wide goals
- **Automation & Workflows**: Custom templates, forms, and workflow automation
- **AI-Powered Features**: Smart status monitoring, editing, summaries, and goal optimization
- **Admin & Security**: Role-based access, guest management, audit suite, and permissions

### Technical Features
- **Real-time Updates**: WebSocket support for live notifications and updates
- **RESTful API**: Comprehensive API for integration and mobile apps
- **Multi-tenant**: Team-based organization with role-based permissions
- **Audit Logging**: Complete audit trail for compliance and security
- **Scalable Architecture**: Built with Django and modern web technologies

## 🏗️ Architecture

### Backend
- **Framework**: Django 4.2 + Django REST Framework
- **Database**: MySQL/PostgreSQL (SQLite for development)
- **Real-time**: Django Channels with Redis
- **Authentication**: JWT-based authentication
- **Task Queue**: Celery with Redis

### Frontend
- **UI Framework**: Bootstrap 5 for responsive design
- **JavaScript**: Vanilla JS with WebSocket support
- **Views**: List, Board (Kanban), Calendar, Timeline/Gantt
- **Dashboard**: Real-time monitoring and reporting

## 📋 Prerequisites

- Python 3.8+
- Redis 6.0+
- MySQL 8.0+ or PostgreSQL 12+ (optional for development)
- Node.js 16+ (for frontend assets)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Inspora
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
cp env.example .env
# Edit .env with your configuration
```

### 5. Database Setup
```bash
# For SQLite (development)
python manage.py makemigrations
python manage.py migrate

# For MySQL/PostgreSQL
# Update .env with database credentials
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Start Redis
```bash
# Install Redis if not already installed
redis-server
```

### 8. Run the Application
```bash
python manage.py runserver
```

## 🚀 Quick Start

### 1. Access the Application
- **Main Application**: http://localhost:8000
- **Admin Interface**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/

### 2. Create Your First Project
1. Log in with your superuser account
2. Navigate to Projects
3. Click "Create New Project"
4. Fill in project details and save

### 3. Add Team Members
1. Go to Teams section
2. Create a new team
3. Invite team members
4. Assign roles and permissions

## 📱 API Usage

### Authentication
```bash
# Get JWT token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Use token in subsequent requests
curl -H "Authorization: Bearer <your_token>" \
  http://localhost:8000/api/projects/
```

### Example API Endpoints
- `GET /api/projects/` - List all projects
- `POST /api/projects/` - Create new project
- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create new task
- `GET /api/goals/` - List all goals

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Django secret key
- `DEBUG`: Enable/disable debug mode
- `DB_ENGINE`: Database backend
- `REDIS_URL`: Redis connection string
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

### Database Configuration
The application supports multiple database backends:
- **SQLite**: Default for development
- **MySQL**: Production-ready
- **PostgreSQL**: Production-ready

### Redis Configuration
Redis is used for:
- WebSocket channel layers
- Celery task queue
- Caching
- Session storage

## 🏗️ Development

### Project Structure
```
Inspora/
├── accounts/          # User management
├── projects/          # Project management
├── tasks/            # Task management
├── goals/            # Goal management
├── portfolios/       # Portfolio management
├── templates/        # Template system
├── forms/            # Dynamic forms
├── automations/      # Workflow automation
├── notifications_app/ # Notification system
├── audit/            # Audit logging
├── inspora/          # Main project settings
├── static/           # Static files
├── templates/        # HTML templates
└── manage.py         # Django management script
```

### Adding New Features
1. Create new Django app: `python manage.py startapp your_app`
2. Add app to `INSTALLED_APPS` in settings
3. Create models, views, and URLs
4. Add to main URL configuration
5. Create migrations and apply

### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure production database
- [ ] Set secure `SECRET_KEY`
- [ ] Configure static file serving
- [ ] Set up SSL/TLS certificates
- [ ] Configure Redis for production
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t inspora .
docker run -p 8000:8000 inspora
```

### Cloud Deployment
The application is designed to be cloud-ready and can be deployed to:
- **AWS**: EC2, RDS, ElastiCache
- **Google Cloud**: Compute Engine, Cloud SQL, Memorystore
- **Azure**: Virtual Machines, Azure SQL, Redis Cache
- **Heroku**: With PostgreSQL add-on

## 📊 Monitoring & Analytics

### Built-in Monitoring
- **Audit Logs**: Complete activity tracking
- **Performance Metrics**: Response times and throughput
- **User Analytics**: Usage patterns and engagement
- **System Health**: Database performance and Redis status

### Integration Options
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Sentry**: Error tracking
- **Logstash**: Log aggregation

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-based Access Control**: Granular permissions system
- **Audit Logging**: Complete activity trail
- **Data Encryption**: Sensitive data encryption at rest
- **CSRF Protection**: Cross-site request forgery protection
- **XSS Protection**: Cross-site scripting protection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Include type hints where appropriate

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Documentation
- **API Documentation**: Available at `/api/` when running
- **Code Documentation**: Inline docstrings and comments
- **User Guide**: Built into the application

### Community
- **Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Wiki**: Additional documentation and guides

### Professional Support
For enterprise support and consulting, contact the development team.

## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Core project and task management
- ✅ User authentication and permissions
- ✅ Basic views (List, Calendar)
- ✅ Template and form systems

### Phase 2 (Next)
- 🔄 Board and Timeline views
- 🔄 Dependencies and recurring tasks
- 🔄 Reporting dashboards
- 🔄 Advanced admin controls

### Phase 3 (Future)
- 📋 Portfolios and goals
- 📋 Branching forms
- 📋 Rules and automations
- 📋 Template library

### Phase 4 (Advanced)
- 🚀 AI Studio for smart workflows
- 🚀 Smart chat and summaries
- 🚀 Field suggestions
- 🚀 Goal recommendations

## 🙏 Acknowledgments

- **Django**: The web framework for perfectionists with deadlines
- **Bootstrap**: The most popular HTML, CSS, and JS framework
- **Asana**: Inspiration for the user experience and feature set
- **Open Source Community**: For the amazing packages and tools

---

**Inspora** - Empowering teams to work smarter, not harder. 🚀
