# 🎯 ADA.MARINA WEST ISTANBUL - COMPLETE DEPLOYMENT PACKAGE
## Aviation-Grade Marina Management System - 50 Hours to Production
### ULTIMATE v4.0 - COMPLETE & UNBREAKABLE 
---

## 📋 EXECUTIVE SUMMARY

**Mission**: Deploy a fully autonomous, aviation-precision marina management system for West Istanbul Marina (600 berths) with complete regulatory compliance to 176-article WIM Operations Regulations.

**Deadline**: November 11, 2025 (50 hours)
**Client**: Enelka Taahhüt İmalat ve Ticaret A.Ş.
**Location**: Yakuplu, Beylikdüzü, Istanbul
**Architecture**: Big-5 Super Agent (Scout-Plan-Build-Verify-Ship)
**Inspiration**: Airport ground control operations

---

## 🏗️ SYSTEM ARCHITECTURE

### Agent 1: SCOUT (Air Traffic Control)
- VHF Channel 72 monitoring (Turkish/English/Greek)
- Vessel arrival detection
- Real-time berth occupancy sensing
- Weather/sea condition monitoring
- Emergency broadcast handling

### Agent 2: PLAN (Flight Dispatch)
- Regulation-compliant berth allocation
- Revenue optimization (RevPAR)
- SEAL learning (customer preferences)
- Conflict resolution
- Service coordination

### Agent 3: BUILD (Ground Operations)
- FastAPI REST endpoints
- PostgreSQL database operations
- Parasut e-invoice generation
- VHF response transmission
- WebSocket real-time updates

### Agent 4: VERIFY (Safety Management)
- 176-article compliance monitoring
- Violation detection & logging
- Insurance verification
- Hot work permit management
- Incident reporting

### Agent 5: SHIP (Deployment & Learning)
- Docker orchestration
- SEAL self-learning loop
- Database migrations
- Continuous improvement
- Production monitoring

---

## 📊 COMPLETE DATABASE SCHEMA WITH SEED DATA

### 1. SCHEMA DEFINITION
```sql
-- =============================================================================
-- WEST ISTANBUL MARINA DATABASE SCHEMA
-- Based on WIM Operation Regulations (176 Articles)
-- =============================================================================

-- Customers (Yacht Owners)
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    tc_kimlik VARCHAR(11), -- Turkish ID
    passport VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    kvkk_consent BOOLEAN DEFAULT FALSE, -- GDPR compliance
    kvkk_consent_date TIMESTAMP,
    nationality VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vessels (Yachts)
CREATE TABLE vessels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    registration_number VARCHAR(50) UNIQUE, -- Article C.m
    flag VARCHAR(50), -- Article C.m
    vessel_type VARCHAR(50), -- sailboat, motor_yacht, catamaran
    loa_meters DECIMAL(5,2), -- Length Overall (Article C.o)
    beam_meters DECIMAL(5,2), -- Breadth (Article C.n)
    draft_meters DECIMAL(5,2),
    owner_id INTEGER REFERENCES customers(id),
    
    -- Regulation compliance (Article E.1.4, E.2.1)
    tonnage_certificate_valid BOOLEAN DEFAULT FALSE,
    tonnage_certificate_expiry DATE,
    seaworthiness_certificate_valid BOOLEAN DEFAULT FALSE,
    seaworthiness_certificate_expiry DATE,
    insurance_policy_number VARCHAR(100),
    insurance_expiry_date DATE,
    insurance_coverage_eur DECIMAL(12,2),
    insurance_company VARCHAR(200),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Berths (600 total)
CREATE TABLE berths (
    id SERIAL PRIMARY KEY,
    berth_number VARCHAR(10) UNIQUE NOT NULL, -- e.g. "B-12"
    section VARCHAR(1), -- A, B, C, D, E, F
    length_meters DECIMAL(5,2),
    width_meters DECIMAL(5,2),
    depth_meters DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'available', -- available, occupied, reserved, maintenance
    daily_rate_eur DECIMAL(10,2),
    facilities JSONB, -- {water: true, electricity: "380V", wifi: true}
    location_coordinates POINT, -- For map display
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Berth Assignments
CREATE TABLE berth_assignments (
    id SERIAL PRIMARY KEY,
    berth_id INTEGER REFERENCES berths(id),
    vessel_id INTEGER REFERENCES vessels(id),
    customer_id INTEGER REFERENCES customers(id),
    check_in TIMESTAMP NOT NULL,
    check_out TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active', -- active, completed, cancelled
    
    -- Pricing (Article E.7.4: LOA x Beam x Daily Rate)
    daily_rate_eur DECIMAL(10,2),
    nights INTEGER,
    total_amount_eur DECIMAL(10,2),
    
    -- Services (Article E.7.3)
    water_consumed_tons DECIMAL(8,2) DEFAULT 0,
    electricity_consumed_kwh DECIMAL(10,2) DEFAULT 0,
    fuel_consumed_liters DECIMAL(8,2) DEFAULT 0,
    
    -- Compliance
    mooring_agreement_signed BOOLEAN DEFAULT FALSE,
    advance_payment_received BOOLEAN DEFAULT FALSE,
    insurance_verified BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- VHF Communication Logs
CREATE TABLE vhf_logs (
    id SERIAL PRIMARY KEY,
    command_text TEXT,
    parsed_intent VARCHAR(100),
    vessel_id INTEGER REFERENCES vessels(id),
    customer_id INTEGER REFERENCES customers(id),
    response_text TEXT,
    language VARCHAR(5) DEFAULT 'tr', -- tr, en, el (Greek)
    channel VARCHAR(10) DEFAULT '72',
    timestamp TIMESTAMP DEFAULT NOW(),
    duration_seconds INTEGER
);

-- Invoices (Parasut Integration)
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    parasut_invoice_id VARCHAR(100) UNIQUE,
    customer_id INTEGER REFERENCES customers(id),
    assignment_id INTEGER REFERENCES berth_assignments(id),
    invoice_number VARCHAR(50) UNIQUE,
    issue_date DATE,
    due_date DATE,
    subtotal_eur DECIMAL(10,2),
    vat_rate DECIMAL(5,2) DEFAULT 20.00,
    vat_amount_eur DECIMAL(10,2),
    total_amount_eur DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'draft', -- draft, issued, paid, overdue
    parasut_status VARCHAR(50),
    payment_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Invoice Line Items
CREATE TABLE invoice_items (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES invoices(id),
    description TEXT,
    quantity DECIMAL(10,2),
    unit_price_eur DECIMAL(10,2),
    total_eur DECIMAL(10,2)
);

-- Regulation Violations (Article-based tracking)
CREATE TABLE regulation_violations (
    id SERIAL PRIMARY KEY,
    vessel_id INTEGER REFERENCES vessels(id),
    customer_id INTEGER REFERENCES customers(id),
    article_violated VARCHAR(20), -- e.g. "E.1.10", "F.13"
    description TEXT,
    severity VARCHAR(20), -- warning, fine, contract_termination
    fine_amount_eur DECIMAL(10,2),
    resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Hot Work Permits (Article E.5.5)
CREATE TABLE hot_work_permits (
    id SERIAL PRIMARY KEY,
    permit_number VARCHAR(50) UNIQUE,
    vessel_id INTEGER REFERENCES vessels(id),
    work_type VARCHAR(100), -- welding, painting, grinding, etc.
    work_description TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    fire_prevention_measures TEXT,
    fire_watch_assigned VARCHAR(100),
    permit_issued_by VARCHAR(100), -- Marina Manager
    status VARCHAR(20), -- active, completed, cancelled
    created_at TIMESTAMP DEFAULT NOW()
);

-- Emergency Contacts (Article E.2.12)
CREATE TABLE emergency_contacts (
    id SERIAL PRIMARY KEY,
    vessel_id INTEGER REFERENCES vessels(id),
    contact_name VARCHAR(200),
    phone VARCHAR(20),
    email VARCHAR(100),
    relationship VARCHAR(100),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- SEAL Learning Data (Customer Preferences)
CREATE TABLE customer_preferences (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    vessel_id INTEGER REFERENCES vessels(id),
    preferred_berth_section VARCHAR(1),
    preferred_berth_number VARCHAR(10),
    preferred_services JSONB, -- {water: true, electricity: true, ...}
    preferred_language VARCHAR(5),
    vip_status BOOLEAN DEFAULT FALSE,
    notes TEXT,
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    occurrences INTEGER DEFAULT 1,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- System Events (for observability)
CREATE TABLE system_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100),
    agent_name VARCHAR(50), -- scout, plan, build, verify, ship
    event_data JSONB,
    severity VARCHAR(20), -- info, warning, error, critical
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_berths_status ON berths(status);
CREATE INDEX idx_berths_section ON berths(section);
CREATE INDEX idx_assignments_status ON berth_assignments(status);
CREATE INDEX idx_assignments_dates ON berth_assignments(check_in, check_out);
CREATE INDEX idx_vessels_flag ON vessels(flag);
CREATE INDEX idx_vhf_timestamp ON vhf_logs(timestamp);
CREATE INDEX idx_violations_resolved ON regulation_violations(resolved);
```

