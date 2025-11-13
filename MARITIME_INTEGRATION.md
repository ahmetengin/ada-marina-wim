# 🌊 Maritime Services Integration

Ada.marina now integrates critical maritime intelligence from three authoritative sources:

## 🎯 Integrated Services

### 1. Piri Reis (Turkish Meteorological Service)
**Source**: https://pirireis.mgm.gov.tr

**Provides**:
- 24-hour maritime weather forecasts
- 3-day and 5-day extended forecasts
- Marina-specific forecasts
- Turkish waters coverage:
  - Marmara Sea
  - Black Sea (Karadeniz)
  - Aegean Sea (Ege)
  - Mediterranean (Akdeniz)

**Data Includes**:
- Wind speed and direction (including Turkish wind names: Poyraz, Lodos, etc.)
- Wave height and conditions
- Visibility
- Air and water temperature
- Storm warnings

### 2. Poseidon HCMR (Hellenic Centre for Marine Research)
**Source**: https://poseidon.hcmr.gr

**Provides**:
- 5-day ocean forecasts
- High-resolution hydrodynamic models (1/30° for Aegean)
- Sea currents forecasts
- Coverage: Aegean Sea and Eastern Mediterranean
- Integration with Copernicus CMEMS

**Data Includes**:
- Wave height, direction, and period
- Sea currents (speed and direction)
- Water temperature
- Salinity levels
- Detailed hydrodynamic modeling

### 3. Turkish Coast Guard (Sahil Güvenlik Komutanlığı)
**Source**: https://www.sg.gov.tr

**Provides**:
- Emergency contact information
- Maritime terminology dictionary (Denizci Dili)
- Regional command contacts
- Incident reporting system
- VHF communication standards

**Key Features**:
- **Emergency Number**: 158 (24/7)
- **VHF Channels**: 16 (International), 72 (Marina)
- Regional commands for all Turkish coasts
- Turkish-English-Greek maritime terminology
- Coast Guard incident tracking

---

## 🚀 API Endpoints

All maritime endpoints are available under `/api/v1/maritime`

### Weather & Sea Conditions

#### Get Weather Dashboard
```bash
GET /api/v1/maritime/dashboard
```
Complete maritime intelligence dashboard with current conditions, forecasts, and safety assessments.

#### Get Weather Summary
```bash
GET /api/v1/maritime/weather/summary
```
Concise weather summary with current and forecast data.

#### Create Piri Reis Forecast (Manual Entry)
```bash
POST /api/v1/maritime/weather/piri-reis?region=Marmara&wind_speed_knots=15&wave_height_meters=1.5
```
Manually enter Piri Reis data when API access is not available.

#### Create Poseidon Forecast (Manual Entry)
```bash
POST /api/v1/maritime/weather/poseidon?region=North%20Aegean&wave_height_meters=2.0
```
Manually enter Poseidon HCMR data.

#### Create Poseidon Currents
```bash
POST /api/v1/maritime/currents/poseidon?current_speed_knots=1.5&current_direction=NE
```
Add sea currents data.

#### Check Departure Safety
```bash
GET /api/v1/maritime/departure-check?vessel_length_meters=15
```
Assess if conditions are safe for vessel departure based on size.

### Coast Guard Services

#### Get Emergency Information
```bash
GET /api/v1/maritime/coast-guard/emergency
```
Emergency procedures, contact numbers, and protocols.

#### Initialize Coast Guard Data
```bash
GET /api/v1/maritime/coast-guard/initialize
```
Initialize regional Coast Guard contacts in database.

#### Get Regional Contacts
```bash
GET /api/v1/maritime/coast-guard/contacts?region=Marmara
```
Get Coast Guard contacts by region.

#### Report Incident
```bash
POST /api/v1/maritime/incidents
{
  "incident_type": "emergency",
  "incident_time": "2025-11-13T10:00:00Z",
  "location_description": "West Istanbul Marina, Berth B-12",
  "description": "Medical emergency on vessel",
  "severity": "high",
  "coast_guard_notified": true,
  "notification_method": "VHF Channel 16"
}
```
Report incident for Coast Guard notification.

#### Get Open Incidents
```bash
GET /api/v1/maritime/incidents/open
```
List all unresolved incidents.

#### Get Incident Statistics
```bash
GET /api/v1/maritime/incidents/statistics
```
Statistical overview of all incidents.

### Maritime Terminology

