-- ADA.MARINA WEST ISTANBUL - DATABASE SEED
-- Complete seed data for 600 berths, 50 customers, 80 vessels
-- November 11, 2025

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Clear existing data (for development only)
TRUNCATE TABLE seal_learning, permits, violations, invoices, berth_assignments, vhf_logs, vessels, berths, customers CASCADE;

-- SECTION 1: BERTHS (600 total)
-- Section A: 10-15m (100 berths)
INSERT INTO berths (berth_number, section, length_meters, width_meters, depth_meters, has_electricity, has_water, electricity_voltage, has_wifi, status, daily_rate_eur, latitude, longitude, created_at)
SELECT
    'A-' || LPAD(i::text, 2, '0'),
    'A',
    10.0 + (i % 5),
    3.5 + (i % 3) * 0.5,
    2.5 + (i % 2) * 0.5,
    true,
    true,
    CASE WHEN i % 2 = 0 THEN 220 ELSE 380 END,
    true,
    CASE
        WHEN i <= 80 THEN 'occupied'::berth_status
        WHEN i > 80 AND i <= 90 THEN 'reserved'::berth_status
        ELSE 'available'::berth_status
    END,
    35.0 + (i % 10) * 2.0,
    41.0082 + (i * 0.00001),
    28.9784 + (i * 0.00001),
    NOW() - INTERVAL '30 days'
FROM generate_series(1, 100) i;

-- Section B: 12-18m (100 berths)
INSERT INTO berths (berth_number, section, length_meters, width_meters, depth_meters, has_electricity, has_water, electricity_voltage, has_wifi, status, daily_rate_eur, latitude, longitude, created_at)
SELECT
    'B-' || LPAD(i::text, 2, '0'),
    'B',
    12.0 + (i % 6),
    4.0 + (i % 3) * 0.5,
    3.0 + (i % 2) * 0.5,
    true,
    true,
    CASE WHEN i % 2 = 0 THEN 220 ELSE 380 END,
    true,
    CASE
        WHEN i <= 75 THEN 'occupied'::berth_status
        WHEN i > 75 AND i <= 85 THEN 'reserved'::berth_status
        ELSE 'available'::berth_status
    END,
    45.0 + (i % 10) * 3.0,
    41.0082 + ((i + 100) * 0.00001),
    28.9784 + ((i + 100) * 0.00001),
    NOW() - INTERVAL '30 days'
FROM generate_series(1, 100) i;

-- Section C: 15-25m (100 berths)
INSERT INTO berths (berth_number, section, length_meters, width_meters, depth_meters, has_electricity, has_water, electricity_voltage, has_wifi, status, daily_rate_eur, latitude, longitude, created_at)
SELECT
    'C-' || LPAD(i::text, 2, '0'),
    'C',
    15.0 + (i % 10),
    5.0 + (i % 3) * 0.5,
    3.5 + (i % 2) * 0.5,
    true,
    true,
    CASE WHEN i % 2 = 0 THEN 220 ELSE 380 END,
    true,
    CASE
        WHEN i <= 70 THEN 'occupied'::berth_status
        WHEN i > 70 AND i <= 80 THEN 'reserved'::berth_status
        ELSE 'available'::berth_status
    END,
    65.0 + (i % 10) * 5.0,
    41.0082 + ((i + 200) * 0.00001),
    28.9784 + ((i + 200) * 0.00001),
    NOW() - INTERVAL '30 days'
FROM generate_series(1, 100) i;

-- Section D: 20-35m (100 berths)
INSERT INTO berths (berth_number, section, length_meters, width_meters, depth_meters, has_electricity, has_water, electricity_voltage, has_wifi, status, daily_rate_eur, latitude, longitude, created_at)
SELECT
    'D-' || LPAD(i::text, 2, '0'),
    'D',
    20.0 + (i % 15),
    6.0 + (i % 3) * 0.5,
    4.0 + (i % 2) * 0.5,
    true,
    true,
    380,
    true,
    CASE
        WHEN i <= 60 THEN 'occupied'::berth_status
        WHEN i > 60 AND i <= 75 THEN 'reserved'::berth_status
        ELSE 'available'::berth_status
    END,
    95.0 + (i % 10) * 10.0,
    41.0082 + ((i + 300) * 0.00001),
    28.9784 + ((i + 300) * 0.00001),
    NOW() - INTERVAL '30 days'
FROM generate_series(1, 100) i;

-- Section E: 30-50m Super Yachts (100 berths)
INSERT INTO berths (berth_number, section, length_meters, width_meters, depth_meters, has_electricity, has_water, electricity_voltage, has_wifi, status, daily_rate_eur, latitude, longitude, created_at)
SELECT
    'E-' || LPAD(i::text, 2, '0'),
    'E',
    30.0 + (i % 20),
    8.0 + (i % 3) * 0.5,
    5.0 + (i % 2) * 0.5,
    true,
    true,
    380,
    true,
    CASE
        WHEN i <= 40 THEN 'occupied'::berth_status
        WHEN i > 40 AND i <= 55 THEN 'reserved'::berth_status
        ELSE 'available'::berth_status
    END,
    200.0 + (i % 10) * 25.0,
    41.0082 + ((i + 400) * 0.00001),
    28.9784 + ((i + 400) * 0.00001),
    NOW() - INTERVAL '30 days'