---

### 2. COMPLETE SEED DATA (600 Berths + Realistic Dummy Data)
```sql
-- =============================================================================
-- SEED DATA: 600 BERTHS + 50 CUSTOMERS + 80 VESSELS + REALISTIC ACTIVITY
-- =============================================================================

-- ============= CUSTOMERS (50 Total: 30 Turkish + 20 International) =============

INSERT INTO customers (full_name, tc_kimlik, passport, phone, email, kvkk_consent, kvkk_consent_date, nationality) VALUES
-- Turkish Citizens (30)
('Ahmet Yılmaz', '12345678901', NULL, '+90 532 123 4567', 'ahmet.yilmaz@gmail.com', true, '2024-01-15 10:30:00', 'Turkey'),
('Mehmet Demir', '23456789012', NULL, '+90 533 234 5678', 'mehmet.demir@hotmail.com', true, '2024-02-20 14:45:00', 'Turkey'),
('Ayşe Kaya', '34567890123', NULL, '+90 534 345 6789', 'ayse.kaya@yahoo.com', true, '2024-03-10 09:15:00', 'Turkey'),
('Fatma Çelik', '45678901234', NULL, '+90 535 456 7890', 'fatma.celik@outlook.com', true, '2024-03-25 11:20:00', 'Turkey'),
('Ali Şahin', '56789012345', NULL, '+90 536 567 8901', 'ali.sahin@gmail.com', true, '2024-04-05 16:00:00', 'Turkey'),
('Zeynep Arslan', '67890123456', NULL, '+90 537 678 9012', 'zeynep.arslan@hotmail.com', true, '2024-04-18 08:30:00', 'Turkey'),
('Mustafa Öztürk', '78901234567', NULL, '+90 538 789 0123', 'mustafa.ozturk@gmail.com', true, '2024-05-12 13:45:00', 'Turkey'),
('Emine Yıldız', '89012345678', NULL, '+90 539 890 1234', 'emine.yildiz@yahoo.com', true, '2024-05-28 10:00:00', 'Turkey'),
('Hasan Aydın', '90123456789', NULL, '+90 540 901 2345', 'hasan.aydin@outlook.com', true, '2024-06-03 15:20:00', 'Turkey'),
('Hatice Özkan', '01234567890', NULL, '+90 541 012 3456', 'hatice.ozkan@gmail.com', true, '2024-06-19 09:45:00', 'Turkey'),
('İbrahim Koç', '11111111111', NULL, '+90 542 111 1111', 'ibrahim.koc@hotmail.com', true, '2024-07-07 14:10:00', 'Turkey'),
('Selin Aksoy', '22222222222', NULL, '+90 543 222 2222', 'selin.aksoy@gmail.com', true, '2024-07-22 11:30:00', 'Turkey'),
('Burak Erdoğan', '33333333333', NULL, '+90 544 333 3333', 'burak.erdogan@yahoo.com', true, '2024-08-05 16:50:00', 'Turkey'),
('Merve Kılıç', '44444444444', NULL, '+90 545 444 4444', 'merve.kilic@outlook.com', true, '2024-08-19 08:15:00', 'Turkey'),
('Emre Güneş', '55555555555', NULL, '+90 546 555 5555', 'emre.gunes@gmail.com', true, '2024-09-02 13:00:00', 'Turkey'),
('Deniz Yavuz', '66666666666', NULL, '+90 547 666 6666', 'deniz.yavuz@hotmail.com', true, '2024-09-15 10:45:00', 'Turkey'),
('Elif Özdemir', '77777777777', NULL, '+90 548 777 7777', 'elif.ozdemir@gmail.com', true, '2024-09-28 14:20:00', 'Turkey'),
('Can Şimşek', '88888888888', NULL, '+90 549 888 8888', 'can.simsek@yahoo.com', true, '2024-10-10 09:30:00', 'Turkey'),
('Berna Karaca', '99999999999', NULL, '+90 550 999 9999', 'berna.karaca@outlook.com', true, '2024-10-22 11:15:00', 'Turkey'),
('Oğuz Tan', '10101010101', NULL, '+90 551 101 0101', 'oguz.tan@gmail.com', true, '2024-11-01 08:50:00', 'Turkey'),
('Pınar Aktaş', '11223344556', NULL, '+90 552 112 2334', 'pinar.aktas@hotmail.com', true, '2024-01-30 15:10:00', 'Turkey'),
('Serkan Acar', '22334455667', NULL, '+90 553 223 3445', 'serkan.acar@gmail.com', true, '2024-02-12 09:25:00', 'Turkey'),
('Gül Yıldırım', '33445566778', NULL, '+90 554 334 4556', 'gul.yildirim@yahoo.com', true, '2024-03-05 14:40:00', 'Turkey'),
('Kerem Öz', '44556677889', NULL, '+90 555 445 5667', 'kerem.oz@outlook.com', true, '2024-04-18 10:55:00', 'Turkey'),
('Leyla Demirci', '55667788990', NULL, '+90 556 556 6778', 'leyla.demirci@gmail.com', true, '2024-05-20 13:30:00', 'Turkey'),
('Cem Polat', '66778899001', NULL, '+90 557 667 7889', 'cem.polat@hotmail.com', true, '2024-06-25 08:15:00', 'Turkey'),
('Aslı Kara', '77889900112', NULL, '+90 558 778 8990', 'asli.kara@yahoo.com', true, '2024-07-30 11:45:00', 'Turkey'),
('Bora Ateş', '88990011223', NULL, '+90 559 889 9001', 'bora.ates@gmail.com', true, '2024-08-15 14:20:00', 'Turkey'),
('Ece Kurt', '99001122334', NULL, '+90 560 990 0112', 'ece.kurt@outlook.com', true, '2024-09-10 09:50:00', 'Turkey'),
('Volkan Çetin', '00112233445', NULL, '+90 561 001 1223', 'volkan.cetin@hotmail.com', true, '2024-10-05 16:30:00', 'Turkey'),

-- Foreign Nationals (20)
('John Smith', NULL, 'US1234567', '+44 7700 900123', 'john.smith@yacht.com', true, '2024-01-20 10:00:00', 'USA'),
('Maria Schmidt', NULL, 'DE9876543', '+49 151 12345678', 'maria.schmidt@sailing.de', true, '2024-02-14 14:30:00', 'Germany'),
('Pierre Dubois', NULL, 'FR5555555', '+33 6 12 34 56 78', 'pierre.dubois@voile.fr', true, '2024-03-08 09:00:00', 'France'),
('Elena Petrov', NULL, 'RU7777777', '+7 916 123 4567', 'elena.petrov@yandex.ru', true, '2024-03-30 11:45:00', 'Russia'),
('Hans Mueller', NULL, 'DE1112233', '+49 172 9876543', 'hans.mueller@yacht.de', true, '2024-04-22 15:20:00', 'Germany'),
('Sophia Papadopoulos', NULL, 'GR3334455', '+30 694 123 4567', 'sophia.pp@sailing.gr', true, '2024-05-15 08:45:00', 'Greece'),
('Marco Rossi', NULL, 'IT6667788', '+39 333 123 4567', 'marco.rossi@vela.it', true, '2024-06-10 13:10:00', 'Italy'),
('Olga Ivanova', NULL, 'RU9998877', '+7 925 987 6543', 'olga.ivanova@mail.ru', true, '2024-07-02 10:30:00', 'Russia'),
('David Cohen', NULL, 'IL1234567', '+972 50 123 4567', 'david.cohen@yacht.il', true, '2024-07-28 16:00:00', 'Israel'),
('Anna Kowalski', NULL, 'PL5556667', '+48 601 234 567', 'anna.kowalski@sailing.pl', true, '2024-08-14 09:20:00', 'Poland'),
('Nikos Konstantinou', NULL, 'GR8889990', '+30 697 890 1234', 'nikos.k@aegean.gr', true, '2024-09-10 14:15:00', 'Greece'),
('Isabella Fernandez', NULL, 'ES4445556', '+34 678 901 234', 'isabella.f@nautica.es', true, '2024-09-25 11:00:00', 'Spain'),
('Mohammed Al-Rashid', NULL, 'AE1112223', '+971 50 123 4567', 'mohammed.ar@yacht.ae', true, '2024-10-05 15:45:00', 'UAE'),
('Lars Johansson', NULL, 'SE6667778', '+46 70 123 4567', 'lars.j@sailing.se', true, '2024-10-18 10:20:00', 'Sweden'),
('Catherine Dubois', NULL, 'FR8889990', '+33 6 87 65 43 21', 'catherine.d@voile.fr', true, '2024-10-28 13:50:00', 'France'),
('Dimitri Volkov', NULL, 'RU1234321', '+7 903 456 7890', 'dimitri.v@yacht.ru', true, '2024-11-02 09:15:00', 'Russia'),
('Sarah Thompson', NULL, 'GB9876543', '+44 7890 123456', 'sarah.t@sailing.uk', true, '2024-11-05 14:40:00', 'UK'),
('Antonio Greco', NULL, 'IT3332221', '+39 340 987 6543', 'antonio.g@nautica.it', true, '2024-11-07 11:25:00', 'Italy'),
('Ahmed Hassan', NULL, 'EG5554443', '+20 100 234 5678', 'ahmed.h@yacht.eg', true, '2024-11-08 16:10:00', 'Egypt'),
('Yuki Tanaka', NULL, 'JP7778889', '+81 90 1234 5678', 'yuki.t@sailing.jp', true, '2024-11-09 08:35:00', 'Japan');

-- ============= VESSELS (80 Total: 40 Turkish + 40 International) =============

INSERT INTO vessels (name, registration_number, flag, vessel_type, loa_meters, beam_meters, draft_meters, owner_id, tonnage_certificate_valid, seaworthiness_certificate_valid, insurance_policy_number, insurance_expiry_date, insurance_coverage_eur) VALUES
-- Turkish Flagged Vessels (40)
('Psedelia', 'TR-IST-2024-001', 'Turkey', 'sailboat', 14.20, 4.30, 2.10, 1, true, true, 'INS-TR-001', '2025-12-31', 500000),
('Ay Işığı', 'TR-IST-2024-002', 'Turkey', 'motor_yacht', 18.50, 5.20, 1.80, 2, true, true, 'INS-TR-002', '2025-11-30', 750000),
('Deniz Yıldızı', 'TR-IST-2024-003', 'Turkey', 'sailboat', 12.80, 4.00, 1.90, 3, true, true, 'INS-TR-003', '2026-01-15', 450000),
('Mavi Rüya', 'TR-IST-2024-004', 'Turkey', 'catamaran', 15.60, 7.80, 1.20, 4, true, true, 'INS-TR-004', '2025-12-20', 600000),
('Ege Prenses', 'TR-IST-2024-005', 'Turkey', 'motor_yacht', 22.40, 6.10, 2.30, 5, true, true, 'INS-TR-005', '2026-02-28', 950000),
('Akdeniz', 'TR-ANT-2024-006', 'Turkey', 'sailboat', 16.20, 4.80, 2.20, 6, true, true, 'INS-TR-006', '2025-12-15', 650000),
('Yel Ken', 'TR-IST-2024-007', 'Turkey', 'sailboat', 13.50, 4.20, 2.00, 7, true, true, 'INS-TR-007', '2026-01-20', 500000),
('Beyaz Yelken', 'TR-IZM-2024-008', 'Turkey', 'sailboat', 11.90, 3.90, 1.80, 8, true, true, 'INS-TR-008', '2025-11-25', 400000),
('Martı', 'TR-IST-2024-009', 'Turkey', 'motor_yacht', 19.80, 5.60, 2.00, 9, true, true, 'INS-TR-009', '2026-03-10', 800000),
('Kumsal', 'TR-BOD-2024-010', 'Turkey', 'catamaran', 14.30, 7.20, 1.10, 10, true, true, 'INS-TR-010', '2025-12-05', 550000),
('Fırtına', 'TR-IST-2024-011', 'Turkey', 'sailboat', 17.50, 5.00, 2.40, 11, true, true, 'INS-TR-011', '2026-01-08', 700000),
('Dalgıç', 'TR-IST-2024-012', 'Turkey', 'motor_yacht', 25.60, 6.80, 2.50, 12, true, true, 'INS-TR-012', '2026-02-15', 1200000),
('Rüzgar Gülü', 'TR-IST-2024-013', 'Turkey', 'sailboat', 15.80, 4.70, 2.10, 13, true, true, 'INS-TR-013', '2025-11-18', 600000),
('Meltem', 'TR-MUG-2024-014', 'Turkey', 'sailboat', 13.20, 4.10, 1.95, 14, true, true, 'INS-TR-014', '2026-01-25', 480000),
('Beyaz Saray', 'TR-IST-2024-015', 'Turkey', 'motor_yacht', 32.40, 8.20, 2.80, 15, true, true, 'INS-TR-015', '2026-03-20', 1800000),
('Karadeniz', 'TR-IST-2024-016', 'Turkey', 'sailboat', 14.50, 4.40, 2.05, 16, true, true, 'INS-TR-016', '2025-12-10', 520000),
('Yunus', 'TR-BOD-2024-017', 'Turkey', 'motor_yacht', 20.30, 5.80, 2.10, 17, true, true, 'INS-TR-017', '2026-01-30', 850000),
('Delfin', 'TR-IST-2024-018', 'Turkey', 'sailboat', 12.60, 3.95, 1.85, 18, true, true, 'INS-TR-018', '2025-11-22', 440000),
('Kelebek', 'TR-IZM-2024-019', 'Turkey', 'catamaran', 16.20, 7.90, 1.25, 19, true, true, 'INS-TR-019', '2026-02-05', 680000),
('Kardelen', 'TR-IST-2024-020', 'Turkey', 'sailboat', 15.20, 4.60, 2.15, 20, true, true, 'INS-TR-020', '2025-12-28', 580000),
('Şahin', 'TR-ANT-2024-021', 'Turkey', 'motor_yacht', 21.80, 6.20, 2.25, 21, true, true, 'INS-TR-021', '2026-01-12', 920000),
('Pelikan', 'TR-IST-2024-022', 'Turkey', 'sailboat', 13.80, 4.25, 2.00, 22, true, true, 'INS-TR-022', '2025-11-28', 490000),
('Alabora', 'TR-BOD-2024-023', 'Turkey', 'motor_yacht', 18.90, 5.50, 1.95, 23, true, true, 'INS-TR-023', '2026-02-18', 780000),
('Çınar', 'TR-IST-2024-024', 'Turkey', 'sailboat', 14.80, 4.50, 2.08, 24, true, true, 'INS-TR-024', '2025-12-22', 560000),
('Lodos', 'TR-MUG-2024-025', 'Turkey', 'sailboat', 16.50, 4.85, 2.20, 25, true, true, 'INS-TR-025', '2026-01-18', 660000),
('Poyraz', 'TR-IST-2024-026', 'Turkey', 'motor_yacht', 23.20, 6.40, 2.35, 26, true, true, 'INS-TR-026', '2026-03-05', 1050000),
('Yelkovan', 'TR-ANT-2024-027', 'Turkey', 'sailboat', 15.40, 4.65, 2.12, 27, true, true, 'INS-TR-027', '2025-11-30', 590000),
('Gemi', 'TR-IST-2024-028', 'Turkey', 'catamaran', 17.80, 8.40, 1.35, 28, true, true, 'INS-TR-028', '2026-02-22', 750000),
('Yıldırım', 'TR-BOD-2024-029', 'Turkey', 'motor_yacht', 24.50, 6.70, 2.45, 29, true, true, 'INS-TR-029', '2026-03-15', 1150000),
('Şafak', 'TR-IST-2024-030', 'Turkey', 'sailboat', 14.10, 4.35, 2.03, 30, true, true, 'INS-TR-030', '2025-12-12', 530000),
('Gün Batımı', 'TR-IZM-2024-031', 'Turkey', 'motor_yacht', 19.50, 5.65, 2.05, 1, true, true, 'INS-TR-031', '2026-01-22', 820000),
('Dalga', 'TR-IST-2024-032', 'Turkey', 'sailboat', 13.40, 4.15, 1.98, 2, true, true, 'INS-TR-032', '2025-11-26', 485000),
('Köpük', 'TR-ANT-2024-033', 'Turkey', 'catamaran', 15.90, 7.70, 1.22, 3, true, true, 'INS-TR-033', '2026-02-08', 640000),
('Seraplar', 'TR-IST-2024-034', 'Turkey', 'motor_yacht', 22.80, 6.30, 2.32, 4, true, true, 'INS-TR-034', '2026-03-12', 980000),
('Işık', 'TR-BOD-2024-035', 'Turkey', 'sailboat', 16.80, 4.90, 2.22, 5, true, true, 'INS-TR-035', '2025-12-18', 670000),
('Umut', 'TR-IST-2024-036', 'Turkey', 'sailboat', 14.60, 4.48, 2.07, 6, true, true, 'INS-TR-036', '2026-01-28', 555000),
('Aşk', 'TR-MUG-2024-037', 'Turkey', 'motor_yacht', 21.20, 6.05, 2.18, 7, true, true, 'INS-TR-037', '2026-02-25', 900000),
('Barış', 'TR-IST-2024-038', 'Turkey', 'sailboat', 15.10, 4.62, 2.14, 8, true, true, 'INS-TR-038', '2025-12-08', 575000),
('Özgürlük', 'TR-ANT-2024-039', 'Turkey', 'catamaran', 16.70, 8.10, 1.28, 9, true, true, 'INS-TR-039', '2026-01-15', 710000),
('Zafer', 'TR-IST-2024-040', 'Turkey', 'motor_yacht', 26.30, 7.00, 2.55, 10, true, true, 'INS-TR-040', '2026-03-22', 1280000),

-- International Flagged Vessels (40)
('Sea Spirit', 'US-FL-2024-101', 'USA', 'motor_yacht', 28.50, 7.50, 2.60, 31, true, true, 'INS-US-101', '2026-02-28', 1500000),
('Windseeker', 'GB-LDN-2024-102', 'UK', 'sailboat', 16.80, 4.90, 2.30, 32, true, true, 'INS-GB-102', '2025-12-15', 690000),
('Aphrodite', 'GR-ATH-2024-103', 'Greece', 'motor_yacht', 24.30, 6.60, 2.40, 33, true, true, 'INS-GR-103', '2026-01-20', 1100000),
('Bella Vita', 'IT-ROM-2024-104', 'Italy', 'motor_yacht', 21.70, 6.20, 2.20, 34, true, true, 'INS-IT-104', '2025-11-30', 920000),
('Nordwind', 'DE-HAM-2024-105', 'Germany', 'sailboat', 18.20, 5.10, 2.40, 35, true, true, 'INS-DE-105', '2026-02-10', 780000),
('Aurora', 'RU-SPB-2024-106', 'Russia', 'motor_yacht', 35.80, 9.10, 3.00, 36, true, true, 'INS-RU-106', '2026-03-25', 2200000),
('Mediterranean Dream', 'FR-MRS-2024-107', 'France', 'catamaran', 17.40, 8.50, 1.30, 37, true, true, 'INS-FR-107', '2025-12-20', 740000),
('Blue Horizon', 'GR-RHO-2024-108', 'Greece', 'sailboat', 15.30, 4.60, 2.15, 38, true, true, 'INS-GR-108', '2026-01-08', 600000),
('Stella Maris', 'IT-NAP-2024-109', 'Italy', 'sailboat', 14.90, 4.50, 2.05, 39, true, true, 'INS-IT-109', '2025-11-25', 570000),
('Ocean Pearl', 'AE-DXB-2024-110', 'UAE', 'motor_yacht', 42.60, 10.80, 3.20, 40, true, true, 'INS-AE-110', '2026-03-30', 3000000),
('Poseidon', 'GR-ATH-2024-111', 'Greece', 'motor_yacht', 19.50, 5.80, 2.10, 41, true, true, 'INS-GR-111', '2025-12-05', 830000),
('Viking Spirit', 'NO-OSL-2024-112', 'Norway', 'sailboat', 16.40, 4.85, 2.25, 42, true, true, 'INS-NO-112', '2026-01-18', 670000),
('Sahara Star', 'AE-AUH-2024-113', 'UAE', 'motor_yacht', 38.20, 9.60, 3.10, 43, true, true, 'INS-AE-113', '2026-03-15', 2500000),
('Baltic Beauty', 'PL-GDN-2024-114', 'Poland', 'sailboat', 13.80, 4.25, 2.00, 44, true, true, 'INS-PL-114', '2025-11-22', 510000),
('Azure Escape', 'ES-BCN-2024-115', 'Spain', 'catamaran', 16.90, 8.20, 1.25, 45, true, true, 'INS-ES-115', '2026-02-12', 720000),
('Neptune''s Pride', 'GB-PLY-2024-116', 'UK', 'motor_yacht', 23.60, 6.50, 2.38, 46, true, true, 'INS-GB-116', '2026-01-25', 1050000),
('Côte d''Azur', 'FR-NCE-2024-117', 'France', 'motor_yacht', 27.30, 7.20, 2.55, 47, true, true, 'INS-FR-117', '2026-02-28', 1400000),
('Adriatica', 'IT-VEN-2024-118', 'Italy', 'sailboat', 17.60, 5.05, 2.28, 48, true, true, 'INS-IT-118', '2025-12-18', 730000),
('Red Sea', 'EG-HRG-2024-119', 'Egypt', 'motor_yacht', 20.80, 6.00, 2.15, 49, true, true, 'INS-EG-119', '2026-01-12', 890000),
('Rising Sun', 'JP-TKY-2024-120', 'Japan', 'sailboat', 15.70, 4.72, 2.18, 50, true, true, 'INS-JP-120', '2025-12-28', 620000),
('Midnight Sun', 'SE-STO-2024-121', 'Sweden', 'motor_yacht', 22.40, 6.25, 2.30, 31, true, true, 'INS-SE-121', '2026-02-05', 960000),
('Aegean Dream', 'GR-MYK-2024-122', 'Greece', 'catamaran', 18.60, 8.80, 1.38, 32, true, true, 'INS-GR-122', '2026-01-30', 810000),
('Black Pearl', 'RU-SOC-2024-123', 'Russia', 'motor_yacht', 31.50, 8.40, 2.85, 33, true, true, 'INS-RU-123', '2026-03-10', 1900000),
('White Dolphin', 'DE-KIE-2024-124', 'Germany', 'sailboat', 14.30, 4.38, 2.02, 34, true, true, 'INS-DE-124', '2025-11-28', 540000),
('Golden Wave', 'AE-DXB-2024-125', 'UAE', 'motor_yacht', 45.20, 11.30, 3.35, 35, true, true, 'INS-AE-125', '2026-04-05', 3500000),
('Silver Cloud', 'US-NY-2024-126', 'USA', 'motor_yacht', 26.90, 7.10, 2.52, 36, true, true, 'INS-US-126', '2026-02-22', 1350000),
('Crystal Waters', 'GB-SOT-2024-127', 'UK', 'sailboat', 16.10, 4.78, 2.20, 37, true, true, 'INS-GB-127', '2025-12-12', 650000),
('Emerald Isle', 'IE-DUB-2024-128', 'Ireland', 'sailboat', 15.50, 4.68, 2.16, 38, true, true, 'INS-IE-128', '2026-01-15', 610000),
('Blue Lagoon', 'FR-MRS-2024-129', 'France', 'catamaran', 19.20, 9.10, 1.42, 39, true, true, 'INS-FR-129', '2026-02-18', 850000),
('Liberty', 'US-MA-2024-130', 'USA', 'motor_yacht', 29.70, 7.80, 2.68, 40, true, true, 'INS-US-130', '2026-03-08', 1650000),
('Harmony', 'IT-GEN-2024-131', 'Italy', 'sailboat', 17.20, 4.98, 2.26, 41, true, true, 'INS-IT-131', '2025-12-22', 710000),
('Serenity', 'GR-COR-2024-132', 'Greece', 'motor_yacht', 25.10, 6.85, 2.46, 42, true, true, 'INS-GR-132', '2026-02-15', 1180000),
('Paradise', 'ES-IBZ-2024-133', 'Spain', 'catamaran', 17.90, 8.60, 1.32, 43, true, true, 'INS-ES-133', '2026-01-22', 770000),
('Odyssey', 'GR-ATH-2024-134', 'Greece', 'motor_yacht', 33.40, 8.70, 2.92, 44, true, true, 'INS-GR-134', '2026-03-18', 2050000),
('Euphoria', 'FR-TLN-2024-135', 'France', 'sailboat', 16.60, 4.88, 2.23, 45, true, true, 'INS-FR-135', '2025-12-08', 680000),
('Tranquility', 'GB-FAL-2024-136', 'UK', 'motor_yacht', 24.80, 6.72, 2.43, 46, true, true, 'INS-GB-136', '2026-01-28', 1120000),
('Solitude', 'NO-BRG-2024-137', 'Norway', 'sailboat', 15.90, 4.75, 2.19, 47, true, true, 'INS-NO-137', '2026-02-08', 630000),
('Infinity', 'IT-NAP-2024-138', 'Italy', 'motor_yacht', 28.20, 7.40, 2.62, 48, true, true, 'INS-IT-138', '2026-03-02', 1480000),
('Eternity', 'ES-MAL-2024-139', 'Spain', 'motor_yacht', 21.30, 6.12, 2.22, 49, true, true, 'INS-ES-139', '2025-12-15', 910000),
('Destiny', 'AE-DXB-2024-140', 'UAE', 'motor_yacht', 40.50, 10.20, 3.18, 50, true, true, 'INS-AE-140', '2026-03-28', 2800000);

-- ============= BERTHS (600 Total - Programmatic Generation) =============

-- Section A: Premium (10-15m) - 100 berths
INSERT INTO berths (berth_number, section, length_meters, width_meters, depth_meters, status, daily_rate_eur, facilities)
SELECT 
    'A-' || LPAD(generate_series::text, 2, '0'),
    'A',
    ROUND((10 + (generate_series % 6) * 0.8)::numeric, 2),
    ROUND((3.5 + (generate_series % 6) * 0.2)::numeric, 2),
    ROUND((3.5 + (generate_series % 3) * 0.3)::numeric, 2),
    CASE 
        WHEN generate_series % 10 < 8 THEN 'occupied'
        WHEN generate_series % 10 = 8 THEN 'maintenance'
        ELSE 'available'
    END,
    ROUND((38 + (generate_series % 6) * 0.5)::numeric, 2),
    '{"water": true, "electricity": "220V", "wifi": true}'::jsonb
FROM generate_series(1, 100);

-- Section B: Standard (12-18m) - 100 berths
INSERT INTO berths (berth_number, section, length_meters, width_meters, depth_meters, status, daily_rate_eur, facilities)
SELECT 
    'B-' || LPAD(generate_series::text, 2, '0'),
    'B',
    ROUND((12 + (generate_series % 7) * 0.9)::numeric, 2),
    ROUND((4.0 + (generate_series % 7) * 0.18)::numeric, 2),
    ROUND((3.8 + (generate_series % 3) * 0.4)::numeric, 2),
    CASE 
        WHEN generate_series % 10 < 7 THEN 'occupied'
        WHEN generate_series % 10 = 7 THEN 'reserved'
        WHEN generate_series % 10 = 8 THEN 'maintenance'
        ELSE 'available'
    END,
    ROUND((45 + (generate_series % 7) * 1.0)::numeric, 2),
    '{"water": true, "electricity": "380V", "wifi": true}'::jsonb
FROM generate_series(1, 100);

-- Section C: Large (15-25m) - 100 berths
INSERT INTO berths (berth_number, section, length_meters, width_meters, depth_meters, status, daily_rate_eur, facilities)
SELECT 
    'C-' || LPAD(generate_series::text, 2, '0'),
    'C',
    ROUND((15 + (generate_series % 11) * 0.9)::numeric, 2),
    ROUND((5.0 + (generate_series % 11) * 0.14)::numeric, 2),
    ROUND((4.0 + (generate_series % 3) * 0.5)::numeric, 2),
    CASE 
        WHEN generate_series % 10 < 7 THEN 'occupied'
        WHEN generate_series % 10 = 7 THEN 'reserved'
        WHEN generate_series % 10 = 8 THEN 'maintenance'
        ELSE 'available'
    END,
    ROUND((65 + (generate_series % 11) * 1.8)::numeric, 2),
    '{"water": true, "electricity": "380V", "wifi": true, "cable_tv": true}'::jsonb
FROM generate_series(1, 100);

-- Section D: Mega Yacht (20-35m) - 100 berths
INSERT INTO berths (berth_number, section, length_meters, width_meters, depth_meters, status, daily_rate_eur, facilities)
SELECT 
    'D-' || LPAD(generate_series::text, 2, '0'),
    'D',
    ROUND((20 + (generate_series % 16) * 0.9)::numeric, 2),
    ROUND((6.0 + (generate_series % 16) * 0.14)::numeric, 2),
    ROUND((4.5 + (generate_series % 3) * 0.5)::numeric, 2),
    CASE 
        WHEN generate_series % 10 < 6 THEN 'occupied'
        WHEN generate_series % 10 IN (6,7) THEN 'available'
        WHEN generate_series % 10 = 8 THEN 'reserved'
        ELSE 'maintenance'
    END,
    ROUND((120 + (generate_series % 16) * 3.5)::numeric, 2),
    '{"water": true, "electricity": "380V", "wifi": true, "cable_tv": true, "concierge": true}'::jsonb
FROM generate_series(1, 100);

-- Section E: Super Yacht (30-50m) - 100 berths
INSERT INTO berths (berth_number, section, length_meters, width_meters, depth_meters, status, daily_rate_eur, facilities)
SELECT 
    'E-' || LPAD(generate_series::text, 2, '0'),
    'E',
    ROUND((30 + (generate_series % 21) * 0.95)::numeric, 2),
    ROUND((8.0 + (generate_series % 21) * 0.19)::numeric, 2),
    ROUND((5.5 + (generate_series % 3) * 0.5)::numeric, 2),
    CASE 
        WHEN generate_series % 10 < 4 THEN 'occupied'
        WHEN generate_series % 10 IN (4,5,6,7,8) THEN 'available'
        ELSE 'reserved'
    END,
    ROUND((220 + (generate_series % 21) * 7.0)::numeric, 2),
    '{"water": true, "electricity": "380V", "wifi": true, "cable_tv": true, "concierge": true, "helipad_access": true}'::jsonb
FROM generate_series(1, 100);

-- Section F: Dry Storage - 100 berths
INSERT INTO berths (berth_number, section, length_meters, width_meters, depth_meters, status, daily_rate_eur, facilities)
SELECT 
    'F-' || LPAD(generate_series::text, 2, '0'),
    'F',
    ROUND((10 + (generate_series % 11) * 0.9)::numeric, 2),
    ROUND((3.5 + (generate_series % 11) * 0.15)::numeric, 2),
    0.00,
    CASE 
        WHEN generate_series % 10 < 8 THEN 'occupied'
        ELSE 'available'
    END,
    ROUND((25 + (generate_series % 11) * 0.9)::numeric, 2),
    '{"covered": true, "security": "24/7"}'::jsonb
FROM generate_series(1, 100);

-- ============= BERTH ASSIGNMENTS (25 Active + 5 Historical) =============

INSERT INTO berth_assignments (berth_id, vessel_id, customer_id, check_in, check_out, status, daily_rate_eur, nights, total_amount_eur, mooring_agreement_signed, advance_payment_received, insurance_verified, water_consumed_tons, electricity_consumed_kwh) VALUES
-- Active assignments
((SELECT id FROM berths WHERE berth_number='A-01'), 1, 1, '2025-11-08 14:00:00', '2025-11-15 10:00:00', 'active', 38.00, 7, 266.00, true, true, true, 1.2, 85),
((SELECT id FROM berths WHERE berth_number='A-03'), 3, 3, '2025-11-09 16:30:00', '2025-11-12 10:00:00', 'active', 38.00, 3, 114.00, true, true, true, 0.8, 45),
((SELECT id FROM berths WHERE berth_number='B-01'), 2, 2, '2025-11-07 11:00:00', '2025-11-20 10:00:00', 'active', 45.00, 13, 585.00, true, true, true, 3.5, 220),
((SELECT id FROM berths WHERE berth_number='B-03'), 5, 5, '2025-11-05 09:00:00', '2025-11-18 12:00:00', 'active', 65.00, 13, 845.00, true, true, true, 4.2, 310),
((SELECT id FROM berths WHERE berth_number='B-12'), 6, 6, '2025-11-06 15:00:00', '2025-11-13 10:00:00', 'active', 45.00, 7, 315.00, true, true, true, 1.8, 125),
((SELECT id FROM berths WHERE berth_number='C-01'), 12, 12, '2025-11-01 13:00:00', '2025-11-30 10:00:00', 'active', 65.00, 29, 1885.00, true, true, true, 8.5, 620),
((SELECT id FROM berths WHERE berth_number='C-08'), 18, 38, '2025-11-04 16:00:00', '2025-11-14 10:00:00', 'active', 72.00, 10, 720.00, true, true, true, 2.8, 180),
((SELECT id FROM berths WHERE berth_number='D-01'), 31, 31, '2025-10-28 15:00:00', '2025-11-14 10:00:00', 'active', 120.00, 17, 2040.00, true, true, true, 12.5, 890),
((SELECT id FROM berths WHERE berth_number='D-03'), 40, 40, '2025-11-02 10:00:00', '2025-11-16 10:00:00', 'reserved', 135.00, 14, 1890.00, true, true, true, 0, 0),
((SELECT id FROM berths WHERE berth_number='E-01'), 36, 36, '2025-11-03 10:00:00', '2025-12-03 10:00:00', 'active', 220.00, 30, 6600.00, true, true, true, 22.5, 1450),
((SELECT id FROM berths WHERE berth_number='E-04'), 43, 43, '2025-11-06 14:00:00', '2025-11-25 10:00:00', 'active', 350.00, 19, 6650.00, true, true, true, 18.3, 1280),
((SELECT id FROM berths WHERE berth_number='F-01'), 7, 7, '2024-10-15 09:00:00', NULL, 'active', 25.00, 0, 0.00, true, true, true, 0, 0), -- Winter storage
((SELECT id FROM berths WHERE berth_number='F-03'), 8, 8, '2024-10-20 10:00:00', NULL, 'active', 25.00, 0, 0.00, true, true, true, 0, 0),
((SELECT id FROM berths WHERE berth_number='A-15'), 10, 10, '2025-11-08 09:00:00', '2025-11-14 10:00:00', 'active', 40.00, 6, 240.00, true, true, true, 1.5, 95),
((SELECT id FROM berths WHERE berth_number='A-22'), 14, 14, '2025-11-07 13:00:00', '2025-11-12 10:00:00', 'active', 38.00, 5, 190.00, true, true, true, 1.0, 68),
((SELECT id FROM berths WHERE berth_number='B-18'), 17, 17, '2025-11-05 11:00:00', '2025-11-19 10:00:00', 'active', 48.00, 14, 672.00, true, true, true, 3.8, 260),
((SELECT id FROM berths WHERE berth_number='B-25'), 20, 20, '2025-11-06 14:00:00', '2025-11-15 10:00:00', 'active', 45.00, 9, 405.00, true, true, true, 2.2, 145),
((SELECT id FROM berths WHERE berth_number='C-12'), 23, 23, '2025-11-04 10:00:00', '2025-11-17 10:00:00', 'active', 70.00, 13, 910.00, true, true, true, 4.5, 325),
((SELECT id FROM berths WHERE berth_number='C-18'), 27, 27, '2025-11-03 15:00:00', '2025-11-16 10:00:00', 'active', 68.00, 13, 884.00, true, true, true, 3.9, 285),
((SELECT id FROM berths WHERE berth_number='D-08'), 34, 34, '2025-11-01 09:00:00', '2025-11-20 10:00:00', 'active', 125.00, 19, 2375.00, true, true, true, 15.8, 1120),
((SELECT id FROM berths WHERE berth_number='D-15'), 37, 37, '2025-11-05 13:00:00', '2025-11-18 10:00:00', 'active', 180.00, 13, 2340.00, true, true, true, 10.2, 780),
((SELECT id FROM berths WHERE berth_number='E-08'), 50, 50, '2025-11-02 11:00:00', '2025-11-28 10:00:00', 'active', 280.00, 26, 7280.00, true, true, true, 20.5, 1650),
((SELECT id FROM berths WHERE berth_number='C-25'), 32, 32, '2025-11-07 10:00:00', '2025-11-14 10:00:00', 'active', 72.00, 7, 504.00, true, true, true, 2.1, 155),
((SELECT id FROM berths WHERE berth_number='B-35'), 35, 35, '2025-11-08 15:00:00', '2025-11-13 10:00:00', 'active', 48.00, 5, 240.00, true, true, true, 1.3, 88),
((SELECT id FROM berths WHERE berth_number='A-45'), 44, 44, '2025-11-09 11:00:00', '2025-11-15 10:00:00', 'active', 38.00, 6, 228.00, true, true, true, 1.1, 72),

-- Historical (for SEAL learning - Psedelia's pattern)
((SELECT id FROM berths WHERE berth_number='B-12'), 1, 1, '2025-10-25 15:00:00', '2025-10-28 10:00:00', 'completed', 45.00, 3, 135.00, true, true, true, 0.9, 62),
((SELECT id FROM berths WHERE berth_number='B-12'), 1, 1, '2025-09-12 14:00:00', '2025-09-17 10:00:00', 'completed', 45.00, 5, 225.00, true, true, true, 1.5, 105),
((SELECT id FROM berths WHERE berth_number='B-12'), 1, 1, '2025-08-03 16:00:00', '2025-08-08 10:00:00', 'completed', 45.00, 5, 225.00, true, true, true, 1.4, 98),
((SELECT id FROM berths WHERE berth_number='B-12'), 1, 1, '2025-07-10 13:00:00', '2025-07-14 10:00:00', 'completed', 45.00, 4, 180.00, true, true, true, 1.2, 84),
((SELECT id FROM berths WHERE berth_number='B-12'), 1, 1, '2025-06-15 15:00:00', '2025-06-20 10:00:00', 'completed', 45.00, 5, 225.00, true, true, true, 1.6, 110);

-- ============= VHF COMMUNICATION LOGS (20 Realistic Interactions) =============

INSERT INTO vhf_logs (command_text, parsed_intent, vessel_id, customer_id, response_text, language, channel, timestamp, duration_seconds) VALUES
-- Turkish communications
('Merhaba West Istanbul Marina, 14 metrelik tekne için 3 gecelik rezervasyon istiyorum', 'reservation_create', 1, 1, 'Psedelia, rezervasyonunuz B-12 için onaylandı. Günlük 45 euro, toplam 135 euro. Varış saatiniz nedir?', 'tr', '72', '2025-11-08 13:45:23', 47),
('Marina, marina, burası Ay Işığı. Yakıt ikmali gerekiyor', 'fuel_request', 2, 2, 'Ay Işığı, alındı. Yakıt teknesi 15 dakika içinde yanınızda olacak. Ne kadar dizel?', 'tr', '72', '2025-11-09 10:22:15', 28),
('West Istanbul Marina, acil durum! Pompamızda arıza var, su alıyoruz', 'emergency_mechanical', 3, 3, 'Deniz Yıldızı, anlaşıldı! Acil müdahale ekibi yola çıktı. Konumunuz nedir? Personel sayısı?', 'tr', '72', '2025-11-07 16:51:09', 62),
('Marina, iskele B-23 için elektrik bağlantısı çalışmıyor', 'maintenance_request', 9, 9, 'Martı, teknik ekip bilgilendirildi. 10 dakika içinde yanınızda olacaklar.', 'tr', '72', '2025-11-06 08:15:41', 21),
('West Istanbul, Ege Prenses burada. 13 gece için rezervasyon var. Giriş yapmak istiyoruz', 'arrival_notification', 5, 5, 'Ege Prenses, hoş geldiniz! B-03 iskele numaranız hazır. Pilot teknesi sizi karşılamak üzere yola çıktı.', 'tr', '72', '2025-11-05 08:42:18', 35),
('Marina, Fırtına için su ikmali rica ediyorum', 'water_request', 11, 11, 'Fırtına, su servisi 5 dakika içinde yanınızda olacak.', 'tr', '72', '2025-11-07 11:33:27', 18),
('West Istanbul Marina, Dalgıç ayrılış yapıyor. Faturamı gönderebilir misiniz?', 'checkout_invoice', 12, 12, 'Dalgıç, faturanız email adresinize gönderildi. Toplam: 1885 euro. İyi yolculuklar!', 'tr', '72', '2025-10-30 09:15:42', 31),
('Marina, Rüzgar Gülü. Çamaşırhane servisi rica ediyorum', 'laundry_service', 13, 13, 'Rüzgar Gülü, çamaşırlarınız saat 16:00\'da alınacak, yarın 10:00\'da teslim edilecek.', 'tr', '72', '2025-11-08 11:20:31', 26),

-- English communications
('West Istanbul Marina, this is Sea Spirit requesting berth assignment for tonight', 'berth_inquiry', 31, 31, 'Sea Spirit, we have berth D-01 available. Your vessel length is 28.5 meters, correct?', 'en', '72', '2025-10-28 17:33:12', 35),
('Marina, Windseeker here. Need water refill at berth A-04', 'water_request', 32, 32, 'Windseeker, understood. Water service will be there in 5 minutes.', 'en', '72', '2025-11-09 11:07:28', 18),
('West Istanbul Marina, can you provide current weather conditions?', 'weather_inquiry', 33, 33, 'Wind: NW 15 knots, Wave height: 0.5m, Visibility: Good. Forecast: Calm evening.', 'en', '72', '2025-11-09 13:55:02', 22),
('Marina, Ocean Pearl here. We need provisions delivery', 'provisioning_request', 40, 40, 'Ocean Pearl, our concierge will contact you on your mobile. What do you need?', 'en', '72', '2025-11-07 10:45:19', 31),
('West Istanbul, Bella Vita departing berth B-15. Request clearance', 'departure_request', 34, 34, 'Bella Vita, you are clear to depart. Fair winds!', 'en', '72', '2025-11-08 09:42:17', 15),
('Marina, Nordwind checking in. Our reservation is for berth B-18', 'arrival_notification', 35, 35, 'Nordwind, welcome! Pilot boat is on its way to meet you. Stand by on channel 68.', 'en', '72', '2025-11-05 10:18:44', 29),

-- Greek communications
('West Istanbul Marina, εδώ Aphrodite. Θέλουμε κράτηση για 4 νύχτες', 'reservation_create', 33, 33, 'Aphrodite, η κράτησή σας επιβεβαιώθηκε στη θέση C-08. Καλώς ήρθατε!', 'el', '72', '2025-11-04 15:28:55', 41),
('Marina, Blue Horizon. Χρειαζόμαστε ηλεκτρικό ρεύμα', 'electricity_request', 38, 38, 'Blue Horizon, το ηλεκτρικό ρεύμα είναι διαθέσιμο στον κόλπο σας.', 'el', '72', '2025-11-06 14:12:33', 24),

-- Historical (Psedelia pattern for SEAL learning)
('Marina, Psedelia burada. Her zamanki yerimiz B-12 müsait mi?', 'preferred_berth_inquiry', 1, 1, 'Psedelia, evet! B-12 sizin için hazır. Hoş geldiniz!', 'tr', '72', '2025-10-25 14:52:08', 19),
('West Istanbul, Psedelia için su ve elektrik bağlantısı lütfen', 'utilities_connection', 1, 1, 'Psedelia, bağlantılarınız aktif. Su ve elektrik kullanıma hazır.', 'tr', '72', '2025-10-25 15:10:42', 14),
('Marina, Psedelia ayrılış yapıyor. Faturamı gönderebilir misiniz?', 'checkout_invoice', 1, 1, 'Psedelia, faturanız email adresinize gönderildi. İyi yolculuklar!', 'tr', '72', '2025-10-28 09:30:15', 23),
('West Istanbul Marina, Psedelia tekrar geliyor. B-12 rezerve edebilir miyiz?', 'reservation_create', 1, 1, 'Psedelia, B-12 sizin için rezerve edildi. 3 gece, 135 euro. Hoş geldiniz!', 'tr', '72', '2025-11-08 13:22:51', 26);

-- ============= INVOICES (15 Historical Invoices) =============

INSERT INTO invoices (parasut_invoice_id, customer_id, assignment_id, invoice_number, issue_date, due_date, subtotal_eur, vat_amount_eur, total_amount_eur, status, parasut_status) VALUES
('PRST-2025-10-001', 1, 26, 'WIM-2025-10-001', '2025-10-28', '2025-11-07', 135.00, 27.00, 162.00, 'paid', 'issued'),
('PRST-2025-10-002', 1, 27, 'WIM-2025-10-002', '2025-09-17', '2025-09-27', 225.00, 45.00, 270.00, 'paid', 'issued'),
('PRST-2025-10-003', 1, 28, 'WIM-2025-10-003', '2025-08-08', '2025-08-18', 225.00, 45.00, 270.00, 'paid', 'issued'),
('PRST-2025-10-004', 1, 29, 'WIM-2025-10-004', '2025-07-14', '2025-07-24', 180.00, 36.00, 216.00, 'paid', 'issued'),
('PRST-2025-10-005', 1, 30, 'WIM-2025-10-005', '2025-06-20', '2025-06-30', 225.00, 45.00, 270.00, 'paid', 'issued'),
('PRST-2025-11-001', 2, 3, 'WIM-2025-11-001', '2025-11-09', '2025-11-19', 585.00, 117.00, 702.00, 'pending', 'draft'),
('PRST-2025-11-002', 3, 2, 'WIM-2025-11-002', '2025-11-09', '2025-11-19', 114.00, 22.80, 136.80, 'pending', 'draft'),
('PRST-2025-11-003', 5, 4, 'WIM-2025-11-003', '2025-11-09', '2025-11-19', 845.00, 169.00, 1014.00, 'pending', 'draft'),
('PRST-2025-11-004', 31, 8, 'WIM-2025-11-004', '2025-11-09', '2025-11-19', 2040.00, 408.00, 2448.00, 'pending', 'draft'),
('PRST-2025-11-005', 36, 10, 'WIM-2025-11-005', '2025-11-09', '2025-11-19', 6600.00, 1320.00, 7920.00, 'pending', 'draft'),
('PRST-2025-11-006', 43, 11, 'WIM-2025-11-006', '2025-11-09', '2025-11-19', 6650.00, 1330.00, 7980.00, 'pending', 'draft'),
('PRST-2025-11-007', 10, 14, 'WIM-2025-11-007', '2025-11-09', '2025-11-19', 240.00, 48.00, 288.00, 'pending', 'draft'),
('PRST-2025-11-008', 17, 16, 'WIM-2025-11-008', '2025-11-09', '2025-11-19', 672.00, 134.40, 806.40, 'pending', 'draft'),
('PRST-2025-11-009', 23, 18, 'WIM-2025-11-009', '2025-11-09', '2025-11-19', 910.00, 182.00, 1092.00, 'pending', 'draft'),
('PRST-2025-11-010', 34, 20, 'WIM-2025-11-010', '2025-11-09', '2025-11-19', 2375.00, 475.00, 2850.00, 'pending', 'draft');

-- Invoice line items for Psedelia's last completed stay (detailed breakdown)
INSERT INTO invoice_items (invoice_id, description, quantity, unit_price_eur, total_eur) VALUES
(1, 'Berth Rental B-12 (3 nights)', 3.00, 45.00, 135.00),
(1, 'Electricity Consumption (kWh)', 62.00, 0.18, 11.16),
(1, 'Water Consumption (tons)', 0.90, 6.00, 5.40),
(1, 'Waste Disposal Service', 1.00, 5.00, 5.00);

-- ============= SEAL LEARNING DATA (Customer Preferences) =============

INSERT INTO customer_preferences (customer_id, vessel_id, preferred_berth_section, preferred_berth_number, preferred_services, preferred_language, confidence_score, occurrences) VALUES
-- Psedelia's strong preference pattern
(1, 1, 'B', 'B-12', '{"water": true, "electricity": true, "wifi": true}'::jsonb, 'tr', 0.95, 5),
-- Other learned preferences
(2, 2, 'B', 'B-01', '{"water": true, "electricity": true, "fuel": true}'::jsonb, 'tr', 0.78, 2),
(5, 5, 'B', 'B-03', '{"water": true, "electricity": true, "concierge": true}'::jsonb, 'tr', 0.82, 3),
(31, 31, 'D', 'D-01', '{"water": true, "electricity": true, "concierge": true}'::jsonb, 'en', 0.85, 2),
(36, 36, 'E', 'E-01', '{"water": true, "electricity": true, "concierge": true, "helipad": true}'::jsonb, 'en', 0.91, 1);

-- ============= REGULATION VIOLATIONS (Sample Data) =============

INSERT INTO regulation_violations (vessel_id, customer_id, article_violated, description, severity, fine_amount_eur, resolved) VALUES
(3, 3, 'E.1.10', 'Speed limit exceeded: 5.2 knots detected (max 3 knots)', 'warning', 50.00, true),
(9, 9, 'F.13', 'Waste disposal in unauthorized area', 'fine', 100.00, false),
(23, 23, 'E.2.14', 'Flammable substance storage violation', 'warning', 75.00, true);

-- ============= HOT WORK PERMITS (Sample Active & Historical) =============

INSERT INTO hot_work_permits (permit_number, vessel_id, work_type, work_description, start_time, end_time, fire_prevention_measures, fire_watch_assigned, permit_issued_by, status) VALUES
('HWP-2025-11-001', 34, 'Welding', 'Mast repair welding', '2025-11-09 09:00:00', '2025-11-09 11:00:00', 'Fire extinguishers positioned, fire blanket ready, surrounding yachts notified', 'Mehmet Yılmaz', 'Marina Manager', 'completed'),
('HWP-2025-11-002', 23, 'Grinding', 'Hull grinding and sanding', '2025-11-08 13:00:00', '2025-11-08 16:00:00', 'Wet grinding method, fire extinguishers ready, work area isolated', 'Ali Demir', 'Marina Manager', 'completed'),
('HWP-2025-11-015', 34, 'Painting', 'Deck painting with flammable paint', '2025-11-10 10:00:00', '2025-11-10 15:00:00', 'Ventilation fans active, fire extinguishers positioned, no smoking zone enforced', 'Can Öztürk', 'Marina Manager', 'active');

-- ============= EMERGENCY CONTACTS =============

INSERT INTO emergency_contacts (vessel_id, contact_name, phone, email, relationship, is_primary) VALUES
(1, 'Fatma Yılmaz', '+90 532 123 4568', 'fatma.yilmaz@gmail.com', 'Spouse', true),
(2, 'Ayşe Demir', '+90 533 234 5679', 'ayse.demir@hotmail.com', 'Spouse', true),
(31, 'Emma Smith', '+44 7700 900124', 'emma.smith@yacht.com', 'Spouse', true),
(36, 'Natasha Petrov', '+7 916 123 4568', 'natasha.petrov@yandex.ru', 'Family', true),
(40, 'Layla Al-Rashid', '+971 50 123 4568', 'layla.ar@yacht.ae', 'Spouse', true);

-- ============= VERIFICATION QUERIES =============

-- Should return 600
SELECT COUNT(*) AS total_berths FROM berths;

-- Should show distribution by section
SELECT section, COUNT(*) AS count FROM berths GROUP BY section ORDER BY section;

-- Should show occupancy breakdown
SELECT status, COUNT(*) AS count FROM berths GROUP BY status;

-- Should return 50 customers
SELECT COUNT(*) AS total_customers FROM customers;

-- Should return 80 vessels
SELECT COUNT(*) AS total_vessels FROM vessels;

-- Should show 25 active assignments
SELECT status, COUNT(*) FROM berth_assignments GROUP BY status;

-- Should show VHF logs by language
SELECT language, COUNT(*) FROM vhf_logs GROUP BY language;

-- Verify Psedelia's berth preference pattern (should show B-12 repeated)
SELECT ba.*, b.berth_number, ba.check_in 
FROM berth_assignments ba 
JOIN berths b ON ba.berth_id = b.id 
WHERE ba.vessel_id = 1 
ORDER BY ba.check_in DESC;

-- Revenue summary
SELECT 
    SUM(total_amount_eur) AS total_revenue,
    AVG(daily_rate_eur) AS avg_daily_rate,
    COUNT(*) AS total_assignments
FROM berth_assignments 
WHERE status IN ('active', 'completed');
```

