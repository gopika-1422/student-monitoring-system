"""
Student Monitoring System with Face Recognition and Attendance
Supports both laptop camera and CCTV camera feeds
"""

import cv2
import face_recognition
import numpy as np
import sqlite3
import datetime
import os
import pickle
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
import time

class StudentMonitorSystem:
    def __init__(self):
        self.db_path = "student_monitor.db"
        self.encodings_path = "face_encodings.pkl"
        self.student_images_dir = "student_images"
        
        # Create necessary directories
        Path(self.student_images_dir).mkdir(exist_ok=True)
        
        # Initialize database
        self.init_database()
        
        # Load face encodings
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_face_encodings()
        
        # Camera settings
        self.camera = None
        self.camera_running = False
        
        # Activity detection settings
        self.activity_threshold = 5  # Movement threshold
        self.last_positions = {}  # Track last known positions
        
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_number TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                department TEXT,
                year TEXT,
                face_encoding_path TEXT,
                photo_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                date DATE NOT NULL,
                check_in_time TIME,
                check_out_time TIME,
                status TEXT DEFAULT 'Present',
                activity_level TEXT DEFAULT 'Active',
                notes TEXT,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                UNIQUE(student_id, date)
            )
        ''')
        
        # Activity logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activity_type TEXT,
                confidence REAL,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        
        # Authority users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authorities (
                authority_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'Teacher',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default admin if not exists
        cursor.execute('''
            INSERT OR IGNORE INTO authorities (username, password, full_name, role)
            VALUES ('admin', 'admin123', 'System Administrator', 'Admin')
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Database initialized successfully")
    
    def add_student(self, student_data, photo_path=None):
        """Add a new student to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO students (roll_number, name, email, phone, department, year, photo_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                student_data['roll_number'],
                student_data['name'],
                student_data.get('email', ''),
                student_data.get('phone', ''),
                student_data.get('department', ''),
                student_data.get('year', ''),
                photo_path
            ))
            
            student_id = cursor.lastrowid
            conn.commit()
            
            # Process face encoding if photo provided
            if photo_path and os.path.exists(photo_path):
                self.process_student_face(student_id, photo_path, student_data['name'])
            
            print(f"✓ Student {student_data['name']} added successfully (ID: {student_id})")
            return student_id
            
        except sqlite3.IntegrityError:
            print(f"✗ Student with roll number {student_data['roll_number']} already exists")
            return None
        finally:
            conn.close()
    
    def process_student_face(self, student_id, photo_path, student_name):
        """Process and store face encoding for a student"""
        try:
            # Load image
            image = face_recognition.load_image_file(photo_path)
            
            # Get face encoding
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) > 0:
                face_encoding = face_encodings[0]
                
                # Save encoding
                encoding_file = f"{self.student_images_dir}/encoding_{student_id}.pkl"
                with open(encoding_file, 'wb') as f:
                    pickle.dump(face_encoding, f)
                
                # Update database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE students SET face_encoding_path = ? WHERE student_id = ?
                ''', (encoding_file, student_id))
                conn.commit()
                conn.close()
                
                # Add to known faces
                self.known_face_encodings.append(face_encoding)
                self.known_face_names.append(f"{student_id}:{student_name}")
                
                print(f"✓ Face encoding processed for {student_name}")
                return True
            else:
                print(f"✗ No face detected in image for {student_name}")
                return False
                
        except Exception as e:
            print(f"✗ Error processing face: {e}")
            return False
    
    def load_face_encodings(self):
        """Load all face encodings from database"""
        self.known_face_encodings = []
        self.known_face_names = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT student_id, name, face_encoding_path 
            FROM students 
            WHERE face_encoding_path IS NOT NULL
        ''')
        
        students = cursor.fetchall()
        conn.close()
        
        for student_id, name, encoding_path in students:
            if os.path.exists(encoding_path):
                with open(encoding_path, 'rb') as f:
                    encoding = pickle.load(f)
                    self.known_face_encodings.append(encoding)
                    self.known_face_names.append(f"{student_id}:{name}")
        
        print(f"✓ Loaded {len(self.known_face_encodings)} face encodings")
    
    def mark_attendance(self, student_id, activity_level="Active"):
        """Mark attendance for a student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.date.today()
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        try:
            # Try to insert new attendance record
            cursor.execute('''
                INSERT INTO attendance (student_id, date, check_in_time, activity_level)
                VALUES (?, ?, ?, ?)
            ''', (student_id, today, current_time, activity_level))
            conn.commit()
            print(f"✓ Attendance marked for student ID {student_id} at {current_time}")
            
        except sqlite3.IntegrityError:
            # Update existing record
            cursor.execute('''
                UPDATE attendance 
                SET check_out_time = ?, activity_level = ?
                WHERE student_id = ? AND date = ?
            ''', (current_time, activity_level, student_id, today))
            conn.commit()
            
        finally:
            conn.close()
    
    def log_activity(self, student_id, activity_type, confidence):
        """Log student activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO activity_logs (student_id, activity_type, confidence)
            VALUES (?, ?, ?)
        ''', (student_id, activity_type, confidence))
        
        conn.commit()
        conn.close()
    
    def detect_activity(self, face_location, student_id):
        """Detect if student is active based on movement"""
        if student_id not in self.last_positions:
            self.last_positions[student_id] = face_location
            return "Active"
        
        last_top, last_right, last_bottom, last_left = self.last_positions[student_id]
        top, right, bottom, left = face_location
        
        # Calculate movement
        movement = abs(top - last_top) + abs(left - last_left)
        
        self.last_positions[student_id] = face_location
        
        if movement > self.activity_threshold:
            return "Active"
        else:
            return "Inactive"
    
    def start_camera(self, camera_index=0):
        """Start camera feed"""
        self.camera = cv2.VideoCapture(camera_index)
        if not self.camera.isOpened():
            print(f"✗ Cannot open camera {camera_index}")
            return False
        
        self.camera_running = True
        print(f"✓ Camera {camera_index} started")
        return True
    
    def stop_camera(self):
        """Stop camera feed"""
        self.camera_running = False
        if self.camera:
            self.camera.release()
        print("✓ Camera stopped")
    
    def process_frame(self, frame):
        """Process a single frame for face recognition and activity detection"""
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Find faces
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        face_names = []
        face_activities = []
        
        for (face_encoding, face_location) in zip(face_encodings, face_locations):
            # Compare with known faces
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
            name = "Unknown"
            student_id = None
            
            # Find best match
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    student_id = int(name.split(':')[0])
                    name = name.split(':')[1]
                    
                    # Detect activity
                    activity = self.detect_activity(face_location, student_id)
                    
                    # Mark attendance
                    self.mark_attendance(student_id, activity)
                    
                    # Log activity
                    confidence = 1 - face_distances[best_match_index]
                    self.log_activity(student_id, f"Detected_{activity}", confidence)
                    
                    face_activities.append(activity)
            
            face_names.append(name)
        
        # Scale back face locations
        face_locations = [(top*4, right*4, bottom*4, left*4) for (top, right, bottom, left) in face_locations]
        
        return frame, face_locations, face_names, face_activities


class StudentMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Monitoring System")
        self.root.geometry("1200x800")
        
        self.system = StudentMonitorSystem()
        self.current_user = None
        
        # Login screen
        self.show_login()
    
    def show_login(self):
        """Display login screen"""
        login_frame = tk.Frame(self.root, bg='#2c3e50')
        login_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(login_frame, text="Student Monitoring System", 
                font=('Arial', 24, 'bold'), bg='#2c3e50', fg='white').pack(pady=40)
        
        form_frame = tk.Frame(login_frame, bg='#34495e', padx=40, pady=40)
        form_frame.pack(pady=20)
        
        tk.Label(form_frame, text="Username:", font=('Arial', 12), 
                bg='#34495e', fg='white').grid(row=0, column=0, pady=10, sticky='e')
        username_entry = tk.Entry(form_frame, font=('Arial', 12), width=25)
        username_entry.grid(row=0, column=1, pady=10, padx=10)
        
        tk.Label(form_frame, text="Password:", font=('Arial', 12), 
                bg='#34495e', fg='white').grid(row=1, column=0, pady=10, sticky='e')
        password_entry = tk.Entry(form_frame, font=('Arial', 12), width=25, show='*')
        password_entry.grid(row=1, column=1, pady=10, padx=10)
        
        def login():
            username = username_entry.get()
            password = password_entry.get()
            
            conn = sqlite3.connect(self.system.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT authority_id, full_name, role 
                FROM authorities 
                WHERE username = ? AND password = ?
            ''', (username, password))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                self.current_user = {'id': user[0], 'name': user[1], 'role': user[2]}
                login_frame.destroy()
                self.show_main_interface()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
        
        tk.Button(form_frame, text="Login", font=('Arial', 12, 'bold'), 
                 bg='#3498db', fg='white', width=20, command=login).grid(row=2, column=0, 
                                                                         columnspan=2, pady=20)
        
        tk.Label(login_frame, text="Default: admin / admin123", 
                font=('Arial', 10), bg='#2c3e50', fg='#95a5a6').pack()
    
    def show_main_interface(self):
        """Display main interface after login"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Camera Monitoring Tab
        camera_frame = tk.Frame(notebook)
        notebook.add(camera_frame, text="📹 Live Monitoring")
        self.setup_camera_tab(camera_frame)
        
        # Student Management Tab
        students_frame = tk.Frame(notebook)
        notebook.add(students_frame, text="👥 Manage Students")
        self.setup_students_tab(students_frame)
        
        # Attendance Tab
        attendance_frame = tk.Frame(notebook)
        notebook.add(attendance_frame, text="📊 Attendance Records")
        self.setup_attendance_tab(attendance_frame)
        
        # Reports Tab
        reports_frame = tk.Frame(notebook)
        notebook.add(reports_frame, text="📈 Reports")
        self.setup_reports_tab(reports_frame)
    
    def setup_camera_tab(self, parent):
        """Setup camera monitoring interface"""
        # Controls
        control_frame = tk.Frame(parent)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        tk.Label(control_frame, text="Camera Source:", font=('Arial', 11)).pack(side=tk.LEFT, padx=5)
        
        camera_var = tk.StringVar(value="0")
        camera_combo = ttk.Combobox(control_frame, textvariable=camera_var, 
                                    values=["0 (Laptop Camera)", "1", "2", "RTSP URL"], width=20)
        camera_combo.pack(side=tk.LEFT, padx=5)
        
        self.video_label = tk.Label(parent, bg='black')
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.camera_thread = None
        self.camera_active = False
        
        def start_monitoring():
            camera_index = camera_var.get().split()[0]
            try:
                camera_index = int(camera_index)
            except:
                messagebox.showerror("Error", "Invalid camera source")
                return
            
            if self.system.start_camera(camera_index):
                self.camera_active = True
                self.camera_thread = threading.Thread(target=self.update_camera_feed, daemon=True)
                self.camera_thread.start()
                start_btn.config(state='disabled')
                stop_btn.config(state='normal')
        
        def stop_monitoring():
            self.camera_active = False
            self.system.stop_camera()
            self.video_label.config(image='', bg='black')
            start_btn.config(state='normal')
            stop_btn.config(state='disabled')
        
        start_btn = tk.Button(control_frame, text="▶ Start Monitoring", 
                             bg='#27ae60', fg='white', font=('Arial', 11, 'bold'), 
                             command=start_monitoring)
        start_btn.pack(side=tk.LEFT, padx=5)
        
        stop_btn = tk.Button(control_frame, text="⏹ Stop", 
                            bg='#e74c3c', fg='white', font=('Arial', 11, 'bold'), 
                            command=stop_monitoring, state='disabled')
        stop_btn.pack(side=tk.LEFT, padx=5)
    
    def update_camera_feed(self):
        """Update camera feed in GUI"""
        while self.camera_active and self.system.camera_running:
            ret, frame = self.system.camera.read()
            if ret:
                # Process frame
                processed_frame, face_locations, face_names, face_activities = self.system.process_frame(frame)
                
                # Draw rectangles and labels
                for (top, right, bottom, left), name, activity in zip(face_locations, face_names, face_activities):
                    # Draw box
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(processed_frame, (left, top), (right, bottom), color, 2)
                    
                    # Draw label background
                    cv2.rectangle(processed_frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                    
                    # Draw text
                    font = cv2.FONT_HERSHEY_DUPLEX
                    text = f"{name} - {activity}" if name != "Unknown" else "Unknown"
                    cv2.putText(processed_frame, text, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
                
                # Convert to PhotoImage
                cv2image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                
                # Resize to fit
                img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=img)
                
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
            
            time.sleep(0.033)  # ~30 FPS
    
    def setup_students_tab(self, parent):
        """Setup student management interface"""
        # Add student form
        form_frame = tk.LabelFrame(parent, text="Add New Student", font=('Arial', 12, 'bold'))
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        fields = ['Roll Number', 'Name', 'Email', 'Phone', 'Department', 'Year']
        entries = {}
        
        for i, field in enumerate(fields):
            tk.Label(form_frame, text=f"{field}:", font=('Arial', 10)).grid(row=i//2, column=(i%2)*2, 
                                                                            padx=10, pady=5, sticky='e')
            entry = tk.Entry(form_frame, font=('Arial', 10), width=25)
            entry.grid(row=i//2, column=(i%2)*2+1, padx=10, pady=5)
            entries[field.lower().replace(' ', '_')] = entry
        
        photo_path_var = tk.StringVar()
        
        def browse_photo():
            filename = filedialog.askopenfilename(
                title="Select Student Photo",
                filetypes=[("Image files", "*.jpg *.jpeg *.png")]
            )
            if filename:
                photo_path_var.set(filename)
        
        tk.Button(form_frame, text="📷 Select Photo", command=browse_photo).grid(row=3, column=0, padx=10, pady=10)
        tk.Label(form_frame, textvariable=photo_path_var, fg='blue').grid(row=3, column=1, columnspan=3, sticky='w')
        
        def add_student():
            student_data = {key: entry.get() for key, entry in entries.items()}
            
            if not student_data['roll_number'] or not student_data['name']:
                messagebox.showerror("Error", "Roll Number and Name are required!")
                return
            
            photo_path = photo_path_var.get() if photo_path_var.get() else None
            
            student_id = self.system.add_student(student_data, photo_path)
            
            if student_id:
                messagebox.showinfo("Success", f"Student added successfully! ID: {student_id}")
                for entry in entries.values():
                    entry.delete(0, tk.END)
                photo_path_var.set("")
                self.refresh_student_list()
            else:
                messagebox.showerror("Error", "Failed to add student. Roll number may already exist.")
        
        tk.Button(form_frame, text="➕ Add Student", bg='#3498db', fg='white', 
                 font=('Arial', 11, 'bold'), command=add_student).grid(row=4, column=0, 
                                                                       columnspan=4, pady=10)
        
        # Student list
        list_frame = tk.LabelFrame(parent, text="Registered Students", font=('Arial', 12, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('ID', 'Roll Number', 'Name', 'Department', 'Year', 'Face Registered')
        self.student_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.student_tree.yview)
        self.student_tree.configure(yscroll=scrollbar.set)
        
        self.student_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_student_list()
    
    def refresh_student_list(self):
        """Refresh the student list"""
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        conn = sqlite3.connect(self.system.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT student_id, roll_number, name, department, year, face_encoding_path
            FROM students
        ''')
        
        students = cursor.fetchall()
        conn.close()
        
        for student in students:
            face_status = "✓ Yes" if student[5] else "✗ No"
            self.student_tree.insert('', tk.END, values=(
                student[0], student[1], student[2], student[3], student[4], face_status
            ))
    
    def setup_attendance_tab(self, parent):
        """Setup attendance records interface"""
        control_frame = tk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(control_frame, text="Date:", font=('Arial', 11)).pack(side=tk.LEFT, padx=5)
        
        date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(control_frame, textvariable=date_var, font=('Arial', 11), width=15)
        date_entry.pack(side=tk.LEFT, padx=5)
        
        def load_attendance():
            self.refresh_attendance_list(date_var.get())
        
        tk.Button(control_frame, text="🔍 Load Attendance", bg='#3498db', fg='white',
                 font=('Arial', 10, 'bold'), command=load_attendance).pack(side=tk.LEFT, padx=5)
        
        # Attendance list
        list_frame = tk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('Student ID', 'Name', 'Roll Number', 'Check In', 'Check Out', 'Status', 'Activity')
        self.attendance_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.attendance_tree.heading(col, text=col)
            self.attendance_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscroll=scrollbar.set)
        
        self.attendance_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_attendance_list(date_var.get())
    
    def refresh_attendance_list(self, date):
        """Refresh the attendance list for a specific date"""
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        conn = sqlite3.connect(self.system.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.student_id, s.name, s.roll_number, 
                   a.check_in_time, a.check_out_time, a.status, a.activity_level
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.date = ?
            ORDER BY a.check_in_time
        ''', (date,))
        
        records = cursor.fetchall()
        conn.close()
        
        for record in records:
            self.attendance_tree.insert('', tk.END, values=record)
    
    def setup_reports_tab(self, parent):
        """Setup reports interface"""
        tk.Label(parent, text="📈 Attendance Reports & Analytics", 
                font=('Arial', 16, 'bold')).pack(pady=20)
        
        stats_frame = tk.Frame(parent)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        def generate_report():
            conn = sqlite3.connect(self.system.db_path)
            cursor = conn.cursor()
            
            # Total students
            cursor.execute("SELECT COUNT(*) FROM students")
            total_students = cursor.fetchone()[0]
            
            # Today's attendance
            today = datetime.date.today()
            cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = ?", (today,))
            today_present = cursor.fetchone()[0]
            
            # This week's average
            week_ago = today - datetime.timedelta(days=7)
            cursor.execute('''
                SELECT AVG(daily_count) FROM (
                    SELECT COUNT(*) as daily_count 
                    FROM attendance 
                    WHERE date >= ? AND date <= ?
                    GROUP BY date
                )
            ''', (week_ago, today))
            
            week_avg = cursor.fetchone()[0] or 0
            
            conn.close()
            
            report_text = f"""
            📊 ATTENDANCE STATISTICS
            ═══════════════════════════════════
            
            Total Registered Students: {total_students}
            
            Today's Attendance: {today_present} students
            Attendance Rate: {(today_present/total_students*100 if total_students > 0 else 0):.1f}%
            
            7-Day Average: {week_avg:.1f} students/day
            
            Date: {today.strftime("%A, %B %d, %Y")}
            """
            
            report_label.config(text=report_text)
        
        report_label = tk.Label(stats_frame, text="Click 'Generate Report' to view statistics", 
                               font=('Courier', 12), justify=tk.LEFT, bg='#ecf0f1', 
                               relief=tk.SUNKEN, padx=20, pady=20)
        report_label.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(parent, text="📊 Generate Report", bg='#27ae60', fg='white',
                 font=('Arial', 12, 'bold'), command=generate_report).pack(pady=10)


def main():
    root = tk.Tk()
    app = StudentMonitorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
