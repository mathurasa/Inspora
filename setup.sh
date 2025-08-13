#!/bin/bash

echo "🚀 Setting up Inspora - Asana-Inspired Work Management Platform"
echo "================================================================"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [ "$python_version" \< "3.8" ]; then
    echo "❌ Python 3.8+ is required. Current version: $python_version"
    exit 1
fi
echo "✅ Python $python_version detected"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Setup environment
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ Environment file created from template"
        echo "⚠️  Please edit .env file with your configuration"
    else
        echo "❌ env.example file not found"
        exit 1
    fi
else
    echo "✅ Environment file already exists"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p static media logs templates
mkdir -p static/css static/js static/images
echo "✅ Directories created"

# Setup database
echo "Setting up database..."
python manage.py makemigrations
if [ $? -ne 0 ]; then
    echo "❌ Failed to create migrations"
    exit 1
fi

python manage.py migrate
if [ $? -eq 0 ]; then
    echo "✅ Database setup completed"
else
    echo "❌ Failed to run migrations"
    exit 1
fi

# Check for superuser
echo "Checking superuser accounts..."
superuser_count=$(python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).count())" 2>/dev/null)

if [ "$superuser_count" = "0" ]; then
    echo "⚠️  No superuser found. Please create one manually:"
    echo "   python manage.py createsuperuser"
else
    echo "✅ Superuser account already exists"
fi

# Check Redis
echo "Checking Redis connection..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is not running. Please start Redis:"
        echo "   redis-server"
    fi
else
    echo "⚠️  Redis CLI not found. Please install Redis"
fi

echo ""
echo "================================================================"
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Start Redis: redis-server"
echo "3. Run the application: python manage.py runserver"
echo "4. Access the application at: http://localhost:8000"
echo "5. Access admin at: http://localhost:8000/admin"
echo ""
echo "For more information, see README.md"