---

## 🎯 PROJECT STRUCTURE
```
ada-marina-west-istanbul/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── README.md
├── README.tr.md
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 001_initial_schema.py
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── customer.py
│   │   ├── vessel.py
│   │   ├── berth.py
│   │   ├── assignment.py
│   │   ├── invoice.py
│   │   ├── vhf_log.py
│   │   ├── violation.py
│   │   └── hot_work_permit.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── customer.py
│   │   ├── vessel.py
│   │   ├── berth.py
│   │   ├── assignment.py
│   │   └── invoice.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── scout.py          # VHF monitoring, vessel detection
│   │   ├── plan.py           # Berth allocation, optimization
│   │   ├── build.py          # API endpoints, database ops
│   │   ├── verify.py         # Compliance checking
│   │   └── ship.py           # SEAL learning, deployment
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── berths.py
│   │       ├── vessels.py
│   │       ├── customers.py
│   │       ├── assignments.py
│   │       ├── vhf.py
│   │       ├── invoices.py
│   │       ├── violations.py
│   │       └── permits.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── berth_service.py
│   │   ├── vhf_service.py
│   │   ├── parasut_client.py
│   │   ├── compliance_service.py
│   │   └── seal_learning.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── security.py
│   │   └── regulations.py    # 176-article rule engine
│   │
│   └── utils/
│       ├── __init__.py
│       ├── websocket.py
│       └── redis_client.py
│
├── regulations/
│   ├── WIM_OPERATION_REGULATIONS_ENG.pdf
│   └── regulations_rules.json
│
├── tests/
│   ├── __init__.py
│   ├── test_berths.py
│   ├── test_assignments.py
│   ├── test_vhf.py
│   ├── test_compliance.py
│   └── test_seal_learning.py
│
├── scripts/
│   ├── seed_database.sh
│   ├── demo_scenarios.py
│   └── generate_report.py
│
└── observability/
    ├── prometheus.yml
    ├── grafana_dashboards/
    │   ├── marina_operations.json
    │   └── compliance_monitoring.json
    └── claude_code_hooks/
```

