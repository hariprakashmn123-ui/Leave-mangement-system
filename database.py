import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Create Employees table
    c.execute('''
    CREATE TABLE IF NOT EXISTS Employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        department TEXT,
        joining_date DATE,
        total_leaves INTEGER DEFAULT 20,
        leaves_taken INTEGER DEFAULT 0
    )''')

    # Create LeaveRequests table
    c.execute('''
    CREATE TABLE IF NOT EXISTS LeaveRequests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        start_date DATE,
        end_date DATE,
        reason TEXT,
        status TEXT DEFAULT 'Pending',
        applied_on DATE,
        FOREIGN KEY(employee_id) REFERENCES Employees(id)
    )''')

    conn.commit()
    conn.close()

# Call on startup
if __name__ == "__main__":
    init_db()
    print("Database initialized.")
