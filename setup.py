#!/usr/bin/env python3
"""
Setup script for Inspora - Asana-Inspired Work Management Platform
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, check=True):
    """Run a shell command."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return e

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_virtual_environment():
    """Create virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return
    
    print("Creating virtual environment...")
    result = run_command("python -m venv venv")
    if result.returncode == 0:
        print("✅ Virtual environment created")
    else:
        print("❌ Failed to create virtual environment")
        sys.exit(1)

def install_dependencies():
    """Install Python dependencies."""
    print("Installing dependencies...")
    
    # Activate virtual environment and install requirements
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip install -r requirements.txt"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip install -r requirements.txt"
    
    result = run_command(pip_cmd)
    if result.returncode == 0:
        print("✅ Dependencies installed successfully")
    else:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def setup_environment():
    """Setup environment configuration."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ Environment file already exists")
        return
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Environment file created from template")
        print("⚠️  Please edit .env file with your configuration")
    else:
        print("❌ env.example file not found")
        sys.exit(1)

def setup_database():
    """Setup database and run migrations."""
    print("Setting up database...")
    
    # Activate virtual environment and run migrations
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_cmd = "venv/bin/python"
    
    # Make migrations
    result = run_command(f"{python_cmd} manage.py makemigrations")
    if result.returncode != 0:
        print("❌ Failed to create migrations")
        sys.exit(1)
    
    # Run migrations
    result = run_command(f"{python_cmd} manage.py migrate")
    if result.returncode == 0:
        print("✅ Database setup completed")
    else:
        print("❌ Failed to run migrations")
        sys.exit(1)

def create_superuser():
    """Create a superuser account."""
    print("Creating superuser account...")
    
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_cmd = "venv/bin/python"
    
    # Check if superuser already exists
    result = run_command(f"{python_cmd} manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); print('Superusers:', User.objects.filter(is_superuser=True).count())\"")
    
    if "Superusers: 0" in result.stdout:
        print("⚠️  No superuser found. Please create one manually:")
        print(f"   {python_cmd} manage.py createsuperuser")
    else:
        print("✅ Superuser account already exists")

def check_redis():
    """Check if Redis is running."""
    print("Checking Redis connection...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
    except ImportError:
        print("⚠️  Redis Python client not installed")
    except redis.ConnectionError:
        print("⚠️  Redis is not running. Please start Redis:")
        print("   redis-server")
    except Exception as e:
        print(f"⚠️  Redis check failed: {e}")

def create_directories():
    """Create necessary directories."""
    directories = [
        "static",
        "media",
        "logs",
        "templates",
        "static/css",
        "static/js",
        "static/images"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def main():
    """Main setup function."""
    print("🚀 Setting up Inspora - Asana-Inspired Work Management Platform")
    print("=" * 70)
    
    # Check prerequisites
    check_python_version()
    
    # Create virtual environment
    create_virtual_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Setup environment
    setup_environment()
    
    # Create directories
    create_directories()
    
    # Setup database
    setup_database()
    
    # Create superuser
    create_superuser()
    
    # Check Redis
    check_redis()
    
    print("\n" + "=" * 70)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your configuration")
    print("2. Start Redis: redis-server")
    print("3. Run the application:")
    
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\python manage.py runserver")
    else:  # Unix/Linux/macOS
        print("   venv/bin/python manage.py runserver")
    
    print("\n4. Access the application at: http://localhost:8000")
    print("5. Access admin at: http://localhost:8000/admin")
    
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()