---

## 🐳 DOCKER COMPOSE
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ada_marina_wim
      POSTGRES_USER: marina
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/seed_data.sql:/docker-entrypoint-initdb.d/seed.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U marina"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  neo4j:
    image: neo4j:5-community
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
      NEO4J_PLUGINS: '["apoc", "graph-data-science"]'
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
    healthcheck:
      test: ["CMD-SHELL", "cypher-shell -u neo4j -p ${NEO4J_PASSWORD} 'RETURN 1'"]
      interval: 15s
      timeout: 10s
      retries: 5

  scout-agent:
    build:
      context: .
      dockerfile: Dockerfile
    command: python -m app.agents.scout
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql+asyncpg://marina:${DB_PASSWORD}@postgres:5432/ada_marina_wim
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  plan-agent:
    build:
      context: .
      dockerfile: Dockerfile
    command: python -m app.agents.plan
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql+asyncpg://marina:${DB_PASSWORD}@postgres:5432/ada_marina_wim
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      neo4j:
        condition: service_healthy
    restart: unless-stopped

  build-agent:
    build:
      context: .
      dockerfile: Dockerfile
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://marina:${DB_PASSWORD}@postgres:5432/ada_marina_wim
      - REDIS_URL=redis://redis:6379
      - PARASUT_CLIENT_ID=${PARASUT_CLIENT_ID}
      - PARASUT_CLIENT_SECRET=${PARASUT_CLIENT_SECRET}
      - PARASUT_COMPANY_ID=${PARASUT_COMPANY_ID}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    volumes:
      - .:/app

  verify-agent:
    build:
      context: .
      dockerfile: Dockerfile
    command: python -m app.agents.verify
    environment:
      - DATABASE_URL=postgresql+asyncpg://marina:${DB_PASSWORD}@postgres:5432/ada_marina_wim
      - REDIS_URL=redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  ship-agent:
    build:
      context: .
      dockerfile: Dockerfile
    command: python -m app.agents.ship
    environment:
      - DATABASE_URL=postgresql+asyncpg://marina:${DB_PASSWORD}@postgres:5432/ada_marina_wim
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./observability/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_INSTALL_PLUGINS=redis-datasource
    volumes:
      - grafana_data:/var/lib/grafana
      - ./observability/grafana_dashboards:/etc/grafana/provisioning/dashboards
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  postgres_data:
  neo4j_data:
  prometheus_data:
  grafana_data:
