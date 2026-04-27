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

-- n년간의 휘발유값 데이터
CREATE TABLE fuel_price (
    date DATE PRIMARY KEY,
    regular_price FLOAT,
    premium_price FLOAT
);


-- n년간 경유 데이터
CREATE TABLE diesel_price (
    date DATE PRIMARY KEY,
    price FLOAT,
    FOREIGN KEY (date) REFERENCES fuel_price(date)
);
ALTER TABLE diesel_price
ADD UNIQUE (date);

-- n년간 전기요금 데이터
CREATE TABLE e_price (
     date DATE PRIMARY KEY,
     price FLOAT,
     FOREIGN KEY (date) REFERENCES fuel_price(date)
);
ALTER TABLE e_price
ADD UNIQUE (date);	

-- n년간 전기차 신규 등록 데이터
CREATE TABLE ev_registration_by_year (
            year    INT   PRIMARY KEY  COMMENT '연도',
            car     INT               COMMENT '전체 자동차 신규등록 대수',
            ev_car  INT   NOT NULL     COMMENT '전기차 신규등록 대수'
        );