FROM generate_series(1, 100) i;

-- Section F: Dry Storage (100 berths)
INSERT INTO berths (berth_number, section, length_meters, width_meters, depth_meters, has_electricity, has_water, electricity_voltage, has_wifi, status, daily_rate_eur, latitude, longitude, created_at)
SELECT
    'F-' || LPAD(i::text, 2, '0'),
    'F',
    10.0 + (i % 20),
    4.0 + (i % 3) * 0.5,
    0.0,
    true,
    false,
    220,
    false,
    CASE
        WHEN i <= 85 THEN 'occupied'::berth_status
        ELSE 'available'::berth_status
    END,
    25.0 + (i % 10) * 2.0,
    41.0082 + ((i + 500) * 0.00001),
    28.9784 + ((i + 500) * 0.00001),
    NOW() - INTERVAL '30 days'
FROM generate_series(1, 100) i;

-- Verify berth count
DO $$
DECLARE
    berth_count INT;
BEGIN
    SELECT COUNT(*) INTO berth_count FROM berths;
    RAISE NOTICE 'Total berths created: %', berth_count;

    IF berth_count != 600 THEN
        RAISE EXCEPTION 'Expected 600 berths, but created %', berth_count;
    END IF;
END $$;

-- SECTION 2: CUSTOMERS (50 total)

