-- Use the database
USE reporting_db;

-- Create tables
CREATE TABLE tasks (
    task_id VARCHAR(10) PRIMARY KEY,
    task_name VARCHAR(255) NOT NULL,
    assigned_to VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    due_date DATE,
    project_id VARCHAR(10)
);

CREATE TABLE leads (
    lead_id VARCHAR(10) PRIMARY KEY,
    lead_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    assigned_to VARCHAR(100) NOT NULL,
    created_date DATE
);

CREATE TABLE projects (
    project_id VARCHAR(10) PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    start_date DATE,
    end_date DATE
);

CREATE TABLE timesheets (
    timesheet_id VARCHAR(10) PRIMARY KEY,
    employee_name VARCHAR(100) NOT NULL,
    task_id VARCHAR(10),
    hours DECIMAL(5,2),
    date DATE
);

-- Insert dummy data into projects
INSERT INTO projects (project_id, project_name, status, start_date, end_date) VALUES
('P-101', 'Website Redesign', 'Active', '2024-01-15', '2024-06-30'),
('P-102', 'Mobile App Development', 'In Progress', '2024-02-01', '2024-08-15'),
('P-103', 'Marketing Campaign', 'Completed', '2024-01-01', '2024-03-31'),
('P-104', 'Product Launch', 'Planning', '2024-05-01', '2024-11-30');

-- Insert dummy data into tasks
INSERT INTO tasks (task_id, task_name, assigned_to, status, due_date, project_id) VALUES
('T-101', 'Design Homepage', 'Humam Ahmed', 'Pending', '2024-04-15', 'P-101'),
('T-102', 'Develop API endpoints', 'M Humam', 'In Progress', '2024-04-20', 'P-102'),
('T-103', 'Client Meeting', 'Jane Smith', 'Completed', '2024-04-10', 'P-101'),
('T-104', 'Write documentation', 'Humam Khan', 'Pending', '2024-04-25', 'P-102'),
('T-105', 'Testing phase 1', 'John Doe', 'In Progress', '2024-04-18', 'P-102'),
('T-106', 'Social media campaign', 'Humam XYZ', 'Pending', '2024-04-30', 'P-103'),
('T-107', 'Budget planning', 'Alice Johnson', 'Completed', '2024-04-05', 'P-104');

-- Insert dummy data into leads
INSERT INTO leads (lead_id, lead_name, status, assigned_to, created_date) VALUES
('L-201', 'ABC Corporation', 'Contacted', 'Humam Ahmed', '2024-03-15'),
('L-202', 'XYZ Enterprises', 'Qualified', 'Jane Smith', '2024-04-01'),
('L-203', 'Tech Solutions Inc', 'New', 'M Humam', '2024-04-10'),
('L-204', 'Global Services', 'Contacted', 'John Doe', '2024-03-28'),
('L-205', 'Innovate Labs', 'Qualified', 'Humam Khan', '2024-04-05');

-- Insert dummy data into timesheets
INSERT INTO timesheets (timesheet_id, employee_name, task_id, hours, date) VALUES
('TS-301', 'Humam Ahmed', 'T-101', 5.5, '2024-04-01'),
('TS-302', 'M Humam', 'T-102', 7.0, '2024-04-02'),
('TS-303', 'Jane Smith', 'T-103', 3.5, '2024-04-01'),
('TS-304', 'Humam Khan', 'T-104', 6.0, '2024-04-03'),
('TS-305', 'John Doe', 'T-105', 8.0, '2024-04-02'),
('TS-306', 'Humam XYZ', 'T-106', 4.5, '2024-04-03'),
('TS-307', 'Humam Ahmed', 'T-101', 6.5, '2024-04-04');
