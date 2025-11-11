# 🚢 ADA.MARINA - WEST ISTANBUL MARINA YÖNETİM SİSTEMİ

## 🎯 Genel Bakış

West Istanbul Marina için havaalanı hassasiyetinde, tam otonom marina yönetim sistemi. 600 yat yeri için gerçek zamanlı operasyon yönetimi, 176 maddelik WIM İşletme Yönetmeliği tam uyumluluk.

## ✨ Özellikler

### 🤖 Big-5 Super Agent Mimarisi

1. **SCOUT Agent** (Hava Trafik Kontrolü)
   - VHF Kanal 72 izleme (Türkçe/İngilizce/Yunanca)
   - Gemi geliş tespiti
   - Gerçek zamanlı iskele doluluk takibi

2. **PLAN Agent** (Uçuş Planlama)
   - Yönetmelik uyumlu iskele tahsisi
   - Gelir optimizasyonu (RevPAR)
   - SEAL öğrenme (müşteri tercihleri)

3. **BUILD Agent** (Yer Hizmetleri)
   - FastAPI REST endpoints
   - Parasut e-fatura entegrasyonu
   - WebSocket gerçek zamanlı güncellemeler

4. **VERIFY Agent** (Güvenlik Yönetimi)
   - 176 madde uyumluluk kontrolü
   - İhlal tespiti ve loglama
   - Sigorta doğrulama

5. **SHIP Agent** (Dağıtım ve Öğrenme)
   - Docker orkestrasyon
   - SEAL kendini geliştirme
   - Sürekli iyileştirme

## 🚀 Kurulum

### Ön Gereksinimler

- Docker ve Docker Compose
- 8GB+ RAM
- 20GB disk alanı

### Adım 1: Projeyi Klonlayın
```bash
git clone https://github.com/ahmetengin/ada-marina-wim.git
cd ada-marina-wim
```

### Adım 2: Çevre Değişkenlerini Ayarlayın
```bash
cp .env.example .env
# .env dosyasını düzenleyin ve gerekli API anahtarlarını ekleyin
```

### Adım 3: Sistemi Başlatın
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Adım 4: Demo'yu Çalıştırın
```bash
docker-compose run --rm build-agent python scripts/demo_scenarios.py
```

## 📊 Erişim Noktaları

- **API Dokümantasyonu**: http://localhost:8000/docs
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Neo4j Tarayıcı**: http://localhost:7474

## 🎬 Demo Senaryoları

### Senaryo 1: VHF Sesli Rezervasyon
```
📻 Kanal 72: "Merhaba West Istanbul Marina, 14 metrelik tekne..."
🤖 6.2 saniyede işlem: Iskele B-12 atandı
✅ Parasut fatura oluşturuldu: 135 EUR
```

### Senaryo 2: Yönetmelik İhlali Tespiti
```
⚠️  Hız limiti aşıldı: 5.2 knot (max 3 knot)
📋 Madde E.1.10 uygulandı
💰 Ceza: 50 EUR
```

### Senaryo 3: Sıcak İş İzni
```
🔥 Kaynak yapılacak → İzin gerekli (Madde E.5.5)
✅ Yangın önleme tedbirleri onaylandı
📝 İzin verildi: HWP-2025-11-016
```

### Senaryo 4: SEAL Öğrenme
```
🧠 Psedelia her zaman B-12 istiyor (5/5 ziyaret)
📈 Güven: %95
⚡ Otomatik öneri aktif
```

## 📋 Veri Tabanı İstatistikleri

- **Toplam İskele**: 600 (6 sektör: A-F)
- **Müşteriler**: 50 (Türk ve uluslararası)
- **Gemiler**: 80 (10m - 50m+)
- **Aktif Atamalar**: 25+
- **VHF Logları**: 20+ (Kanal 72)

## 🏢 İskele Sektörleri

- **Sektör A**: 10-15m tekneler (100 iskele)
- **Sektör B**: 12-18m tekneler (100 iskele)
- **Sektör C**: 15-25m tekneler (100 iskele)
- **Sektör D**: 20-35m tekneler (100 iskele)
- **Sektör E**: 30-50m süper yatlar (100 iskele)
- **Sektör F**: Kuru depolama (100 iskele)

## 🔒 Güvenlik ve Uyumluluk

- ✅ 176 maddelik WIM Yönetmeliği tam uyum
- ✅ KVKK/GDPR veri koruma
- ✅ Parasut e-fatura entegrasyonu
- ✅ 7 yıllık veri saklama
- ✅ SSL/TLS şifreleme

## 📞 Destek

Sorularınız için: support@ada-marina.com

## 📄 Lisans

Copyright © 2025 Ada Ecosystem. Tüm hakları saklıdır.