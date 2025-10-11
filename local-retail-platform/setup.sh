#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "🚀 Starting Local Retail Platform setup..."

# --- Backend Setup ---
echo "---"
echo "🐍 Setting up Backend (Django)..."
cd backend

# Check if Poetry is installed
if ! command -v poetry &> /dev/null
then
    echo "Poetry could not be found. Please install it first."
    echo "Follow the instructions at: https://python-poetry.org/docs/#installation"
    exit 1
fi

echo "📦 Installing Python dependencies with Poetry..."
poetry install --no-root

echo "🗃️ Applying database migrations..."
python manage.py migrate

echo "👤 Creating Django admin superuser..."
echo "Please enter a password for the 'admin' user (email: admin@example.com)"
python manage.py createsuperuser --username admin --email admin@example.com

echo "✅ Backend setup complete."
echo "---"


# --- Frontend Setup ---
echo "🌐 Setting up Frontend (Next.js)..."
cd ../frontend

echo "📦 Installing Node.js dependencies with npm..."
npm install

echo "✅ Frontend setup complete."
cd ..
echo "---"

# --- Finish ---
echo "🎉 Setup finished successfully!"
echo ""
echo "To run the application, you need two terminals:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    cd backend"
echo "    poetry run python manage.py runserver"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd frontend"
echo "    npm run dev"
echo ""
echo "Then, open http://localhost:3000 in your browser."
