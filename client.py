import socket
import pyautogui
import mss
import numpy as np
import cv2
import threading
import time
import sys
from queue import Queue
import struct

DEFAULT_IP = "27.147.170.213"  # Replace this with your server's default IP
DEFAULT_PORT = 12345

class RemoteControlClient:
    def __init__(self, host=DEFAULT_IP, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.client_socket = None
        pyautogui.FAILSAFE = False
        self.command_queue = Queue()
        self.last_frame_time = 0
        self.frame_count = 0
        self.fps = 0

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def start(self):
        if not self.connect():
            print("Failed to connect. Exiting in 10 seconds...")
            time.sleep(10)
            sys.exit(1)

        screenshot_thread = threading.Thread(target=self.send_screenshots)
        screenshot_thread.daemon = True
        screenshot_thread.start()

        command_thread = threading.Thread(target=self.process_commands)
        command_thread.daemon = True
        command_thread.start()

        self.receive_commands()

    def send_screenshots(self):
        with mss.mss() as sct:
            while True:
                start_time = time.time()

                # Capture screenshot
                screenshot = np.array(sct.grab(sct.monitors[0]))
                
                # Convert to JPEG
                _, buffer = cv2.imencode('.jpg', screenshot, [cv2.IMWRITE_JPEG_QUALITY, 80])
                jpg_as_text = buffer.tobytes()

                # Send size and then the image
                size = len(jpg_as_text)
                size_data = struct.pack('>I', size)
                try:
                    self.client_socket.sendall(size_data)
                    self.client_socket.sendall(jpg_as_text)
                except Exception as e:
                    print(f"Error sending screenshot: {e}")
                    break

                # Calculate and limit FPS
                self.frame_count += 1
                elapsed_time = time.time() - start_time
                sleep_time = max(0, (1 / 60) - elapsed_time)
                time.sleep(sleep_time)

                # Update FPS counter
                if time.time() - self.last_frame_time >= 1:
                    self.fps = self.frame_count
                    print(f"FPS: {self.fps}")
                    self.frame_count = 0
                    self.last_frame_time = time.time()

    def receive_commands(self):
        buffer = ""
        while True:
            try:
                data = self.client_socket.recv(4096).decode()
                if not data:
                    break
                buffer += data
                while '\n' in buffer:
                    command, buffer = buffer.split('\n', 1)
                    self.command_queue.put(command)
            except Exception as e:
                print(f"Error receiving command: {e}")
                break
        print("Disconnected from server")
        print("Exiting in 10 seconds...")
        time.sleep(10)

    def process_commands(self):
        while True:
            if not self.command_queue.empty():
                command = self.command_queue.get()
                self.execute_command(command)
            else:
                time.sleep(0.001)  # Minimal sleep to prevent CPU overuse

    def execute_command(self, command):
        parts = command.split()
        action = parts[0]

        try:
            if action == "MOVE":
                x, y = map(int, parts[1:])
                pyautogui.moveTo(x, y, duration=0)  # Instant move
            elif action == "CLICK":
                x, y = map(int, parts[1:])
                pyautogui.click(x, y)
            elif action == "RIGHTCLICK":
                x, y = map(int, parts[1:])
                pyautogui.rightClick(x, y)
            elif action == "KEYDOWN":
                key = parts[1]
                pyautogui.keyDown(key)
            elif action == "KEYUP":
                key = parts[1]
                pyautogui.keyUp(key)
        except Exception as e:
            print(f"Error executing command {command}: {e}")

def get_server_ip():
    user_input = input(f"Enter server IP address (press Enter to use default {DEFAULT_IP}): ").strip()
    return user_input if user_input else DEFAULT_IP

if __name__ == "__main__":
    server_ip = get_server_ip()
    client = RemoteControlClient(host=server_ip)
    client.start()
