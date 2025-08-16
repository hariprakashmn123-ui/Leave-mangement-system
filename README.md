# 🗂 Leave Management System (Flask + SQLite)

A simple **Leave Management System API** built using **Python (Flask)** and **SQLite**.  
It supports adding employees, applying for leave, approving/rejecting requests, and checking leave balance.

---

## 📌 Features
- Add new employees with unique email IDs.
- Employees can apply for leave with start & end dates.
- HR/Admin can approve or reject leave requests.
- Tracks leave balance for each employee.
- Input validation & error handling.
- SQLite database for data storage.

---

## 🛠 Tech Stack
- **Backend**: Python 3.x, Flask
- **Database**: SQLite
- **Tools**: Postman (for API testing)

---

## ⚙️ Project Setup

### **1. Clone the Repository**
git clone https://github.com/hariprakashmn123-ui/Leave-mangement-system


### **2. Create Virtual Environment** *(optional but recommended)*
python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows


### **3. Install Dependencies**
pip install -r requirements.txt


### **4. Initialize the Database**
python database.py

*(Creates `database.db` with Employees & LeaveRequests tables)*

### **5. Run the Application**
python app.py


The API will run at:  
`http://127.0.0.1:5000/`

## 📊 Leave Management System ER Diagram
   This ER diagram illustrates the core database structure for an efficient Leave Management System.


<img width="506" height="531" alt="image" src="https://github.com/user-attachments/assets/09f54e17-8745-42c7-b1bf-6ba16698c0f1" />


### Entities & Relationships
## Employee
   - Stores details for all employees.
   #### Fields:
      EmployeeID (PK) — unique identifier
      Name, Email, Department, JoiningDate, LeaveBalance
   #### Purpose: 
      Foundation for all leave tracking; every request and approval links back to an employee.
## LeaveRequest
      Logs individual leave applications.
   #### Fields:
       RequestID (PK) — unique request
       EmployeeID (FK) — references Employee
       LeaveType, StartDate, EndDate, Status
   #### Purpose: 
       Manages leave requests; connects to the requesting employee.
## LeaveTransaction
      Tracks actions and decision history for each leave request.
   #### Fields:
       TransactionID (PK) — unique transaction
        RequestID (FK) — references LeaveRequest
        Action, ActionDate, ApproverID (FK) — references Employee
   #### Purpose: 
        Monitors approvals and updates for each request, maintaining workflow and audit trail.
### How Relationships Work
**Employee** → **LeaveRequest**: Each Employee can submit multiple LeaveRequests.  
**LeaveRequest** → **LeaveTransaction**: Each LeaveRequest can have multiple actions (approved, rejected, modified).  
**Employee** → **LeaveTransaction** (ApproverID): Only an Employee can process or approve a leave (accountability & security).

### Design Benefits
   **Normalized**: Avoids redundant data, keeps tables focused.
   **Scalable**: Easily supports growth to many employees and leave policies.
   **Traceable**: Robust audit trail for all actions and approvals.

## Table Definitions

 ### Employees

| Column       | Type    | Key/Index    | Description                  |
|--------------|---------|--------------|------------------------------|
| id           | INTEGER | PK, auto-inc | Unique employee identifier   |
| name         | TEXT    |              | Employee name                |
| email        | TEXT    | Unique       | Employee email (must be unique) |
| department   | TEXT    |              | Employee's department        |
| joining_date | TEXT    |              | Date of joining (YYYY-MM-DD) |
| total_leaves | INTEGER |              | Total allotted leave days    |
| leaves_taken | INTEGER |              | Number of leaves taken       |


### LeaveRequests

| Column      | Type    | Key/Index         | Description             |
|-------------|---------|-------------------|-------------------------|
| id          | INTEGER | PK, auto-inc      | Unique leave request ID |
| employee_id | INTEGER | FK                | References Employees(id) |
| start_date  | TEXT    |                   | Start date of the leave  |
| end_date    | TEXT    |                   | End date of the leave    |
| reason      | TEXT    |                   | Reason for leave         |
| status      | TEXT    |                   | Pending/Approved/Rejected|
| applied_on  | TEXT    |                   | Date requested          |

---

## 📮 API Endpoints

### **1. Test Server**
**GET** `/`  
Returns:
{ "message": "Leave Management System API" }


---

### **2. Add Employee**
**POST** `/employee`
{
"name": "John Doe",
"email": "john@example.com",
"department": "IT",
"joining_date": "2025-01-10"
}

Response:
{"message": "Employee added successfully"}


---

### **3. Apply for Leave**
**POST** `/leave`

{
"employee_id": 1,
"start_date": "2025-03-10",
"end_date": "2025-03-12",
"reason": "Vacation"
}

Response:
{"message": "Leave request submitted successfully, pending approval."}


---

### **4. Approve/Reject Leave**
**PUT** `/leave/<leave_id>`
{
"status": "Approved"
}

   or

{
"status": "Rejected"
}

Response:
{"message": "Leave approved successfully."}


---

