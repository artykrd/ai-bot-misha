#!/bin/bash

# ============================================
# AI Telegram Bot - Environment Setup Script
# ============================================
# This script installs and configures all
# required dependencies for the bot
# ============================================

set -e  # Exit on error

echo "🚀 Starting AI Bot environment setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

# ============================================
# 1. System Update
# ============================================
print_info "Updating system packages..."
sudo apt-get update

# ============================================
# 2. Install PostgreSQL
# ============================================
print_info "Installing PostgreSQL 15..."

if ! command -v psql &> /dev/null; then
    # Add PostgreSQL repository
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install -y postgresql-15 postgresql-contrib-15
else
    print_info "PostgreSQL already installed"
fi

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# ============================================
# 3. Create Database
# ============================================
print_info "Creating database..."

DB_NAME="ai_bot"
DB_USER="ai_bot_user"
DB_PASSWORD="your_password_here"  # TODO: Change this!

sudo -u postgres psql <<EOF
-- Create user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

print_info "Database '$DB_NAME' created successfully"

# ============================================
# 4. Install Redis
# ============================================
print_info "Installing Redis..."

if ! command -v redis-server &> /dev/null; then
    sudo apt-get install -y redis-server
else
    print_info "Redis already installed"
fi

# Configure Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
if redis-cli ping | grep -q PONG; then
    print_info "Redis is running"
else
    print_error "Redis failed to start"
    exit 1
fi

# ============================================
# 5. Install Python 3.11+
# ============================================
print_info "Checking Python version..."

if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if (( $(echo "$PYTHON_VERSION >= 3.11" | bc -l) )); then
        PYTHON_CMD="python3"
    else
        print_error "Python 3.11+ is required. Current version: $PYTHON_VERSION"
        print_info "Installing Python 3.11..."
        sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
        PYTHON_CMD="python3.11"
    fi
else
    print_info "Installing Python 3.11..."
    sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
    PYTHON_CMD="python3.11"
fi

print_info "Using Python: $($PYTHON_CMD --version)"

# ============================================
# 6. Install pip
# ============================================
print_info "Installing pip..."
sudo apt-get install -y python3-pip

# ============================================
# 7. Create Virtual Environment
# ============================================
print_info "Creating virtual environment..."

if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    print_info "Virtual environment created"
else
    print_warn "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# ============================================
# 8. Install Python Dependencies
# ============================================
print_info "Installing Python dependencies..."

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_info "Dependencies installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

# ============================================
# 9. Create .env file
# ============================================
print_info "Creating .env file..."

if [ ! -f ".env" ]; then
    cp .env.example .env
    print_warn "Created .env from .env.example"
    print_warn "⚠️  IMPORTANT: Edit .env file with your actual credentials!"
else
    print_warn ".env file already exists"
fi

# ============================================
# 10. Create alembic.ini
# ============================================
print_info "Creating alembic.ini..."

if [ ! -f "alembic.ini" ]; then
    cp alembic.ini.example alembic.ini
    print_info "Created alembic.ini"
fi

# ============================================
# 11. Run Database Migrations
# ============================================
print_info "Running database migrations..."

# Initialize alembic if needed
if [ ! -d "alembic/versions" ] || [ -z "$(ls -A alembic/versions)" ]; then
    print_info "Creating initial migration..."
    alembic revision --autogenerate -m "Initial migration"
fi

# Run migrations
alembic upgrade head
print_info "Database migrations completed"

# ============================================
# 12. Create necessary directories
# ============================================
print_info "Creating storage directories..."

mkdir -p storage/images storage/videos storage/audio storage/documents storage/temp
mkdir -p logs

print_info "Directories created"

# ============================================
# Setup Complete
# ============================================
echo ""
print_info "=========================================="
print_info "✅ Setup completed successfully!"
print_info "=========================================="
echo ""
print_warn "⚠️  NEXT STEPS:"
echo "1. Edit .env file with your actual API keys and tokens"
echo "2. Update database credentials in .env if needed"
echo "3. Activate virtual environment: source venv/bin/activate"
echo "4. Run the bot: python main.py"
echo "5. Run admin bot: python admin_main.py"
echo "6. Run API server: python api_main.py"
echo ""
print_info "For more information, see README.md"
echo ""
