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

-- To be continued in next file (vessels, assignments, etc.)
-- This seed file is getting large, will create part 2
