create database vehicle_db;

use vehicle_db;

-- 2015 2025 전기차 등록 테이블
CREATE TABLE electric_vehicle_count (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year INT,
    month INT,
    region VARCHAR(50),
    count INT
);
ALTER TABLE electric_vehicle_count
ADD UNIQUE KEY unique_data (year, month, region);

-- 2015 2025 총 자동차 등록 테이블
CREATE TABLE car_total (
    year INT PRIMARY KEY,
    total BIGINT
);

-- 2020 2025년 전기차 충전소 현황
CREATE TABLE ev_charger (
    id INT AUTO_INCREMENT PRIMARY KEY,
    month VARCHAR(20),
    speed VARCHAR(20),
    region VARCHAR(20),
    count INT
);
ALTER TABLE ev_charger
ADD UNIQUE KEY unique_ev (month, speed, region);

-- n년간의 기름값 데이터
CREATE TABLE fuel_price (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    week INT,
    premium FLOAT,
    regular FLOAT
);
ALTER TABLE fuel_price
ADD UNIQUE KEY unique_fuel (date, week);

select * from fuel_price;