#### Search Maritime Terms
```bash
GET /api/v1/maritime/terminology/search?query=poyraz&category=Navigation
```
Search Turkish-English maritime terminology.

#### Get VHF Commands
```bash
GET /api/v1/maritime/terminology/vhf
```
Get all VHF radio communication terms.

#### Add Maritime Term
```bash
POST /api/v1/maritime/terminology
{
  "term_turkish": "Fırtına",
  "term_english": "Storm",
  "definition_turkish": "Şiddetli rüzgar ve dalga koşulları",
  "category": "Weather"
}
```
Add new term to dictionary.

---

## 📊 Database Models

### New Tables

#### `maritime_weather_forecasts`
Stores weather and sea condition forecasts from Piri Reis and Poseidon.

**Key Fields**:
- `source`: piri_reis, poseidon, manual
- `forecast_time`, `valid_from`, `valid_to`
- `wind_speed_knots`, `wind_direction`
- `wave_height_meters`, `sea_condition`
- `visibility_km`, `water_temp_celsius`
- `has_storm_warning`, `warning_level`

#### `maritime_currents_forecasts`
Sea currents and hydrodynamic data from Poseidon.

**Key Fields**:
- `current_speed_knots`, `current_direction`
- `water_temp_celsius`, `salinity_psu`
- `depth_meters`

#### `coast_guard_contacts`
Coast Guard regional command contact information.

**Key Fields**:
- `region_name`: Marmara, Ege, Akdeniz, Karadeniz
- `command_type`: Bölge, Grup, İstasyon
- `emergency_number`: 158
- `vhf_channel`, `phone_number`
- `coverage_area`

#### `maritime_terminology`
Turkish-English-Greek maritime terminology dictionary.

**Key Fields**:
- `term_turkish`, `term_english`, `term_greek`
- `definition_turkish`, `definition_english`
- `category`, `subcategory`
- `is_vhf_command`, `vhf_usage_notes`

#### `coast_guard_incidents`
Incident reports for Coast Guard coordination.

**Key Fields**:
- `incident_type`: emergency, suspicious_activity, pollution, accident, etc.
- `incident_time`, `location_description`
- `severity`: low, medium, high, critical
- `coast_guard_notified`, `notification_method`
- `status`: reported, investigating, resolved, closed

---

## 🔧 Services Architecture

### MaritimeService (Main Coordinator)
**File**: `app/services/maritime_service.py`

Coordinates all maritime intelligence:
- Combines Piri Reis + Poseidon forecasts
- Assesses safety conditions
- Provides departure recommendations
- Generates unified dashboard

**Key Methods**:
- `get_weather_dashboard()`: Complete maritime intelligence
- `check_departure_safety()`: Vessel-specific safety check
- `get_weather_summary()`: Quick weather overview

### PiriReisService
**File**: `app/services/pirireis_service.py`

Turkish Meteorological Service integration:
- Manual forecast entry (API access limited)
- Turkish wind direction mapping
- Marmara region focus
- 24-hour forecasts

### PoseidonService
**File**: `app/services/poseidon_service.py`

Poseidon HCMR integration:
- Manual forecast and currents entry
- Aegean Sea coverage check
- 5-day hydrodynamic forecasts
- High-resolution modeling

### CoastGuardService
**File**: `app/services/coast_guard_service.py`

Coast Guard integration:
- Emergency information
- Regional contacts management
- Maritime terminology dictionary
- Incident reporting and tracking

---

## 🎯 Safety Thresholds

Marina operations use these safety thresholds:

```python
SAFETY_THRESHOLDS = {
    "max_wind_knots": 25,
    "max_gust_knots": 35,
    "max_wave_height_meters": 2.5,
    "min_visibility_km": 1.0,
    "max_current_knots": 3.0
}
```

Thresholds are adjusted based on vessel size:
- **< 12m vessels**: Lower thresholds (20 knots, 1.5m waves)
- **12-20m vessels**: Standard thresholds (25 knots, 2.0m waves)
- **> 20m vessels**: Higher thresholds (30 knots, 2.5m waves)

---

## 🚀 Getting Started

### 1. Initialize Database Tables
```bash
# Tables are auto-created on first run
python -m uvicorn app.main:app --reload
```

### 2. Seed Maritime Data
```bash
# Seed Coast Guard contacts and maritime terminology
python database/seeds/maritime_data.py
```

