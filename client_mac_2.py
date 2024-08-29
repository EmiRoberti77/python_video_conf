import socket
import threading
import subprocess
import numpy as np
import cv2

# Server settings
server_ip = '127.0.0.1'
server_port = 8000

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Attempt to connect to the server
try:
    client_socket.connect((server_ip, server_port))
    print("Connected to server")
except socket.error as e:
    print(f"Failed to connect to server: {e}")
    exit(1)

def capture_and_send_video():
    # FFmpeg command for video capture using avfoundation with specified settings
    command = [
        'ffmpeg',
        '-f', 'avfoundation',  # Input format for macOS
        '-framerate', '30',  # Frame rate set to 30 fps
        '-video_size', '1280x720',  # Supported resolution set to 1280x720
        '-pixel_format', 'uyvy422',  # Use a supported pixel format
        '-i', '0',  # Use device 0, typically the default FaceTime HD Camera
        '-f', 'rawvideo',  # Output format
        'pipe:1'  # Output to stdout
    ]

    # Start the FFmpeg process
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("FFmpeg process started for video capture")

    frame_width, frame_height = 1280, 720
    bytes_per_pixel = 2  # 'uyvy422' format uses 2 bytes per pixel
    frame_size = frame_width * frame_height * bytes_per_pixel

    while True:
        try:
            # Read raw video frame from FFmpeg stdout
            frame_data = process.stdout.read(frame_size)
            
            if not frame_data:
                print("No video frame received from FFmpeg.")
                break

            # Send the raw video frame data to the server
            try:
                client_socket.sendall(frame_data)
            except socket.error as e:
                print(f"Error in video transmission: {e}")
                break

            # Convert frame data to a numpy array
            frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((frame_height, frame_width, 2))

            # Convert UYVY to BGR format for display using OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_UYVY)

            # Display frame using OpenCV
            cv2.imshow('Video Stream', frame_bgr)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exiting video display...")
                break
        except cv2.error as e:
            print(f"OpenCV error: {e}")
            continue  # Skip this frame if it fails

    # Clean up
    process.terminate()
    cv2.destroyAllWindows()
    client_socket.close()

if __name__ == "__main__":
    capture_and_send_video()