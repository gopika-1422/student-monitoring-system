# 🎓 Student Monitoring System - Quick Reference Guide

## 📦 Package Contents

1. **student_monitor_app.py** - Main application (GUI)
2. **test_camera.py** - Camera testing utility
3. **db_manager.py** - Database management utility
4. **requirements.txt** - Python dependencies
5. **install.sh** - Linux/Mac installation script
6. **install_windows.bat** - Windows installation script
7. **README.md** - Detailed documentation

## 🚀 Quick Start (3 Steps)

### Step 1: Install
**Windows:**
```batch
install_windows.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

### Step 2: Test Camera
```bash
python test_camera.py
```
Enter `0` for laptop camera, then press 'q' to quit

### Step 3: Run Application
```bash
python student_monitor_app.py
```
Login: admin / admin123

## 📸 Camera Setup

### Laptop Camera
- **Camera Index**: 0
- **No configuration needed**

### USB Camera
- **Camera Index**: 1 or 2
- **Plug in and test with test_camera.py**

### CCTV/IP Camera
Edit `student_monitor_app.py`, find `start_camera` method:

```python
# Replace this line:
self.camera = cv2.VideoCapture(camera_index)

# With this (for RTSP):
rtsp_url = "rtsp://username:password@192.168.1.100:554/stream"
self.camera = cv2.VideoCapture(rtsp_url)
```

**Common CCTV Formats:**
- Hikvision: `rtsp://admin:pass@192.168.1.100:554/Streaming/Channels/101`
- Dahua: `rtsp://admin:pass@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0`

## 👥 Adding Students

1. Login to application
2. Go to **"Manage Students"** tab
3. Fill in student details:
   - Roll Number (required)
   - Name (required)
   - Email, Phone, Department, Year (optional)
4. Click **"Select Photo"** - Choose a clear front-facing photo
5. Click **"Add Student"**

**Photo Requirements:**
- Clear, well-lit face
- Front-facing
- JPG, JPEG, or PNG format
- One face per photo

## 🎥 Live Monitoring

1. Go to **"Live Monitoring"** tab
2. Select camera source (0 for laptop)
3. Click **"Start Monitoring"**
4. Students will be automatically:
   - Detected
   - Recognized
   - Attendance marked
   - Activity tracked

## 📊 Viewing Attendance

1. Go to **"Attendance Records"** tab
2. Enter date (YYYY-MM-DD format)
3. Click **"Load Attendance"**

View shows:
- Student ID & Name
- Check-in time
- Check-out time (last seen)
- Activity level (Active/Inactive)

## 🛠️ Database Manager

Run the database manager for advanced operations:

```bash
python db_manager.py
```

**Features:**
1. View all students
2. View today's attendance
3. View attendance by date
4. View student history
5. Add authority users
6. View authority users
7. Generate statistics
8. Delete students

## 🔑 Default Login Credentials

- **Username**: admin
- **Password**: admin123

**⚠️ IMPORTANT**: Change this immediately in production!

## 📁 Data Storage

All data is stored locally in:
- `student_monitor.db` - SQLite database
- `student_images/` - Face encodings and photos

**Backup regularly!**

## 🐛 Common Issues & Solutions

### "Camera cannot be opened"
- ✅ Close other apps using camera
- ✅ Try different camera index (0, 1, 2)
- ✅ Check camera permissions
- ✅ Restart application

### "No face detected"
- ✅ Ensure good lighting
- ✅ Face should be front-facing
- ✅ Use higher quality photo
- ✅ Try different photo

### "Student not recognized"
- ✅ Re-register with better photo
- ✅ Ensure good lighting during monitoring
- ✅ Student should face camera
- ✅ Adjust face_recognition tolerance

### "Installation failed (dlib)"
**Windows:**
- Install Visual Studio Build Tools
- Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/

**Mac:**
- Install Xcode tools: `xcode-select --install`

**Linux:**
- Install: `sudo apt-get install build-essential`

### "Module not found"
```bash
pip install [module-name]
```

## 🎯 Best Practices

### For Best Recognition:
1. **Good Lighting**: Ensure classroom is well-lit
2. **Camera Position**: Mount at eye level, 2-3 meters from students
3. **Quality Photos**: Use high-resolution, clear photos for registration
4. **Regular Updates**: Update face encodings if student appearance changes significantly

### For Attendance:
1. **Morning Check-in**: Start monitoring when class begins
2. **End of Day**: Check-out times are automatically updated when students leave
3. **Regular Backups**: Backup database weekly
4. **Review Reports**: Check attendance reports daily

### For Security:
1. **Change Default Password**: Immediately after installation
2. **Limit Access**: Only authorize necessary personnel
3. **Secure Database**: Keep student_monitor.db secure
4. **Privacy Compliance**: Follow local data protection laws

## ⚙️ Configuration

### Adjust Activity Detection Sensitivity
In `student_monitor_app.py`:
```python
self.activity_threshold = 5  # Increase = less sensitive
```

### Adjust Face Recognition Tolerance
In `process_frame()` method:
```python
tolerance=0.6  # Lower = stricter (0.3-0.7 recommended)
```

### Change Camera Resolution
In `process_frame()`:
```python
small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
# Change fx and fy for different processing size
```

## 📞 Getting Help

1. **Check README.md** for detailed documentation
2. **Review error messages** in terminal/console
3. **Test camera** with test_camera.py first
4. **Check database** with db_manager.py

## 🔄 Regular Maintenance

### Daily:
- Check attendance records
- Verify camera is working
- Monitor activity levels

### Weekly:
- Backup database
- Review statistics
- Update student photos if needed

### Monthly:
- Clean database (remove old logs)
- Update authority users
- System performance check

## 📈 Future Enhancements

Potential features to add:
- Email notifications
- Excel export
- Mobile app
- Cloud sync
- Multi-class support
- Advanced analytics
- Behavior tracking
- Parent notifications

## ⚠️ Legal & Privacy

**Important Reminders:**
1. Obtain student consent for facial recognition
2. Comply with local data protection laws (GDPR, etc.)
3. Secure storage of biometric data
4. Transparent data usage policies
5. Right to opt-out mechanisms
6. Regular data audits

## 📋 Checklist for First Use

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (run install script)
- [ ] Camera tested (test_camera.py)
- [ ] Database initialized (runs automatically)
- [ ] Admin password changed
- [ ] First student added
- [ ] Camera monitoring tested
- [ ] Attendance records verified
- [ ] Backup strategy in place

## 🎓 Training Tips

### For Teachers/Staff:
1. Practice adding students in test environment
2. Understand activity monitoring indicators
3. Learn to generate and interpret reports
4. Know how to troubleshoot common issues

### For Students:
1. Register with clear, recent photo
2. Maintain consistent appearance
3. Face camera during attendance
4. Understand privacy implications

---

**Version**: 1.0  
**Support**: Check README.md for detailed documentation  
**License**: For educational and institutional use
