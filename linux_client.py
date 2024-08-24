import socket
import pyautogui
import mss
import io
import struct
import threading
import time
import sys
import os

DEFAULT_IP = "27.147.170.213"  # Replace this with your server's default IP
DEFAULT_PORT = 12345

class RemoteControlClient:
    def __init__(self, host=DEFAULT_IP, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.client_socket = None
        pyautogui.FAILSAFE = False

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

        self.receive_commands()

    def send_screenshots(self):
        with mss.mss() as sct:
            while True:
                screenshot = sct.shot()
                with open(screenshot, "rb") as image_file:
                    image_data = image_file.read()
                    size = len(image_data)
                    size_data = struct.pack('>I', size)
                    try:
                        self.client_socket.sendall(size_data)
                        self.client_socket.sendall(image_data)
                    except Exception as e:
                        print(f"Error sending screenshot: {e}")
                        break
                time.sleep(0.1)  # Adjust the delay between screenshots as needed

    def receive_commands(self):
        while True:
            try:
                command = self.client_socket.recv(1024).decode()
                if not command:
                    break
                self.execute_command(command)
            except Exception as e:
                print(f"Error receiving command: {e}")
                break
        print("Disconnected from server")
        print("Exiting in 10 seconds...")
        time.sleep(10)

    def execute_command(self, command):
        parts = command.split()
        action = parts[0]

        if action == "MOVE":
            x, y = map(int, parts[1:])
            pyautogui.moveTo(x, y)
        elif action == "CLICK":
            x, y = map(int, parts[1:])
            pyautogui.click(x, y)
        elif action == "KEYDOWN":
            key = parts[1]
            pyautogui.keyDown(key)
        elif action == "KEYUP":
            key = parts[1]
            pyautogui.keyUp(key)

def get_server_ip():
    user_input = input(f"Enter server IP address (press Enter to use default {DEFAULT_IP}): ").strip()
    return user_input if user_input else DEFAULT_IP

if __name__ == "__main__":
    server_ip = get_server_ip()
    client = RemoteControlClient(host=server_ip)
    client.start()
