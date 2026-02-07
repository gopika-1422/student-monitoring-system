"""
Student Monitoring System - Launcher
Simple menu to access all tools
"""

import os
import sys
import subprocess

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print header"""
    print("=" * 70)
    print(" " * 15 + "STUDENT MONITORING SYSTEM")
    print("=" * 70)
    print()

def main_menu():
    """Display main menu"""
    while True:
        clear_screen()
        print_header()
        
        print("📋 MAIN MENU\n")
        print("1. 🎥 Launch Monitoring Application (GUI)")
        print("2. 📹 Test Camera Connection")
        print("3. 💾 Database Manager")
        print("4. 📖 View Quick Start Guide")
        print("5. 📚 View Full Documentation")
        print("6. ℹ️  System Information")
        print("7. ❌ Exit")
        print()
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == '1':
            print("\n🚀 Launching Student Monitoring Application...")
            print("Please wait...\n")
            try:
                subprocess.run([sys.executable, "student_monitor_app.py"])
            except FileNotFoundError:
                print("❌ Error: student_monitor_app.py not found!")
                input("\nPress Enter to continue...")
        
        elif choice == '2':
            print("\n📹 Launching Camera Test Tool...")
            print("Please wait...\n")
            try:
                subprocess.run([sys.executable, "test_camera.py"])
            except FileNotFoundError:
                print("❌ Error: test_camera.py not found!")
                input("\nPress Enter to continue...")
        
        elif choice == '3':
            print("\n💾 Launching Database Manager...")
            print("Please wait...\n")
            try:
                subprocess.run([sys.executable, "db_manager.py"])
            except FileNotFoundError:
                print("❌ Error: db_manager.py not found!")
                input("\nPress Enter to continue...")
        
        elif choice == '4':
            if os.path.exists("QUICKSTART.md"):
                with open("QUICKSTART.md", 'r', encoding='utf-8') as f:
                    content = f.read()
                print("\n" + content)
                input("\n\nPress Enter to continue...")
            else:
                print("❌ QUICKSTART.md not found!")
                input("\nPress Enter to continue...")
        
        elif choice == '5':
            if os.path.exists("README.md"):
                with open("README.md", 'r', encoding='utf-8') as f:
                    content = f.read()
                print("\n" + content)
                input("\n\nPress Enter to continue...")
            else:
                print("❌ README.md not found!")
                input("\nPress Enter to continue...")
        
        elif choice == '6':
            show_system_info()
            input("\nPress Enter to continue...")
        
        elif choice == '7':
            clear_screen()
            print("\n👋 Thank you for using Student Monitoring System!")
            print("Goodbye!\n")
            break
        
        else:
            print("\n❌ Invalid choice! Please enter 1-7.")
            input("\nPress Enter to continue...")

def show_system_info():
    """Display system information"""
    clear_screen()
    print_header()
    
    print("ℹ️  SYSTEM INFORMATION\n")
    
    # Python version
    print(f"Python Version: {sys.version.split()[0]}")
    
    # Check dependencies
    print("\n📦 Installed Packages:")
    
    packages = [
        'opencv-python',
        'face-recognition',
        'numpy',
        'Pillow',
        'dlib',
        'tabulate'
    ]
    
    for package in packages:
        try:
            __import__(package.replace('-', '_').split('[')[0])
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (NOT INSTALLED)")
    
    # Check files
    print("\n📁 Project Files:")
    
    files = [
        'student_monitor_app.py',
        'test_camera.py',
        'db_manager.py',
        'requirements.txt',
        'README.md',
        'QUICKSTART.md'
    ]
    
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024
            print(f"  ✅ {file} ({size:.1f} KB)")
        else:
            print(f"  ❌ {file} (NOT FOUND)")
    
    # Check database
    print("\n💾 Database:")
    
    if os.path.exists('student_monitor.db'):
        size = os.path.getsize('student_monitor.db') / 1024
        print(f"  ✅ student_monitor.db ({size:.1f} KB)")
        
        # Quick stats
        import sqlite3
        try:
            conn = sqlite3.connect('student_monitor.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM students")
            student_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM authorities")
            auth_count = cursor.fetchone()[0]
            
            import datetime
            today = datetime.date.today()
            cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = ?", (today,))
            today_attendance = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"\n  📊 Database Statistics:")
            print(f"     • Total Students: {student_count}")
            print(f"     • Authority Users: {auth_count}")
            print(f"     • Today's Attendance: {today_attendance}")
            
        except Exception as e:
            print(f"  ⚠️  Could not read database stats: {e}")
    else:
        print(f"  ℹ️  student_monitor.db (will be created on first run)")
    
    print("\n" + "=" * 70)

def check_first_run():
    """Check if this is the first run"""
    if not os.path.exists('student_monitor.db'):
        clear_screen()
        print_header()
        print("👋 Welcome to Student Monitoring System!\n")
        print("This appears to be your first time running the system.\n")
        print("🔧 Setup Instructions:\n")
        print("1. First, ensure all dependencies are installed:")
        print("   • Run install_windows.bat (Windows)")
        print("   • Run ./install.sh (Linux/Mac)\n")
        print("2. Test your camera with option 2 (Test Camera Connection)\n")
        print("3. Launch the main application with option 1\n")
        print("4. Default login: admin / admin123\n")
        print("5. Add students and start monitoring!\n")
        input("Press Enter to continue to main menu...")

if __name__ == "__main__":
    try:
        check_first_run()
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        input("\nPress Enter to exit...")