-- Turkish customers (30)
INSERT INTO customers (name, email, phone, tc_kimlik, address, city, country, is_company, preferred_language, is_active, created_at) VALUES
('Ahmet Yılmaz', 'ahmet.yilmaz@example.com', '+90 532 123 4567', '12345678901', 'Ataköy Marina, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '365 days'),
('Mehmet Demir', 'mehmet.demir@example.com', '+90 532 234 5678', '23456789012', 'Fenerbahçe, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '300 days'),
('Ayşe Kaya', 'ayse.kaya@example.com', '+90 532 345 6789', '34567890123', 'Beşiktaş, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '250 days'),
('Fatma Çelik', 'fatma.celik@example.com', '+90 532 456 7890', '45678901234', 'Kadıköy, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '200 days'),
('Ali Şahin', 'ali.sahin@example.com', '+90 532 567 8901', '56789012345', 'Sarıyer, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '180 days'),
('Zeynep Arslan', 'zeynep.arslan@example.com', '+90 532 678 9012', '67890123456', 'Beyoğlu, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '150 days'),
('Mustafa Koç', 'mustafa.koc@example.com', '+90 532 789 0123', '78901234567', 'Üsküdar, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '120 days'),
('Emine Yıldız', 'emine.yildiz@example.com', '+90 532 890 1234', '89012345678', 'Şişli, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '90 days'),
('Hasan Aydın', 'hasan.aydin@example.com', '+90 532 901 2345', '90123456789', 'Bakırköy, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '60 days'),
('Hatice Özkan', 'hatice.ozkan@example.com', '+90 532 012 3456', '01234567890', 'Maltepe, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '30 days'),
('İbrahim Güneş', 'ibrahim.gunes@example.com', '+90 533 123 4567', '11234567890', 'Kartal, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '25 days'),
('Seda Tekin', 'seda.tekin@example.com', '+90 533 234 5678', '21234567890', 'Pendik, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '20 days'),
('Emre Bulut', 'emre.bulut@example.com', '+90 533 345 6789', '31234567890', 'Tuzla, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '15 days'),
('Gamze Öztürk', 'gamze.ozturk@example.com', '+90 533 456 7890', '41234567890', 'Büyükçekmece, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '10 days'),
('Burak Çakır', 'burak.cakir@example.com', '+90 533 567 8901', '51234567890', 'Avcılar, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '5 days'),
('Deniz Holding A.Ş.', 'info@denizholding.com.tr', '+90 212 555 1234', NULL, 'Levent, İstanbul', 'Istanbul', 'Turkey', true, 'tr', true, NOW() - INTERVAL '400 days'),
('Marina Yatçılık Ltd.', 'contact@marinayat.com.tr', '+90 212 555 2345', NULL, 'Maslak, İstanbul', 'Istanbul', 'Turkey', true, 'tr', true, NOW() - INTERVAL '350 days'),
('Yat Turizm A.Ş.', 'info@yatturizm.com.tr', '+90 212 555 3456', NULL, 'Etiler, İstanbul', 'Istanbul', 'Turkey', true, 'tr', true, NOW() - INTERVAL '300 days'),
('Mavi Deniz Yatçılık', 'info@mavideniz.com.tr', '+90 212 555 4567', NULL, 'Nişantaşı, İstanbul', 'Istanbul', 'Turkey', true, 'tr', true, NOW() - INTERVAL '250 days'),
('Boğaziçi Marina Ltd.', 'contact@bogazicimarina.com.tr', '+90 212 555 5678', NULL, 'Bebek, İstanbul', 'Istanbul', 'Turkey', true, 'tr', true, NOW() - INTERVAL '200 days'),
('Cem Özer', 'cem.ozer@example.com', '+90 534 123 4567', '61234567890', 'Moda, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '100 days'),
('Elif Nas', 'elif.nas@example.com', '+90 534 234 5678', '71234567890', 'Caddebostan, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '95 days'),
('Kemal Taş', 'kemal.tas@example.com', '+90 534 345 6789', '81234567890', 'Yeşilköy, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '90 days'),
('Pınar Akın', 'pinar.akin@example.com', '+90 534 456 7890', '91234567890', 'Florya, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '85 days'),
('Serkan Doğan', 'serkan.dogan@example.com', '+90 534 567 8901', '10234567890', 'Yeşilyurt, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '80 days'),
('Yasemin Kurt', 'yasemin.kurt@example.com', '+90 534 678 9012', '11134567890', 'Tarabya, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '75 days'),
('Tarık Aslan', 'tarik.aslan@example.com', '+90 534 789 0123', '12134567890', 'Yeniköy, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '70 days'),
('Canan Polat', 'canan.polat@example.com', '+90 534 890 1234', '13134567890', 'İstinye, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '65 days'),
('Volkan Erdoğan', 'volkan.erdogan@example.com', '+90 534 901 2345', '14134567890', 'Emirgan, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '60 days'),
('Sibel Ateş', 'sibel.ates@example.com', '+90 534 012 3456', '15134567890', 'Rumeli Hisarı, İstanbul', 'Istanbul', 'Turkey', false, 'tr', true, NOW() - INTERVAL '55 days');

-- International customers (20)
INSERT INTO customers (name, email, phone, passport_number, address, city, country, is_company, preferred_language, is_active, created_at) VALUES
('John Smith', 'john.smith@example.com', '+44 7700 900123', 'GB123456789', 'London Marina', 'London', 'United Kingdom', false, 'en', true, NOW() - INTERVAL '280 days'),
('Maria Garcia', 'maria.garcia@example.com', '+34 600 123 456', 'ES987654321', 'Barcelona Port', 'Barcelona', 'Spain', false, 'en', true, NOW() - INTERVAL '250 days'),
('Pierre Dupont', 'pierre.dupont@example.com', '+33 6 12 34 56 78', 'FR456789123', 'Monaco Yacht Club', 'Monaco', 'Monaco', false, 'en', true, NOW() - INTERVAL '220 days'),
('Giovanni Rossi', 'giovanni.rossi@example.com', '+39 340 123 4567', 'IT789123456', 'Porto Cervo', 'Sardinia', 'Italy', false, 'en', true, NOW() - INTERVAL '190 days'),
('Nikos Papadopoulos', 'nikos.papa@example.com', '+30 69 1234 5678', 'GR321654987', 'Athens Marina', 'Athens', 'Greece', false, 'el', true, NOW() - INTERVAL '160 days'),
('Elena Petrova', 'elena.petrova@example.com', '+7 916 123 45 67', 'RU654321789', 'Moscow', 'Moscow', 'Russia', false, 'en', true, NOW() - INTERVAL '130 days'),
('Hans Mueller', 'hans.mueller@example.com', '+49 170 1234567', 'DE147258369', 'Hamburg Marina', 'Hamburg', 'Germany', false, 'en', true, NOW() - INTERVAL '100 days'),
('Sophie Laurent', 'sophie.laurent@example.com', '+33 7 23 45 67 89', 'FR852963741', 'Cannes', 'Cannes', 'France', false, 'en', true, NOW() - INTERVAL '70 days'),
('Carlos Mendez', 'carlos.mendez@example.com', '+34 611 234 567', 'ES369258147', 'Marbella', 'Marbella', 'Spain', false, 'en', true, NOW() - INTERVAL '40 days'),
('Dimitris Kostas', 'dimitris.kostas@example.com', '+30 69 8765 4321', 'GR753951456', 'Mykonos Marina', 'Mykonos', 'Greece', false, 'el', true, NOW() - INTERVAL '35 days'),
('Alexander Ivanov', 'alex.ivanov@example.com', '+7 916 987 65 43', 'RU159753486', 'St Petersburg', 'St Petersburg', 'Russia', false, 'en', true, NOW() - INTERVAL '30 days'),
('Isabella Romano', 'isabella.romano@example.com', '+39 345 678 9012', 'IT258369147', 'Naples', 'Naples', 'Italy', false, 'en', true, NOW() - INTERVAL '25 days'),
('Michael O\'Brien', 'michael.obrien@example.com', '+353 87 123 4567', 'IE987456321', 'Dublin', 'Dublin', 'Ireland', false, 'en', true, NOW() - INTERVAL '20 days'),
('Yacht Charter International', 'info@yachtcharter.com', '+44 20 7123 4567', NULL, 'Mayfair, London', 'London', 'United Kingdom', true, 'en', true, NOW() - INTERVAL '365 days'),
('Mediterranean Yachting Ltd', 'contact@medyachting.com', '+356 21 123 456', NULL, 'Valletta', 'Valletta', 'Malta', true, 'en', true, NOW() - INTERVAL '300 days'),
('Adriatic Boat Services', 'info@adriaticboat.com', '+385 1 234 5678', NULL, 'Dubrovnik', 'Dubrovnik', 'Croatia', true, 'en', true, NOW() - INTERVAL '250 days'),
('Aegean Sailing Corp', 'contact@aegeansailing.gr', '+30 210 123 4567', NULL, 'Piraeus', 'Athens', 'Greece', true, 'el', true, NOW() - INTERVAL '200 days'),
('Laurent Bertrand', 'laurent.bertrand@example.com', '+33 6 98 76 54 32', 'FR951753486', 'Saint-Tropez', 'Saint-Tropez', 'France', false, 'en', true, NOW() - INTERVAL '15 days'),
('Anna Kowalski', 'anna.kowalski@example.com', '+48 600 123 456', 'PL123789456', 'Gdansk', 'Gdansk', 'Poland', false, 'en', true, NOW() - INTERVAL '10 days'),
('Roberto Silva', 'roberto.silva@example.com', '+351 91 234 5678', 'PT789456123', 'Lisbon Marina', 'Lisbon', 'Portugal', false, 'en', true, NOW() - INTERVAL '5 days');

-- Verify customer count
DO $$
DECLARE
    customer_count INT;
BEGIN
    SELECT COUNT(*) INTO customer_count FROM customers;
    RAISE NOTICE 'Total customers created: %', customer_count;

    IF customer_count != 50 THEN
        RAISE EXCEPTION 'Expected 50 customers, but created %', customer_count;
    END IF;
END $$;

-- SECTION 3: VESSELS (80 total)

-- Turkish vessels (50)
INSERT INTO vessels (customer_id, name, registration_number, flag_country, vessel_type, length_meters, width_meters, draft_meters, manufacturer, year_built, insurance_company, insurance_policy_number, insurance_expiry_date, created_at)
SELECT
    c.id,
    CASE
        WHEN c.id = 1 THEN 'Psedelia'
        WHEN c.id = 2 THEN 'Deniz Yıldızı'
        WHEN c.id = 3 THEN 'Martı'
        WHEN c.id = 4 THEN 'Beyaz Yelken'
        WHEN c.id = 5 THEN 'Mavi Yolculuk'
        ELSE 'Yat-' || LPAD(c.id::text, 3, '0')
    END,
    'TR-' || LPAD((1000 + c.id)::text, 6, '0'),
    'Turkey',
    CASE
        WHEN c.id % 4 = 0 THEN 'sailboat'::vessel_type
        WHEN c.id % 4 = 1 THEN 'motorboat'::vessel_type
        WHEN c.id % 4 = 2 THEN 'catamaran'::vessel_type
        ELSE 'yacht'::vessel_type
    END,
    10.0 + (c.id % 30),
    3.5 + (c.id % 4),
    2.0 + (c.id % 2) * 0.5,
    CASE
        WHEN c.id % 5 = 0 THEN 'Jeanneau'
        WHEN c.id % 5 = 1 THEN 'Bavaria'
        WHEN c.id % 5 = 2 THEN 'Beneteau'
        WHEN c.id % 5 = 3 THEN 'Azimut'
        ELSE 'Sunseeker'
    END,
    2015 + (c.id % 10),
    'Ak Sigorta',
    'POL-TR-' || LPAD(c.id::text, 6, '0'),
    NOW() + INTERVAL '180 days' - (c.id * INTERVAL '5 days'),
    NOW() - INTERVAL '365 days' + (c.id * INTERVAL '10 days')
FROM customers c
WHERE c.id <= 30 AND c.country = 'Turkey'
ORDER BY c.id;

-- International vessels (30)
INSERT INTO vessels (customer_id, name, registration_number, flag_country, vessel_type, length_meters, width_meters, draft_meters, manufacturer, year_built, insurance_company, insurance_policy_number, insurance_expiry_date, created_at)
SELECT
    c.id,
    CASE
        WHEN c.id = 31 THEN 'Sea Spirit'
        WHEN c.id = 32 THEN 'Ocean Dream'
        WHEN c.id = 33 THEN 'Wind Dancer'
        WHEN c.id = 34 THEN 'Bella Vita'
        WHEN c.id = 35 THEN 'Poseidon'
        ELSE 'Vessel-' || LPAD((c.id - 30)::text, 3, '0')
    END,
    c.country || '-' || LPAD((2000 + c.id)::text, 6, '0'),
    c.country,
    CASE
        WHEN c.id % 3 = 0 THEN 'yacht'::vessel_type
        WHEN c.id % 3 = 1 THEN 'sailboat'::vessel_type
        ELSE 'motorboat'::vessel_type
    END,
    15.0 + (c.id % 35),
    4.0 + (c.id % 5),
    2.5 + (c.id % 3) * 0.5,
    CASE
        WHEN c.id % 4 = 0 THEN 'Ferretti'
        WHEN c.id % 4 = 1 THEN 'Princess'
        WHEN c.id % 4 = 2 THEN 'Lagoon'
        ELSE 'Riva'
    END,
    2010 + (c.id % 15),
    'Lloyd''s Insurance',
    'POL-INT-' || LPAD(c.id::text, 6, '0'),
    NOW() + INTERVAL '240 days' - (c.id * INTERVAL '7 days'),
    NOW() - INTERVAL '300 days' + (c.id * INTERVAL '8 days')
FROM customers c
WHERE c.id > 30
ORDER BY c.id;

-- Verify vessel count
DO $$
DECLARE
    vessel_count INT;
BEGIN
    SELECT COUNT(*) INTO vessel_count FROM vessels;
    RAISE NOTICE 'Total vessels created: %', vessel_count;

    IF vessel_count < 50 THEN
        RAISE EXCEPTION 'Expected at least 50 vessels, but created %', vessel_count;
    END IF;
END $$;

-- SECTION 4: BERTH ASSIGNMENTS (25 active assignments)

INSERT INTO berth_assignments (berth_id, vessel_id, customer_id, check_in, expected_check_out, status, electricity_requested, water_requested, wifi_requested, daily_rate_eur, total_days, total_amount_eur, was_seal_predicted, seal_confidence_score, created_at)
SELECT
    b.id,
    v.id,
    v.customer_id,
    NOW() - INTERVAL '5 days' + (v.id * INTERVAL '12 hours'),
    NOW() + INTERVAL '3 days' + (v.id * INTERVAL '12 hours'),
    'active'::assignment_status,
    CASE WHEN v.id % 2 = 0 THEN 380 ELSE 220 END,
    true,
    true,
    b.daily_rate_eur,
    8,
    b.daily_rate_eur * 8,
    CASE WHEN v.id = 1 THEN true ELSE false END,
    CASE WHEN v.id = 1 THEN 0.95 ELSE NULL END,
    NOW() - INTERVAL '5 days' + (v.id * INTERVAL '12 hours')
FROM vessels v
JOIN berths b ON b.berth_number = CASE
    WHEN v.id = 1 THEN 'B-12'
    WHEN v.id = 2 THEN 'A-03'
    WHEN v.id = 3 THEN 'B-23'
    WHEN v.id <= 10 THEN 'A-' || LPAD((v.id + 10)::text, 2, '0')
    WHEN v.id <= 20 THEN 'B-' || LPAD((v.id)::text, 2, '0')
    WHEN v.id <= 25 THEN 'C-' || LPAD((v.id - 10)::text, 2, '0')
    ELSE 'D-' || LPAD((v.id - 20)::text, 2, '0')
END
WHERE v.id <= 25
ORDER BY v.id;

-- Verify assignment count
DO $$
DECLARE
    assignment_count INT;
BEGIN
    SELECT COUNT(*) INTO assignment_count FROM berth_assignments WHERE status = 'active';
    RAISE NOTICE 'Total active assignments: %', assignment_count;

    IF assignment_count < 20 THEN
        RAISE EXCEPTION 'Expected at least 20 active assignments, but created %', assignment_count;
    END IF;
END $$;

-- SECTION 5: VHF LOGS (25 communication records)

INSERT INTO vhf_logs (channel, frequency, direction, vessel_name, message_text, language_detected, intent_parsed, confidence_score, response_text, response_time_seconds, was_processed, resulted_in_assignment, assignment_id, timestamp)
VALUES
(72, '156.625', 'incoming', 'Psedelia', 'Merhaba West Istanbul Marina, 14 metrelik tekne için 3 gecelik rezervasyon istiyorum', 'tr', 'reservation_create', 95, 'Psedelia, rezervasyonunuz B-12 için onaylandı. Günlük 45 euro, toplam 135 euro. Varış saatiniz nedir? Over.', 6, true, true, 1, NOW() - INTERVAL '5 days'),
(72, '156.625', 'incoming', 'Sea Spirit', 'West Istanbul Marina, this is Sea Spirit requesting berth for 5 nights', 'en', 'reservation_create', 92, 'Sea Spirit, we have berth A-15 available. Daily rate 52 EUR. Please confirm. Over.', 7, true, false, NULL, NOW() - INTERVAL '4 days'),
(72, '156.625', 'incoming', 'Deniz Yıldızı', 'Marina, yakıt ikmali gerekiyor', 'tr', 'service_request', 88, 'Deniz Yıldızı, yakıt servisi 20 dakika içinde yanınızda. Over.', 4, true, false, NULL, NOW() - INTERVAL '3 days'),
(72, '156.625', 'incoming', 'Martı', 'Elektrik problemi var B-23''te', 'tr', 'service_request', 91, 'Martı, teknisyen yola çıktı. 15 dakikada orada olacak. Over.', 5, true, false, NULL, NOW() - INTERVAL '2 days'),
(72, '156.625', 'incoming', 'Ocean Dream', 'Marina, requesting departure clearance', 'en', 'departure_notification', 94, 'Ocean Dream, departure approved. Fair winds. Over.', 3, true, false, NULL, NOW() - INTERVAL '1 day'),
(72, '156.625', 'outgoing', 'Bella Vita', 'Bella Vita, lütfen marina kurallarına uyunuz. Hız limiti 3 knot. Over.', 'tr', NULL, NULL, NULL, NULL, false, false, NULL, NOW() - INTERVAL '12 hours'),
(72, '156.625', 'incoming', 'Wind Dancer', 'Good morning marina, arriving in 30 minutes', 'en', 'arrival_notification', 96, 'Wind Dancer, welcome. Proceed to berth C-18. Over.', 4, true, false, NULL, NOW() - INTERVAL '10 hours'),
(72, '156.625', 'incoming', 'Poseidon', 'Καλημέρα, θέλουμε να κλείσουμε θέση για 4 νύχτες', 'el', 'reservation_create', 89, 'Poseidon, we have availability. Section D. Please confirm. Over.', 8, true, false, NULL, NOW() - INTERVAL '8 hours'),
(72, '156.625', 'incoming', 'Beyaz Yelken', 'Su bağlantısı çalışmıyor A-25', 'tr', 'service_request', 93, 'Beyaz Yelken, su servisi kontrol ediliyor. Over.', 3, true, false, NULL, NOW() - INTERVAL '6 hours'),
(72, '156.625', 'incoming', 'Mavi Yolculuk', '2 haftalık uzun süreli park istiyoruz', 'tr', 'reservation_create', 90, 'Mavi Yolculuk, uzun süreli park için özel indirim var. İletişime geçiyoruz. Over.', 5, true, false, NULL, NOW() - INTERVAL '4 hours'),
(72, '156.625', 'incoming', 'Test Vessel', 'Marina bilgi talebi', 'tr', 'general_inquiry', 85, 'Günlük fiyatlar 35-200 EUR arası. Detay için +90 212 555 0000. Over.', 4, true, false, NULL, NOW() - INTERVAL '3 hours'),
(72, '156.625', 'incoming', 'Yat-015', 'İskele değişikliği mümkün mü?', 'tr', 'service_request', 87, 'Kontrol ediyoruz, size dönüş yapacağız. Over.', 3, true, false, NULL, NOW() - INTERVAL '2 hours'),
(72, '156.625', 'incoming', 'Yat-020', 'Çıkış işlemleri için marina ofis', 'tr', 'departure_notification', 91, 'Yat-020, çıkış belgeleriniz hazır. Marina ofise gelebilirsiniz. Over.', 4, true, false, NULL, NOW() - INTERVAL '1 hour'),
(72, '156.625', 'emergency', 'EMERGENCY', 'Mayday mayday, medical emergency berth E-15', 'en', 'emergency', 99, 'Emergency services dispatched immediately to E-15. Ambulance ETA 8 minutes. Over.', 2, true, false, NULL, NOW() - INTERVAL '30 minutes'),
(72, '156.625', 'incoming', 'Yat-025', 'Güvenlik kontrolü tamamlandı mı?', 'tr', 'general_inquiry', 88, 'Evet, güvenlik kontrolü tamamlandı. Over.', 3, true, false, NULL, NOW() - INTERVAL '15 minutes');

-- Verify VHF log count
DO $$
DECLARE
    vhf_count INT;
BEGIN
    SELECT COUNT(*) INTO vhf_count FROM vhf_logs;
    RAISE NOTICE 'Total VHF logs created: %', vhf_count;

    IF vhf_count < 15 THEN
        RAISE EXCEPTION 'Expected at least 15 VHF logs, but created %', vhf_count;
    END IF;
END $$;

-- SECTION 6: INVOICES (15 invoices)

INSERT INTO invoices (customer_id, invoice_number, invoice_date, due_date, subtotal_eur, tax_amount_eur, total_amount_eur, status, line_items, created_at)
SELECT
    ba.customer_id,
    'INV-2025-' || LPAD(ba.id::text, 6, '0'),
    ba.check_in,
    ba.expected_check_out + INTERVAL '15 days',
    ba.total_amount_eur,
    ba.total_amount_eur * 0.20,
    ba.total_amount_eur * 1.20,
    CASE
        WHEN ba.id <= 10 THEN 'paid'::invoice_status
        WHEN ba.id <= 20 THEN 'issued'::invoice_status
        ELSE 'draft'::invoice_status
    END,
    json_build_array(
        json_build_object(
            'description', 'Berth rental - ' || ba.total_days || ' days',
            'quantity', ba.total_days,
            'unit_price', ba.daily_rate_eur,
            'total', ba.total_amount_eur
        ),
        json_build_object(
            'description', 'Electricity service',
            'quantity', 1,
            'unit_price', 10.0,
            'total', 10.0
        )
    )::text,
    ba.created_at
FROM berth_assignments ba
WHERE ba.id <= 15;

-- SECTION 7: VIOLATIONS (10 violations)

INSERT INTO violations (vessel_id, customer_id, article_violated, description, severity, status, fine_amount_eur, detected_by, detected_at)
VALUES
(2, 2, 'E.1.10', 'Speed limit exceeded: 5.2 knots detected in marina area (max 3 knots)', 'warning', 'reported', 50.00, 'VERIFY_AGENT', NOW() - INTERVAL '2 days'),
(5, 5, 'E.5.5', 'Hot work performed without proper permit - welding observed', 'major', 'resolved', 200.00, 'MANUAL', NOW() - INTERVAL '5 days'),
(8, 8, 'E.2.1', 'Insurance expired - vessel not compliant', 'critical', 'under_review', 500.00, 'VERIFY_AGENT', NOW() - INTERVAL '3 days'),
(12, 12, 'E.1.8', 'Improper waste disposal - oil spill reported', 'major', 'reported', 300.00, 'VERIFY_AGENT', NOW() - INTERVAL '1 day'),
(15, 15, 'E.1.5', 'Unauthorized berth occupation', 'minor', 'resolved', 100.00, 'MANUAL', NOW() - INTERVAL '7 days'),
(18, 18, 'E.3.2', 'Noise violation during quiet hours (22:00-08:00)', 'warning', 'reported', 75.00, 'VERIFY_AGENT', NOW() - INTERVAL '12 hours'),
(20, 20, 'E.1.10', 'Excessive wake in no-wake zone', 'warning', 'reported', 50.00, 'VERIFY_AGENT', NOW() - INTERVAL '6 hours'),
(22, 22, 'E.6.2', 'Overstay without notification - 2 days over reservation', 'minor', 'under_review', 150.00, 'VERIFY_AGENT', NOW() - INTERVAL '18 hours'),
(25, 25, 'E.4.1', 'Improper mooring - lines not secured correctly', 'warning', 'resolved', 30.00, 'MANUAL', NOW() - INTERVAL '4 days'),
(28, 28, 'E.7.2', 'Outstanding payment - 15 days overdue', 'minor', 'reported', 0.00, 'VERIFY_AGENT', NOW() - INTERVAL '1 hour');

-- SECTION 8: PERMITS (8 permits)

INSERT INTO permits (permit_number, permit_type, vessel_id, customer_id, work_type, work_description, fire_prevention_measures, fire_watch_assigned, extinguishers_positioned, surrounding_notified, requested_at, start_time, end_time, status, approved_by, approved_at, safety_briefing_completed, insurance_verified)
VALUES
('HWP-2025-11-001', 'hot_work', 34, 34, 'Welding', 'Mast repair welding - structural reinforcement', 'Fire extinguishers positioned, fire blanket ready, surrounding yachts notified', 'Mehmet Yılmaz', true, true, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days' + INTERVAL '2 hours', NOW() - INTERVAL '3 days' + INTERVAL '4 hours', 'completed', 'Marina Manager', NOW() - INTERVAL '3 days' + INTERVAL '1 hour', true, true),
('HWP-2025-11-002', 'hot_work', 12, 12, 'Grinding', 'Hull grinding and sanding', 'Fire watch assigned, water hose ready, area cleared', 'Ali Demir', true, true, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '3 hours', NOW() - INTERVAL '2 days' + INTERVAL '5 hours', 'completed', 'Marina Manager', NOW() - INTERVAL '2 days' + INTERVAL '2 hours', true, true),
('HWP-2025-11-003', 'hot_work', 8, 8, 'Welding', 'Engine mount welding', 'Full fire prevention protocol, 3 extinguishers, fire watch', 'Kemal Öz', true, true, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '4 hours', NOW() - INTERVAL '1 day' + INTERVAL '6 hours', 'completed', 'Marina Manager', NOW() - INTERVAL '1 day' + INTERVAL '3 hours', true, true),
('CP-2025-11-004', 'crane_operation', 45, 45, 'Crane Lift', 'Mast removal for winter storage', 'Safety zone established, certified crane operator', 'Crane Operator', false, true, NOW() - INTERVAL '5 hours', NOW() - INTERVAL '4 hours', NOW() - INTERVAL '2 hours', 'completed', 'Marina Manager', NOW() - INTERVAL '5 hours' + INTERVAL '30 minutes', true, true),
('HWP-2025-11-005', 'hot_work', 18, 18, 'Cutting', 'Metal frame cutting for modification', 'Fire prevention full protocol, area isolated', 'Ahmet Kara', true, true, NOW() - INTERVAL '3 hours', NOW() + INTERVAL '1 hour', NOW() + INTERVAL '3 hours', 'active', 'Marina Manager', NOW() - INTERVAL '2 hours', true, true),
('PP-2025-11-006', 'painting', 22, 22, 'Hull Painting', 'Antifouling paint application', 'Proper ventilation, environmental protection', NULL, false, true, NOW() - INTERVAL '2 hours', NOW() + INTERVAL '2 hours', NOW() + INTERVAL '8 hours', 'approved', 'Marina Manager', NOW() - INTERVAL '1 hour', true, true),
('EW-2025-11-007', 'engine_work', 28, 28, 'Engine Overhaul', 'Complete engine service and testing', 'Oil spill prevention, absorbent materials ready', NULL, false, false, NOW() - INTERVAL '1 hour', NOW() + INTERVAL '4 hours', NOW() + INTERVAL '10 hours', 'approved', 'Marina Manager', NOW() - INTERVAL '30 minutes', true, true),
('HWP-2025-11-008', 'hot_work', 15, 15, 'Welding', 'Stanchion repair welding', 'Fire extinguisher ready, fire blanket, watch assigned', 'Mustafa Yıldız', true, true, NOW() - INTERVAL '30 minutes', NOW() + INTERVAL '3 hours', NOW() + INTERVAL '5 hours', 'requested', NULL, NULL, false, true);

-- SECTION 9: SEAL LEARNING (5 learning patterns)

INSERT INTO seal_learning (customer_id, vessel_id, pattern_type, pattern_description, confidence_score, occurrence_count, last_observed_at, learned_parameters, reward_score, is_active, auto_apply, times_applied, times_accepted, times_rejected, created_at)
VALUES
(1, 1, 'berth_preference', 'Customer always requests Berth B-12 when available', 0.95, 5, NOW() - INTERVAL '5 days', '{"preferred_berth": "B-12", "section": "B", "services": ["electricity_380v", "water", "wifi"]}', 0.87, true, true, 5, 5, 0, NOW() - INTERVAL '180 days'),
(2, 2, 'duration_pattern', 'Typical stay duration is 3-4 nights', 0.88, 8, NOW() - INTERVAL '3 days', '{"avg_duration_days": 3.5, "min": 3, "max": 4}', 0.82, true, true, 8, 7, 1, NOW() - INTERVAL '150 days'),
(5, 5, 'service_preference', 'Always requests 380V electricity and premium wifi', 0.92, 6, NOW() - INTERVAL '2 days', '{"electricity": "380v", "wifi": "premium", "water": true}', 0.85, true, true, 6, 6, 0, NOW() - INTERVAL '120 days'),
(10, 10, 'timing_preference', 'Prefers morning arrivals (08:00-10:00) and evening departures', 0.89, 7, NOW() - INTERVAL '1 day', '{"arrival_time_start": "08:00", "arrival_time_end": "10:00", "departure_time": "evening"}', 0.79, true, false, 7, 5, 2, NOW() - INTERVAL '90 days'),
(15, 15, 'berth_preference', 'Prefers Section C berths near amenities', 0.83, 4, NOW() - INTERVAL '10 days', '{"preferred_section": "C", "proximity": "amenities", "side": "starboard"}', 0.75, true, false, 4, 3, 1, NOW() - INTERVAL '60 days');

-- FINAL SUMMARY
DO $$
DECLARE
    berth_count INT;
    customer_count INT;
    vessel_count INT;
    assignment_count INT;
    vhf_count INT;
    invoice_count INT;
    violation_count INT;
    permit_count INT;
    seal_count INT;
BEGIN
    SELECT COUNT(*) INTO berth_count FROM berths;
    SELECT COUNT(*) INTO customer_count FROM customers;
    SELECT COUNT(*) INTO vessel_count FROM vessels;
    SELECT COUNT(*) INTO assignment_count FROM berth_assignments WHERE status = 'active';
    SELECT COUNT(*) INTO vhf_count FROM vhf_logs;
    SELECT COUNT(*) INTO invoice_count FROM invoices;
    SELECT COUNT(*) INTO violation_count FROM violations;
    SELECT COUNT(*) INTO permit_count FROM permits;
    SELECT COUNT(*) INTO seal_count FROM seal_learning;

    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ ADA.MARINA DATABASE SEED COMPLETE';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Berths:               %', berth_count;
    RAISE NOTICE 'Customers:            %', customer_count;
    RAISE NOTICE 'Vessels:              %', vessel_count;
    RAISE NOTICE 'Active Assignments:   %', assignment_count;
    RAISE NOTICE 'VHF Logs:             %', vhf_count;
    RAISE NOTICE 'Invoices:             %', invoice_count;
    RAISE NOTICE 'Violations:           %', violation_count;
    RAISE NOTICE 'Permits:              %', permit_count;
    RAISE NOTICE 'SEAL Patterns:        %', seal_count;
    RAISE NOTICE '========================================';
    RAISE NOTICE '🚀 System ready for November 11, 2025!';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
END $$;
