-- Run once as your existing MySQL administrator, never through the Python app.
CREATE DATABASE IF NOT EXISTS nl_sql_demo CHARACTER SET utf8mb4;
USE nl_sql_demo;
CREATE TABLE IF NOT EXISTS employees (
 employee_id INT PRIMARY KEY,
 employee_name VARCHAR(100) NOT NULL,
 department VARCHAR(50) NOT NULL,
 salary DECIMAL(10,2) NOT NULL,
 joining_date DATE NOT NULL
);
INSERT IGNORE INTO employees VALUES
(1,'Aarav Sharma','IT',65000,'2023-01-10'),
(2,'Priya Deshmukh','HR',42000,'2023-03-15'),
(3,'Rahul Patil','Sales',55000,'2022-07-01'),
(4,'Sneha Joshi','IT',80000,'2021-11-20'),
(5,'Amit Verma','Finance',48000,'2024-02-05'),
(6,'Neha Kulkarni','HR',52000,'2022-09-12'),
(7,'Rohan Shah','Sales',39000,'2024-06-17'),
(8,'Isha Mehta','Finance',72000,'2021-05-03'),
(9,'Kunal Pawar','IT',50000,'2025-01-08'),
(10,'Ananya Rao','Marketing',60000,'2023-08-21');

-- Replace this password before running. This must be a NEW dedicated account.
-- CREATE USER intentionally fails if it already exists: inspect its grants first.
CREATE USER 'nl_sql_reader'@'localhost' IDENTIFIED BY 'Choose_A_Strong_Password_123!';
GRANT SELECT ON nl_sql_demo.employees TO 'nl_sql_reader'@'localhost';
SHOW GRANTS FOR 'nl_sql_reader'@'localhost';