### **5. Get Leave Balance**
**GET** `/employee/<id>/balance`  
Example:
GET /employee/1/balance
Response:
{
"employee_id": 1,
"total_leaves": 20,
"leaves_taken": 5,
"remaining_leaves": 15
}



-----

## Class/Module Design

| Class/Module     | Main Methods                  | Responsibility          |
|------------------|------------------------------|-------------------------|
| EmployeeService  | add_employee, get_balance    | Manages employees       |
| LeaveService     | apply_leave, approve_leave, reject_leave | Handles leave logic |


-----

## Low-Level Design — Backend Logic (Pseudocode)

START APP

IMPORT Flask, request, jsonify IMPORT sqlite3 IMPORT init_db FROM database

INITIALIZE Flask app CALL init_db() # create tables if not exist

---------------------------------------------------------------------------------------------------------------------------

ROUTE: GET / RETURN {"message": "Leave Management System API"}

--------------------------------------------------------------------------------------------------------------------------

### ROUTE: POST /employee READ JSON body → name, email, department, joining_date


```
IF name/email/joining_date missing:
    RETURN error (400)
TRY:
    CONNECT to database
    INSERT INTO Employees(name, email, department, joining_date)
    COMMIT changes
    RETURN success (201)
EXCEPT IntegrityError:
    RETURN {"error": "Email already exists"} (400)
```

-------------------------------------------------------------------------------------------------------------------

### ROUTE: POST /leave READ JSON body → employee_id, start_date, end_date, reason
```
IF any field missing:
    RETURN error (400)

CONNECT to database
QUERY employee details (joining_date, total_leaves, leaves_taken)

IF employee not found:
    RETURN error (404)

PARSE dates (joining_date, start_date, end_date)

IF start_date > end_date:
    RETURN error (400)

IF start_date < joining_date:
    RETURN error (400)

CALCULATE leave_days = (end_date - start_date) + 1
CALCULATE remaining_leaves = total_leaves - leaves_taken

IF leave_days > remaining_leaves:
    RETURN error (400)

CHECK overlapping approved leaves for this employee
IF overlap exists:
    RETURN error (400)

INSERT leave request (status = "Pending", applied_on = today)
COMMIT changes
RETURN success (201)
```
---------------------------------------------------------------------------------------------------------------------------

### ROUTE: PUT /leave/<leave_id> READ JSON body → status ("Approved" or "Rejected")
```
IF status invalid:
    RETURN error (400)

CONNECT to database
QUERY leave request by leave_id

IF not found:
    RETURN error (404)

IF leave not in "Pending" state:
    RETURN error (400)

IF status == "Approved":
    CALCULATE leave_days = (end_date - start_date) + 1
    GET employee leave balance

    IF leave_days > remaining_leaves:
        RETURN error (400)

    UPDATE employee leaves_taken += leave_days

UPDATE LeaveRequests status = new_status
COMMIT changes
RETURN success (200)
```
--------------------------------------------------------------------------------------------------------------------------

### ROUTE: GET /employee/<employee_id>/balance CONNECT to database QUERY employee total_leaves, leaves_taken

```
IF not found:
    RETURN error (404)

CALCULATE remaining_leaves = total_leaves - leaves_taken
RETURN {employee_id, total_leaves, leaves_taken, remaining_leaves} (200)
```
-------------------------------------------------------------------------------------------------------------------------
START Flask app (debug mode)

END

## 📷 API Testing Screenshots

### 1. Add Employee
![Add Employee](screenshots/add_employee.png)

### 2. Apply for Leave
![Apply Leave](screenshots/apply_leave.png)

### 3. Approve Leave
![Approve Leave](screenshots/approve_leave.png)

### 4. Leave Balance
![Leave Balance](screenshots/leave_balance.png)



---

## ✅ Assumptions
- Each employee starts with **20 days total leave**.
- Dates are given in `YYYY-MM-DD` format.
- Weekends and holidays are **counted** in leave days (can be improved later).
- Only pending leave requests can be approved/rejected.

---

## 🔮 Possible Future Improvements
- Scalability:
  - Migrate from SQLite to PostgreSQL/MySQL for better concurrency.
  - Deploy with Docker and Kubernetes for horizontal scaling.
  - Use caching (Redis) to speed up common queries.
 
- Features:

   - Build a user-friendly frontend (web or mobile).
   - Add authentication and role-based access.
   - Support half-day and varied leave types.
   - Auto-exclude weekends and holidays from leave duration.
   - Department-specific leave policies and approvals.
   - Notifications for leave status updates via email/SMS.

- Optimizations:

   - Database indexing for faster queries.
   - Bulk import of employee and leave data.
   - Data backup and export features.
   - Analytics dashboard for HR insights.

- Deployment & Integration:

   - Continuous integration and automated tests.
   - Integration with HRMS or payroll systems.

---

## 🖼 High-Level Design
![High-Level Design](hld.png)

**Basic Flow:**
[Postman/Frontend]
|
Flask API
|
SQLite Database


---
