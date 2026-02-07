"""
Database Management Utility
Manage students, attendance, and authorities
"""

import sqlite3
import datetime
from tabulate import tabulate

DB_PATH = "student_monitor.db"


def connect_db():
    """Connect to database"""
    return sqlite3.connect(DB_PATH)


def view_all_students():
    """Display all registered students"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT student_id, roll_number, name, email, phone, department, year,
               CASE WHEN face_encoding_path IS NOT NULL THEN 'Yes' ELSE 'No' END as face_registered
        FROM students
    ''')
    
    students = cursor.fetchall()
    conn.close()
    
    if students:
        headers = ['ID', 'Roll No', 'Name', 'Email', 'Phone', 'Department', 'Year', 'Face Registered']
        print("\n" + "="*100)
        print("ALL REGISTERED STUDENTS")
        print("="*100)
        print(tabulate(students, headers=headers, tablefmt='grid'))
        print(f"\nTotal Students: {len(students)}")
    else:
        print("\n⚠️  No students registered yet")


def view_attendance(date=None):
    """View attendance for a specific date"""
    if date is None:
        date = datetime.date.today()
    
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.student_id, s.roll_number, s.name, 
               a.check_in_time, a.check_out_time, a.status, a.activity_level
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        WHERE a.date = ?
        ORDER BY a.check_in_time
    ''', (date,))
    
    records = cursor.fetchall()
    conn.close()
    
    if records:
        headers = ['ID', 'Roll No', 'Name', 'Check In', 'Check Out', 'Status', 'Activity']
        print("\n" + "="*100)
        print(f"ATTENDANCE REPORT - {date}")
        print("="*100)
        print(tabulate(records, headers=headers, tablefmt='grid'))
        print(f"\nTotal Present: {len(records)}")
    else:
        print(f"\n⚠️  No attendance records for {date}")


def view_student_attendance_history(roll_number):
    """View attendance history for a specific student"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Get student info
    cursor.execute('SELECT student_id, name FROM students WHERE roll_number = ?', (roll_number,))
    student = cursor.fetchone()
    
    if not student:
        print(f"\n✗ Student with roll number {roll_number} not found")
        conn.close()
        return
    
    student_id, name = student
    
    # Get attendance history
    cursor.execute('''
        SELECT date, check_in_time, check_out_time, status, activity_level
        FROM attendance
        WHERE student_id = ?
        ORDER BY date DESC
        LIMIT 30
    ''', (student_id,))
    
    records = cursor.fetchall()
    conn.close()
    
    if records:
        headers = ['Date', 'Check In', 'Check Out', 'Status', 'Activity']
        print("\n" + "="*80)
        print(f"ATTENDANCE HISTORY - {name} ({roll_number})")
        print("="*80)
        print(tabulate(records, headers=headers, tablefmt='grid'))
        print(f"\nTotal Days Present: {len(records)}")
    else:
        print(f"\n⚠️  No attendance records for {name}")


def add_authority():
    """Add a new authority user"""
    print("\n" + "="*60)
    print("ADD NEW AUTHORITY USER")
    print("="*60)
    
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    full_name = input("Full Name: ").strip()
    role = input("Role (Admin/Teacher/Staff): ").strip() or "Teacher"
    
    if not username or not password:
        print("✗ Username and password are required!")
        return
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO authorities (username, password, full_name, role)
            VALUES (?, ?, ?, ?)
        ''', (username, password, full_name, role))
        conn.commit()
        print(f"\n✓ Authority user '{username}' added successfully!")
    except sqlite3.IntegrityError:
        print(f"\n✗ Username '{username}' already exists!")
    finally:
        conn.close()


def view_authorities():
    """Display all authority users"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT authority_id, username, full_name, role, created_at
        FROM authorities
    ''')
    
    authorities = cursor.fetchall()
    conn.close()
    
    if authorities:
        headers = ['ID', 'Username', 'Full Name', 'Role', 'Created At']
        print("\n" + "="*80)
        print("AUTHORITY USERS")
        print("="*80)
        print(tabulate(authorities, headers=headers, tablefmt='grid'))
        print(f"\nTotal Users: {len(authorities)}")
    else:
        print("\n⚠️  No authority users found")


