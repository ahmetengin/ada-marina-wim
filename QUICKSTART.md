# 🚀 Quick Start Guide - ADA.MARINA + ADA.SEA

Bu kılavuz, ADA.MARINA + ADA.SEA sistemini **5 dakikada** çalıştırmanız için hazırlanmıştır.

## 📋 Ön Gereksinimler

### Yazılım Gereksinimleri:
- **Docker** 24.0+ → [İndir](https://docs.docker.com/get-docker/)
- **Docker Compose** 2.20+ → [İndir](https://docs.docker.com/compose/install/)
- **Git** → [İndir](https://git-scm.com/)

### Donanım Gereksinimleri:
- CPU: 4+ çekirdek (8 önerilir)
- RAM: 16GB minimum (32GB önerilir)
- Disk: 256GB SSD minimum (512GB önerilir)
- Ağ: Gigabit Ethernet + WiFi 6

### API Anahtarları (Opsiyonel):
- **Anthropic API Key** → [Alın](https://console.anthropic.com/) (AI özellikler için)
- **Parasut Credentials** → [Parasut](https://parasut.com/) (E-fatura için)

---

## ⚡ 1-Dakikalık Kurulum

### Otomatik Kurulum (Önerilen)

```bash
# 1. Projeyi klonlayın
git clone https://github.com/ahmetengin/ada-marina-wim.git
cd ada-marina-wim

# 2. Başlatma scriptini çalıştırın
./init.sh
```

Bu kadar! Script otomatik olarak:
- ✅ .env dosyasını oluşturur
- ✅ Docker container'ları başlatır
- ✅ Database migration çalıştırır
- ✅ İlk verileri yükler (600 rıhtım, 50 müşteri, 80 tekne)
- ✅ Sistem sağlığını kontrol eder

---

## 🔧 Manuel Kurulum

Eğer adım adım ilerlemek isterseniz:

### Adım 1: Çevre Değişkenlerini Ayarlayın (2 dakika)

```bash
# .env dosyasını oluşturun
cp .env.example .env

# API anahtarınızı ekleyin (opsiyonel ama önerili)
nano .env
# Şunu değiştirin: ANTHROPIC_API_KEY="your-key-here"
```

### Adım 2: Docker Container'ları Başlatın (3 dakika)

```bash
# Servisleri başlat
docker-compose up -d

# Container'ların hazır olmasını bekleyin (30 saniye)
sleep 30

# Logları kontrol edin
docker-compose logs -f build-agent
```

### Adım 3: Database'i Hazırlayın (2 dakika)

```bash
# Migration çalıştır
docker-compose exec build-agent alembic upgrade head

# İlk verileri yükle
docker-compose exec build-agent python database/seeds/seed_berths.py
docker-compose exec build-agent python database/seeds/seed_customers.py
docker-compose exec build-agent python database/seeds/seed_vessels.py
```

### Adım 4: Sistem Sağlığını Kontrol Edin

```bash
# Health check
curl http://localhost:8000/health
# Çıktı: {"status": "healthy"}

# Marina dashboard
curl http://localhost:8000/api/v1/dashboard/overview
```

---

## 🌐 Erişim Noktaları

Sistem başarıyla çalıştıktan sonra:

| Servis | URL | Kullanıcı Adı | Şifre |
|--------|-----|---------------|-------|
| **API Dokümantasyonu** | http://localhost:8000/docs | - | - |
| **API Health Check** | http://localhost:8000/health | - | - |
| **Privacy Status** | http://localhost:8000/api/v1/privacy/status | - | - |
| **Marina Dashboard** | http://localhost:8000/api/v1/dashboard/overview | - | - |
| **Grafana** | http://localhost:3000 | admin | admin_secure_2025 |
| **Prometheus** | http://localhost:9090 | - | - |
| **Neo4j Browser** | http://localhost:7474 | neo4j | neo4j_secure_pass_2025 |

---

## 🧪 Demo Senaryolarını Çalıştırın

### 1. Production Demo (7 Senaryo)
```bash
docker-compose exec build-agent python scripts/production_demo.py
```

**Senaryolar:**
1. ✅ West Istanbul Marina check-in
2. ✅ Yalikavak reservation
3. ✅ Privacy status check
4. ✅ Anonymous weather request
5. ✅ KVKK compliance access
6. ✅ Revoke all permissions
7. ✅ Audit trail export

### 2. Autonomous MOB Demo
```bash
docker-compose exec build-agent python scripts/single_handed_mob_demo.py
```

**Senaryo:** Tek kişilik yelkenli → MOB → Otonom müdahale

### 3. Weather-Aware Route Planning
```bash
docker-compose exec build-agent python scripts/adalar_route_demo.py
```

**Senaryo:** 3-günlük Adalar rotası, hava durumu kontrolü

### 4. Smart Privacy Demo
```bash
docker-compose exec build-agent python scripts/smart_privacy_demo.py
```

**Senaryo:** AIS-aware privacy sınıflandırması

---

## 🧪 Testleri Çalıştırın

```bash
# Tüm testler (90+)
docker-compose exec build-agent pytest tests/ -v --cov=app

# Sadece privacy testleri
docker-compose exec build-agent pytest tests/privacy/ -v

# Sadece integration testleri
docker-compose exec build-agent pytest tests/integration/ -v

# Coverage raporu
docker-compose exec build-agent pytest tests/ --cov=app --cov-report=html
```

---

## 🔍 İlk API İstekleriniz

### 1. Rıhtımları Listeleyin
```bash
curl http://localhost:8000/api/v1/berths | jq
```

### 2. Müşterileri Listeleyin
```bash
curl http://localhost:8000/api/v1/customers | jq
```

### 3. Tekneleri Listeleyin
```bash
curl http://localhost:8000/api/v1/vessels | jq
```

### 4. Privacy Durumunu Kontrol Edin
```bash
curl http://localhost:8000/api/v1/privacy/status | jq
```

### 5. Marina Dashboard
```bash
curl http://localhost:8000/api/v1/dashboard/overview | jq
```

---

## 📱 VHF Sesli Komut Örneği

```bash
# VHF Channel 72 simülasyonu
curl -X POST http://localhost:8000/api/v1/vhf/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Merhaba West Istanbul Marina, 14 metrelik tekne için yer var mı?",
    "language": "tr",
    "vessel_name": "Phisedelia"
  }' | jq
```

**Beklenen Çıktı:**
- 🤖 Claude AI intent parsing (6.2 saniye)
- 🎯 PLAN Agent rıhtım ataması (B-12)
- ✅ Fiyat hesaplama (135 EUR)

---

## 🔧 Yararlı Docker Komutları

```bash
# Servisleri durdur
docker-compose down

# Servisleri yeniden başlat
docker-compose restart

# Logları izle
docker-compose logs -f

# Belirli bir servisin logu
docker-compose logs -f build-agent

# Container'a bağlan
docker-compose exec build-agent bash

# Database'e bağlan
docker-compose exec postgres psql -U marina -d ada_marina_wim

# Redis'e bağlan
docker-compose exec redis redis-cli -a redis_secure_pass_2025

# Neo4j Cypher shell
docker-compose exec neo4j cypher-shell -u neo4j -p neo4j_secure_pass_2025
```

---

## 🐛 Sorun Giderme

### Problem: Container başlamıyor

```bash
# Tüm container'ları durdur
docker-compose down

# Volume'ları temizle
docker-compose down -v

# Yeniden başlat
docker-compose up -d
```

### Problem: Port zaten kullanımda

```bash
# Port'u kullanan process'i bul
sudo lsof -i :8000

# İsteğe bağlı docker-compose.yml'de port değiştir
# API_PORT=8001 olarak ayarla
```

### Problem: Database migration hatası

```bash
# Migration'ları sıfırla
docker-compose exec build-agent alembic downgrade base
docker-compose exec build-agent alembic upgrade head
```

### Problem: API sağlık kontrolü başarısız

```bash
# Build agent loglarını kontrol et
docker-compose logs build-agent

# Container'ı yeniden başlat
docker-compose restart build-agent

# Health check
curl http://localhost:8000/health
```

---

## 📊 Sistem Durumunu İzleyin

### Prometheus Metrics
http://localhost:9090/targets - Tüm hedeflerin durumu

### Grafana Dashboards
http://localhost:3000/dashboards
- **Marina Overview** - Genel durum
- **API Performance** - API metrikleri
- **Database Stats** - Veritabanı istatistikleri

---

## 🚀 Üretim Ortamına Geçiş

Sistem **production-ready** durumda. WIM marinasına kurulum için:

1. **Sunucu Hazırlığı** (30 dakika)
   - Ubuntu 22.04 LTS önerilir
   - Docker ve Docker Compose kurulumu
   - Firewall ayarları (8000, 3000, 9090 portları)

2. **Kurulum** (10 dakika)
   ```bash
   git clone https://github.com/ahmetengin/ada-marina-wim.git
   cd ada-marina-wim
   cp .env.example .env
   nano .env  # ANTHROPIC_API_KEY ekle
   ```

3. **Deploy** (5 dakika)
   ```bash
   ./init.sh
   ```

4. **Doğrulama** (2 dakika)
   ```bash
   curl http://server-ip:8000/health
   curl http://server-ip:8000/api/v1/dashboard/overview
   ```

**Toplam Kurulum Süresi:** ~1 saat

---

## 📚 Ek Kaynaklar

| Doküman | İçerik |
|---------|--------|
| **README.md** | Tam sistem genel bakış |
| **ADA_SEA_PRIVACY_ARCHITECTURE.md** | Privacy sistem mimarisi |
| **ADA_SEA_SMART_PRIVACY.md** | AIS-aware privacy |
| **DEPLOYMENT.md** | Production deployment kılavuzu |
| **TEST_COVERAGE.md** | Test dokümantasyonu |
| **CONCLUSION.md** | Proje özeti ve vizyon |
| **README.TR.md** | Türkçe dokümantasyon |

---

## 🆘 Destek

**Teknik Destek:**
- Email: support@ada-marina.com
- Privacy: privacy@ada.sea
- DPO: veri-sorumlusu@ada.sea
- Security: security@ada.sea

**Demo Tekne:**
- Tekne: Phisedelia (65 feet)
- Lokasyon: West Istanbul Marina, Berth C-42
- Kaptan: boss@ada.sea

---

## ✅ Başarı Kriterleri

Sistem başarıyla çalışıyorsa:
- ✅ http://localhost:8000/health → `{"status": "healthy"}`
- ✅ http://localhost:8000/docs → Swagger UI görünüyor
- ✅ http://localhost:3000 → Grafana açılıyor
- ✅ `docker-compose ps` → 10 servis "Up" durumunda
- ✅ `curl http://localhost:8000/api/v1/berths` → 600 rıhtım listesi

---

**"Kaptan ne derse o olur. Nokta."** 🔒⛵

**Sistem production'a hazır. İyi seyirler!** 🚀
