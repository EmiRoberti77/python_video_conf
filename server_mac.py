import socket
import threading
import cv2
import numpy as np

# Server settings
server_ip = '127.0.0.1'
server_port = 8000

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Enable socket reuse option to avoid 'address already in use' error on restart
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the server IP and port
try:
    server_socket.bind((server_ip, server_port))
    print(f"Server started on {server_ip}:{server_port}")
except socket.error as e:
    print(f"Failed to bind server socket: {e}")
    exit(1)

# Start listening for incoming connections
server_socket.listen(5)
print("Server is listening for connections...")

clients = []

def handle_client(client_socket):
    """
    Handles communication with a connected client.
    """
    data_buffer = b''
    frame_width, frame_height = 1280, 720
    bytes_per_pixel = 2  # 'uyvy422' format uses 2 bytes per pixel
    frame_size = frame_width * frame_height * bytes_per_pixel

    while True:
        try:
            # Receive data from the client
            data = client_socket.recv(4096)
            if not data:
                print("Client disconnected.")
                break

            data_buffer += data
            print(f"Received data size: {len(data)}, Buffer size: {len(data_buffer)}")

            # Process complete frames
            while len(data_buffer) >= frame_size:
                print(f"Processing frame of size: {frame_size}")
                # Extract a frame
                frame_data = data_buffer[:frame_size]
                data_buffer = data_buffer[frame_size:]

                try:
                    # Convert frame data to a numpy array
                    frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((frame_height, frame_width, 2))

                    # Print frame info for debugging
                    print(f"Frame shape: {frame.shape}, Frame dtype: {frame.dtype}")

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

        except ConnectionResetError:
            print("Connection reset by client.")
            break
        except Exception as e:
            print(f"An error occurred while handling client: {e}")
            break

    # Clean up client connection
    client_socket.close()
    clients.remove(client_socket)
    print("Client connection closed.")

def accept_clients():
    """
    Accepts new clients and starts a new thread to handle each client.
    """
    while True:
        try:
            client_socket, addr = server_socket.accept()
            print(f"Accepted new connection from {addr}.")
            clients.append(client_socket)

            # Start a new thread for each client
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()

        except Exception as e:
            print(f"Error accepting new client: {e}")

# Start accepting clients in the main thread
accept_clients_thread = threading.Thread(target=accept_clients)
accept_clients_thread.start()

# To safely shut down the server, handle signals or implement a shutdown mechanism