# 🚀 ADA.SEA Production Deployment Guide

## Prerequisites

### Hardware Requirements

**Recommended: Mac Mini M4**
- CPU: Apple M4 chip
- RAM: 16GB minimum (32GB recommended)
- Storage: 256GB SSD minimum (512GB recommended)
- Network: Gigabit Ethernet + WiFi 6
- Location: On-board vessel (edge computing)

### Software Requirements

- Docker 24.0+
- Docker Compose 2.20+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Neo4j 5+

---

## Quick Start (Production)

### 1. Clone Repository

```bash
git clone https://github.com/ahmetengin/ada-marina-wim.git
cd ada-marina-wim
```

### 2. Configure Environment

```bash
# Copy production environment template
cp .env.production.example .env.production

# Edit with secure values
nano .env.production
```

**CRITICAL: Change these values:**
- `SECRET_KEY` - Generate with `openssl rand -hex 32`
- `POSTGRES_PASSWORD` - Strong password
- `REDIS_PASSWORD` - Strong password
- `NEO4J_PASSWORD` - Strong password
- `ANTHROPIC_API_KEY` - Your Claude API key
- `GRAFANA_PASSWORD` - Monitoring dashboard password

### 3. Generate SSL Certificates

```bash
# For production, use real SSL certificates
# Self-signed for testing:
mkdir -p /etc/ssl/certs /etc/ssl/private

openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
  -keyout /etc/ssl/private/ada-sea.key \
  -out /etc/ssl/certs/ada-sea.crt \
  -subj "/C=TR/ST=Istanbul/L=Istanbul/O=Ada.sea/CN=ada.sea"
```

### 4. Build and Deploy

```bash
# Build production images
docker-compose -f docker-compose.yml build

# Start services
docker-compose -f docker-compose.yml up -d

# Verify all services are running
docker-compose ps
```

### 5. Initialize Database

```bash
# Run Alembic migrations
docker-compose exec app alembic upgrade head

# Seed initial data
docker-compose exec app python scripts/seed_data.py
```

### 6. Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# Privacy status
curl http://localhost:8000/api/v1/privacy/status

# API documentation
open http://localhost:8000/docs
```

---

## Production Architecture

### Edge-First Deployment

```
┌─────────────────────────────────────────┐
│         Mac Mini M4 (On-Board)          │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐  │
│  │   ADA.SEA Application           │  │
│  │   • FastAPI                     │  │
│  │   • Privacy Core                │  │
│  │   • Captain Control             │  │
│  └─────────────────────────────────┘  │
│                                         │
│  ┌─────────────────────────────────┐  │
│  │   Databases (Local)             │  │
│  │   • PostgreSQL                  │  │
│  │   • Redis                       │  │
│  │   • Neo4j                       │  │
│  └─────────────────────────────────┘  │
│                                         │
│  ┌─────────────────────────────────┐  │
│  │   Monitoring                    │  │
│  │   • Prometheus                  │  │
│  │   • Grafana                     │  │
│  └─────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
         │
         ↓ (Only with captain approval)
┌─────────────────────────────────────────┐
│      External Services (Optional)       │
├─────────────────────────────────────────┤
│  • Marina APIs (privacy-safe)          │
│  • Weather Service (anonymous)         │
│  • Zero-Knowledge Backup (encrypted)   │
└─────────────────────────────────────────┘
```

---

## Security Hardening

### 1. Network Security

```bash
# Firewall configuration (deny all inbound by default)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 8000/tcp  # API (HTTPS only in production)
sudo ufw allow 9090/tcp  # Prometheus (localhost only)
sudo ufw allow 3000/tcp  # Grafana (localhost only)
sudo ufw enable
```

### 2. SSL/TLS Configuration

Use Let's Encrypt for production SSL:

```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d ada.sea

# Auto-renewal
sudo certbot renew --dry-run
```

Update `docker-compose.yml`:
```yaml
volumes:
  - /etc/letsencrypt/live/ada.sea/fullchain.pem:/etc/ssl/certs/ada-sea.crt
  - /etc/letsencrypt/live/ada.sea/privkey.pem:/etc/ssl/private/ada-sea.key
```

### 3. Encryption Keys

Generate and store encryption keys securely:

```bash
# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Store in environment (production: use Secure Enclave/TPM)
echo "ENCRYPTION_KEY=<generated_key>" >> .env.production
```

### 4. Database Security

```sql
-- Create restricted user
CREATE USER ada_sea_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE ada_sea_production TO ada_sea_user;
GRANT USAGE ON SCHEMA public TO ada_sea_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ada_sea_user;

-- Enable row-level security
ALTER TABLE data_transfers ENABLE ROW LEVEL SECURITY;
CREATE POLICY captain_isolation ON data_transfers
  USING (captain_id = current_setting('app.current_captain'));