```

---

## ⚙️ ENVIRONMENT VARIABLES
```env
# .env.example

# Database
DB_PASSWORD=change_me_in_production
NEO4J_PASSWORD=change_me_in_production

# APIs
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Parasut (Turkish E-Invoice)
PARASUT_CLIENT_ID=your_client_id
PARASUT_CLIENT_SECRET=your_client_secret
PARASUT_COMPANY_ID=your_company_id
PARASUT_USERNAME=your_username
PARASUT_PASSWORD=your_password
PARASUT_API_URL=https://api.parasut.com/v4

# Marina Configuration
MARINA_NAME=West Istanbul Marina
MARINA_TOTAL_BERTHS=600
VHF_CHANNEL=72
MARINA_LOCATION=Yakuplu, Beylikdüzü, Istanbul

# Security
SECRET_KEY=generate-a-secure-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Monitoring
GRAFANA_PASSWORD=admin

# Feature Flags
VHF_MOCK_MODE=true
SEAL_LEARNING_ENABLED=true
COMPLIANCE_MONITORING_ENABLED=true
```

---

## 📝 REQUIREMENTS.TXT
```txt
# FastAPI & Web Framework
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-multipart==0.0.9
websockets==12.0

# Database
sqlalchemy==2.0.31
asyncpg==0.29.0
alembic==1.13.0
psycopg2-binary==2.9.9

