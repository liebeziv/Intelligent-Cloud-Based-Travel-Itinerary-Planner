-- Travel Planner Database Initialization

CREATE DATABASE IF NOT EXISTS travelplanner;
USE travelplanner;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    preferences JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Attractions table
CREATE TABLE IF NOT EXISTS attractions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    location JSON,
    rating DECIMAL(3,2) DEFAULT 0.00,
    price_range VARCHAR(50) DEFAULT 'medium',
    opening_hours JSON,
    contact_info JSON,
    images JSON,
    features JSON,
    weather_dependent VARCHAR(20) DEFAULT 'no',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert sample attractions
INSERT IGNORE INTO attractions (name, description, category, location, rating, price_range, features) VALUES
('Milford Sound', 'Famous fiord in Fiordland National Park', 'nature', '{"lat": -44.6731, "lng": 167.9261, "city": "Fiordland"}', 4.8, 'high', '["scenic", "cruise", "wildlife"]'),
('Queenstown Skyline Gondola', 'Scenic gondola ride with panoramic views', 'adventure', '{"lat": -45.0312, "lng": 168.6626, "city": "Queenstown"}', 4.6, 'medium', '["scenic", "family_friendly"]'),
('Bay of Islands', 'Beautiful bay with 144 islands', 'nature', '{"lat": -35.2081, "lng": 174.1158, "city": "Paihia"}', 4.5, 'medium', '["water_sports", "wildlife"]');
