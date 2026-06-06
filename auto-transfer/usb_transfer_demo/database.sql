-- =========================================
-- CREATE DATABASE
-- =========================================
CREATE DATABASE IF NOT EXISTS usb_transfer_system;

USE usb_transfer_system;

-- =========================================
-- 1. ROUTING TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS routing (
    filename VARCHAR(255) PRIMARY KEY,
    destination VARCHAR(100) NOT NULL
);

-- =========================================
-- INSERT FILE ROUTES
-- =========================================
INSERT INTO routing (filename, destination)
VALUES
    ('01b8c65d-9312-4a5a-a4a5-99f7904459fc.docx', 'SystemA'),
    ('cbe3924e-7392-4284-8c79-6169b47107dc.docx', 'SystemB'),
    ('3a4b6f5a-b2a7-4e72-94ed-5dbaffd6340a.docx', 'SystemA');

-- =========================================
-- 2. TRANSFER LOG TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS transfer_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    filename VARCHAR(255) NOT NULL,
    source_system VARCHAR(100) NOT NULL,
    destination_system VARCHAR(100) NOT NULL,
    transfer_status VARCHAR(50) NOT NULL,
    transfer_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================
-- 3. TRANSFER PROGRESS TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS transfer_progress (
    filename VARCHAR(255) PRIMARY KEY,
    bytes_completed BIGINT DEFAULT 0,
    total_bytes BIGINT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'IN_PROGRESS'
);

-- =========================================
-- 4. USB DEVICES TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS usb_devices (
    usb_id VARCHAR(50) PRIMARY KEY,
    plugged_into VARCHAR(100),
    usb_status VARCHAR(50)
);

-- =========================================
-- INSERT DEFAULT USB DEVICE
-- =========================================
INSERT INTO usb_devices (
    usb_id,
    plugged_into,
    usb_status
)
VALUES (
    'USB1',
    NULL,
    'IDLE'
);

-- =========================================
-- 5. SYSTEM STATUS TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS systems (
    system_name VARCHAR(100) PRIMARY KEY,
    power_state VARCHAR(20) NOT NULL
);

-- =========================================
-- INSERT SYSTEMS
-- =========================================
INSERT INTO systems (
    system_name,
    power_state
)
VALUES
    ('Sender', 'ON'),
    ('SystemA', 'OFF'),
    ('SystemB', 'OFF');