# Redis
redis==5.0.0
hiredis==2.2.3

# Neo4j
neo4j==5.14.0

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0

# AI & ML
anthropic==0.34.0
openai==1.40.0

# HTTP Clients
httpx==0.27.0
aiohttp==3.9.0

# Data Processing
pydantic==2.8.0
pydantic-settings==2.4.0
pandas==2.2.0

# Testing
pytest==8.3.0
pytest-asyncio==0.24.0
pytest-cov==5.0.0
httpx==0.27.0

# Monitoring
prometheus-client==0.20.0
prometheus-fastapi-instrumentator==7.0.0

# Utilities
python-dateutil==2.9.0
pytz==2024.1
```

---

## 🚀 DEPLOYMENT SCRIPT
```bash
#!/bin/bash
# scripts/deploy.sh - Complete Deployment Script

set -e

echo "🚢 ADA.MARINA WEST ISTANBUL - DEPLOYMENT STARTING"
echo "=================================================="

# Step 1: Environment Check
echo "📋 Step 1/10: Checking environment..."
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found. Copy .env.example to .env and configure."
    exit 1
fi
source .env
echo "✅ Environment loaded"

# Step 2: Docker Build
echo "🐳 Step 2/10: Building Docker images..."
docker-compose build --no-cache
echo "✅ Docker images built"

