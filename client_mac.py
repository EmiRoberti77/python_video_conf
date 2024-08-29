import socket
import pyaudio
import threading
import subprocess
import time

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
CHUNK = 1024

# Initialize audio stream
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

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

def send_video():
    try:
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

        while True:
            video_frame = process.stdout.read(4096)  # Read video frame
            if not video_frame:
                print("No video frame received from FFmpeg.")
                break
            try:
                client_socket.sendall(video_frame)  # Send video frame to server
                time.sleep(0.01)  # Small delay to prevent overwhelming the server
            except socket.error as e:
                print(f"Error in video transmission: {e}")
                break

    except Exception as e:
        print(f"Error in video transmission setup: {e}")

def send_audio():
    try:
        while True:
            audio_data = stream.read(CHUNK)
            try:
                client_socket.sendall(audio_data)
                time.sleep(0.01)  # Small delay to prevent overwhelming the server
            except socket.error as e:
                print(f"Error in audio transmission: {e}")
                break
    except Exception as e:
        print(f"Error in audio transmission setup: {e}")

# Create threads for sending video and audio
video_thread = threading.Thread(target=send_video)
audio_thread = threading.Thread(target=send_audio)

video_thread.start()
audio_thread.start()

video_thread.join()
audio_thread.join()

# Close the socket after threads finish
client_socket.close()