```

---

## Monitoring & Alerting

### Access Monitoring Dashboards

- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **Health**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

### Key Metrics to Monitor

1. **Privacy Metrics**
   - Data transfer requests/minute
   - Captain approval rate
   - Denied transfers
   - Audit log size

2. **Performance Metrics**
   - API response time
   - Database query time
   - Memory usage
   - CPU usage

3. **Security Metrics**
   - Failed authentication attempts
   - Rate limit hits
   - Suspicious activities

### Alert Configuration

Edit `monitoring/prometheus/alerts.yml`:

```yaml
groups:
  - name: ada_sea_alerts
    rules:
      - alert: HighDataTransferRate
        expr: rate(data_transfers_total[5m]) > 10
        annotations:
          summary: "Unusually high data transfer rate"

      - alert: PrivacyViolationAttempt
        expr: unauthorized_data_share_attempts_total > 0
        annotations:
          summary: "CRITICAL: Attempted privacy violation"
```

---

## Backup & Recovery

### Automated Database Backups

```bash
# Create backup script
cat > /usr/local/bin/ada-sea-backup.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/ada-sea"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup PostgreSQL
docker-compose exec -T postgres pg_dump -U ada_sea_user ada_sea_production | \
  gzip > "$BACKUP_DIR/postgres_$TIMESTAMP.sql.gz"

# Backup Redis
docker-compose exec -T redis redis-cli SAVE
docker cp ada-marina-wim_redis_1:/data/dump.rdb "$BACKUP_DIR/redis_$TIMESTAMP.rdb"

# Encrypt backups
gpg --encrypt --recipient "captain@ada.sea" \
  "$BACKUP_DIR/postgres_$TIMESTAMP.sql.gz"

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -type f -mtime +30 -delete

echo "Backup completed: $TIMESTAMP"
EOF

chmod +x /usr/local/bin/ada-sea-backup.sh

# Schedule daily backups
echo "0 2 * * * /usr/local/bin/ada-sea-backup.sh" | crontab -
```

### Zero-Knowledge Cloud Backup

**IMPORTANT**: Only captain can decrypt backups!

```bash
# Enable zero-knowledge backup (requires captain passphrase)
curl -X POST http://localhost:8000/api/v1/privacy/backup/enable \
  -H "Content-Type: application/json" \
  -d '{
    "captain_id": "boss@ada.sea",
    "passphrase": "captain_secret_passphrase"
  }'
```

---

## Performance Tuning

### 1. Database Optimization

```sql
-- PostgreSQL configuration (postgresql.conf)
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 20MB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
```

### 2. Application Optimization

```python
# app/core/config.py (production settings)
API_WORKERS = 8  # Match CPU cores
CONNECTION_POOL_SIZE = 20
CONNECTION_POOL_MAX_OVERFLOW = 40
QUERY_TIMEOUT = 30
REQUEST_TIMEOUT = 60
```

### 3. Redis Caching

```bash
# Enable Redis caching for frequent queries
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

---

## Testing Production Deployment

### 1. Run Demo Script

```bash
python scripts/production_demo.py
```

### 2. Load Testing

```bash
# Install k6
curl https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz -L | tar xvz
sudo mv k6-v0.47.0-linux-amd64/k6 /usr/local/bin/

# Run load test
k6 run scripts/load_test.js
```

### 3. Security Scan

```bash
# Install OWASP ZAP
docker pull owasp/zap2docker-stable

# Run security scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:8000
```

---

## Troubleshooting

### Issue: Services Won't Start

```bash
# Check logs
docker-compose logs -f app
docker-compose logs -f postgres
docker-compose logs -f redis

# Restart services
docker-compose restart
```

### Issue: Database Connection Failed

```bash
# Verify PostgreSQL is running
docker-compose exec postgres psql -U ada_sea_user -d ada_sea_production

# Check connection string
echo $DATABASE_URL
```

### Issue: High Memory Usage

```bash
# Check resource usage
docker stats

# Adjust memory limits in docker-compose.yml
services:
  app:
    mem_limit: 4g
```

---

## Maintenance

### Daily Tasks
- ✓ Check monitoring dashboards
- ✓ Review audit logs
- ✓ Verify backups completed

### Weekly Tasks
- ✓ Review privacy metrics
- ✓ Check for security updates
- ✓ Analyze performance trends

### Monthly Tasks
- ✓ Security audit
- ✓ Dependency updates
- ✓ Compliance review (KVKK/GDPR)

---

## Support & Contact

**Technical Support:**
- Email: support@ada.sea
- Slack: ada-sea.slack.com

**Security Issues:**
- Email: security@ada.sea
- PGP: Available at ada.sea/pgp

**Privacy Questions:**
- Email: privacy@ada.sea
- DPO: veri-sorumlusu@ada.sea

---

## License

Copyright © 2025 ADA.SEA Platform

**"Kaptan ne derse o olur. Nokta."**
