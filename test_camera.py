"""
CCTV Camera Integration Helper
Test your CCTV/IP camera connection before using it in the main app
"""

import cv2
import sys

def test_camera(source):
    """Test camera connection and display feed"""
    print(f"Attempting to connect to camera: {source}")
    
    # Try to open camera
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print(f"✗ ERROR: Cannot open camera {source}")
        print("\nTroubleshooting tips:")
        print("1. Check if the camera is powered on and connected")
        print("2. Verify the IP address and port")
        print("3. Check username and password")
        print("4. Ensure your network allows the connection")
        print("5. Try accessing the camera URL in a browser first")
        return False
    
    print(f"✓ Camera connected successfully!")
    print("Press 'q' to quit")
    
    # Display feed
    frame_count = 0
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print(f"✗ Error reading frame after {frame_count} frames")
            break
        
        frame_count += 1
        
        # Add frame counter to display
        cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Resize for display if too large
        height, width = frame.shape[:2]
        if width > 1280:
            scale = 1280 / width
            frame = cv2.resize(frame, (1280, int(height * scale)))
        
        cv2.imshow('Camera Test Feed', frame)
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"\n✓ Successfully displayed {frame_count} frames")
    return True


def main():
    print("=" * 60)
    print("CCTV/IP Camera Connection Tester")
    print("=" * 60)
    print()
    
    print("Camera Source Options:")
    print("1. Laptop Camera (usually 0)")
    print("2. USB Camera (usually 1 or 2)")
    print("3. RTSP Stream (e.g., rtsp://username:password@192.168.1.100:554/stream)")
    print("4. HTTP Stream (e.g., http://192.168.1.100:8080/video)")
    print()
    
    # Get camera source
    source = input("Enter camera source (number or URL): ").strip()
    
    # Try to convert to int if it's a number
    try:
        source = int(source)
    except ValueError:
        pass  # It's a URL string
    
    print()
    test_camera(source)


# Common CCTV Camera URL Formats
COMMON_FORMATS = """
Common CCTV Camera URL Formats:
================================

Generic RTSP:
  rtsp://username:password@ip_address:port/stream

Hikvision:
  rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101
  rtsp://admin:password@192.168.1.100:554/Streaming/Channels/102 (Sub-stream)

Dahua:
  rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0
  rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=1 (Sub-stream)

Axis:
  rtsp://root:password@192.168.1.100/axis-media/media.amp

Foscam:
  rtsp://username:password@192.168.1.100:554/videoMain

Amcrest:
  rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0

TP-Link:
  rtsp://admin:password@192.168.1.100:554/stream1

D-Link:
  rtsp://admin:password@192.168.1.100/live.sdp

Reolink:
  rtsp://admin:password@192.168.1.100:554/h264Preview_01_main

Vivotek:
  rtsp://admin:password@192.168.1.100/live.sdp

Generic HTTP (MJPEG):
  http://192.168.1.100:8080/video
  http://username:password@192.168.1.100/cgi-bin/mjpeg

Notes:
- Replace 'username' and 'password' with actual credentials
- Replace 'ip_address' or '192.168.1.100' with camera's IP
- Main stream is higher quality, sub-stream is lower quality (faster)
- Port 554 is standard for RTSP
- Some cameras may use different ports (check manual)
"""


if __name__ == "__main__":
    print(COMMON_FORMATS)
    print()
    main()