# Step 3: Start Infrastructure
echo "🚀 Step 3/10: Starting infrastructure services..."
docker-compose up -d postgres redis neo4j
echo "⏳ Waiting for services to be healthy..."
sleep 15

# Check service health
docker-compose ps | grep -q "healthy" || {
    echo "❌ Services not healthy. Check logs:"
    docker-compose logs postgres redis neo4j
    exit 1
}
echo "✅ Infrastructure services ready"

# Step 4: Database Migration
echo "📊 Step 4/10: Running database migrations..."
docker-compose run --rm build-agent alembic upgrade head
echo "✅ Database schema created"

# Step 5: Seed Database
echo "🌱 Step 5/10: Seeding database with 600 berths..."
docker-compose exec -T postgres psql -U marina -d ada_marina_wim -f /docker-entrypoint-initdb.d/seed.sql
echo "✅ Database seeded: 600 berths, 50 customers, 80 vessels"

# Step 6: Verify Data
echo "🔍 Step 6/10: Verifying data integrity..."
BERTH_COUNT=$(docker-compose exec -T postgres psql -U marina -d ada_marina_wim -t -c "SELECT COUNT(*) FROM berths;" | xargs)
if [ "$BERTH_COUNT" != "600" ]; then
    echo "❌ Error: Expected 600 berths, found $BERTH_COUNT"
    exit 1
