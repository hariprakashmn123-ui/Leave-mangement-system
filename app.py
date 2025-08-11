from flask import Flask, request, jsonify
import sqlite3
from database import init_db

app = Flask(__name__)
init_db()  # Initialize DB tables at startup

@app.route('/')
def home():
    return {"message": "Leave Management System API"}

# Add Employee API
@app.route('/employee', methods=['POST'])
def add_employee():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    department = data.get("department")
    joining_date = data.get("joining_date")

    # Basic validation
    if not name or not email or not joining_date:
        return jsonify({"error": "Name, email, and joining_date are required"}), 400

    try:
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO Employees (name, email, department, joining_date)
            VALUES (?, ?, ?, ?)
        """, (name, email, department, joining_date))
        conn.commit()
        conn.close()
        return jsonify({"message": "Employee added successfully"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400

@app.route('/leave', methods=['POST'])
def apply_leave():
    data = request.get_json()

    employee_id = data.get("employee_id")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    reason = data.get("reason")

    # Basic validation
    if not all([employee_id, start_date, end_date, reason]):
        return jsonify({"error": "employee_id, start_date, end_date, and reason are required."}), 400

    try:
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # 1. Check if employee exists
        c.execute("SELECT joining_date, total_leaves, leaves_taken FROM Employees WHERE id=?", (employee_id,))
        emp = c.fetchone()
        if not emp:
            return jsonify({"error": "Employee not found."}), 404
        
        joining_date_str, total_leaves, leaves_taken = emp

        # Validate date formats and order
        from datetime import datetime, timedelta

        try:
            join_date = datetime.strptime(joining_date_str, "%Y-%m-%d").date()
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Dates must be in 'YYYY-MM-DD' format."}), 400

        if start > end:
            return jsonify({"error": "End date must be on or after start date."}), 400

        # Check that leave request is not before joining date
        if start < join_date:
            return jsonify({"error": "Leave start date cannot be before joining date."}), 400

        # Calculate requested leave days (simple days count, excluding weekends/holidays as future improvement)
        leave_days = (end - start).days + 1

        remaining_leaves = total_leaves - leaves_taken
        if leave_days > remaining_leaves:
            return jsonify({"error": f"Insufficient leave balance. You have {remaining_leaves} days available."}), 400

        # Check for overlapping leave requests for this employee
        c.execute("""
            SELECT * FROM LeaveRequests 
            WHERE employee_id=? AND status='Approved' 
            AND NOT (end_date < ? OR start_date > ?)
        """, (employee_id, start_date, end_date))
        overlap = c.fetchone()
        if overlap:
            return jsonify({"error": "You have an overlapping approved leave request."}), 400

        # All checks passed, insert leave request with status Pending
        today_str = datetime.today().strftime("%Y-%m-%d")
        c.execute("""
            INSERT INTO LeaveRequests 
            (employee_id, start_date, end_date, reason, status, applied_on) 
            VALUES (?, ?, ?, ?, 'Pending', ?)
        """, (employee_id, start_date, end_date, reason, today_str))

        conn.commit()
        conn.close()
        return jsonify({"message": "Leave request submitted successfully, pending approval."}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/leave/<int:leave_id>', methods=['PUT'])
def update_leave_status(leave_id):
    data = request.get_json()
    status = data.get("status")  # Expected: "Approved" or "Rejected"

    if status not in ["Approved", "Rejected"]:
        return jsonify({"error": "Status must be 'Approved' or 'Rejected'."}), 400

    try:
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # 1. Check if leave request exists and is pending
        c.execute("""
            SELECT employee_id, start_date, end_date, status
            FROM LeaveRequests
            WHERE id=?
        """, (leave_id,))
        leave = c.fetchone()

        if not leave:
            return jsonify({"error": "Leave request not found."}), 404

        employee_id, start_date, end_date, current_status = leave

        if current_status != "Pending":
            return jsonify({"error": f"Leave already {current_status}."}), 400

        # If approving → deduct from balance
        if status == "Approved":
            from datetime import datetime
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            leave_days = (end - start).days + 1

            # Get current balance
            c.execute("SELECT total_leaves, leaves_taken FROM Employees WHERE id=?", (employee_id,))
            emp = c.fetchone()
            if emp:
                total_leaves, leaves_taken = emp
                remaining_leaves = total_leaves - leaves_taken

                if leave_days > remaining_leaves:
                    return jsonify({"error": "Insufficient leave balance for approval."}), 400

                # Deduct leave days
                c.execute("""
                    UPDATE Employees
                    SET leaves_taken = leaves_taken + ?
                    WHERE id=?
                """, (leave_days, employee_id))

        # Update leave request status
        c.execute("UPDATE LeaveRequests SET status=? WHERE id=?", (status, leave_id))

        conn.commit()
        conn.close()

        return jsonify({"message": f"Leave {status.lower()} successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/employee/<int:employee_id>/balance', methods=['GET'])
def get_leave_balance(employee_id):
    try:
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("SELECT total_leaves, leaves_taken FROM Employees WHERE id=?", (employee_id,))
        emp = c.fetchone()
        if not emp:
            return jsonify({"error": "Employee not found."}), 404

        total_leaves, leaves_taken = emp
        remaining_leaves = total_leaves - leaves_taken

        conn.close()
        return jsonify({
            "employee_id": employee_id,
            "total_leaves": total_leaves,
            "leaves_taken": leaves_taken,
            "remaining_leaves": remaining_leaves
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
