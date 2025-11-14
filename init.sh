#!/bin/bash

# ADA.MARINA + ADA.SEA - Project Initialization Script
# This script sets up the project for first-time use

set -e

echo "🚢 ADA.MARINA + ADA.SEA - Project Initialization"
echo "================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Step 1: Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your ANTHROPIC_API_KEY"
    echo "   You can get an API key from: https://console.anthropic.com/"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Step 2: Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p database/migrations/versions
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/prometheus
echo "✅ Directories created"
echo ""

# Step 3: Start Docker containers
echo "🐳 Starting Docker containers..."
echo "This may take a few minutes on first run..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready (30 seconds)..."
sleep 30
echo ""

# Step 4: Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec -T build-agent alembic upgrade head || echo "⚠️  Migration may run on first API start"
echo ""

# Step 5: Seed initial data
echo "🌱 Seeding initial data..."
if [ -f database/seeds/seed_berths.py ]; then
    docker-compose exec -T build-agent python database/seeds/seed_berths.py || echo "⚠️  Seed will run on first API start"
fi
if [ -f database/seeds/seed_customers.py ]; then
    docker-compose exec -T build-agent python database/seeds/seed_customers.py || echo "⚠️  Seed will run on first API start"
fi
if [ -f database/seeds/seed_vessels.py ]; then
    docker-compose exec -T build-agent python database/seeds/seed_vessels.py || echo "⚠️  Seed will run on first API start"
fi
echo ""

# Step 6: Health check
echo "🏥 Running health check..."
sleep 5
HEALTH_CHECK=$(curl -s http://localhost:8000/health || echo "not ready")
if [[ $HEALTH_CHECK == *"healthy"* ]]; then
    echo "✅ API is healthy!"
else
    echo "⚠️  API may still be starting up. Check docker-compose logs build-agent"
fi
echo ""

# Print access information
echo "================================================"
echo "✅ Initialization Complete!"
echo "================================================"
echo ""
echo "📊 Access Points:"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - API Health:        http://localhost:8000/health"
echo "   - Privacy Status:    http://localhost:8000/api/v1/privacy/status"
echo "   - Marina Dashboard:  http://localhost:8000/api/v1/dashboard/overview"
echo "   - Grafana:          http://localhost:3000 (admin/admin_secure_2025)"
echo "   - Prometheus:       http://localhost:9090"
echo "   - Neo4j:            http://localhost:7474 (neo4j/neo4j_secure_pass_2025)"
echo ""
echo "📖 Next Steps:"
echo "   1. Edit .env file and add your ANTHROPIC_API_KEY"
echo "   2. Restart services: docker-compose restart"
echo "   3. Visit http://localhost:8000/docs to explore the API"
echo "   4. Run demo: docker-compose exec build-agent python scripts/production_demo.py"
echo ""
echo "🛑 To stop: docker-compose down"
echo "🔄 To restart: docker-compose restart"
echo "📋 To view logs: docker-compose logs -f"
echo ""
echo "\"Kaptan ne derse o olur. Nokta.\" 🔒⛵"
echo ""