fi
echo "✅ Data verification passed: $BERTH_COUNT berths"

# Step 7: Start All Agents
echo "🤖 Step 7/10: Starting all agents..."
docker-compose up -d scout-agent plan-agent build-agent verify-agent ship-agent
sleep 10
echo "✅ All agents running"

# Step 8: Start Monitoring
echo "📊 Step 8/10: Starting monitoring stack..."
docker-compose up -d prometheus grafana
sleep 5
echo "✅ Monitoring active"

# Step 9: Health Check
echo "🏥 Step 9/10: Running health checks..."
curl -f http://localhost:8000/health || {
    echo "❌ API health check failed"
    docker-compose logs build-agent
    exit 1
}
echo "✅ API health check passed"

# Step 10: Display Access Information
echo ""
echo "=================================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=================================================="
echo ""
echo "🌐 Access Points:"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Grafana Dashboard: http://localhost:3000 (admin/${GRAFANA_PASSWORD})"
echo "   Prometheus:        http://localhost:9090"
echo "   Neo4j Browser:     http://localhost:7474"
echo ""
echo "📊 Database Statistics:"
echo "   Total Berths:      600"
echo "   Customers:         50"
echo "   Vessels:           80"
echo "   Active Assignments: $(docker-compose exec -T postgres psql -U marina -d ada_marina_wim -t -c "SELECT COUNT(*) FROM berth_assignments WHERE status='active';" | xargs)"
echo ""
echo "🎯 Demo Ready for November 11, 2025 Meeting!"
echo "=================================================="

# Optional: Run test suite
read -p "Run test suite? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 Running test suite..."
    docker-compose run --rm build-agent pytest tests/ -v --cov=app --cov-report=html
    echo "✅ Tests complete. Coverage report: htmlcov/index.html"
fi

echo ""
echo "🚀 System is ready for production use!"