### 3. Initialize Coast Guard Contacts via API
```bash
curl http://localhost:8000/api/v1/maritime/coast-guard/initialize
```

### 4. Add Weather Data Manually
Since Piri Reis and Poseidon require manual data entry or API keys:

```bash
# Add Piri Reis forecast
curl -X POST "http://localhost:8000/api/v1/maritime/weather/piri-reis?region=Marmara&wind_speed_knots=15&wave_height_meters=1.2&visibility_km=10"

# Add Poseidon forecast
curl -X POST "http://localhost:8000/api/v1/maritime/weather/poseidon?region=North%20Aegean&wave_height_meters=1.8&water_temp_celsius=18"
```

### 5. Check Dashboard
```bash
curl http://localhost:8000/api/v1/maritime/dashboard
```

---

## 🔍 Example Use Cases

### Use Case 1: Vessel Departure Check
**Scenario**: 14-meter yacht wants to depart

```bash
GET /api/v1/maritime/departure-check?vessel_length_meters=14
```

**Response**:
```json
{
  "is_safe": true,
  "vessel_length_meters": 14,
  "current_conditions": { ... },
  "reasons": ["All conditions suitable for departure"],
  "recommendations": [
    "✅ Conditions are suitable for departure",
    "Monitor weather conditions continuously",
    "Keep VHF Channel 72 and 16 active"
  ],
  "coast_guard_emergency": "158",
  "vhf_channel": "72"
}
```

### Use Case 2: Emergency Incident
**Scenario**: Medical emergency on vessel

```bash
POST /api/v1/maritime/incidents
{
  "incident_type": "medical",
  "incident_time": "2025-11-13T14:30:00Z",
  "location_description": "West Istanbul Marina, Section B",
  "berth_number": "B-12",
  "description": "Crew member injury, requires immediate medical attention",
  "severity": "high",
  "coast_guard_notified": true,
  "notification_method": "VHF Channel 16"
}
```

### Use Case 3: Maritime Term Lookup
**Scenario**: VHF operator needs emergency terminology

```bash
GET /api/v1/maritime/terminology/vhf
```

Returns Mayday, Pan-Pan, Sécurité and other critical VHF terms.

### Use Case 4: Daily Weather Update
**Scenario**: Marina operator checks daily conditions

```bash
GET /api/v1/maritime/dashboard
```

Returns complete dashboard with:
- Current weather (Piri Reis + Poseidon)
- 24-hour and 5-day forecasts
- Safety status
- Departure/arrival recommendations
- Active warnings

---

## 📝 Maritime Terminology Examples

### Turkish Wind Directions
- **Poyraz**: North-East wind (NE)
- **Lodos**: South-West wind (SW) - Strong in Aegean
- **Karayel**: North-West wind (NW)
- **Keşişleme**: South-East wind (SE)
- **Gündoğusu**: East wind (E)
- **Günbatısı**: West wind (W)

### VHF Emergency Calls
- **Mayday**: Life-threatening emergency (repeat 3x on Ch 16)
- **Pan-Pan**: Urgent but not immediately life-threatening (repeat 3x)
- **Sécurité**: Safety message, navigation warnings (repeat 3x)

### Vessel Parts
- **Pruva**: Bow (front)
- **Kıç**: Stern (rear)
- **İskele**: Port (left, red light)
- **Sancak**: Starboard (right, green light)

---

## 🔐 Security & Compliance

### Data Privacy
- All weather data is public information
- Incident reports follow GDPR/KVKK guidelines
- Personal information in incidents is protected

### Coast Guard Integration
- Manual incident reporting (no automatic CG notification)
- All incidents logged for marina records
- Compliance with maritime safety regulations

### API Access
- Piri Reis: Public website (manual entry)
- Poseidon: Public forecasts (manual entry)
- Coast Guard: Public information only

---

## 📞 Support & Resources

### Official Sources
- **Piri Reis**: https://pirireis.mgm.gov.tr
- **Poseidon HCMR**: https://poseidon.hcmr.gr
- **Turkish Coast Guard**: https://www.sg.gov.tr

### Emergency Contacts
- **Coast Guard Emergency**: 158 (24/7)
- **International VHF**: Channel 16
- **Marina VHF**: Channel 72

### Documentation
- Swagger UI: http://localhost:8000/docs
- Specific endpoint: `/api/v1/maritime/*`

---

**Built with precision. Deployed with confidence. Managed with intelligence.**

*Maritime integration completed: November 13, 2025*
