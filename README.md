# Student Monitoring System - Setup Guide

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8 or higher
- Laptop with camera
- Windows/Mac/Linux OS

### Installation Steps

#### Step 1: Install Python Dependencies

For **Windows**:
```bash
# Install Visual Studio Build Tools first (required for dlib)
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Then install packages
pip install opencv-python
pip install numpy
pip install Pillow
pip install cmake
pip install dlib
pip install face-recognition
```

For **Mac**:
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install cmake
brew install cmake

# Install packages
pip3 install opencv-python numpy Pillow cmake dlib face-recognition
```

For **Linux (Ubuntu/Debian)**:
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip cmake libopencv-dev python3-opencv

# Install Python packages
pip3 install opencv-python numpy Pillow cmake dlib face-recognition
```

**Alternative (Easier) Installation**:
```bash
pip install -r requirements.txt
```

#### Step 2: Run the Application
```bash
python student_monitor_app.py
```

## 📋 System Features

### 1. **Face Recognition & Attendance**
- Automatic face detection and recognition
- Real-time attendance marking
- Multiple camera support (laptop camera, CCTV)

### 2. **Activity Monitoring**
- Detects student activity levels (Active/Inactive)
- Tracks student engagement
- Real-time monitoring dashboard

### 3. **Student Database**
- Store student personal information
- Upload and register student photos
- Face encoding storage

### 4. **Authority Access**
- Secure login system
- View and manage attendance records
- Generate reports

### 5. **Reports & Analytics**
- Daily attendance reports
- Weekly statistics
- Activity level tracking

## 🎯 How to Use

### First Time Setup

1. **Login**
   - Default credentials:
     - Username: `admin`
     - Password: `admin123`

2. **Add Students**
   - Go to "Manage Students" tab
   - Fill in student information
   - Upload a clear photo of student's face
   - Click "Add Student"

3. **Start Monitoring**
   - Go to "Live Monitoring" tab
   - Select camera source (0 for laptop camera)
   - Click "Start Monitoring"
   - Students will be automatically recognized and attendance marked

4. **View Attendance**
   - Go to "Attendance Records" tab
   - Select date
   - Click "Load Attendance"

5. **Generate Reports**
   - Go to "Reports" tab
   - Click "Generate Report"

## 📷 Camera Configuration

### Using Laptop Camera
- Camera Index: `0` (default)
- This is usually the built-in webcam

### Using External USB Camera
- Camera Index: `1` or `2`
- Connect USB camera and try different indices

### Using CCTV Camera (IP Camera)
To use CCTV/IP camera, you need to modify the code:

In the `start_camera` method, replace:
```python
self.camera = cv2.VideoCapture(camera_index)
```

With:
```python
# For RTSP stream
rtsp_url = "rtsp://username:password@ip_address:port/stream"
self.camera = cv2.VideoCapture(rtsp_url)

# For HTTP stream
http_url = "http://ip_address:port/video"
self.camera = cv2.VideoCapture(http_url)
```

Example RTSP URLs:
- Generic: `rtsp://admin:password@192.168.1.100:554/stream1`
- Hikvision: `rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101`
- Dahua: `rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0`

## 📊 Database Structure

The system creates a SQLite database `student_monitor.db` with:

### Tables:
1. **students** - Student information and face encodings
2. **attendance** - Daily attendance records
3. **activity_logs** - Activity detection logs
4. **authorities** - Authorized users

## 🛠️ Troubleshooting

### Camera Not Opening
- Check if camera is being used by another application
- Try different camera indices (0, 1, 2)
- Restart the application
- Check camera permissions in OS settings

### Face Not Recognized
- Ensure good lighting conditions
- Student photo should be clear and front-facing
- Re-register student with better photo
- Reduce tolerance in face_recognition.compare_faces()

### Slow Performance
- Reduce camera resolution in code
- Process every 2nd or 3rd frame
- Use smaller frame size for processing

### Installation Issues (dlib)
- **Windows**: Install Visual Studio Build Tools
- **Mac**: Install Xcode command line tools: `xcode-select --install`
- **Linux**: Install build-essential: `sudo apt-get install build-essential`

## 🔐 Security Notes

- Change default admin password immediately
- Store database securely
- Use strong passwords for authorities
- Limit camera access permissions

## 📁 File Structure

```
student_monitoring_system/
│
├── student_monitor_app.py      # Main application
├── requirements.txt              # Python dependencies
├── student_monitor.db           # Database (auto-created)
├── face_encodings.pkl           # Face encodings (auto-created)
│
└── student_images/              # Student photos & encodings
    ├── encoding_1.pkl
    ├── encoding_2.pkl
    └── ...
```

## 🎨 Customization

### Change Activity Detection Sensitivity
In `StudentMonitorSystem.__init__()`:
```python
self.activity_threshold = 5  # Increase for less sensitive, decrease for more
```

### Change Face Recognition Tolerance
In `process_frame()`:
```python
matches = face_recognition.compare_faces(
    self.known_face_encodings, 
    face_encoding, 
    tolerance=0.6  # Lower = stricter, Higher = more lenient
)
```

### Add More Authority Users
Run this SQL in the database:
```sql
INSERT INTO authorities (username, password, full_name, role)
VALUES ('teacher1', 'pass123', 'John Doe', 'Teacher');
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Check camera permissions
4. Review error messages in console

## 🔄 Updates & Improvements

Future enhancements can include:
- Email notifications for absent students
- Export reports to Excel/PDF
- Multi-class support
- Student behavior analytics
- Mobile app integration
- Cloud database sync

## ⚠️ Important Notes

1. **Privacy**: Ensure compliance with local privacy laws when using facial recognition
2. **Data Protection**: Secure the database with proper backups
3. **Consent**: Obtain student consent before face registration
4. **Testing**: Test thoroughly before production use

---

**Version**: 1.0
**Last Updated**: February 2026
**Developed for**: Student Monitoring & Attendance System