def generate_statistics():
    """Generate overall statistics"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Total students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]
    
    # Students with face registered
    cursor.execute("SELECT COUNT(*) FROM students WHERE face_encoding_path IS NOT NULL")
    face_registered = cursor.fetchone()[0]
    
    # Today's attendance
    today = datetime.date.today()
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = ?", (today,))
    today_present = cursor.fetchone()[0]
    
    # This week's attendance
    week_ago = today - datetime.timedelta(days=7)
    cursor.execute('''
        SELECT date, COUNT(*) as count
        FROM attendance
        WHERE date >= ? AND date <= ?
        GROUP BY date
        ORDER BY date DESC
    ''', (week_ago, today))
    
    week_data = cursor.fetchall()
    
    # Most active students (last 7 days)
    cursor.execute('''
        SELECT s.roll_number, s.name, COUNT(*) as days_present
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        WHERE a.date >= ? AND a.date <= ?
        GROUP BY s.student_id
        ORDER BY days_present DESC
        LIMIT 5
    ''', (week_ago, today))
    
    top_students = cursor.fetchall()
    
    conn.close()
    
    print("\n" + "="*80)
    print("SYSTEM STATISTICS")
    print("="*80)
    print(f"\n📊 OVERVIEW:")
    print(f"   Total Students: {total_students}")
    print(f"   Face Registered: {face_registered} ({face_registered/total_students*100 if total_students > 0 else 0:.1f}%)")
    print(f"\n📅 TODAY ({today}):")
    print(f"   Present: {today_present}")
    print(f"   Attendance Rate: {today_present/total_students*100 if total_students > 0 else 0:.1f}%")
    
    if week_data:
        print(f"\n📈 LAST 7 DAYS:")
        for date, count in week_data:
            rate = count/total_students*100 if total_students > 0 else 0
            print(f"   {date}: {count} students ({rate:.1f}%)")
    
    if top_students:
        print(f"\n🏆 TOP ATTENDEES (Last 7 Days):")
        for roll, name, days in top_students:
            print(f"   {roll} - {name}: {days} days")
    
    print("\n" + "="*80)


def delete_student(roll_number):
    """Delete a student (use with caution)"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Check if student exists
    cursor.execute('SELECT student_id, name FROM students WHERE roll_number = ?', (roll_number,))
    student = cursor.fetchone()
    
    if not student:
        print(f"\n✗ Student with roll number {roll_number} not found")
        conn.close()
        return
    
    student_id, name = student
    
    confirm = input(f"\n⚠️  Are you sure you want to delete {name} ({roll_number})? (yes/no): ")
    
    if confirm.lower() == 'yes':
        # Delete from all tables
        cursor.execute('DELETE FROM activity_logs WHERE student_id = ?', (student_id,))
        cursor.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
        cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
        conn.commit()
        print(f"\n✓ Student {name} deleted successfully")
    else:
        print("\n✗ Deletion cancelled")
    
    conn.close()


def main_menu():
    """Display main menu"""
    while True:
        print("\n" + "="*60)
        print("STUDENT MONITORING SYSTEM - DATABASE MANAGER")
        print("="*60)
        print("\n1.  View All Students")
        print("2.  View Today's Attendance")
        print("3.  View Attendance by Date")
        print("4.  View Student Attendance History")
        print("5.  Add Authority User")
        print("6.  View Authority Users")
        print("7.  Generate Statistics")
        print("8.  Delete Student")
        print("9.  Exit")
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == '1':
            view_all_students()
        elif choice == '2':
            view_attendance()
        elif choice == '3':
            date_str = input("Enter date (YYYY-MM-DD): ").strip()
            try:
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                view_attendance(date)
            except ValueError:
                print("✗ Invalid date format!")
        elif choice == '4':
            roll = input("Enter student roll number: ").strip()
            view_student_attendance_history(roll)
        elif choice == '5':
            add_authority()
        elif choice == '6':
            view_authorities()
        elif choice == '7':
            generate_statistics()
        elif choice == '8':
            roll = input("Enter student roll number to delete: ").strip()
            delete_student(roll)
        elif choice == '9':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n✗ Invalid choice! Please try again.")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
